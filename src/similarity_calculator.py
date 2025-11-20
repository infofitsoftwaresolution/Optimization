import re
import json
import hashlib
from typing import Dict, Any, Optional, Tuple, List
from functools import lru_cache
import math

# Optional imports for advanced features
try:
    from sentence_transformers import SentenceTransformer
    import torch
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False

try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False

try:
    from scipy.spatial.distance import cosine as scipy_cosine
    import numpy as np
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

class RobustJSONParser:
    """Parse malformed JSON from LLM responses"""

    @staticmethod
    def extract_note_objects(text: str) -> List[Dict[str, Any]]:
        """Extract note objects from broken JSON"""
        try:
            obj = json.loads(text)
            if isinstance(obj, list) and obj and isinstance(obj[0], dict):
                if "linkId" in obj[0] or "result" in obj[0]:
                    return obj
            elif isinstance(obj, dict) and "linkId" in obj and "result" in obj:
                return [obj]
        except json.JSONDecodeError:
            pass
        
        return RobustJSONParser._extract_objects_regex(text)

    @staticmethod
    def _extract_objects_regex(text: str) -> List[Dict[str, Any]]:
        """Use regex to extract object-like structures from broken JSON"""
        objects = []
        brace_pattern = r'\{[^{}]*\}'
        brace_matches = re.finditer(brace_pattern, text, re.DOTALL)
        
        for match in brace_matches:
            obj_text = match.group(0)
            extracted = RobustJSONParser._parse_object_text(obj_text)
            if extracted and ("linkId" in extracted or "result" in extracted):
                objects.append(extracted)
        
        if not objects:
            objects = RobustJSONParser._extract_from_pairs(text)
        
        return objects

    @staticmethod
    def _parse_object_text(obj_text: str) -> Dict[str, Any]:
        """Parse a single object text into dictionary"""
        content = obj_text.strip()
        if content.startswith('{'):
            content = content[1:]
        if content.endswith('}'):
            content = content[:-1]
        
        if not content:
            return {}
        
        obj = {}
        lines = content.split('\n')
        
        current_key = None
        current_value = ""
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            line = line.rstrip(',')
            
            if ':' in line:
                if current_key:
                    obj[current_key] = RobustJSONParser._parse_value(current_value)
                
                key_part, value_part = line.split(':', 1)
                current_key = key_part.strip().strip('"\'')
                current_value = value_part.strip()
            else:
                if current_key and line:
                    current_value += " " + line
        
        if current_key:
            obj[current_key] = RobustJSONParser._parse_value(current_value)
        
        return obj

    @staticmethod
    def _parse_value(value_str: str) -> Any:
        """Parse value, handling multiple types"""
        value_str = value_str.strip()
        
        if not value_str:
            return None
        
        if value_str.lower() == 'true':
            return True
        if value_str.lower() == 'false':
            return False
        if value_str.lower() == 'null':
            return None
        
        if not (value_str.startswith('"') or value_str.startswith("'")):
            try:
                if '.' in value_str:
                    return float(value_str)
                else:
                    return int(value_str)
            except ValueError:
                pass
        
        try:
            return json.loads(value_str)
        except:
            pass
        
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
        
        return value_str

    @staticmethod
    def _extract_from_pairs(text: str) -> List[Dict[str, Any]]:
        """Fallback: Extract key-value pairs directly"""
        objects = []
        linkid_pattern = r'["\']?linkId["\']?\s*:\s*["\']?([^",}\n]+)'
        result_pattern = r'["\']?result["\']?\s*:\s*["\']?([^",}\n]+)'
        
        linkid_matches = list(re.finditer(linkid_pattern, text))
        result_matches = list(re.finditer(result_pattern, text))
        
        for linkid_match in linkid_matches:
            linkid_value = linkid_match.group(1).strip().strip('"\'')
            nearest_result = None
            for result_match in result_matches:
                if result_match.start() > linkid_match.start():
                    nearest_result = result_match.group(1).strip().strip('"\'')
                    break
            
            obj = {"linkId": linkid_value}
            if nearest_result:
                obj["result"] = nearest_result
            
            objects.append(obj)
        
        return objects

    @staticmethod
    def is_note_audit(text: str) -> bool:
        """Detect if response is Note Audit format"""
        objects = RobustJSONParser.extract_note_objects(text)
        
        if not objects:
            return False
        
        for obj in objects:
            if "linkId" in obj and "result" in obj:
                return True
        
        return False

class EnhancedSimilarityCalculator:
    def __init__(
        self,
        use_semantic: bool = False,
        semantic_model: str = "all-MiniLM-L6-v2",
        weights: Optional[Dict[str, float]] = None,
        cache_size: int = 1000
    ):
        
        self.use_semantic = use_semantic and SEMANTIC_AVAILABLE
        self.cache_size = cache_size
        
        # Default weights (can be customized per use case)
        self.weights = weights or {
            'semantic': 0.40 if self.use_semantic else 0.0,
            'cosine': 0.30 if not self.use_semantic else 0.20,
            'jaccard': 0.20,
            'ngram': 0.15,
            'levenshtein': 0.15 if not self.use_semantic else 0.05
        }
        
        # Normalize weights to sum to 1.0
        total_weight = sum(self.weights.values())
        self.weights = {k: v / total_weight for k, v in self.weights.items()}
        
        # Load semantic model if enabled
        self.semantic_model = None
        if self.use_semantic:
            try:
                self.semantic_model = SentenceTransformer(semantic_model)
            except Exception as e:
                self.use_semantic = False
                self.weights['semantic'] = 0.0
                self.weights['cosine'] = 0.35
                total_weight = sum(self.weights.values())
                self.weights = {k: v / total_weight for k, v in self.weights.items()}
    
    def calculate_similarity(
        self,
        master_response: str,
        candidate_response: str,
        method: str = "combined",
        return_details: bool = False
    ) -> Dict[str, Any]:
        
        if not master_response or not candidate_response:
            return {
                "similarity_score": 0.0,
                "similarity_percentage": 0.0,
                "method": method,
                "error": "Empty response(s)"
            }
        
        if master_response == candidate_response:
            return {
                "similarity_score": 1.0,
                "similarity_percentage": 100.0,
                "method": method,
                "note": "Identical responses"
            }
        
        is_json_master = self._is_json(master_response)
        is_json_candidate = self._is_json(candidate_response)
        
        if method == "combined" and is_json_master and is_json_candidate:
            method = "json_aware"
        
        if method == "json_aware":
            return self._calculate_json_similarity(master_response, candidate_response, return_details)
        elif method == "semantic":
            return self._calculate_semantic_similarity(master_response, candidate_response)
        elif method == "combined":
            return self._calculate_combined_similarity(master_response, candidate_response, return_details)
        elif method == "cosine":
            return self._single_method_result("cosine", master_response, candidate_response)
        elif method == "jaccard":
            return self._single_method_result("jaccard", master_response, candidate_response)
        elif method == "ngram":
            return self._single_method_result("ngram", master_response, candidate_response)
        elif method == "levenshtein":
            return self._single_method_result("levenshtein", master_response, candidate_response)
        else:
            raise ValueError(f"Unknown similarity method: {method}")
    
    def _calculate_combined_similarity(
        self,
        text1: str,
        text2: str,
        return_details: bool = False
    ) -> Dict[str, Any]:
        text1_norm = self._normalize_text(text1)
        text2_norm = self._normalize_text(text2)
        
        scores = {}
        
        if self.use_semantic and self.weights.get('semantic', 0) > 0:
            scores['semantic'] = self._semantic_similarity(text1, text2)
        
        if self.weights.get('cosine', 0) > 0:
            scores['cosine'] = self._cosine_similarity(text1_norm, text2_norm)
        
        if self.weights.get('jaccard', 0) > 0:
            scores['jaccard'] = self._jaccard_similarity(text1_norm, text2_norm)
        
        if self.weights.get('ngram', 0) > 0:
            scores['ngram'] = self._ngram_similarity(text1_norm, text2_norm)
        
        if self.weights.get('levenshtein', 0) > 0:
            scores['levenshtein'] = self._levenshtein_similarity_fast(text1_norm, text2_norm)
        
        combined_score = sum(scores[method] * self.weights.get(method, 0) 
                           for method in scores.keys())
        
        result = {
            "similarity_score": combined_score,
            "similarity_percentage": round(combined_score * 100, 2),
            "method": "combined",
        }
        
        if return_details:
            result["details"] = {
                method: {
                    "score": round(score * 100, 2),
                    "weight": round(self.weights.get(method, 0) * 100, 2),
                    "contribution": round(score * self.weights.get(method, 0) * 100, 2)
                }
                for method, score in scores.items()
            }
            result["weights_used"] = {k: round(v * 100, 2) for k, v in self.weights.items() if v > 0}
        
        return result
    
    def _calculate_json_similarity(
        self,
        json1: str,
        json2: str,
        return_details: bool = False
    ) -> Dict[str, Any]:
        try:
            obj1 = json.loads(json1)
            obj2 = json.loads(json2)
            
            structural_score = self._json_structural_similarity(obj1, obj2)
            content_score = self._json_content_similarity(obj1, obj2)
            
            combined_score = (content_score * 0.7) + (structural_score * 0.3)
            
            result = {
                "similarity_score": combined_score,
                "similarity_percentage": round(combined_score * 100, 2),
                "method": "json_aware",
                "is_json": True
            }
            
            if return_details:
                result["details"] = {
                    "structural_similarity": round(structural_score * 100, 2),
                    "content_similarity": round(content_score * 100, 2)
                }
            
            return result
            
        except json.JSONDecodeError:
            return self._calculate_combined_similarity(json1, json2, return_details)
    
    def _semantic_similarity(self, text1: str, text2: str) -> float:
        if not self.use_semantic or not self.semantic_model:
            return 0.0
        
        try:
            embedding1 = self.semantic_model.encode(text1, convert_to_tensor=True)
            embedding2 = self.semantic_model.encode(text2, convert_to_tensor=True)
            
            similarity = torch.nn.functional.cosine_similarity(
                embedding1.unsqueeze(0),
                embedding2.unsqueeze(0)
            ).item()
            
            return (similarity + 1) / 2
            
        except Exception as e:
            return 0.0
    
    @lru_cache(maxsize=1000)
    def _cosine_similarity(self, text1: str, text2: str) -> float:
        words1 = text1.split()
        words2 = text2.split()
        
        all_words = set(words1 + words2)
        
        if not all_words:
            return 1.0 if text1 == text2 else 0.0
        
        vec1 = [words1.count(word) for word in all_words]
        vec2 = [words2.count(word) for word in all_words]
        
        if SCIPY_AVAILABLE:
            try:
                vec1_arr = np.array(vec1)
                vec2_arr = np.array(vec2)
                similarity = 1 - scipy_cosine(vec1_arr, vec2_arr)
                return max(0.0, similarity)
            except:
                pass
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    @lru_cache(maxsize=1000)
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _ngram_similarity(self, text1: str, text2: str, n: int = 2) -> float:
        def get_ngrams(text: str, n: int) -> set:
            return set(text[i:i+n] for i in range(len(text) - n + 1))
        
        char_ngrams1 = get_ngrams(text1, n)
        char_ngrams2 = get_ngrams(text2, n)
        
        if not char_ngrams1 and not char_ngrams2:
            return 1.0
        
        intersection = len(char_ngrams1.intersection(char_ngrams2))
        union = len(char_ngrams1.union(char_ngrams2))
        
        if union == 0:
            return 0.0
        
        char_sim = intersection / union
        
        words1 = text1.split()
        words2 = text2.split()
        
        word_bigrams1 = set(zip(words1[:-1], words1[1:]))
        word_bigrams2 = set(zip(words2[:-1], words2[1:]))
        
        if word_bigrams1 or word_bigrams2:
            word_intersection = len(word_bigrams1.intersection(word_bigrams2))
            word_union = len(word_bigrams1.union(word_bigrams2))
            word_sim = word_intersection / word_union if word_union > 0 else 0.0
        else:
            word_sim = 0.0
        
        return (char_sim * 0.6) + (word_sim * 0.4)
    
    def _levenshtein_similarity_fast(self, text1: str, text2: str) -> float:
        if RAPIDFUZZ_AVAILABLE:
            similarity = fuzz.ratio(text1, text2) / 100.0
            return similarity
        else:
            return self._levenshtein_similarity(text1, text2)
    
    @lru_cache(maxsize=1000)
    def _levenshtein_similarity(self, text1: str, text2: str) -> float:
        def levenshtein_distance(s1: str, s2: str) -> int:
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        distance = levenshtein_distance(text1, text2)
        max_len = max(len(text1), len(text2))
        
        if max_len == 0:
            return 1.0
        
        similarity = 1.0 - (distance / max_len)
        return max(0.0, similarity)
    
    def _json_structural_similarity(self, obj1: Any, obj2: Any) -> float:
        if type(obj1) != type(obj2):
            return 0.0
        
        if not isinstance(obj1, (dict, list)):
            return 1.0 if obj1 == obj2 else 0.0
        
        if isinstance(obj1, dict):
            keys1 = set(obj1.keys())
            keys2 = set(obj2.keys())
            
            if not keys1 and not keys2:
                return 1.0
            
            key_intersection = len(keys1.intersection(keys2))
            key_union = len(keys1.union(keys2))
            key_similarity = key_intersection / key_union if key_union > 0 else 0.0
            
            if key_intersection > 0:
                struct_scores = []
                for key in keys1.intersection(keys2):
                    score = self._json_structural_similarity(obj1[key], obj2[key])
                    struct_scores.append(score)
                nested_similarity = sum(struct_scores) / len(struct_scores)
            else:
                nested_similarity = 0.0
            
            return (key_similarity * 0.5) + (nested_similarity * 0.5)
        
        if isinstance(obj1, list):
            if len(obj1) != len(obj2):
                return max(0.0, 1.0 - abs(len(obj1) - len(obj2)) / max(len(obj1), len(obj2)))
            
            if not obj1 and not obj2:
                return 1.0
            
            scores = [self._json_structural_similarity(obj1[i], obj2[i]) 
                     for i in range(len(obj1))]
            return sum(scores) / len(scores) if scores else 0.0
        
        return 0.0
    
    def _json_content_similarity(self, obj1: Any, obj2: Any) -> float:
        str1 = self._flatten_json_to_text(obj1)
        str2 = self._flatten_json_to_text(obj2)
        
        return self._cosine_similarity(str1, str2)
    
    def _flatten_json_to_text(self, obj: Any) -> str:
        if isinstance(obj, dict):
            parts = []
            for key in sorted(obj.keys()):
                value_text = self._flatten_json_to_text(obj[key])
                parts.append(f"{key} {value_text}")
            return " ".join(parts)
        elif isinstance(obj, list):
            return " ".join(self._flatten_json_to_text(item) for item in obj)
        else:
            return str(obj)
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> Dict[str, Any]:
        if not self.use_semantic:
            return {
                "similarity_score": 0.0,
                "similarity_percentage": 0.0,
                "method": "semantic",
                "error": "Semantic similarity not available"
            }
        
        score = self._semantic_similarity(text1, text2)
        return {
            "similarity_score": score,
            "similarity_percentage": round(score * 100, 2),
            "method": "semantic",
        }
    
    def _single_method_result(self, method: str, text1: str, text2: str) -> Dict[str, Any]:
        text1_norm = self._normalize_text(text1)
        text2_norm = self._normalize_text(text2)
        
        if method == "cosine":
            score = self._cosine_similarity(text1_norm, text2_norm)
        elif method == "jaccard":
            score = self._jaccard_similarity(text1_norm, text2_norm)
        elif method == "ngram":
            score = self._ngram_similarity(text1_norm, text2_norm)
        elif method == "levenshtein":
            score = self._levenshtein_similarity_fast(text1_norm, text2_norm)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return {
            "similarity_score": score,
            "similarity_percentage": round(score * 100, 2),
            "method": method,
        }
    
    @staticmethod
    @lru_cache(maxsize=2000)
    def _normalize_text(text: str) -> str:
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    @staticmethod
    def _is_json(text: str) -> bool:
        try:
            json.loads(text.strip())
            return True
        except (json.JSONDecodeError, TypeError, ValueError):
            return False


class SimilarityCalculator(EnhancedSimilarityCalculator):
    
    def __init__(self):
        super().__init__(use_semantic=False)
    
    def is_note_audit_response(self, text: str) -> bool:
        
        """
        Detect Note Audit using robust parser.
        Handles broken/malformed JSON from LLM responses.
        """
        return RobustJSONParser.is_note_audit(text)
    
    def extract_response_text(self, response: str) -> str:
        try:
            obj = json.loads(response)
            
            # Try common response keys in order of preference
            for key in ["response", "message", "text", "output", "answer", "content"]:
                if isinstance(obj, dict) and key in obj:
                    return str(obj[key]).strip()

            # If no common key found and it's a dict, flatten all values
            if isinstance(obj, dict):
                values = [str(v).strip() for v in obj.values() if v]
                return " ".join(values)
            
            # If it's a list, convert to string
            if isinstance(obj, list):
                return " ".join(str(item) for item in obj)

            # Fallback to string representation
            return str(obj).strip()
        except:
            # If not JSON, return as-is
            return response.strip()
    
    def extract_noteaudit_result(self, response_text: str) -> str:
        """
        For Note Audit responses, extract only the 'result' field.
        Falls back to full text if JSON parsing fails.
        """
        try:
            obj = json.loads(response_text)

            if isinstance(obj, dict) and "result" in obj:
                return str(obj["result"])

            if isinstance(obj, list):
                results = []
                for item in obj:
                    if isinstance(item, dict) and "result" in item:
                        results.append(str(item["result"]))
                return " ".join(results) if results else response_text

            return response_text
        except:
            return response_text
    
    def calculate_noteaudit_similarity(self, master_response: str, candidate_response: str) -> Dict[str, Any]:
        
        try:
            master_obj = json.loads(master_response)
            candidate_obj = json.loads(candidate_response)
            
            if isinstance(master_obj, dict):
                master_notes = [master_obj]
            elif isinstance(master_obj, list):
                master_notes = master_obj
            else:
                return self._error_result_noteaudit("Invalid master response format")
            
            if isinstance(candidate_obj, dict):
                candidate_notes = [candidate_obj]
            elif isinstance(candidate_obj, list):
                candidate_notes = candidate_obj
            else:
                return self._error_result_noteaudit("Invalid candidate response format")
            
            master_map = {}
            for note in master_notes:
                if isinstance(note, dict) and "linkId" in note and "result" in note:
                    link_id = str(note["linkId"])
                    result = str(note["result"]).strip().lower()
                    master_map[link_id] = result
            
            candidate_map = {}
            for note in candidate_notes:
                if isinstance(note, dict) and "linkId" in note and "result" in note:
                    link_id = str(note["linkId"])
                    result = str(note["result"]).strip().lower()
                    candidate_map[link_id] = result
            
            common_link_ids = set(master_map.keys()).intersection(set(candidate_map.keys()))
            
            if not common_link_ids:
                return {
                    "similarity_score": 0.0,
                    "similarity_percentage": 0.0,
                    "total_notes": max(len(master_map), len(candidate_map)),
                    "matching_notes": 0,
                    "mismatched_notes": max(len(master_map), len(candidate_map)),
                    "method": "noteaudit_exact_match",
                    "error": "No common linkIds found"
                }
            
            matching_count = 0
            mismatched_count = 0
            
            for link_id in common_link_ids:
                master_result = master_map[link_id]
                candidate_result = candidate_map[link_id]
                
                if master_result == candidate_result:
                    matching_count += 1
                else:
                    mismatched_count += 1
            
            total_notes = len(common_link_ids)
            similarity_score = matching_count / total_notes if total_notes > 0 else 0.0
            similarity_percentage = similarity_score * 100.0
            
            return {
                "similarity_score": similarity_score,
                "similarity_percentage": round(similarity_percentage, 2),
                "total_notes": total_notes,
                "matching_notes": matching_count,
                "mismatched_notes": mismatched_count,
                "method": "noteaudit_exact_match",
                "note": f"{matching_count}/{total_notes} notes match exactly"
            }
            
        except json.JSONDecodeError as e:
            return self._error_result_noteaudit(f"JSON parsing error: {str(e)}")
        except Exception as e:
            return self._error_result_noteaudit(f"Error: {str(e)}")
    
    def _error_result_noteaudit(self, error_msg: str) -> Dict[str, Any]:
        """Helper to return consistent error format for note audit."""
        return {
            "similarity_score": 0.0,
            "similarity_percentage": 0.0,
            "total_notes": 0,
            "matching_notes": 0,
            "mismatched_notes": 0,
            "method": "noteaudit_exact_match",
            "error": error_msg
        }


if __name__ == "__main__":
    print("="*70)
    print("Enhanced Similarity Calculator - Examples")
    print("="*70)
    
    calc = SimilarityCalculator()
    result = calc.calculate_similarity(
        "The cat sat on the mat",
        "The cat sat on the mat"
    )
    print(f"\n1. Identical texts: {result['similarity_percentage']}%")
    
    result = calc.calculate_similarity(
        "The cat sat on the mat",
        "A dog stood on the floor"
    )
    print(f"2. Different texts: {result['similarity_percentage']}%")
    
    if SEMANTIC_AVAILABLE:
        calc_semantic = EnhancedSimilarityCalculator(use_semantic=True)
        result = calc_semantic.calculate_similarity(
            "The cat sat on the mat",
            "A feline rested on the rug",
            return_details=True
        )
        print(f"\n3. Semantic similarity (paraphrase): {result['similarity_percentage']}%")
    else:
        print("\n3. (Semantic similarity requires sentence-transformers)")
    
    json1 = '{"name": "John", "age": 30, "city": "New York"}'
    json2 = '{"age": 30, "name": "John", "city": "New York"}'
    result = calc.calculate_similarity(json1, json2, method="json_aware")
    print(f"\n4. JSON (same data, different order): {result['similarity_percentage']}%")
    
    print("\n5. Note Audit Example:")
    master = '[{"linkId":"1","result":"Normal"},{"linkId":"2","result":"Abnormal"}]'
    candidate = '[{"linkId":"1","result":"Normal"},{"linkId":"2","result":"Normal"}]'
    result = calc.calculate_noteaudit_similarity(master, candidate)
    print(f"   {result['matching_notes']}/{result['total_notes']} notes match = {result['similarity_percentage']}%")
    
    print("\n" + "="*70)
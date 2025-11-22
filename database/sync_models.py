"""
Sync models from models.yaml configuration to database.
This script reads the models.yaml file and creates/updates models in the database.
"""

import sys
from pathlib import Path
import yaml
from dotenv import load_dotenv
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from database.connection import get_db_session
from database.models import User
from sqlalchemy import text
import uuid

def sync_models_from_yaml():
    """Sync models from models.yaml to database."""
    
    # Load models.yaml
    config_path = Path(__file__).parent.parent / "configs" / "models.yaml"
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return False
    
    print(f"Loading models from: {config_path}")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    models_config = config.get('models', [])
    region_name = config.get('region_name', 'us-east-2')
    
    print(f"Found {len(models_config)} models in configuration")
    
    try:
        with get_db_session() as session:
            # Map provider names to IDs
            provider_map = {}
            providers_result = session.execute(text("SELECT id, name FROM model_providers"))
            for row in providers_result:
                provider_map[row.name] = row.id
            
            print(f"\nAvailable providers: {list(provider_map.keys())}")
            
            # Sync each model
            synced_count = 0
            for model_config in models_config:
                model_name = model_config['name']
                provider_name = model_config['provider']
                bedrock_model_id = model_config.get('bedrock_model_id', '')
                tokenizer = model_config.get('tokenizer', 'heuristic')
                pricing = model_config.get('pricing', {})
                gen_params = model_config.get('generation_params', {})
                
                # Get provider ID
                if provider_name not in provider_map:
                    print(f"⚠️  Provider '{provider_name}' not found, skipping model '{model_name}'")
                    continue
                
                provider_id = provider_map[provider_name]
                
                # Check if model exists
                result = session.execute(
                    text("SELECT id FROM models WHERE name = :name AND provider_id = :provider_id"),
                    {"name": model_name, "provider_id": provider_id}
                )
                existing = result.fetchone()
                
                if existing:
                    model_id = existing[0]
                    print(f"✓ Model '{model_name}' already exists (ID: {model_id})")
                else:
                    # Create new model
                    model_id = uuid.uuid4()
                    session.execute(
                        text("""
                            INSERT INTO models (id, name, provider_id, bedrock_model_id, tokenizer_type, region_name, is_active)
                            VALUES (:id, :name, :provider_id, :bedrock_model_id, :tokenizer, :region, :is_active)
                        """),
                        {
                            "id": model_id,
                            "name": model_name,
                            "provider_id": provider_id,
                            "bedrock_model_id": bedrock_model_id,
                            "tokenizer": tokenizer,
                            "region": region_name,
                            "is_active": True
                        }
                    )
                    print(f"✓ Created model '{model_name}' (ID: {model_id})")
                
                # Sync pricing
                if pricing:
                    input_price = pricing.get('input_per_1k_tokens_usd', 0)
                    output_price = pricing.get('output_per_1k_tokens_usd', 0)
                    
                    # Check if pricing exists
                    pricing_result = session.execute(
                        text("""
                            SELECT id FROM model_pricing 
                            WHERE model_id = :model_id AND effective_to IS NULL
                        """),
                        {"model_id": model_id}
                    )
                    existing_pricing = pricing_result.fetchone()
                    
                    if not existing_pricing:
                        session.execute(
                            text("""
                                INSERT INTO model_pricing (model_id, input_per_1k_tokens_usd, output_per_1k_tokens_usd)
                                VALUES (:model_id, :input_price, :output_price)
                            """),
                            {
                                "model_id": model_id,
                                "input_price": input_price,
                                "output_price": output_price
                            }
                        )
                        print(f"  ✓ Added pricing for '{model_name}'")
                
                # Sync generation parameters
                if gen_params:
                    max_tokens = gen_params.get('max_tokens', 512)
                    temperature = gen_params.get('temperature', 0.7)
                    top_p = gen_params.get('top_p', 0.95)
                    
                    # Check if params exist
                    params_result = session.execute(
                        text("""
                            SELECT id FROM model_generation_params 
                            WHERE model_id = :model_id AND effective_to IS NULL
                        """),
                        {"model_id": model_id}
                    )
                    existing_params = params_result.fetchone()
                    
                    if not existing_params:
                        session.execute(
                            text("""
                                INSERT INTO model_generation_params (model_id, max_tokens, temperature, top_p)
                                VALUES (:model_id, :max_tokens, :temperature, :top_p)
                            """),
                            {
                                "model_id": model_id,
                                "max_tokens": max_tokens,
                                "temperature": temperature,
                                "top_p": top_p
                            }
                        )
                        print(f"  ✓ Added generation params for '{model_name}'")
                
                synced_count += 1
                session.commit()
            
            print(f"\n✅ Successfully synced {synced_count} models to database")
            return True
            
    except Exception as e:
        print(f"❌ Error syncing models: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Syncing Models from YAML to Database")
    print("=" * 60)
    print()
    
    success = sync_models_from_yaml()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Model sync completed!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Model sync failed!")
        print("=" * 60)
        sys.exit(1)


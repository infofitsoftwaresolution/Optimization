-- ============================================================================
-- Production Database Schema for BellaTrix LLM Evaluation Framework
-- Database: PostgreSQL 14+
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text similarity searches

-- ============================================================================
-- 1. USERS & AUTHENTICATION
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

-- ============================================================================
-- 2. MODELS & CONFIGURATIONS
-- ============================================================================

CREATE TABLE model_providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL, -- 'anthropic', 'meta', 'amazon', 'openai'
    display_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    provider_id UUID NOT NULL REFERENCES model_providers(id) ON DELETE RESTRICT,
    bedrock_model_id VARCHAR(255), -- AWS Bedrock model ID
    tokenizer_type VARCHAR(50) DEFAULT 'heuristic', -- 'anthropic', 'llama', 'gpt2', 'heuristic'
    region_name VARCHAR(50) DEFAULT 'us-east-2',
    is_active BOOLEAN DEFAULT TRUE,
    is_master_model BOOLEAN DEFAULT FALSE, -- True for reference models like ChatGPT
    use_inference_profile BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb, -- Store additional model config
    UNIQUE(name, provider_id)
);

CREATE INDEX idx_models_provider ON models(provider_id);
CREATE INDEX idx_models_active ON models(is_active);
CREATE INDEX idx_models_bedrock_id ON models(bedrock_model_id);

-- Model Pricing (supports price changes over time)
CREATE TABLE model_pricing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    input_per_1k_tokens_usd DECIMAL(10, 6) NOT NULL,
    output_per_1k_tokens_usd DECIMAL(10, 6) NOT NULL,
    effective_from TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    effective_to TIMESTAMP WITH TIME ZONE, -- NULL means current pricing
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_model_pricing_model ON model_pricing(model_id);
CREATE INDEX idx_model_pricing_effective ON model_pricing(effective_from, effective_to);

-- Model Generation Parameters (supports parameter changes over time)
CREATE TABLE model_generation_params (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    max_tokens INTEGER DEFAULT 512,
    temperature DECIMAL(4, 2) DEFAULT 0.7,
    top_p DECIMAL(4, 2) DEFAULT 0.95,
    effective_from TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    effective_to TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_model_params_model ON model_generation_params(model_id);
CREATE INDEX idx_model_params_effective ON model_generation_params(effective_from, effective_to);

-- ============================================================================
-- 3. PROMPTS
-- ============================================================================

CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    prompt_text TEXT NOT NULL,
    prompt_hash VARCHAR(64), -- SHA-256 hash for deduplication
    source_type VARCHAR(50) DEFAULT 'manual', -- 'manual', 'csv', 'json', 'cloudwatch'
    source_file_name VARCHAR(255),
    expected_json BOOLEAN DEFAULT FALSE,
    tags TEXT[], -- Array of tags for categorization
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_prompts_user ON prompts(user_id);
CREATE INDEX idx_prompts_hash ON prompts(prompt_hash);
CREATE INDEX idx_prompts_source ON prompts(source_type);
CREATE INDEX idx_prompts_created ON prompts(created_at);
CREATE INDEX idx_prompts_tags ON prompts USING GIN(tags); -- GIN index for array search

-- ============================================================================
-- 4. EVALUATION RUNS
-- ============================================================================

CREATE TABLE evaluation_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id VARCHAR(50) UNIQUE NOT NULL, -- Human-readable run ID
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    name VARCHAR(255), -- Optional run name/description
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed', 'cancelled'
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    total_prompts INTEGER DEFAULT 0,
    total_models INTEGER DEFAULT 0,
    total_evaluations INTEGER DEFAULT 0,
    successful_evaluations INTEGER DEFAULT 0,
    failed_evaluations INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_eval_runs_user ON evaluation_runs(user_id);
CREATE INDEX idx_eval_runs_status ON evaluation_runs(status);
CREATE INDEX idx_eval_runs_started ON evaluation_runs(started_at);
CREATE INDEX idx_eval_runs_run_id ON evaluation_runs(run_id);

-- ============================================================================
-- 5. EVALUATION METRICS (Raw Metrics)
-- ============================================================================

CREATE TABLE evaluation_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID NOT NULL REFERENCES evaluation_runs(id) ON DELETE CASCADE,
    model_id UUID NOT NULL REFERENCES models(id) ON DELETE RESTRICT,
    prompt_id UUID NOT NULL REFERENCES prompts(id) ON DELETE RESTRICT,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Token metrics
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    
    -- Performance metrics
    latency_ms DECIMAL(10, 2) NOT NULL DEFAULT 0,
    
    -- Cost metrics
    cost_usd_input DECIMAL(10, 6) NOT NULL DEFAULT 0,
    cost_usd_output DECIMAL(10, 6) NOT NULL DEFAULT 0,
    cost_usd_total DECIMAL(10, 6) NOT NULL DEFAULT 0,
    
    -- Response validation
    json_valid BOOLEAN, -- NULL = not applicable, TRUE = valid, FALSE = invalid
    response_text TEXT, -- Full response text (can be large)
    cleaned_response TEXT, -- Cleaned/parsed JSON if applicable
    original_response TEXT, -- Original response for debugging
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'success', -- 'success', 'error'
    error_message TEXT,
    
    -- Timestamps
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_eval_metrics_run ON evaluation_metrics(run_id);
CREATE INDEX idx_eval_metrics_model ON evaluation_metrics(model_id);
CREATE INDEX idx_eval_metrics_prompt ON evaluation_metrics(prompt_id);
CREATE INDEX idx_eval_metrics_user ON evaluation_metrics(user_id);
CREATE INDEX idx_eval_metrics_status ON evaluation_metrics(status);
CREATE INDEX idx_eval_metrics_evaluated ON evaluation_metrics(evaluated_at);
CREATE INDEX idx_eval_metrics_cost ON evaluation_metrics(cost_usd_total);
CREATE INDEX idx_eval_metrics_latency ON evaluation_metrics(latency_ms);

-- Composite indexes for common queries
CREATE INDEX idx_eval_metrics_run_model ON evaluation_metrics(run_id, model_id);
CREATE INDEX idx_eval_metrics_run_prompt ON evaluation_metrics(run_id, prompt_id);
CREATE INDEX idx_eval_metrics_model_status ON evaluation_metrics(model_id, status);

-- ============================================================================
-- 6. AGGREGATED REPORTS
-- ============================================================================

CREATE TABLE model_aggregated_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID NOT NULL REFERENCES evaluation_runs(id) ON DELETE CASCADE,
    model_id UUID NOT NULL REFERENCES models(id) ON DELETE RESTRICT,
    
    -- Counts
    total_count INTEGER NOT NULL DEFAULT 0,
    success_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    
    -- Token averages
    avg_input_tokens DECIMAL(10, 2) NOT NULL DEFAULT 0,
    avg_output_tokens DECIMAL(10, 2) NOT NULL DEFAULT 0,
    
    -- Latency percentiles
    p50_latency_ms DECIMAL(10, 2),
    p95_latency_ms DECIMAL(10, 2),
    p99_latency_ms DECIMAL(10, 2),
    min_latency_ms DECIMAL(10, 2),
    max_latency_ms DECIMAL(10, 2),
    
    -- JSON validation
    json_valid_count INTEGER DEFAULT 0,
    json_valid_percentage DECIMAL(5, 2) DEFAULT 0,
    
    -- Cost metrics
    avg_cost_usd_per_request DECIMAL(10, 6) NOT NULL DEFAULT 0,
    total_cost_usd DECIMAL(12, 6) NOT NULL DEFAULT 0,
    
    -- Timestamps
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(run_id, model_id)
);

CREATE INDEX idx_agg_metrics_run ON model_aggregated_metrics(run_id);
CREATE INDEX idx_agg_metrics_model ON model_aggregated_metrics(model_id);
CREATE INDEX idx_agg_metrics_cost ON model_aggregated_metrics(total_cost_usd);

-- ============================================================================
-- 7. MASTER MODEL COMPARISONS
-- ============================================================================

CREATE TABLE master_model_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES evaluation_runs(id) ON DELETE CASCADE,
    prompt_id UUID NOT NULL REFERENCES prompts(id) ON DELETE RESTRICT,
    model_id UUID NOT NULL REFERENCES models(id) ON DELETE RESTRICT, -- Master model
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    latency_ms DECIMAL(10, 2) NOT NULL DEFAULT 0,
    response_text TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'success',
    error_message TEXT,
    
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_master_eval_run ON master_model_evaluations(run_id);
CREATE INDEX idx_master_eval_prompt ON master_model_evaluations(prompt_id);
CREATE INDEX idx_master_eval_model ON master_model_evaluations(model_id);

-- ============================================================================
-- 8. SIMILARITY SCORES
-- ============================================================================

CREATE TABLE similarity_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID NOT NULL REFERENCES evaluation_runs(id) ON DELETE CASCADE,
    prompt_id UUID NOT NULL REFERENCES prompts(id) ON DELETE RESTRICT,
    model_a_id UUID NOT NULL REFERENCES models(id) ON DELETE RESTRICT,
    model_b_id UUID NOT NULL REFERENCES models(id) ON DELETE RESTRICT,
    master_model_id UUID REFERENCES models(id) ON DELETE SET NULL, -- Optional reference
    
    -- Similarity metrics
    cosine_similarity DECIMAL(5, 4), -- 0.0 to 1.0
    jaccard_similarity DECIMAL(5, 4),
    fuzzy_ratio DECIMAL(5, 2), -- 0 to 100
    semantic_similarity DECIMAL(5, 4), -- If using embeddings
    
    -- Comparison method used
    comparison_method VARCHAR(50) DEFAULT 'cosine', -- 'cosine', 'jaccard', 'fuzzy', 'semantic', 'combined'
    
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(run_id, prompt_id, model_a_id, model_b_id)
);

CREATE INDEX idx_similarity_run ON similarity_scores(run_id);
CREATE INDEX idx_similarity_prompt ON similarity_scores(prompt_id);
CREATE INDEX idx_similarity_models ON similarity_scores(model_a_id, model_b_id);
CREATE INDEX idx_similarity_cosine ON similarity_scores(cosine_similarity);

-- ============================================================================
-- 9. CLOUDWATCH LOGS
-- ============================================================================

CREATE TABLE cloudwatch_log_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    log_file_name VARCHAR(255),
    log_entry_number INTEGER,
    raw_log_data JSONB NOT NULL,
    
    -- Extracted fields
    event_name VARCHAR(100),
    event_time TIMESTAMP WITH TIME ZONE,
    model_id VARCHAR(255),
    model_name VARCHAR(200),
    region VARCHAR(50),
    
    -- Parsed metrics (if available)
    input_tokens INTEGER,
    output_tokens INTEGER,
    latency_ms DECIMAL(10, 2),
    
    -- Status
    parsed BOOLEAN DEFAULT FALSE,
    parse_error TEXT,
    
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    parsed_at TIMESTAMP WITH TIME ZONE,
    
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_cw_logs_user ON cloudwatch_log_entries(user_id);
CREATE INDEX idx_cw_logs_file ON cloudwatch_log_entries(log_file_name);
CREATE INDEX idx_cw_logs_event_time ON cloudwatch_log_entries(event_time);
CREATE INDEX idx_cw_logs_parsed ON cloudwatch_log_entries(parsed);
CREATE INDEX idx_cw_logs_model ON cloudwatch_log_entries(model_name);

-- ============================================================================
-- 10. AUDIT LOG
-- ============================================================================

CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL, -- 'login', 'logout', 'create_run', 'delete_run', etc.
    resource_type VARCHAR(50), -- 'user', 'run', 'model', 'prompt', etc.
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_resource ON audit_log(resource_type, resource_id);
CREATE INDEX idx_audit_created ON audit_log(created_at);

-- ============================================================================
-- 11. VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Current model pricing
CREATE OR REPLACE VIEW v_current_model_pricing AS
SELECT DISTINCT ON (model_id)
    mp.id,
    mp.model_id,
    m.name AS model_name,
    mp.input_per_1k_tokens_usd,
    mp.output_per_1k_tokens_usd,
    mp.effective_from,
    mp.effective_to
FROM model_pricing mp
JOIN models m ON m.id = mp.model_id
WHERE mp.effective_to IS NULL OR mp.effective_to > CURRENT_TIMESTAMP
ORDER BY model_id, effective_from DESC;

-- View: Current model generation parameters
CREATE OR REPLACE VIEW v_current_model_params AS
SELECT DISTINCT ON (model_id)
    mgp.id,
    mgp.model_id,
    m.name AS model_name,
    mgp.max_tokens,
    mgp.temperature,
    mgp.top_p,
    mgp.effective_from,
    mgp.effective_to
FROM model_generation_params mgp
JOIN models m ON m.id = mgp.model_id
WHERE mgp.effective_to IS NULL OR mgp.effective_to > CURRENT_TIMESTAMP
ORDER BY model_id, effective_from DESC;

-- View: Evaluation summary by run
CREATE OR REPLACE VIEW v_evaluation_summary AS
SELECT 
    er.id AS run_id,
    er.run_id AS run_identifier,
    er.name AS run_name,
    er.status,
    er.started_at,
    er.completed_at,
    er.total_prompts,
    er.total_models,
    er.total_evaluations,
    er.successful_evaluations,
    er.failed_evaluations,
    u.username,
    COUNT(DISTINCT em.model_id) AS models_evaluated,
    COUNT(DISTINCT em.prompt_id) AS prompts_evaluated,
    SUM(em.cost_usd_total) AS total_cost,
    AVG(em.latency_ms) AS avg_latency,
    COUNT(*) FILTER (WHERE em.status = 'success') AS success_count,
    COUNT(*) FILTER (WHERE em.status = 'error') AS error_count
FROM evaluation_runs er
LEFT JOIN users u ON u.id = er.user_id
LEFT JOIN evaluation_metrics em ON em.run_id = er.id
GROUP BY er.id, er.run_id, er.name, er.status, er.started_at, er.completed_at,
         er.total_prompts, er.total_models, er.total_evaluations,
         er.successful_evaluations, er.failed_evaluations, u.username;

-- View: Model performance summary
CREATE OR REPLACE VIEW v_model_performance AS
SELECT 
    m.id AS model_id,
    m.name AS model_name,
    pp.name AS provider_name,
    COUNT(em.id) AS total_evaluations,
    COUNT(*) FILTER (WHERE em.status = 'success') AS success_count,
    COUNT(*) FILTER (WHERE em.status = 'error') AS error_count,
    AVG(em.latency_ms) AS avg_latency_ms,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY em.latency_ms) AS p50_latency_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY em.latency_ms) AS p95_latency_ms,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY em.latency_ms) AS p99_latency_ms,
    AVG(em.input_tokens) AS avg_input_tokens,
    AVG(em.output_tokens) AS avg_output_tokens,
    SUM(em.cost_usd_total) AS total_cost_usd,
    AVG(em.cost_usd_total) AS avg_cost_per_request,
    COUNT(*) FILTER (WHERE em.json_valid = TRUE) AS json_valid_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE em.json_valid = TRUE) / NULLIF(COUNT(*), 0), 2) AS json_valid_percentage
FROM models m
JOIN model_providers pp ON pp.id = m.provider_id
LEFT JOIN evaluation_metrics em ON em.model_id = m.id
WHERE m.is_active = TRUE
GROUP BY m.id, m.name, pp.name;

-- ============================================================================
-- 12. FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_models_updated_at BEFORE UPDATE ON models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prompts_updated_at BEFORE UPDATE ON prompts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate prompt hash
CREATE OR REPLACE FUNCTION calculate_prompt_hash()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.prompt_hash IS NULL THEN
        NEW.prompt_hash = encode(digest(NEW.prompt_text, 'sha256'), 'hex');
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER calculate_prompt_hash_trigger BEFORE INSERT OR UPDATE ON prompts
    FOR EACH ROW EXECUTE FUNCTION calculate_prompt_hash();

-- ============================================================================
-- 13. INITIAL DATA (Seed Data)
-- ============================================================================

-- Insert default providers
INSERT INTO model_providers (name, display_name) VALUES
    ('anthropic', 'Anthropic'),
    ('meta', 'Meta'),
    ('amazon', 'Amazon'),
    ('openai', 'OpenAI'),
    ('alibaba', 'Alibaba')
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================



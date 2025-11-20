# Database Schema Documentation

## Overview

This directory contains the production-level database schema for the BellaTrix LLM Evaluation Framework. The schema is designed for PostgreSQL 14+ and follows best practices for scalability, performance, and data integrity.

## Database Structure

### Core Tables

1. **users** - User authentication and profile data
2. **model_providers** - LLM providers (Anthropic, Meta, Amazon, etc.)
3. **models** - Model configurations and metadata
4. **model_pricing** - Historical pricing data (supports price changes over time)
5. **model_generation_params** - Historical generation parameters
6. **prompts** - User prompts for evaluation
7. **evaluation_runs** - Batch evaluation runs
8. **evaluation_metrics** - Raw evaluation metrics per prompt-model pair
9. **model_aggregated_metrics** - Pre-calculated aggregated metrics
10. **master_model_evaluations** - Reference model (e.g., ChatGPT) evaluations
11. **similarity_scores** - Similarity comparisons between model outputs
12. **cloudwatch_log_entries** - Parsed CloudWatch log data
13. **audit_log** - System audit trail

### Key Features

- **Normalized Design**: Proper foreign keys and relationships
- **Historical Data**: Pricing and parameters support time-based changes
- **Performance**: Comprehensive indexing strategy
- **Scalability**: Partitioning-ready structure for large datasets
- **Audit Trail**: Complete audit logging
- **Data Integrity**: Constraints, triggers, and validation

## Installation

### Prerequisites

- PostgreSQL 14 or higher
- psql command-line tool

### Setup

```bash
# Create database
createdb bellatrix_db

# Run schema
psql -d bellatrix_db -f schema.sql

# Or using connection string
psql postgresql://user:password@localhost/bellatrix_db -f schema.sql
```

## Schema Details

### Users Table

Stores user authentication and profile information.

```sql
- id: UUID primary key
- username: Unique username
- email: Unique email address
- password_hash: Bcrypt hashed password
- is_active: Account status
- is_admin: Admin privileges
- created_at, updated_at, last_login: Timestamps
- metadata: JSONB for additional user data
```

### Models Table

Stores LLM model configurations.

```sql
- id: UUID primary key
- name: Model display name
- provider_id: Foreign key to model_providers
- bedrock_model_id: AWS Bedrock model identifier
- tokenizer_type: Tokenizer to use
- region_name: AWS region
- is_active: Whether model is currently available
- is_master_model: True for reference models
- metadata: JSONB for additional configuration
```

### Evaluation Metrics Table

Core table storing raw evaluation results.

```sql
- id: UUID primary key
- run_id: Foreign key to evaluation_runs
- model_id: Foreign key to models
- prompt_id: Foreign key to prompts
- input_tokens, output_tokens: Token counts
- latency_ms: Response latency
- cost_usd_*: Cost breakdown
- json_valid: JSON validation result
- response_text: Full model response
- status: 'success' or 'error'
- error_message: Error details if failed
```

## Indexes

The schema includes comprehensive indexing:

- **Primary Keys**: All tables have UUID primary keys
- **Foreign Keys**: Indexed for join performance
- **Common Queries**: Composite indexes for frequent query patterns
- **Time-based**: Indexes on timestamp columns for time-range queries
- **Text Search**: GIN indexes for array and JSONB columns

## Views

Pre-built views for common queries:

- `v_current_model_pricing` - Current pricing for all models
- `v_current_model_params` - Current generation parameters
- `v_evaluation_summary` - Summary statistics per run
- `v_model_performance` - Aggregated performance metrics per model

## Triggers

- **Auto-update timestamps**: `updated_at` columns automatically updated
- **Prompt hashing**: Automatic SHA-256 hash calculation for deduplication

## Data Migration

### From CSV/JSON to Database

The application currently stores data in CSV files. To migrate:

1. Export existing data from CSV files
2. Load into staging tables
3. Transform and insert into production schema
4. Verify data integrity

See `migrations/` directory for migration scripts.

## Performance Considerations

### Partitioning

For large-scale deployments, consider partitioning:

- `evaluation_metrics` by `evaluated_at` (monthly/quarterly)
- `audit_log` by `created_at` (monthly)

### Archiving

Implement data archiving strategy:

- Move old evaluation runs to archive tables
- Compress historical data
- Maintain summary statistics

### Query Optimization

- Use views for common aggregations
- Leverage materialized views for heavy calculations
- Monitor slow queries and add indexes as needed

## Security

- Use connection pooling (PgBouncer)
- Implement row-level security (RLS) for multi-tenant scenarios
- Encrypt sensitive data at rest
- Use SSL/TLS for connections
- Regular security updates

## Backup & Recovery

- Regular automated backups
- Point-in-time recovery (PITR) enabled
- Test restore procedures regularly
- Off-site backup storage

## Monitoring

Monitor:

- Database size and growth
- Query performance
- Connection pool usage
- Index usage statistics
- Lock contention

## Maintenance

Regular maintenance tasks:

- VACUUM ANALYZE on high-traffic tables
- REINDEX on fragmented indexes
- Update table statistics
- Check for unused indexes

## Example Queries

### Get latest evaluation results

```sql
SELECT 
    m.name AS model_name,
    p.prompt_text,
    em.latency_ms,
    em.cost_usd_total,
    em.status
FROM evaluation_metrics em
JOIN models m ON m.id = em.model_id
JOIN prompts p ON p.id = em.prompt_id
WHERE em.run_id = 'your-run-id'
ORDER BY em.evaluated_at DESC;
```

### Model performance comparison

```sql
SELECT * FROM v_model_performance
WHERE total_evaluations > 100
ORDER BY avg_latency_ms ASC;
```

### Cost analysis by user

```sql
SELECT 
    u.username,
    COUNT(DISTINCT er.id) AS run_count,
    SUM(em.cost_usd_total) AS total_cost
FROM users u
JOIN evaluation_runs er ON er.user_id = u.id
JOIN evaluation_metrics em ON em.run_id = er.id
GROUP BY u.id, u.username
ORDER BY total_cost DESC;
```

## Support

For schema questions or issues, refer to:
- PostgreSQL documentation: https://www.postgresql.org/docs/
- Schema design best practices
- Application code for usage examples



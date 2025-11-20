# RDS Database Setup Guide

This guide will help you set up your RDS PostgreSQL database for BellaTrix.

## Prerequisites

1. RDS PostgreSQL instance running (endpoint: `bellatrix-db.c3ea24kmsrmf.ap-south-1.rds.amazonaws.com`)
2. Database credentials (username and password)
3. Python 3.8+ installed
4. Required Python packages installed

## Step 1: Install Dependencies

```bash
pip install psycopg2-binary python-dotenv
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment Variables

Create a `.env` file in the project root (or update existing one) with your RDS credentials:

```env
# RDS Database Configuration
DB_HOST=bellatrix-db.c3ea24kmsrmf.ap-south-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=bellatrix_db
DB_USER=your_rds_username
DB_PASSWORD=your_rds_password

# Optional: Full connection string (overrides above)
# DATABASE_URL=postgresql://username:password@bellatrix-db.c3ea24kmsrmf.ap-south-1.rds.amazonaws.com:5432/bellatrix_db
```

**Important:** Replace `your_rds_username` and `your_rds_password` with your actual RDS credentials.

## Step 3: Run Database Setup

Execute the setup script to create all tables and schema:

```bash
python database/setup_rds.py
```

This script will:
- Connect to your RDS instance
- Create the database if it doesn't exist
- Create all tables, indexes, views, and triggers
- Insert initial seed data (model providers)
- Verify the setup

## Step 4: Verify Setup

After running the setup script, you should see output like:

```
============================================================
BellaTrix RDS Database Setup
============================================================
Connected to database: bellatrix-db.c3ea24kmsrmf.ap-south-1.rds.amazonaws.com:5432/postgres
Database 'bellatrix_db' already exists
Connecting to target database...
Executing schema from: database/schema.sql
Executing schema SQL...
Schema executed successfully

Verifying database setup...

Created 13 tables:
  - audit_log
  - cloudwatch_log_entries
  - evaluation_metrics
  - evaluation_runs
  - master_model_evaluations
  - model_aggregated_metrics
  - model_generation_params
  - model_pricing
  - model_providers
  - models
  - prompts
  - similarity_scores
  - users

============================================================
Database setup completed successfully!
============================================================
```

## Troubleshooting

### Connection Issues

If you get connection errors:

1. **Check Security Groups**: Ensure your RDS security group allows inbound connections on port 5432 from your IP address or EC2 instance.

2. **Check VPC/Network**: If connecting from outside AWS, ensure your RDS is publicly accessible or use a VPN/bastion host.

3. **Verify Credentials**: Double-check your DB_USER and DB_PASSWORD in the `.env` file.

### SSL Connection (if required)

If your RDS requires SSL, update the connection in `database/connection.py`:

```python
connect_args={
    "connect_timeout": 10,
    "application_name": "bellatrix_app",
    "sslmode": "require"  # Add this
}
```

### Database Already Exists

If the database already exists, the script will skip creation and proceed with schema setup.

## Manual Setup (Alternative)

If you prefer to set up manually using `psql`:

```bash
# Connect to RDS
psql -h bellatrix-db.c3ea24kmsrmf.ap-south-1.rds.amazonaws.com -U your_username -d postgres

# Create database
CREATE DATABASE bellatrix_db;

# Connect to the new database
\c bellatrix_db

# Run schema file
\i database/schema.sql
```

## Next Steps

After successful setup:

1. Update your application to use the database connection
2. Test the connection using `database/connection.py`
3. Start using the database for storing evaluation data

## Security Notes

- Never commit your `.env` file to version control
- Use IAM database authentication if possible
- Rotate passwords regularly
- Use SSL/TLS for connections in production
- Restrict database access to necessary IPs only


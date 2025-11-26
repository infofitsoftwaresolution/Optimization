#!/bin/bash
# Script to fix RDS database connection issues
# This script can be run on EC2 instance to automatically fix security group and user issues

set -e

echo "🔧 Database Connection Fix Script"
echo "=================================="
echo ""

# Load environment variables
if [ -f "/home/ec2-user/Optimization/.env" ]; then
    source /home/ec2-user/Optimization/.env
    echo "✅ Loaded environment variables from .env"
else
    echo "❌ .env file not found at /home/ec2-user/Optimization/.env"
    exit 1
fi

# Check required variables
if [ -z "$DB_HOST" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
    echo "❌ Missing required database variables: DB_HOST, DB_USER, DB_PASSWORD"
    exit 1
fi

# Fix DB_NAME if it's incorrectly set to the username
if [ "$DB_NAME" == "$DB_USER" ] || [ -z "$DB_NAME" ]; then
    echo "⚠️  DB_NAME is set to '$DB_NAME' (same as username or empty)"
    echo "   Fixing to 'postgres'..."
    DB_NAME="postgres"
    # Update .env file
    if [ -f "/home/ec2-user/Optimization/.env" ]; then
        # Remove old DB_NAME line and add correct one
        sed -i '/^DB_NAME=/d' /home/ec2-user/Optimization/.env
        echo "DB_NAME=postgres" >> /home/ec2-user/Optimization/.env
        echo "✅ Updated .env file with correct DB_NAME=postgres"
    fi
fi

# Check if DATABASE_URL is set and might be overriding
if [ -n "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL is set, checking if it uses correct database name..."
    if echo "$DATABASE_URL" | grep -q "/$DB_USER[/?]"; then
        echo "   DATABASE_URL appears to use username as database name"
        echo "   This will override DB_NAME. Consider removing DATABASE_URL or fixing it."
    fi
fi

echo "Database Configuration:"
echo "  Host: $DB_HOST"
echo "  User: $DB_USER"
echo "  Database: ${DB_NAME:-postgres}"
echo "  Port: ${DB_PORT:-5432}"
if [ -n "$DATABASE_URL" ]; then
    echo "  DATABASE_URL: ***SET*** (may override above)"
fi
echo ""

# Get EC2 instance metadata
EC2_IP=$(hostname -I | awk '{print $1}' || curl -s http://169.254.169.254/latest/meta-data/local-ipv4)
EC2_INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null || echo "")
EC2_REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region 2>/dev/null || echo "${AWS_REGION:-ap-south-1}")

echo "EC2 Instance Info:"
echo "  Instance ID: $EC2_INSTANCE_ID"
echo "  Private IP: $EC2_IP"
echo "  Region: $EC2_REGION"
echo ""

# Install PostgreSQL client if needed
if ! command -v psql &> /dev/null; then
    echo "📦 Installing PostgreSQL client..."
    if command -v yum &> /dev/null; then
        sudo yum install -y postgresql15 || sudo yum install -y postgresql
    elif command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y postgresql-client
    fi
fi

# Install AWS CLI if needed
if ! command -v aws &> /dev/null; then
    echo "📦 Installing AWS CLI..."
    if command -v yum &> /dev/null; then
        sudo yum install -y aws-cli
    elif command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y awscli
    fi
fi

# Step 1: Fix RDS Security Group
echo ""
echo "🔧 Step 1: Configuring RDS Security Group..."
if [ -n "$EC2_INSTANCE_ID" ] && command -v aws &> /dev/null && [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    # Get EC2 security group
    EC2_SG=$(aws ec2 describe-instances \
        --region "$EC2_REGION" \
        --instance-ids "$EC2_INSTANCE_ID" \
        --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$EC2_SG" ] && [ "$EC2_SG" != "None" ]; then
        echo "  Found EC2 security group: $EC2_SG"
        
        # Get RDS instance identifier
        RDS_ID=$(aws rds describe-db-instances \
            --region "$EC2_REGION" \
            --query "DBInstances[?Endpoint.Address=='$DB_HOST'].DBInstanceIdentifier" \
            --output text 2>/dev/null || echo "")
        
        if [ -n "$RDS_ID" ]; then
            echo "  Found RDS instance: $RDS_ID"
            
            # Get RDS security groups
            RDS_SGS=$(aws rds describe-db-instances \
                --region "$EC2_REGION" \
                --db-instance-identifier "$RDS_ID" \
                --query 'DBInstances[0].VpcSecurityGroups[*].VpcSecurityGroupId' \
                --output text 2>/dev/null || echo "")
            
            if [ -n "$RDS_SGS" ] && [ "$RDS_SGS" != "None" ]; then
                echo "  RDS security groups: $RDS_SGS"
                
                for RDS_SG in $RDS_SGS; do
                    echo "  Configuring: $RDS_SG"
                    
                    # Check if rule exists
                    EXISTING=$(aws ec2 describe-security-group-rules \
                        --region "$EC2_REGION" \
                        --filters "Name=group-id,Values=$RDS_SG" "Name=ip-protocol,Values=tcp" "Name=from-port,Values=5432" "Name=to-port,Values=5432" \
                        --query "SecurityGroupRules[?ReferencedGroupInfo.GroupId==\`$EC2_SG\`].SecurityGroupRuleId" \
                        --output text 2>/dev/null || echo "")
                    
                    if [ -z "$EXISTING" ] || [ "$EXISTING" == "None" ]; then
                        # Add rule
                        if aws ec2 authorize-security-group-ingress \
                            --region "$EC2_REGION" \
                            --group-id "$RDS_SG" \
                            --protocol tcp \
                            --port 5432 \
                            --source-group "$EC2_SG" \
                            2>/dev/null; then
                            echo "  ✅ Added security group rule: PostgreSQL (5432) from $EC2_SG"
                        else
                            # Try with IP
                            if aws ec2 authorize-security-group-ingress \
                                --region "$EC2_REGION" \
                                --group-id "$RDS_SG" \
                                --protocol tcp \
                                --port 5432 \
                                --cidr "$EC2_IP/32" \
                                2>/dev/null; then
                                echo "  ✅ Added security group rule: PostgreSQL (5432) from $EC2_IP/32"
                            else
                                echo "  ⚠️  Could not add security group rule (may already exist)"
                            fi
                        fi
                    else
                        echo "  ✅ Security group rule already exists"
                    fi
                done
                
                echo "  Waiting 5 seconds for changes to propagate..."
                sleep 5
            else
                echo "  ⚠️  Could not retrieve RDS security groups"
            fi
        else
            echo "  ⚠️  Could not find RDS instance for endpoint: $DB_HOST"
        fi
    else
        echo "  ⚠️  Could not retrieve EC2 security group"
    fi
else
    echo "  ⚠️  AWS CLI not available or credentials not set, skipping security group configuration"
fi

# Step 2: Test and fix database user
echo ""
echo "🔧 Step 2: Testing database connection..."
export PGPASSWORD="$DB_PASSWORD"

# Test connection
CONNECTION_OUTPUT=$(psql -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USER" -d "${DB_NAME:-postgres}" -c "SELECT 1;" 2>&1)
CONNECTION_EXIT=$?

if [ $CONNECTION_EXIT -eq 0 ]; then
    echo "  ✅ Database connection successful!"
    unset PGPASSWORD
    exit 0
fi

echo "  ❌ Connection failed"
echo "  Error: $CONNECTION_OUTPUT" | head -2

# Step 3: Try to create user using master credentials (DB_MASTER_USER or fallback to DB_USER)
MASTER_USER="${DB_MASTER_USER:-$DB_USER}"
MASTER_PASSWORD="${DB_MASTER_PASSWORD:-$DB_PASSWORD}"

if [ -n "$MASTER_USER" ] && [ -n "$MASTER_PASSWORD" ]; then
    echo ""
    echo "🔧 Step 3: Attempting to create database user (if needed)..."
    echo "  Using master credentials: $MASTER_USER"
    export PGPASSWORD="$MASTER_PASSWORD"
    
    # Check if user exists
    USER_EXISTS=$(psql -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$MASTER_USER" -d "postgres" -tAc "SELECT 1 FROM pg_user WHERE usename = '$DB_USER';" 2>/dev/null || echo "0")
    
    if [ "$USER_EXISTS" != "1" ]; then
        echo "  User '$DB_USER' does not exist, creating..."
        
        # Create user
        if psql -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$MASTER_USER" -d "postgres" -c "CREATE USER \"$DB_USER\" WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null; then
            echo "  ✅ User '$DB_USER' created"
            
            # Grant permissions
            psql -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$MASTER_USER" -d "postgres" -c "GRANT CONNECT ON DATABASE ${DB_NAME:-postgres} TO \"$DB_USER\";" 2>/dev/null || true
            psql -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$MASTER_USER" -d "${DB_NAME:-postgres}" -c "GRANT USAGE ON SCHEMA public TO \"$DB_USER\"; GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \"$DB_USER\";" 2>/dev/null || true
            
            echo "  ✅ Permissions granted"
            
            # Test connection again
            unset PGPASSWORD
            export PGPASSWORD="$DB_PASSWORD"
            sleep 2
            
            if psql -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USER" -d "${DB_NAME:-postgres}" -c "SELECT 1;" &>/dev/null 2>&1; then
                echo "  ✅ Connection successful after creating user!"
                unset PGPASSWORD
                exit 0
            else
                echo "  ⚠️  User created but connection still fails"
            fi
        else
            echo "  ⚠️  Failed to create user (may not have permissions or user creation not needed)"
        fi
    else
        echo "  User '$DB_USER' already exists"
        if [ "$MASTER_USER" == "$DB_USER" ]; then
            echo "  ✅ Using same credentials for master and application user"
        else
            echo "  ⚠️  Password may be incorrect or user lacks permissions"
            echo ""
            echo "  To fix password, connect as master user and run:"
            echo "    ALTER USER \"$DB_USER\" WITH PASSWORD '$DB_PASSWORD';"
        fi
    fi
    unset PGPASSWORD
else
    echo ""
    echo "⚠️  Cannot determine master credentials"
    echo "   DB_USER and DB_PASSWORD must be set"
fi

unset PGPASSWORD

echo ""
echo "=================================="
echo "Fix script completed"
echo ""
echo "If connection still fails:"
echo "1. Verify RDS security group allows connections from EC2"
echo "2. Verify database user exists and password is correct"
echo "3. Check AWS credentials have proper permissions"


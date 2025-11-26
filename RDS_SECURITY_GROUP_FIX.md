# Fix RDS Database Connection Issues

## Error: "no pg_hba.conf entry for host"

This error means your RDS database security group is not allowing connections from your EC2 instance.

## Quick Fix Steps

### 1. Find Your EC2 Instance Security Group

1. Go to **EC2 Console** → **Instances**
2. Select your EC2 instance
3. Click on the **Security** tab
4. Note the **Security groups** name (e.g., `sg-xxxxxxxxx`)

### 2. Update RDS Security Group

1. Go to **RDS Console** → **Databases**
2. Click on your database instance: `optimization.c3ea24kmsrmf.ap-south-1.rds.amazonaws.com`
3. Click on the **Connectivity & security** tab
4. Under **VPC security groups**, click on the security group link
5. Click **Edit inbound rules**
6. Click **Add rule**
7. Configure:
   - **Type**: PostgreSQL
   - **Port**: 5432
   - **Source**: 
     - **Option 1 (Recommended)**: Select "Custom" and choose your EC2 instance's security group
     - **Option 2**: Select "Custom" and enter the EC2 private IP: `172.31.3.210/32`
     - **Option 3**: Select "My IP" if testing from your local machine
8. Click **Save rules**

### 3. Verify Database Credentials

Check your GitHub Secrets:
- `DB_HOST`: Should be `optimization.c3ea24kmsrmf.ap-south-1.rds.amazonaws.com`
- `DB_USER`: Should match the database username (case-sensitive!)
- `DB_PASSWORD`: Should be the correct password
- `DB_NAME`: Should be the database name (e.g., `postgres` or `optimization_db`)
- `DB_PORT`: Should be `5432`

### 4. Test Connection

After updating the security group, the deployment will automatically test the connection. If it still fails:

1. SSH into your EC2 instance
2. Run:
   ```bash
   source /home/ec2-user/Optimization/.env
   psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME
   ```

## Common Issues

### Issue: Password authentication failed

**Solution**: 
- Verify the password in GitHub Secrets matches the RDS database password
- Check if the username is case-sensitive (PostgreSQL usernames are case-sensitive)
- The error shows user "Optimization" - make sure this matches exactly in your secrets

### Issue: Connection timeout

**Solution**:
- Check RDS security group allows connections from EC2
- Verify both EC2 and RDS are in the same VPC or have proper network connectivity
- Check RDS subnet group allows connections from EC2 subnet

### Issue: Database user doesn't exist

**Solution**:
- Connect to RDS as the master user
- Create the user if it doesn't exist:
  ```sql
  CREATE USER "Optimization" WITH PASSWORD 'your_password';
  GRANT CONNECT ON DATABASE postgres TO "Optimization";
  ```

## Verification

After fixing the security group, wait 1-2 minutes for changes to propagate, then:
1. Re-run the deployment workflow
2. Check the deployment logs for "✅ Database connection successful"
3. Try accessing the application and registering a user


"""Quick test script for authentication database"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import os
import subprocess

# Try to load from GitHub secrets first (if gh CLI is available)
def load_from_github_secrets():
    """Try to load secrets from GitHub if gh CLI is available"""
    try:
        # Check if gh is available and authenticated
        result = subprocess.run(['gh', 'auth', 'status'], 
                               capture_output=True, 
                               text=True, 
                               timeout=5)
        if result.returncode != 0:
            return False
            
        # Check if we're in a git repository
        repo_check = subprocess.run(['git', 'rev-parse', '--git-dir'],
                                   capture_output=True,
                                   text=True,
                                   timeout=5)
        if repo_check.returncode != 0:
            print("⚠️  Not in a git repository, cannot load GitHub secrets")
            return False
        
        # Try to list secrets first to verify access
        list_result = subprocess.run(['gh', 'secret', 'list'],
                                    capture_output=True,
                                    text=True,
                                    timeout=10)
        
        if list_result.returncode != 0:
            print(f"⚠️  Cannot access GitHub secrets: {list_result.stderr.strip()}")
            return False
        
        # GitHub CLI is authenticated, try to get secrets
        secrets = {}
        secret_names = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 
                      'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION']
        
        print("Loading secrets from GitHub...")
        for secret_name in secret_names:
            try:
                # Try with repository context
                result = subprocess.run(['gh', 'secret', 'get', secret_name],
                                       capture_output=True,
                                       text=True,
                                       timeout=10,
                                       cwd=str(Path(__file__).parent.parent))
                
                # Check both returncode and stderr
                if result.returncode == 0 and result.stdout.strip():
                    secrets[secret_name] = result.stdout.strip()
                    os.environ[secret_name] = result.stdout.strip()
                    print(f"  ✓ Loaded {secret_name}")
                else:
                    # Try to get more info about why it failed
                    error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                    if "not found" in error_msg.lower() or "no secret" in error_msg.lower():
                        print(f"  ⚠️  {secret_name} not found in repository secrets")
                    elif result.stdout.strip():
                        # Sometimes secrets return empty but command succeeds
                        print(f"  ⚠️  {secret_name} is empty")
                    else:
                        print(f"  ⚠️  {secret_name} failed: {error_msg}")
            except Exception as e:
                print(f"  ❌ Error loading {secret_name}: {e}")
        
        if secrets:
            print(f"\n✅ Loaded {len(secrets)} secrets from GitHub")
            return True
        else:
            print("\n⚠️  No secrets loaded from GitHub")
            return False
    except FileNotFoundError:
        print("⚠️  GitHub CLI (gh) not found")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout while accessing GitHub secrets")
        return False
    except Exception as e:
        print(f"⚠️  Error loading GitHub secrets: {e}")
        return False

# Try GitHub secrets first
github_loaded = load_from_github_secrets()

# Fallback to .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    if not github_loaded:
        print(f"✅ Loaded .env file from: {env_path}")
elif not github_loaded:
    print(f"⚠️  .env file not found at: {env_path}")

# Check environment variables
print("\nEnvironment Variables Check:")
db_host = os.getenv("DB_HOST", "Not set")
db_name = os.getenv("DB_NAME", "Not set")
db_user = os.getenv("DB_USER", "Not set")
db_password = "***SET***" if os.getenv("DB_PASSWORD") else "❌ NOT SET"
database_url = os.getenv("DATABASE_URL", "Not set")

print(f"  DB_HOST: {db_host}")
print(f"  DB_NAME: {db_name}")
print(f"  DB_USER: {db_user}")
print(f"  DB_PASSWORD: {db_password}")
print(f"  DATABASE_URL: {'***SET***' if database_url != 'Not set' else 'Not set'}")

if not os.getenv("DB_PASSWORD") and database_url == "Not set":
    print("\n❌ ERROR: DB_PASSWORD or DATABASE_URL must be set!")
    print("   Please check your .env file or GitHub Secrets setup.")
    print("   You can load secrets using: ./scripts/setup-from-github-secrets.sh")
    sys.exit(1)

from database.connection import get_db_session, test_connection
from database.models import User
from src.auth import sign_up, sign_in
import time

print("\n" + "=" * 60)
print("Testing Database Authentication")
print("=" * 60)

# Test 1: Database connection
print("\n1. Testing database connection...")
if test_connection():
    print("   ✅ Database connection successful!")
else:
    print("   ❌ Database connection failed!")
    sys.exit(1)

# Test 2: Check existing users
print("\n2. Checking existing users...")
try:
    with get_db_session() as session:
        user_count = session.query(User).count()
        print(f"   Found {user_count} users in database")
        if user_count > 0:
            users = session.query(User).all()
            for u in users:
                print(f"   - {u.username} ({u.email})")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Try to register a test user
print("\n3. Testing user registration...")
test_user = f"test_{int(time.time())}"
test_email = f"test_{int(time.time())}@test.com"
test_pass = "testpass123"

success, msg = sign_up(test_user, test_email, test_pass)
if success:
    print(f"   ✅ Registration successful: {msg}")
    
    # Verify it's in database
    with get_db_session() as session:
        user = session.query(User).filter(User.username == test_user).first()
        if user:
            print(f"   ✅ User found in database: {user.username} ({user.email})")
        else:
            print("   ❌ User NOT found in database after registration!")
else:
    print(f"   ❌ Registration failed: {msg}")

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)


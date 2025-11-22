"""Quick test script for authentication database"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from database.connection import get_db_session, test_connection
from database.models import User
from src.auth import sign_up, sign_in
import time

print("=" * 60)
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


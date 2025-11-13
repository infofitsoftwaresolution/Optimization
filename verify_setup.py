"""
Quick verification script to check if the project is set up correctly.
Run this after installation to verify everything is working.
"""

import sys
from pathlib import Path

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_directories():
    """Check if required directories exist."""
    project_root = Path(__file__).parent
    required_dirs = [
        project_root / "data" / "runs",
        project_root / "data" / "cache",
        project_root / "src",
        project_root / "configs",
    ]
    
    all_exist = True
    for directory in required_dirs:
        if directory.exists():
            print(f"✅ {directory.name} directory exists")
        else:
            print(f"❌ {directory.name} directory missing")
            all_exist = False
    
    return all_exist

def check_files():
    """Check if required files exist."""
    project_root = Path(__file__).parent
    required_files = [
        project_root / "requirements.txt",
        project_root / "configs" / "models.yaml",
        project_root / "src" / "dashboard.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        if file_path.exists():
            print(f"✅ {file_path.name} exists")
        else:
            print(f"❌ {file_path.name} missing")
            all_exist = False
    
    return all_exist

def check_env_file():
    """Check if .env file exists."""
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        print("✅ .env file exists")
        # Check if it has placeholder values
        try:
            content = env_file.read_text()
            if "your_access_key_id_here" in content or "your_secret_key_here" in content:
                print("⚠️  .env file contains placeholder values - please update with real credentials")
                return False
            return True
        except:
            return True
    else:
        print("⚠️  .env file not found - please create it from .env.example")
        return False

def check_virtual_environment():
    """Check if virtual environment exists."""
    project_root = Path(__file__).parent
    venv_path = project_root / ".venv"
    
    if venv_path.exists():
        print("✅ Virtual environment exists")
        return True
    else:
        print("⚠️  Virtual environment not found - run: python -m venv .venv")
        return False

def check_dependencies():
    """Check if key dependencies are installed."""
    try:
        import streamlit
        import pandas
        import boto3
        import numpy
        import plotly
        import openai
        print("✅ All key dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("   Run: pip install -r requirements.txt")
        return False

def main():
    """Run all checks."""
    print("="*60)
    print("🔍 Verifying Project Setup")
    print("="*60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Directories", check_directories),
        ("Required Files", check_files),
        ("Environment File", check_env_file),
        ("Virtual Environment", check_virtual_environment),
        ("Dependencies", check_dependencies),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        result = check_func()
        results.append((name, result))
    
    print("\n" + "="*60)
    print("📊 Verification Summary")
    print("="*60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All checks passed! Project is ready to use.")
        print("\n🚀 Start the dashboard:")
        print("   Windows: start_dashboard.bat")
        print("   Linux/Mac: ./start_dashboard.sh")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\n📖 See INSTALL.md for installation instructions.")
    print("="*60)

if __name__ == "__main__":
    main()


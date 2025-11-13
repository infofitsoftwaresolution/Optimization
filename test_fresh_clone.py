"""
Test script to simulate a fresh clone scenario.
This checks if all necessary files and dependencies are present.
"""

import sys
from pathlib import Path

def test_fresh_clone():
    """Test if project can be set up from a fresh clone."""
    project_root = Path(__file__).parent
    
    print("="*60)
    print("🧪 Testing Fresh Clone Scenario")
    print("="*60)
    print()
    
    # Check 1: Required files exist
    print("📋 Checking required files...")
    required_files = [
        "setup.py",
        "requirements.txt",
        "README.md",
        "CLONE_AND_RUN.md",
        "INSTALL.md",
        "verify_setup.py",
        ".env.example",
        "start_dashboard.bat",
        "start_dashboard.sh",
        "configs/models.yaml",
        "src/dashboard.py",
        "src/evaluator.py",
        "src/model_registry.py",
        "src/metrics_logger.py",
        "src/report_generator.py",
        "src/cloudwatch_parser.py",
        "src/master_model_evaluator.py",
        "src/similarity_calculator.py",
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING!")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} required file(s)!")
        return False
    else:
        print(f"\n✅ All {len(required_files)} required files present!")
    
    # Check 2: Requirements.txt has all dependencies
    print("\n📦 Checking requirements.txt...")
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        content = requirements_file.read_text(encoding='utf-8')
        required_packages = [
            "streamlit",
            "pandas",
            "boto3",
            "numpy",
            "plotly",
            "openai",
            "python-dotenv",
            "PyYAML",
            "tiktoken",
        ]
        
        missing_packages = []
        for package in required_packages:
            if package.lower() in content.lower():
                print(f"  ✅ {package}")
            else:
                print(f"  ❌ {package} - NOT FOUND!")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n⚠️  Missing {len(missing_packages)} package(s) in requirements.txt!")
        else:
            print(f"\n✅ All {len(required_packages)} required packages listed!")
    else:
        print("  ❌ requirements.txt not found!")
        return False
    
    # Check 3: Setup script is executable and complete
    print("\n🔧 Checking setup.py...")
    setup_file = project_root / "setup.py"
    if setup_file.exists():
        content = setup_file.read_text(encoding='utf-8')
        required_functions = [
            "check_python_version",
            "create_directories",
            "setup_env_file",
            "create_virtual_environment",
            "install_dependencies",
        ]
        
        missing_functions = []
        for func in required_functions:
            if func in content:
                print(f"  ✅ {func}()")
            else:
                print(f"  ❌ {func}() - NOT FOUND!")
                missing_functions.append(func)
        
        if missing_functions:
            print(f"\n⚠️  Missing {len(missing_functions)} function(s) in setup.py!")
        else:
            print(f"\n✅ Setup script is complete!")
    else:
        print("  ❌ setup.py not found!")
        return False
    
    # Check 4: Documentation files
    print("\n📚 Checking documentation...")
    doc_files = [
        "README.md",
        "INSTALL.md",
        "CLONE_AND_RUN.md",
        "QUICK_START.md",
    ]
    
    missing_docs = []
    for doc_file in doc_files:
        full_path = project_root / doc_file
        if full_path.exists():
            size = full_path.stat().st_size
            if size > 1000:  # At least 1KB
                print(f"  ✅ {doc_file} ({size} bytes)")
            else:
                print(f"  ⚠️  {doc_file} - Too small ({size} bytes)")
        else:
            print(f"  ❌ {doc_file} - MISSING!")
            missing_docs.append(doc_file)
    
    if missing_docs:
        print(f"\n⚠️  Missing {len(missing_docs)} documentation file(s)!")
    else:
        print(f"\n✅ All documentation files present!")
    
    # Check 5: Startup scripts
    print("\n🚀 Checking startup scripts...")
    startup_scripts = [
        "start_dashboard.bat",
        "start_dashboard.sh",
    ]
    
    for script in startup_scripts:
        full_path = project_root / script
        if full_path.exists():
            try:
                content = full_path.read_text(encoding='utf-8')
            except:
                try:
                    content = full_path.read_text(encoding='latin-1')
                except:
                    content = ""
            if "streamlit" in content.lower() or "dashboard" in content.lower():
                print(f"  ✅ {script}")
            else:
                print(f"  ⚠️  {script} - May not work correctly")
        else:
            print(f"  ❌ {script} - MISSING!")
    
    # Check 6: .env.example has all required fields
    print("\n🔐 Checking .env.example...")
    env_example = project_root / ".env.example"
    if env_example.exists():
        content = env_example.read_text(encoding='utf-8')
        required_vars = [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_REGION",
        ]
        
        missing_vars = []
        for var in required_vars:
            if var in content:
                print(f"  ✅ {var}")
            else:
                print(f"  ❌ {var} - NOT FOUND!")
                missing_vars.append(var)
        
        if missing_vars:
            print(f"\n⚠️  Missing {len(missing_vars)} environment variable(s)!")
        else:
            print(f"\n✅ All required environment variables documented!")
    else:
        print("  ❌ .env.example not found!")
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    if not missing_files and not missing_packages:
        print("✅ Project is ready for fresh clone!")
        print("\nA user can now:")
        print("  1. Clone the repository")
        print("  2. Run: python setup.py")
        print("  3. Configure .env file")
        print("  4. Run: start_dashboard.bat (Windows) or ./start_dashboard.sh (Linux/Mac)")
        print("  5. Open: http://localhost:8501")
        return True
    else:
        print("⚠️  Some issues found. Please fix before committing.")
        return False

if __name__ == "__main__":
    success = test_fresh_clone()
    sys.exit(0 if success else 1)


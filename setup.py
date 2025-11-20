"""
Automated setup script for BellaTrixject.
Run this after cloning to set up the project automatically.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_step(step_num, message):
    """Print a formatted step message."""
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {message}")
    print(f"{'='*60}")

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f" Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(" ERROR: Python 3.8+ is required!")
        print("   Please install Python 3.8 or higher from https://www.python.org/")
        return False
    else:
        print(" Python version is compatible")
        return True

def create_directories(project_root):
    """Create necessary directories."""
    directories = [
        project_root / "data" / "runs",
        project_root / "data" / "cache",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f" Created directory: {directory}")
        
        # Create .gitkeep file
        gitkeep = directory / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()
    
    return True

def setup_env_file(project_root):
    """Set up .env file from .env.example if it doesn't exist."""
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if env_file.exists():
        print(f" .env file already exists: {env_file}")
        return True
    
    if env_example.exists():
        print(f" Creating .env file from .env.example...")
        try:
            shutil.copy(env_example, env_file)
            print(f" Created .env file: {env_file}")
            print("  IMPORTANT: Please edit .env and add your AWS credentials!")
            return True
        except Exception as e:
            print(f" Error creating .env file: {e}")
            return False
    else:
        print("  .env.example not found. Creating basic .env file...")
        try:
            with open(env_file, 'w') as f:
                f.write("# AWS Configuration\n")
                f.write("AWS_ACCESS_KEY_ID=your_access_key_id_here\n")
                f.write("AWS_SECRET_ACCESS_KEY=your_secret_access_key_here\n")
                f.write("AWS_REGION=us-east-2\n")
                f.write("\n# OpenAI API Key (for master model comparison)\n")
                f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
            print(f" Created basic .env file: {env_file}")
            print("  IMPORTANT: Please edit .env and add your credentials!")
            return True
        except Exception as e:
            print(f" Error creating .env file: {e}")
            return False

def check_config_files(project_root):
    """Check if required configuration files exist."""
    models_yaml = project_root / "configs" / "models.yaml"
    
    if models_yaml.exists():
        print(f" Found models configuration: {models_yaml}")
        return True
    else:
        print(f" Missing models configuration: {models_yaml}")
        print("   This file is required for the project to work!")
        return False

def create_virtual_environment(project_root):
    """Create virtual environment if it doesn't exist."""
    venv_path = project_root / ".venv"
    
    if venv_path.exists():
        print(f" Virtual environment already exists: {venv_path}")
        return True
    
    print(" Creating virtual environment...")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            check=True,
            capture_output=True
        )
        print(f" Created virtual environment: {venv_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f" Error creating virtual environment: {e}")
        return False

def install_dependencies(project_root):
    """Install Python dependencies."""
    venv_path = project_root / ".venv"
    requirements = project_root / "requirements.txt"
    
    if not requirements.exists():
        print(" requirements.txt not found!")
        return False
    
    # Determine pip path based on OS
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    if not pip_path.exists():
        print(" Virtual environment not found. Please run setup again.")
        return False
    
    print(" Installing dependencies (this may take a few minutes)...")
    try:
        # Upgrade pip first
        subprocess.run(
            [str(python_path), "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True
        )
        
        # Install requirements
        result = subprocess.run(
            [str(pip_path), "install", "-r", str(requirements)],
            check=True,
            capture_output=True,
            text=True
        )
        print(" Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f" Error installing dependencies: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def verify_installation(project_root):
    """Verify that key packages are installed."""
    venv_path = project_root / ".venv"
    
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        python_path = venv_path / "bin" / "python"
    
    if not python_path.exists():
        print(" Cannot verify installation: virtual environment not found")
        return False
    
    print(" Verifying installation...")
    required_packages = [
        "streamlit",
        "pandas",
        "boto3",
        "numpy",
        "plotly",
        "openai"
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            result = subprocess.run(
                [str(python_path), "-c", f"import {package}"],
                check=True,
                capture_output=True
            )
            print(f" {package} is installed")
        except subprocess.CalledProcessError:
            print(f" {package} is NOT installed")
            all_installed = False
    
    return all_installed

def print_next_steps(project_root):
    """Print instructions for next steps."""
    print("\n" + "="*60)
    print(" SETUP COMPLETE!")
    print("="*60)
    print("\n Next Steps:\n")
    print("1. Configure AWS credentials:")
    print(f"   Edit: {project_root / '.env'}")
    print("   Add your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
    print("\n2. (Optional) Configure OpenAI API key for master model comparison:")
    print("   Add OPENAI_API_KEY to your .env file")
    print("\n3. Start the dashboard:")
    print("   Windows:")
    print("     start_dashboard.bat")
    print("   Linux/Mac:")
    print("     chmod +x start_dashboard.sh")
    print("     ./start_dashboard.sh")
    print("\n   Or manually:")
    if sys.platform == "win32":
        print("     .venv\\Scripts\\activate")
        print("     streamlit run src/dashboard.py")
    else:
        print("     source .venv/bin/activate")
        print("     streamlit run src/dashboard.py")
    print("\n4. Open your browser to: http://localhost:8501")
    print("\n For more help, see README.md for full documentation")
    print("\n" + "="*60)

def main():
    """Main setup function."""
    project_root = Path(__file__).parent
    
    print("\n" + "="*60)
    print(" AI Cost Optimizer - Automated Setup")
    print("="*60)
    print(f"📁 Project root: {project_root}")
    
    # Step 1: Check Python version
    print_step(1, "Checking Python Version")
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Create directories
    print_step(2, "Creating Directories")
    if not create_directories(project_root):
        sys.exit(1)
    
    # Step 3: Set up .env file
    print_step(3, "Setting Up Environment File")
    if not setup_env_file(project_root):
        print("  Warning: Could not create .env file. Please create it manually.")
    
    # Step 4: Check configuration files
    print_step(4, "Checking Configuration Files")
    if not check_config_files(project_root):
        sys.exit(1)
    
    # Step 5: Create virtual environment
    print_step(5, "Setting Up Virtual Environment")
    if not create_virtual_environment(project_root):
        print("  Warning: Could not create virtual environment. You may need to create it manually.")
        print("   Run: python -m venv .venv")
    
    # Step 6: Install dependencies
    print_step(6, "Installing Dependencies")
    print(" Installing dependencies automatically...")
    if not install_dependencies(project_root):
        print("  Warning: Could not install dependencies automatically.")
        print("   Please run manually:")
        if sys.platform == "win32":
            print("   .venv\\Scripts\\activate")
        else:
            print("   source .venv/bin/activate")
        print("   pip install -r requirements.txt")
    else:
        # Step 7: Verify installation
        print_step(7, "Verifying Installation")
        verify_installation(project_root)
    
    # Print next steps
    print_next_steps(project_root)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n Unexpected error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

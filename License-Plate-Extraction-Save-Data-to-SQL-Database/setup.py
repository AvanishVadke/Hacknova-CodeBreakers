"""
Simple setup script - Just run: python setup.py
"""
import subprocess
import sys
import os

def run_command(cmd):
    print(f"\n>>> {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False
    print(result.stdout)
    return True

def main():
    print("=" * 60)
    print("License Plate Detection - Quick Setup")
    print("=" * 60)
    
    # Check if venv exists
    if not os.path.exists("venv_license"):
        print("\n[1/6] Creating virtual environment...")
        if not run_command(f"{sys.executable} -m venv venv_license"):
            print("Failed to create venv")
            return
    else:
        print("\n[1/6] Virtual environment already exists ✓")
    
    # Determine pip path
    if os.name == 'nt':
        pip_path = "venv_license\\Scripts\\pip.exe"
        python_path = "venv_license\\Scripts\\python.exe"
    else:
        pip_path = "venv_license/bin/pip"
        python_path = "venv_license/bin/python"
    
    print("\n[2/6] Upgrading pip...")
    run_command(f"{python_path} -m pip install --upgrade pip")
    
    print("\n[3/6] Installing PyTorch with CUDA support...")
    run_command(f"{pip_path} install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
    
    print("\n[4/6] Cloning YOLOv10...")
    if not os.path.exists("yolov10"):
        run_command("git clone https://github.com/THU-MIG/yolov10.git")
    else:
        print("YOLOv10 already cloned ✓")
    
    print("\n[5/6] Installing main requirements...")
    run_command(f"{pip_path} install -r requirements.txt")
    
    print("\n[6/6] Installing YOLOv10...")
    run_command(f"{pip_path} install -e yolov10")
    
    # Fix NumPy if needed
    print("\n[FIX] Ensuring NumPy 1.26.4...")
    run_command(f"{pip_path} uninstall numpy -y")
    run_command(f"{pip_path} install numpy==1.26.4")
    
    # Initialize database
    print("\n[DB] Initializing database...")
    run_command(f"{python_path} sqldb.py")
    
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\nTo run:")
    print("  venv_license\\Scripts\\activate")
    print("  python main.py")
    print("\nOr just run:")
    print("  python run_simple.py")

if __name__ == "__main__":
    main()

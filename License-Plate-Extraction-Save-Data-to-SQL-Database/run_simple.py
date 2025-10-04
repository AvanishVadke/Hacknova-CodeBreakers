"""
Simple runner - Activates venv and runs main.py
Usage: python run_simple.py
"""
import subprocess
import sys
import os

def main():
    # Check if venv exists
    if not os.path.exists("venv_license"):
        print("❌ Virtual environment not found!")
        print("Run: python setup.py")
        return
    
    # Determine python path
    if os.name == 'nt':
        python_path = "venv_license\\Scripts\\python.exe"
    else:
        python_path = "venv_license/bin/python"
    
    # Check if main.py exists
    if not os.path.exists("main.py"):
        print("❌ main.py not found!")
        return
    
    print("=" * 60)
    print("🚀 Starting License Plate Detection")
    print("=" * 60)
    
    # Run main.py with the venv python
    subprocess.run([python_path, "main.py"])

if __name__ == "__main__":
    main()

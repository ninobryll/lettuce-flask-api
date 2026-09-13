#!/usr/bin/env python3
"""Setup script to ensure dependencies are properly installed"""
import subprocess
import sys

def install_requirements():
    """Install requirements"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

if __name__ == "__main__":
    install_requirements()
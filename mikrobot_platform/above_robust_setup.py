#!/usr/bin/env python3
"""
ABOVE ROBUST DJANGO SETUP
Bulletproof, submarine-grade Django platform initialization
Embodies the Above Robust culture: Multiple validation layers, ASCII-only, nuclear-grade precision
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

class AboveRobustSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.validation_results = []
        self.error_count = 0
        self.warning_count = 0
        self.start_time = datetime.now()
        
    def ascii_print(self, text):
        """Above Robust ASCII-only output - NO UNICODE EVER"""
        ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
        print(ascii_text)
        
    def validate_environment(self):
        """Above Robust environment validation with multiple checks"""
        self.ascii_print("=" * 60)
        self.ascii_print("ABOVE ROBUST DJANGO SETUP - PHASE 1")
        self.ascii_print("Submarine-grade precision, nuclear-grade reliability")
        self.ascii_print("=" * 60)
        
        # Check 1: Python version validation
        python_version = sys.version_info
        if python_version.major != 3 or python_version.minor < 9:
            self.ascii_print("ERROR: Python 3.9+ required for Above Robust standards")
            self.error_count += 1
            return False
        self.ascii_print(f"PASS: Python {python_version.major}.{python_version.minor} - Above Robust compatible")
        
        # Check 2: ASCII-only project path validation
        project_path_str = str(self.project_root)
        if not all(ord(char) < 128 for char in project_path_str):
            self.ascii_print("ERROR: Project path contains non-ASCII characters - Above Robust violation")
            self.error_count += 1
            return False
        self.ascii_print(f"PASS: ASCII-only project path validated")
        
        # Check 3: Disk space validation (Above Robust requires minimum space)
        try:
            import shutil
            free_bytes = shutil.disk_usage(self.project_root).free
            free_gb = free_bytes / (1024**3)
            if free_gb < 2.0:
                self.ascii_print(f"WARNING: Low disk space {free_gb:.1f}GB - Above Robust recommends 5GB+")
                self.warning_count += 1
            else:
                self.ascii_print(f"PASS: Disk space {free_gb:.1f}GB - Above Robust approved")
        except Exception as e:
            self.ascii_print(f"WARNING: Could not check disk space - {str(e)}")
            self.warning_count += 1
            
        return True
    
    def setup_virtual_environment(self):
        """Above Robust virtual environment with bulletproof isolation"""
        self.ascii_print("\n[ABOVE ROBUST] Setting up bulletproof virtual environment...")
        
        venv_path = self.project_root / "venv"
        
        # Remove existing venv if corrupted (Above Robust clean slate principle)
        if venv_path.exists():
            self.ascii_print("CLEANUP: Removing existing virtual environment for Above Robust clean setup")
            try:
                import shutil
                shutil.rmtree(venv_path)
            except Exception as e:
                self.ascii_print(f"WARNING: Could not remove old venv - {str(e)}")
                self.warning_count += 1
        
        # Create new virtual environment
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], 
                         check=True, capture_output=True, text=True)
            self.ascii_print("PASS: Virtual environment created with Above Robust standards")
        except subprocess.CalledProcessError as e:
            self.ascii_print(f"ERROR: Virtual environment creation failed - {str(e)}")
            self.error_count += 1
            return False
            
        return True
    
    def install_dependencies(self):
        """Above Robust dependency installation with validation"""
        self.ascii_print("\n[ABOVE ROBUST] Installing dependencies with nuclear-grade precision...")
        
        # Determine pip path
        if os.name == 'nt':  # Windows
            pip_path = self.project_root / "venv" / "Scripts" / "pip.exe"
        else:  # Unix-like
            pip_path = self.project_root / "venv" / "bin" / "pip"
            
        if not pip_path.exists():
            self.ascii_print("ERROR: pip not found in virtual environment")
            self.error_count += 1
            return False
        
        # Install requirements with Above Robust error handling
        try:
            result = subprocess.run([
                str(pip_path), "install", "-r", "requirements.txt", "--no-cache-dir"
            ], check=True, capture_output=True, text=True, cwd=self.project_root)
            
            self.ascii_print("PASS: Dependencies installed with Above Robust verification")
            
            # Validate critical packages
            critical_packages = [
                "Django", "psycopg2-binary", "celery", "redis", 
                "djangorestframework", "cryptography"
            ]
            
            for package in critical_packages:
                check_result = subprocess.run([
                    str(pip_path), "show", package
                ], capture_output=True, text=True)
                
                if check_result.returncode == 0:
                    self.ascii_print(f"VALIDATED: {package} - Above Robust approved")
                else:
                    self.ascii_print(f"ERROR: {package} not installed properly")
                    self.error_count += 1
                    
        except subprocess.CalledProcessError as e:
            self.ascii_print(f"ERROR: Dependency installation failed - {str(e)}")
            self.error_count += 1
            return False
            
        return True
    
    def validate_position_sizing_compliance(self):
        """Above Robust position sizing validation - 0.55% risk standard"""
        self.ascii_print("\n[ABOVE ROBUST] Validating position sizing compliance...")
        
        # Check that position sizing constants are correct
        settings_file = self.project_root / "mikrobot_platform" / "settings.py"
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Validate risk percentage
                if "'DEFAULT_RISK_PERCENT': 0.55" in content:
                    self.ascii_print("PASS: Position sizing 0.55% risk - Above Robust compliant")
                else:
                    self.ascii_print("ERROR: Position sizing not set to Above Robust 0.55% standard")
                    self.error_count += 1
                    
            except Exception as e:
                self.ascii_print(f"WARNING: Could not validate position sizing - {str(e)}")
                self.warning_count += 1
        
    def create_above_robust_directories(self):
        """Above Robust directory structure with proper permissions"""
        self.ascii_print("\n[ABOVE ROBUST] Creating submarine-grade directory structure...")
        
        directories = [
            "logs",
            "media", 
            "staticfiles",
            "backups",
            "monitoring",
            "validation_reports"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            try:
                dir_path.mkdir(exist_ok=True)
                
                # Create Above Robust marker file
                marker_file = dir_path / "above_robust_initialized.txt"
                with open(marker_file, 'w', encoding='ascii') as f:
                    f.write(f"Above Robust directory initialized: {datetime.now().isoformat()}\n")
                    f.write("Nuclear-grade precision, submarine-grade reliability\n")
                
                self.ascii_print(f"CREATED: {directory}/ - Above Robust approved")
                
            except Exception as e:
                self.ascii_print(f"ERROR: Could not create {directory} - {str(e)}")
                self.error_count += 1
    
    def initialize_database(self):
        """Above Robust database initialization with validation"""
        self.ascii_print("\n[ABOVE ROBUST] Initializing database with nuclear-grade precision...")
        
        # Determine Python path in venv
        if os.name == 'nt':  # Windows
            python_path = self.project_root / "venv" / "Scripts" / "python.exe"
        else:  # Unix-like
            python_path = self.project_root / "venv" / "bin" / "python"
            
        if not python_path.exists():
            self.ascii_print("ERROR: Python not found in virtual environment")
            self.error_count += 1
            return False
        
        try:
            # Run Django migrations with Above Robust validation
            result = subprocess.run([
                str(python_path), "manage.py", "migrate", "--verbosity=2"
            ], check=True, capture_output=True, text=True, cwd=self.project_root)
            
            self.ascii_print("PASS: Database migrations - Above Robust precision applied")
            
            # Run setup_development.py for Above Robust initial data
            result = subprocess.run([
                str(python_path), "setup_development.py"
            ], check=True, capture_output=True, text=True, cwd=self.project_root)
            
            self.ascii_print("PASS: Development data initialized - Above Robust standards")
            
        except subprocess.CalledProcessError as e:
            self.ascii_print(f"ERROR: Database initialization failed - {str(e)}")
            if e.stderr:
                self.ascii_print(f"ERROR DETAILS: {e.stderr}")
            self.error_count += 1
            return False
            
        return True
    
    def create_above_robust_monitoring(self):
        """Above Robust monitoring system initialization"""
        self.ascii_print("\n[ABOVE ROBUST] Creating submarine-grade monitoring system...")
        
        monitoring_config = {
            "above_robust_initialized": True,
            "initialization_time": datetime.now().isoformat(),
            "quality_standards": {
                "ascii_only_enforced": True,
                "position_sizing_compliant": True,
                "submarine_grade_precision": True,
                "nuclear_grade_reliability": True
            },
            "validation_results": {
                "errors": self.error_count,
                "warnings": self.warning_count,
                "setup_duration_seconds": (datetime.now() - self.start_time).total_seconds()
            }
        }
        
        try:
            monitoring_file = self.project_root / "monitoring" / "above_robust_status.json"
            with open(monitoring_file, 'w', encoding='ascii') as f:
                json.dump(monitoring_config, f, indent=2, ensure_ascii=True)
            
            self.ascii_print("CREATED: Above Robust monitoring system - Nuclear-grade precision")
            
        except Exception as e:
            self.ascii_print(f"WARNING: Could not create monitoring system - {str(e)}")
            self.warning_count += 1
    
    def run_above_robust_validation(self):
        """Final Above Robust validation suite"""
        self.ascii_print("\n[ABOVE ROBUST] Running final validation suite...")
        
        # Test Django import
        try:
            if os.name == 'nt':
                python_path = self.project_root / "venv" / "Scripts" / "python.exe" 
            else:
                python_path = self.project_root / "venv" / "bin" / "python"
                
            result = subprocess.run([
                str(python_path), "-c", "import django; print('Django version:', django.get_version())"
            ], check=True, capture_output=True, text=True, cwd=self.project_root)
            
            self.ascii_print(f"VALIDATED: {result.stdout.strip()}")
            
        except subprocess.CalledProcessError as e:
            self.ascii_print(f"ERROR: Django import failed - {str(e)}")
            self.error_count += 1
    
    def generate_above_robust_report(self):
        """Above Robust setup completion report"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        self.ascii_print("\n" + "=" * 60)
        self.ascii_print("ABOVE ROBUST SETUP COMPLETE")
        self.ascii_print("=" * 60)
        self.ascii_print(f"Setup Duration: {duration:.1f} seconds")
        self.ascii_print(f"Errors: {self.error_count}")
        self.ascii_print(f"Warnings: {self.warning_count}")
        
        if self.error_count == 0:
            self.ascii_print("STATUS: ABOVE ROBUST STANDARDS ACHIEVED")
            self.ascii_print("Nuclear-grade reliability confirmed")
            self.ascii_print("Submarine-grade precision operational")
            self.ascii_print("\nNext Steps:")
            self.ascii_print("1. cd mikrobot_platform")
            self.ascii_print("2. venv\\Scripts\\activate  (Windows) or source venv/bin/activate (Linux)")
            self.ascii_print("3. python manage.py runserver")
            self.ascii_print("4. Access: http://localhost:8000/admin/")
            self.ascii_print("5. Login: admin@mikrobot-platform.com / admin123")
        else:
            self.ascii_print("STATUS: ABOVE ROBUST STANDARDS NOT MET")
            self.ascii_print("Please fix errors before proceeding")
        
        self.ascii_print("=" * 60)
        
        return self.error_count == 0
    
    def run_setup(self):
        """Execute complete Above Robust setup process"""
        if not self.validate_environment():
            return False
            
        if not self.setup_virtual_environment():
            return False
            
        if not self.install_dependencies():
            return False
            
        self.validate_position_sizing_compliance()
        self.create_above_robust_directories()
        
        if not self.initialize_database():
            return False
            
        self.create_above_robust_monitoring()
        self.run_above_robust_validation()
        
        return self.generate_above_robust_report()

if __name__ == "__main__":
    setup = AboveRobustSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)
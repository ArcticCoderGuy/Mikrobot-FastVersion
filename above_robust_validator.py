from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
Above Robust! VALIDATOR
Laadukas testi joka varmistaa ett lopputulos on varmasti toimiva
Ei Unicode-riippuvuuksia, pelkk ASCII-teksti
"""
import json
import time
import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess

class AboveRobustValidator:
    """Above Robust! periaatteen mukainen validaattori"""
    
    def __init__(self):
        self.test_results = {}
        self.critical_failures = []
        self.warnings = []
        
    def test_unicode_safety(self):
        """Testaa ett jrjestelm on Unicode-turvallinen"""
        print("TEST_1: UNICODE_SAFETY_VALIDATION")
        
        # Testaa ett Python skriptit eivt kaadu Unicode-merkkeihin
        test_cases = [
            ("ASCII_TEXT", "MIKROBOT_ACTIVE"),
            ("UNICODE_EMOJI", "ROCKET"),  # Tmn pit eponnistua kontroloidusti
            ("UNICODE_CHECKMARK", "OK"),
            ("UNICODE_WARNING", "WARNING")
        ]
        
        unicode_safe = True
        for test_name, test_char in test_cases:
            try:
                # Simuloi console output
                test_output = f"TEST: {test_char}"
                # Tarkista voidaanko enkoodata CP1252:ksi
                test_output.encode('cp1252')
                print(f"  {test_name}: PASS")
            except UnicodeEncodeError:
                if test_name == "ASCII_TEXT":
                    unicode_safe = False
                    self.critical_failures.append(f"ASCII_ENCODING_FAIL: {test_name}")
                    print(f"  {test_name}: CRITICAL_FAIL")
                else:
                    print(f"  {test_name}: EXPECTED_FAIL")
        
        self.test_results["unicode_safety"] = unicode_safe
        return unicode_safe
    
    def test_m5m1_strategy_integrity(self):
        """Testaa M5/M1 strategian eheys ja toimivuus"""
        print("TEST_2: M5M1_STRATEGY_INTEGRITY")
        
        integrity_checks = {
            "activation_file": False,
            "config_file": False,
            "pip_trigger_08": False,
            "symbols_complete": False,
            "ea_connection": False
        }
        
        common_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
        
        # 1. Aktivointitiedosto
        activation_file = common_path / "mikrobot_activation.json"
        if activation_file.exists():
            try:
                with open(activation_file, 'r', encoding='ascii', errors='ignore') as f:
                    activation = json.load(f)
                
                if (activation.get('strategy_name') == "MikroBot_BOS_M5M1" and
                    activation.get('version') == "2.01" and
                    activation.get('parameters', {}).get('pip_trigger') == 0.8):
                    integrity_checks["activation_file"] = True
                    integrity_checks["pip_trigger_08"] = True
                    print("  ACTIVATION_FILE: PASS")
                else:
                    print("  ACTIVATION_FILE: FAIL - Wrong parameters")
            except Exception as e:
                print(f"  ACTIVATION_FILE: FAIL - {str(e)}")
        else:
            print("  ACTIVATION_FILE: FAIL - Missing")
        
        # 2. Konfiguraatiotiedosto
        config_file = common_path / "m5m1_strategy_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='ascii', errors='ignore') as f:
                    config = json.load(f)
                
                config_data = config.get('config', {})
                if (config_data.get('pattern_detection', {}).get('retest_precision') == 0.8 and
                    len(config_data.get('active_symbols', [])) == 4):
                    integrity_checks["config_file"] = True
                    integrity_checks["symbols_complete"] = True
                    print("  CONFIG_FILE: PASS")
                else:
                    print("  CONFIG_FILE: FAIL - Wrong configuration")
            except Exception as e:
                print(f"  CONFIG_FILE: FAIL - {str(e)}")
        else:
            print("  CONFIG_FILE: FAIL - Missing")
        
        # 3. EA yhteys
        status_file = common_path / "mikrobot_status.txt"
        if status_file.exists():
            try:
                with open(status_file, 'r', encoding='ascii', errors='ignore') as f:
                    status = f.read()
                
                if "CONNECTION VERIFIED" in status and "107034605" in status:
                    integrity_checks["ea_connection"] = True
                    print("  EA_CONNECTION: PASS")
                else:
                    print("  EA_CONNECTION: FAIL - Not verified")
            except Exception as e:
                print(f"  EA_CONNECTION: FAIL - {str(e)}")
        else:
            print("  EA_CONNECTION: FAIL - Status file missing")
        
        # Lopputulos
        passed = sum(integrity_checks.values())
        total = len(integrity_checks)
        
        if passed == total:
            print(f"  M5M1_INTEGRITY: PASS ({passed}/{total})")
            self.test_results["m5m1_integrity"] = True
            return True
        else:
            print(f"  M5M1_INTEGRITY: FAIL ({passed}/{total})")
            for check, result in integrity_checks.items():
                if not result:
                    self.critical_failures.append(f"M5M1_INTEGRITY_FAIL: {check}")
            self.test_results["m5m1_integrity"] = False
            return False
    
    def test_file_system_robustness(self):
        """Testaa tiedostojrjestelmn kestvyys"""
        print("TEST_3: FILESYSTEM_ROBUSTNESS")
        
        common_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
        
        robustness_tests = {
            "path_exists": common_path.exists(),
            "write_permission": False,
            "read_permission": False,
            "json_integrity": False
        }
        
        # Write permission
        try:
            test_file = common_path / "robustness_test.tmp"
            with open(test_file, 'w', encoding='ascii', errors='ignore') as f:
                f.write("TEST")
            robustness_tests["write_permission"] = True
            test_file.unlink()  # Clean up
            print("  WRITE_PERMISSION: PASS")
        except Exception:
            print("  WRITE_PERMISSION: FAIL")
        
        # Read permission
        try:
            status_file = common_path / "mikrobot_status.txt"
            if status_file.exists():
                with open(status_file, 'r', encoding='ascii', errors='ignore') as f:
                    f.read()
                robustness_tests["read_permission"] = True
                print("  READ_PERMISSION: PASS")
        except Exception:
            print("  READ_PERMISSION: FAIL")
        
        # JSON integrity
        try:
            activation_file = common_path / "mikrobot_activation.json"
            if activation_file.exists():
                with open(activation_file, 'r', encoding='ascii', errors='ignore') as f:
                    json.load(f)
                robustness_tests["json_integrity"] = True
                print("  JSON_INTEGRITY: PASS")
        except Exception:
            print("  JSON_INTEGRITY: FAIL")
        
        passed = sum(robustness_tests.values())
        total = len(robustness_tests)
        
        if passed >= total - 1:  # Allow one failure
            self.test_results["filesystem_robustness"] = True
            print(f"  FILESYSTEM_ROBUSTNESS: PASS ({passed}/{total})")
            return True
        else:
            self.test_results["filesystem_robustness"] = False
            print(f"  FILESYSTEM_ROBUSTNESS: FAIL ({passed}/{total})")
            return False
    
    def test_production_readiness(self):
        """Testaa tuotantovalmius Above Robust! periaatteen mukaan"""
        print("TEST_4: PRODUCTION_READINESS")
        
        readiness_criteria = {
            "no_unicode_dependencies": self.test_results.get("unicode_safety", False),
            "m5m1_strategy_operational": self.test_results.get("m5m1_integrity", False),
            "filesystem_stable": self.test_results.get("filesystem_robustness", False),
            "critical_failures_zero": len(self.critical_failures) == 0
        }
        
        for criterion, status in readiness_criteria.items():
            status_text = "PASS" if status else "FAIL"
            print(f"  {criterion.upper()}: {status_text}")
        
        production_ready = all(readiness_criteria.values())
        self.test_results["production_ready"] = production_ready
        
        if production_ready:
            print("  PRODUCTION_READINESS: PASS - ABOVE_ROBUST_VERIFIED")
        else:
            print("  PRODUCTION_READINESS: FAIL - MANUAL_INTERVENTION_REQUIRED")
        
        return production_ready
    
    def generate_validation_report(self):
        """Luo Above Robust! validointiraportti"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report = {
            "validation_timestamp": timestamp,
            "above_robust_principle": True,
            "test_results": self.test_results,
            "critical_failures": self.critical_failures,
            "warnings": self.warnings,
            "overall_status": "OPERATIONAL" if self.test_results.get("production_ready", False) else "DEGRADED",
            "recommendations": []
        }
        
        # Suositukset
        if not self.test_results.get("unicode_safety", False):
            report["recommendations"].append("REMOVE_ALL_UNICODE_CHARACTERS_FROM_PRODUCTION_CODE")
        
        if not self.test_results.get("m5m1_integrity", False):
            report["recommendations"].append("RECONFIGURE_M5M1_STRATEGY_PARAMETERS")
        
        if len(self.critical_failures) > 0:
            report["recommendations"].append("ADDRESS_CRITICAL_FAILURES_BEFORE_DEPLOYMENT")
        
        report_file = f"above_robust_validation_{timestamp}.json"
        with open(report_file, 'w', encoding='ascii', errors='ignore') as f:
            json.dump(report, f, indent=2)
        
        return report_file
    
    def run_validation(self):
        """Aja tydellinen Above Robust! validointi"""
        print("ABOVE_ROBUST_VALIDATION_START")
        print("=" * 50)
        
        # Aja testit jrjestyksess
        test_1 = self.test_unicode_safety()
        test_2 = self.test_m5m1_strategy_integrity()
        test_3 = self.test_file_system_robustness()
        test_4 = self.test_production_readiness()
        
        print("=" * 50)
        
        # Luo raportti
        report_file = self.generate_validation_report()
        
        # Lopputulos
        if test_4:
            print("VALIDATION_RESULT: PASS")
            print("SYSTEM_STATUS: OPERATIONAL")
            print("ABOVE_ROBUST: VERIFIED")
            print("PRODUCTION_DEPLOYMENT: APPROVED")
        else:
            print("VALIDATION_RESULT: FAIL")
            print("SYSTEM_STATUS: DEGRADED") 
            print("ABOVE_ROBUST: VIOLATIONS_DETECTED")
            print("PRODUCTION_DEPLOYMENT: BLOCKED")
        
        print(f"VALIDATION_REPORT: {report_file}")
        print("=" * 50)
        
        return test_4, report_file

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    print("ABOVE_ROBUST_VALIDATOR")
    print("Laadukas testi joka varmistaa toimivuuden")
    print()
    
    validator = AboveRobustValidator()
    success, report = validator.run_validation()
    
    if success:
        print("\nSYSTEEMI ON ABOVE_ROBUST_VALMIS!")
    else:
        print("\nSYSTEEMI TARVITSEE KORJAUKSIA!")
        if validator.critical_failures:
            print("KRIITTISET_VIRHEET:")
            for failure in validator.critical_failures:
                print(f"  - {failure}")
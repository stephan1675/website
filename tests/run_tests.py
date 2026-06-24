import sys
import os

# Ensure the tests directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import test_auth

def run_all_tests():
    print("==========================================================")
    print("PORTAL VERIFICATION RUNNER")
    print("==========================================================")
    
    success = True
    
    # Run auth integration tests
    try:
        auth_success = test_auth.run_tests()
        if not auth_success:
            success = False
    except Exception as e:
        print(f"[FEHLER] Unerwarteter Fehler bei Authentifizierungstests: {e}")
        success = False
        
    print("==========================================================")
    if success:
        print("ERFOLG: Alle Verifikationstests bestanden!")
        sys.exit(0)
    else:
        print("FEHLER: Einige Tests sind fehlgeschlagen. Bitte Log pruefen!")
        sys.exit(1)

if __name__ == '__main__':
    run_all_tests()

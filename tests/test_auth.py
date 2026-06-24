import urllib.request
import json
import os
import glob
import time

BASE_URL = 'http://localhost:8000'

def make_request(path, data=None, headers=None, method='POST'):
    url = f"{BASE_URL}{path}"
    req_data = json.dumps(data).encode('utf-8') if data else None
    
    req_headers = {'Content-Type': 'application/json'}
    if headers:
        req_headers.update(headers)
        
    req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            res_data = response.read()
            return response.status, json.loads(res_data.decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode('utf-8')
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, e.reason
    except Exception as e:
        return 0, str(e)

def run_tests():
    print("-> Starte Integrationstest für Authentifizierung...")
    
    test_user = {
        "username": "testuser_testrunner",
        "email": "testrunner@example.com",
        "password": "SuperSecurePassword123!"
    }
    
    # 1. Register
    code, resp = make_request('/api/auth/register', test_user)
    if code != 200 and "bereits registriert" not in resp.get('message', ''):
        print(f"   [FEHLER] Registrierung fehlgeschlagen: {resp}")
        return False
    print("   [OK] Registrierungs-Endpoint funktioniert.")
            
    # 2. Login
    code, resp = make_request('/api/auth/login', {
        "email": test_user["email"],
        "password": test_user["password"]
    })
    if code != 200:
        print(f"   [FEHLER] Login fehlgeschlagen: {resp}")
        return False
    token = resp.get('sessionToken')
    print("   [OK] Login-Endpoint & Session-Token-Generierung funktioniert.")
    
    # 3. Get Profile (Secure)
    code, resp = make_request('/api/auth/user-profile', headers={"Authorization": f"Bearer {token}"}, method='GET')
    if code != 200:
        print(f"   [FEHLER] Profilabruf fehlgeschlagen: {resp}")
        return False
    print("   [OK] Secure User-Profile-Endpoint funktioniert.")
        
    # 4. Save Notes (Secure)
    notes_payload = {"notes": "Testnotiz des Testrunners."}
    code, resp = make_request('/api/auth/save-notes', data=notes_payload, headers={"Authorization": f"Bearer {token}"})
    if code != 200:
        print(f"   [FEHLER] Speichern der Notizen fehlgeschlagen: {resp}")
        return False
    print("   [OK] Secure Save-Notes-Endpoint funktioniert.")
        
    # 5. Forgot Password
    code, resp = make_request('/api/auth/forgot-password', {"email": test_user["email"]})
    if code != 200:
        print(f"   [FEHLER] Passwort-Vergessen-Request fehlgeschlagen: {resp}")
        return False
    print("   [OK] Forgot-Password-Endpoint funktioniert.")
        
    time.sleep(1)
    
    # 6. Check local email and extract reset token
    email_files = glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sent_emails', 'email_*.html'))
    if not email_files:
        print("   [FEHLER] Keine Mock-E-Mails in sent_emails/ gefunden!")
        return False
        
    newest_email = max(email_files, key=os.path.getctime)
    with open(newest_email, 'r', encoding='utf-8') as f:
        content = f.read()
        
    try:
        idx = content.index('?token=')
        token_part = content[idx+7:]
        reset_token = ''
        for char in token_part:
            if char in ['"', "'", ' ', '<', '\n']:
                break
            reset_token += char
    except ValueError:
        print("   [FEHLER] Reset-Token in E-Mail-Datei nicht gefunden!")
        return False
        
    # 7. Reset Password
    new_password = "EvenMoreSecurePassword456!"
    code, resp = make_request('/api/auth/reset-password', {
        "token": reset_token,
        "password": new_password
    })
    if code != 200:
        print(f"   [FEHLER] Passwort-Reset fehlgeschlagen: {resp}")
        return False
    print("   [OK] Reset-Password-Endpoint & Tokenverifizierung funktioniert.")
        
    # 8. Verify Login with New Password
    code, resp = make_request('/api/auth/login', {
        "email": test_user["email"],
        "password": new_password
    })
    if code != 200:
        print(f"   [FEHLER] Login mit neuem Passwort fehlgeschlagen: {resp}")
        return False
    print("   [OK] Login mit geändertem Passwort funktioniert.")
    
    print("-> Alle Authentifizierungstests erfolgreich abgeschlossen.")
    return True

if __name__ == '__main__':
    run_tests()

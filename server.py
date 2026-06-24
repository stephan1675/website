import http.server
import socketserver
import os
import subprocess
import json
import sys
import threading
import queue
import uuid
import time
import urllib.parse
import urllib.request
import base64
import random
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# User database path
USERS_LOCK = threading.Lock()
USERS_FILE = 'users.json'

# Helper to read users from users.json
def load_users():
    with USERS_LOCK:
        if not os.path.exists(USERS_FILE):
            return []
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Auth] Fehler beim Laden von users.json: {e}")
            return []

# Helper to save users to users.json
def save_users(users):
    with USERS_LOCK:
        try:
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Auth] Fehler beim Speichern von users.json: {e}")

# Helper for salted PBKDF2-HMAC-SHA256 password hashing
def hash_password(password, salt=None):
    if not salt:
        salt = secrets.token_hex(16)
    iterations = 100000
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
    return f"{salt}:{iterations}:{hashed.hex()}"

def verify_password(password, stored_hash):
    try:
        parts = stored_hash.split(':')
        if len(parts) == 3:
            salt, iterations_str, hashed_hex = parts
            iterations = int(iterations_str)
            hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
            return hashed.hex() == hashed_hex
        elif len(parts) == 2:
            # Fallback backward compatibility for SHA-256
            salt, hashed = parts
            return hashlib.sha256((password + salt).encode('utf-8')).hexdigest() == hashed
    except Exception:
        pass
    return False

# Helper to send email or fallback to local files
def send_email(to_email, subject, html_content, text_content):
    env = load_env()
    
    smtp_server = env.get('SMTP_SERVER') or os.environ.get('SMTP_SERVER')
    smtp_port = env.get('SMTP_PORT') or os.environ.get('SMTP_PORT')
    smtp_user = env.get('SMTP_USER') or os.environ.get('SMTP_USER')
    smtp_password = env.get('SMTP_PASSWORD') or os.environ.get('SMTP_PASSWORD')
    smtp_sender = env.get('SMTP_SENDER') or smtp_user or "no-reply@localhost"

    email_sent = False
    
    if smtp_server and smtp_port and smtp_user and smtp_password:
        try:
            print(f"[Email] Sende echte SMTP E-Mail an {to_email}...")
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_sender
            msg['To'] = to_email
            
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)
            
            port = int(smtp_port)
            if port == 465:
                # SSL
                server = smtplib.SMTP_SSL(smtp_server, port, timeout=10)
            else:
                # TLS/StartTLS
                server = smtplib.SMTP(smtp_server, port, timeout=10)
                server.ehlo()
                if port == 587:
                    server.starttls()
                    server.ehlo()
            
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_sender, to_email, msg.as_string())
            server.quit()
            print(f"[Email] Echte SMTP E-Mail erfolgreich an {to_email} gesendet.")
            email_sent = True
        except Exception as e:
            print(f"[Email] Fehler beim Senden der echten SMTP E-Mail an {to_email}: {e}")
            print("[Email] Weiche auf lokale HTML-Aufzeichnung aus.")
            
    if not email_sent:
        # Local mock fallback
        try:
            os.makedirs('sent_emails', exist_ok=True)
            timestamp = int(time.time())
            safe_to = to_email.replace('@', '_at_').replace('.', '_')
            filename = f"sent_emails/email_{timestamp}_{safe_to}.html"
            
            # Debug header
            debug_header = f"""<!-- email_mock_simulator -->
<div style="background:#4f46e5; color:#ffffff; padding:15px; font-family:sans-serif; text-align:center; font-size:14px; margin-bottom:20px; border-radius:8px; line-height:1.5; border:1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    <strong>📬 LOKALER E-MAIL SIMULATOR</strong><br>
    Diese E-Mail wurde abgefangen und lokal gespeichert. In einer Live-Umgebung wäre sie an <strong>{to_email}</strong> gesendet worden.<br>
    Betreff: <strong>{subject}</strong>
</div>
"""
            
            full_html = debug_header + html_content
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(full_html)
                
            print("==========================================================================")
            print(f"[E-MAIL SIMULATOR] Eine E-Mail an {to_email} wurde lokal aufgezeichnet:")
            print(f"   Betreff: {subject}")
            print(f"   Datei: {os.path.abspath(filename)}")
            print("==========================================================================")
        except Exception as e:
            print(f"[Email] Fehler beim Schreiben der Mock-E-Mail: {e}")

# Port selection
PORT = int(os.environ.get("PORT", 8000))

# Global sessions dictionary to manage active console C++ games
# format: { session_id: { 'proc': subprocess.Popen, 'stdout_queue': queue.Queue, 'reader_thread': Thread } }
active_sessions = {}

# Global active AI discussion sessions
# format: { session_id: { 'topic': str, 'agents': list, 'turns_queue': queue.Queue, 'stop_event': threading.Event, 'thread': Thread } }
active_discussions = {}

# Helper to load environmental variables manually from .env file
def load_env():
    env = {}
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, val = line.split('=', 1)
                            env[key.strip()] = val.strip().strip('"').strip("'")
        except Exception as e:
            print(f"[Launcher] Fehler beim Einlesen von .env: {e}")
    return env

# Helper to build multipart/form-data payload without external packages
def build_multipart_formdata(fields, files):
    boundary = "Boundary-" + uuid.uuid4().hex
    body = []
    
    # Add fields
    for key, value in fields.items():
        body.append(f'--{boundary}'.encode('utf-8'))
        body.append(f'Content-Disposition: form-data; name="{key}"'.encode('utf-8'))
        body.append(b'')
        body.append(str(value).encode('utf-8'))
        
    # Add files
    for key, file_info in files.items():
        filename = file_info['filename']
        content = file_info['content']
        mime_type = file_info.get('mime_type', 'application/octet-stream')
        
        body.append(f'--{boundary}'.encode('utf-8'))
        body.append(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"'.encode('utf-8'))
        body.append(f'Content-Type: {mime_type}'.encode('utf-8'))
        body.append(b'')
        body.append(content)
        
    body.append(f'--{boundary}--'.encode('utf-8'))
    body.append(b'')
    
    content_type = f'multipart/form-data; boundary={boundary}'
    return content_type, b'\r\n'.join(body)

# BFH API and AI Discussion Simulation loader from "KI Konversation" package
# Uses dynamic import mechanism to bypass folder name space restrictions in standard python imports
import importlib.util
simulation_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'KI Konversation', 'simulation.py')
spec = importlib.util.spec_from_file_location('ki_konversation_simulation', simulation_file)
simulation_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(simulation_module)

run_discussion_loop = simulation_module.run_discussion_loop
# Background thread function to read C++ stdout process char-by-char
def read_output(proc, q):
    try:
        while True:
            char = proc.stdout.read(1)
            if not char:
                break
            q.put(char)
    except:
        pass
    finally:
        try:
            proc.stdout.close()
        except:
            pass

# Concurrent Multithreaded HTTP Server
class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

class LauncherHTTPHandler(http.server.SimpleHTTPRequestHandler):
    
    # Custom GET overrides
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # 1. SSE Endpoint for C++ console stream
        if parsed_url.path == '/api/terminal/stream':
            session_id = query_params.get('id', [None])[0]
            if not session_id or session_id not in active_sessions:
                self.send_response(404)
                self.end_headers()
                return
            
            session = active_sessions[session_id]
            q = session['stdout_queue']
            proc = session['proc']
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                while True:
                    chars = ""
                    while not q.empty():
                        chars += q.get_nowait()
                    if chars:
                        event_data = json.dumps({"text": chars})
                        self.wfile.write(f"data: {event_data}\n\n".encode('utf-8'))
                        self.wfile.flush()
                    if proc.poll() is not None and q.empty():
                        self.wfile.write(b"event: exit\ndata: {}\n\n")
                        self.wfile.flush()
                        break
                    time.sleep(0.03)
            except Exception as e:
                print(f"[Launcher] C++ Terminal Stream getrennt für {session_id}: {e}")
            return
            
        # 2. SSE Endpoint for AI Discussion room stream
        elif parsed_url.path == '/api/discussion/stream':
            session_id = query_params.get('id', [None])[0]
            if not session_id or session_id not in active_discussions:
                self.send_response(404)
                self.end_headers()
                return
                
            session = active_discussions[session_id]
            q = session['turns_queue']
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                while True:
                    # Retrieve turns from queue
                    turns = []
                    while not q.empty():
                        turns.append(q.get_nowait())
                        
                    for turn in turns:
                        if turn['type'] == 'exit':
                            self.wfile.write(b"event: exit\ndata: {}\n\n")
                            self.wfile.flush()
                            return
                        elif turn['type'] == 'typing':
                            # Trigger "typing" indicator event on browser
                            self.wfile.write(f"event: typing\ndata: {json.dumps(turn)}\n\n".encode('utf-8'))
                            self.wfile.flush()
                        elif turn['type'] == 'user_input_required':
                            # Trigger "user_input_required" event on browser
                            self.wfile.write(f"event: user_input_required\ndata: {json.dumps(turn)}\n\n".encode('utf-8'))
                            self.wfile.flush()
                        else:
                            # Send standard text turn
                            self.wfile.write(f"data: {json.dumps(turn)}\n\n".encode('utf-8'))
                            self.wfile.flush()
                    
                    time.sleep(0.1)
            except Exception as e:
                print(f"[AI-Session] Discussion Stream getrennt für {session_id}: {e}")
                # Safe cleanup in case the client closed the connection/tab without sending close request
                if session_id in active_discussions:
                    try:
                        active_discussions[session_id]['stop_event'].set()
                        del active_discussions[session_id]
                        print(f"[AI-Session] Session [{session_id}] nach Verbindungsabbruch beendet und bereinigt.")
                    except Exception as clean_err:
                        print(f"[AI-Session] Fehler bei automatischer Bereinigung nach Verbindungsabbruch: {clean_err}")
            return
            
        # 3. Ping Endpoint to wake up Render
        elif parsed_url.path == '/api/ping':
            self.send_success_response("pong")
            return
            
        # 4. GET User Profile (Secure token-based auth)
        elif parsed_url.path == '/api/auth/user-profile':
            auth_header = self.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                self.send_error_response(401, "Nicht autorisiert. Fehlendes oder ungültiges Token.")
                return
                
            token = auth_header.split(' ', 1)[1].strip()
            users = load_users()
            user = next((u for u in users if u.get('sessionToken') == token), None)
            if not user:
                self.send_error_response(401, "Nicht autorisiert. Token ist ungültig oder abgelaufen.")
                return
                
            profile = {
                "username": user["username"],
                "email": user["email"],
                "createdAt": user.get("createdAt", ""),
                "loginCount": user.get("loginCount", 0),
                "notes": user.get("notes", "")
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(profile).encode('utf-8'))
            return
            
        else:
            super().do_GET()

    # Custom POST overrides
    def do_POST(self):
        # Auth endpoints
        if self.path == '/api/auth/register':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                
                username = data.get('username', '').strip()
                email = data.get('email', '').strip().lower()
                password = data.get('password', '')
                
                if not username or not email or not password:
                    self.send_error_response(400, "Alle Felder (Benutzername, E-Mail, Passwort) sind erforderlich.")
                    return
                
                if len(username) < 3:
                    self.send_error_response(400, "Der Benutzername muss mindestens 3 Zeichen lang sein.")
                    return
                if len(password) < 8:
                    self.send_error_response(400, "Das Passwort muss mindestens 8 Zeichen lang sein.")
                    return
                    
                users = load_users()
                if any(u['email'] == email for u in users):
                    self.send_error_response(400, "Diese E-Mail-Adresse ist bereits registriert.")
                    return
                if any(u['username'].lower() == username.lower() for u in users):
                    self.send_error_response(400, "Dieser Benutzername ist bereits vergeben.")
                    return
                    
                new_user = {
                    "username": username,
                    "email": email,
                    "passwordHash": hash_password(password),
                    "createdAt": time.strftime("%d.%m.%Y"),
                    "loginCount": 0,
                    "notes": ""
                }
                
                users.append(new_user)
                save_users(users)
                
                # Send welcome email
                subject = "Willkommen im Portal!"
                text_content = f"Hallo {username},\n\nvielen Dank für deine Registrierung auf unserer Website!\n\nDein Benutzername lautet: {username}\nDeine registrierte E-Mail: {email}\n\nDu kannst dich jetzt anmelden.\n\nBeste Grüße,\nDein Portal-Team"
                
                html_content = f"""
                <html>
                <body style="font-family: sans-serif; background-color: #0f0f19; color: #f3f4f6; padding: 30px;">
                    <div style="max-width: 600px; margin: 0 auto; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 30px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);">
                        <h1 style="color: #6366f1; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 15px; margin-top: 0;">Portal.</h1>
                        <p style="font-size: 16px; line-height: 1.6;">Hallo <strong>{username}</strong>,</p>
                        <p style="font-size: 16px; line-height: 1.6;">Vielen Dank für deine Registrierung! Dein Account wurde erfolgreich erstellt.</p>
                        <div style="background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <p style="margin: 5px 0;"><strong>Benutzername:</strong> {username}</p>
                            <p style="margin: 5px 0;"><strong>E-Mail:</strong> {email}</p>
                        </div>
                        <p style="font-size: 16px; line-height: 1.6;">Du kannst dich ab sofort mit deinem Passwort anmelden.</p>
                        <p style="margin-top: 30px; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 20px; font-size: 14px; color: #9ca3af;">
                            Dies ist eine automatisch generierte E-Mail.
                        </p>
                    </div>
                </body>
                </html>
                """
                
                threading.Thread(target=send_email, args=(email, subject, html_content, text_content), daemon=True).start()
                
                self.send_success_response("Konto erfolgreich erstellt! Eine Willkommens-E-Mail wurde gesendet.")
            except Exception as e:
                self.send_error_response(500, f"Registrierungsfehler: {str(e)}")
            return

        elif self.path == '/api/auth/login':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                
                email = data.get('email', '').strip().lower()
                password = data.get('password', '')
                
                if not email or not password:
                    self.send_error_response(400, "E-Mail und Passwort sind erforderlich.")
                    return
                    
                users = load_users()
                user = next((u for u in users if u['email'] == email), None)
                
                if not user or not verify_password(password, user['passwordHash']):
                    self.send_error_response(401, "Ungültige E-Mail-Adresse oder falsches Passwort.")
                    return
                
                # Generate dynamic session token
                session_token = secrets.token_hex(32)
                user['sessionToken'] = session_token
                user['loginCount'] = user.get('loginCount', 0) + 1
                save_users(users)
                
                profile = {
                    "username": user["username"],
                    "email": user["email"],
                    "createdAt": user.get("createdAt", ""),
                    "loginCount": user["loginCount"],
                    "notes": user.get("notes", "")
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "message": f"Willkommen zurück, {user['username']}!",
                    "sessionToken": session_token,
                    "user": profile
                }).encode('utf-8'))
            except Exception as e:
                self.send_error_response(500, f"Login-Fehler: {str(e)}")
            return

        elif self.path == '/api/auth/save-notes':
            try:
                auth_header = self.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    self.send_error_response(401, "Nicht autorisiert. Fehlendes oder ungültiges Token.")
                    return
                token = auth_header.split(' ', 1)[1].strip()
                
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                notes = data.get('notes', '')
                
                users = load_users()
                user = next((u for u in users if u.get('sessionToken') == token), None)
                
                if not user:
                    self.send_error_response(401, "Nicht autorisiert. Token ist ungültig oder abgelaufen.")
                    return
                    
                user['notes'] = notes
                save_users(users)
                
                self.send_success_response("Notiz erfolgreich gespeichert!")
            except Exception as e:
                self.send_error_response(500, f"Fehler beim Speichern: {str(e)}")
            return

        elif self.path == '/api/auth/forgot-password':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                
                email = data.get('email', '').strip().lower()
                
                if not email:
                    self.send_error_response(400, "E-Mail-Adresse fehlt.")
                    return
                    
                users = load_users()
                user = next((u for u in users if u['email'] == email), None)
                
                if not user:
                    self.send_success_response("Wenn diese E-Mail-Adresse existiert, wurde ein Link zum Zurücksetzen gesendet.")
                    return
                    
                token = secrets.token_urlsafe(32)
                expiry = time.time() + 3600
                
                user['resetToken'] = token
                user['resetTokenExpiry'] = expiry
                save_users(users)
                
                env = load_env()
                base_url = env.get('BASE_URL') or os.environ.get('BASE_URL')
                if not base_url:
                    host_header = self.headers.get('Host', 'localhost:8000')
                    protocol = "https" if "render.com" in host_header else "http"
                    base_url = f"{protocol}://{host_header}"
                base_url = base_url.rstrip('/')
                reset_link = f"{base_url}/reset-password.html?token={token}"
                
                subject = "Passwort zurücksetzen"
                text_content = f"Hallo {user['username']},\n\njemand hat das Zurücksetzen deines Passworts angefordert.\n\nKlicke auf den folgenden Link, um ein neues Passwort einzugeben:\n{reset_link}\n\nDieser Link ist für 1 Stunde gültig. Falls du dies nicht angefordert hast, ignoriere diese E-Mail.\n\nBeste Grüße,\nDein Portal-Team"
                
                html_content = f"""
                <html>
                <body style="font-family: sans-serif; background-color: #0f0f19; color: #f3f4f6; padding: 30px;">
                    <div style="max-width: 600px; margin: 0 auto; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 30px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);">
                        <h1 style="color: #6366f1; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 15px; margin-top: 0;">Portal.</h1>
                        <p style="font-size: 16px; line-height: 1.6;">Hallo <strong>{user['username']}</strong>,</p>
                        <p style="font-size: 16px; line-height: 1.6;">Du hast das Zurücksetzen deines Passworts angefordert. Klicke auf die Schaltfläche unten, um ein neues Passwort zu vergeben:</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_link}" style="background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);">Passwort zurücksetzen</a>
                        </div>
                        
                        <p style="font-size: 14px; color: #9ca3af; line-height: 1.6;">Oder kopiere diesen Link in deinen Browser:</p>
                        <p style="font-size: 13px; word-break: break-all; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.05);">{reset_link}</p>
                        
                        <p style="font-size: 14px; color: #9ca3af; margin-top: 20px;">Dieser Link ist <strong>1 Stunde</strong> lang gültig. Falls du diese Anfrage nicht gestellt hast, kannst du diese E-Mail einfach ignorieren.</p>
                        
                        <p style="margin-top: 30px; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 20px; font-size: 14px; color: #9ca3af;">
                            Dies ist eine automatisch generierte E-Mail.
                        </p>
                    </div>
                </body>
                </html>
                """
                
                threading.Thread(target=send_email, args=(email, subject, html_content, text_content), daemon=True).start()
                
                self.send_success_response("Wenn diese E-Mail-Adresse existiert, wurde ein Link zum Zurücksetzen gesendet.")
            except Exception as e:
                self.send_error_response(500, f"Fehler bei Passwort-Zurücksetzungsanfrage: {str(e)}")
            return

        elif self.path == '/api/auth/reset-password':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                
                token = data.get('token', '').strip()
                new_password = data.get('password', '')
                
                if not token or not new_password:
                    self.send_error_response(400, "Token und neues Passwort sind erforderlich.")
                    return
                    
                if len(new_password) < 8:
                    self.send_error_response(400, "Das Passwort muss mindestens 8 Zeichen lang sein.")
                    return
                    
                users = load_users()
                user = None
                for u in users:
                    if u.get('resetToken') == token:
                        expiry = u.get('resetTokenExpiry', 0)
                        if expiry > time.time():
                            user = u
                            break
                            
                if not user:
                    self.send_error_response(400, "Der Token ist ungültig oder bereits abgelaufen.")
                    return
                    
                user['passwordHash'] = hash_password(new_password)
                if 'resetToken' in user:
                    del user['resetToken']
                if 'resetTokenExpiry' in user:
                    del user['resetTokenExpiry']
                    
                save_users(users)
                
                self.send_success_response("Passwort erfolgreich zurückgesetzt! Du kannst dich jetzt einloggen.")
            except Exception as e:
                self.send_error_response(500, f"Fehler beim Passwort-Zurücksetzen: {str(e)}")
            return

        # 1. Python Shooter
        elif self.path == '/api/run-python':
            try:
                game_dir = os.path.join(os.getcwd(), 'python shooter')
                if not os.path.exists(game_dir):
                    self.send_error_response(404, "Der Ordner 'python shooter' wurde nicht gefunden.")
                    return
                
                main_py_path = os.path.join(game_dir, 'main.py')
                if not os.path.exists(main_py_path):
                    self.send_error_response(404, "Die Datei 'main.py' im Ordner 'python shooter' wurde nicht gefunden.")
                    return
                
                python_exe = sys.executable if sys.executable else 'python'
                print(f"[Launcher] Starte Python-Spiel: {python_exe} main.py in {game_dir}")
                subprocess.Popen([python_exe, 'main.py'], cwd=game_dir)
                self.send_success_response("Python-Spiel wird gestartet...")
            except Exception as e:
                self.send_error_response(500, str(e))
                
        # 2. C++ Game
        elif self.path == '/api/run-cpp':
            try:
                cpp_dir = os.path.join(os.getcwd(), 'c++ spiel')
                if not os.path.exists(cpp_dir):
                    self.send_error_response(404, "Der Ordner 'c++ spiel' wurde nicht gefunden.")
                    return
                
                exe_files = [f for f in os.listdir(cpp_dir) if f.endswith('.exe')]
                selected_exe = None
                run_wsl = False
                
                if not exe_files:
                    a_out_path = os.path.join(cpp_dir, 'a.out')
                    if os.path.exists(a_out_path):
                        selected_exe = 'a.out'
                        run_wsl = True
                    else:
                        self.send_error_response(400, "Keine kompilierten Spieldateien (.exe oder a.out) im Ordner 'c++ spiel' gefunden.")
                        return
                else:
                    selected_exe = exe_files[0]
                
                session_id = str(uuid.uuid4())
                if run_wsl:
                    if sys.platform.startswith('win'):
                        cmd = ['wsl', './a.out']
                    else:
                        cmd = ['./a.out']
                else:
                    cmd = [os.path.join(cpp_dir, selected_exe)]
                
                print(f"[Launcher] C++ Spiel [{session_id}] gestartet: {cmd}")
                
                proc = subprocess.Popen(
                    cmd,
                    cwd=cpp_dir,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=0
                )
                
                stdout_queue = queue.Queue()
                reader_thread = threading.Thread(target=read_output, args=(proc, stdout_queue), daemon=True)
                reader_thread.start()
                
                active_sessions[session_id] = {
                    'proc': proc,
                    'stdout_queue': stdout_queue,
                    'reader_thread': reader_thread
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": f"C++ Spiel ({selected_exe}) als Web-Terminal gestartet.",
                    "session_id": session_id
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_error_response(500, str(e))
                
        # 3. C++ Terminal input
        elif self.path == '/api/terminal/input':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                
                session_id = data.get('id')
                user_input = data.get('input', '')
                
                if not session_id or session_id not in active_sessions:
                    self.send_error_response(404, "Session nicht gefunden.")
                    return
                
                session = active_sessions[session_id]
                proc = session['proc']
                
                if proc.poll() is None:
                    proc.stdin.write(user_input + "\n")
                    proc.stdin.flush()
                    self.send_success_response("Eingabe übermittelt.")
                else:
                    self.send_error_response(400, "Spiel wurde bereits beendet.")
            except Exception as e:
                self.send_error_response(500, str(e))
                
        # 4. C++ Terminal close
        elif self.path == '/api/terminal/close':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                session_id = data.get('id')
                
                if not session_id or session_id not in active_sessions:
                    self.send_error_response(404, "Session nicht gefunden.")
                    return
                
                session = active_sessions[session_id]
                proc = session['proc']
                
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=1.0)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                
                del active_sessions[session_id]
                self.send_success_response("Session geschlossen.")
            except Exception as e:
                self.send_error_response(500, str(e))
                
        # 5. [NEW] Upload document for custom AI Personas (JSON Base64 upload)
        elif self.path == '/api/discussion/upload':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                
                filename = data.get('filename')
                content = data.get('content') # Base64 string
                
                if not filename or not content:
                    self.send_error_response(400, "Fehlender Dateiname oder Dateiinhalt.")
                    return
                
                # Create storage folder if not present
                docs_dir = os.path.join(os.getcwd(), 'personas_documents')
                os.makedirs(docs_dir, exist_ok=True)
                
                # Clean up filename to prevent path traversal
                safe_filename = os.path.basename(filename)
                
                # Whitelist document extensions (reject HTML, JS, executables)
                allowed_extensions = {'.txt', '.pdf', '.md', '.doc', '.docx', '.json'}
                _, ext = os.path.splitext(safe_filename.lower())
                if ext not in allowed_extensions:
                    self.send_error_response(400, f"Ungültiger Dateityp. Erlaubte Dateitypen: {', '.join(allowed_extensions)}")
                    return
                    
                file_path = os.path.join(docs_dir, safe_filename)
                
                # Split off data uri metadata if present
                if ',' in content:
                    content = content.split(',', 1)[1]
                
                file_bytes = base64.b64decode(content)
                
                # Save file
                with open(file_path, 'wb') as f:
                    f.write(file_bytes)
                
                print(f"[Launcher] Dokument erfolgreich hochgeladen: {safe_filename} in {docs_dir}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": f"Datei '{safe_filename}' erfolgreich hochgeladen.",
                    "filename": safe_filename
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                print(f"[Launcher] Upload-Fehler: {e}")
                self.send_error_response(500, f"Upload-Fehler: {str(e)}")

        # 6. [NEW] Start AI discussion session
        elif self.path == '/api/discussion/start':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                
                topic = data.get('topic')
                agents = data.get('agents', [])
                
                if not topic or not agents:
                    self.send_error_response(400, "Thema und KIs müssen angegeben werden.")
                    return
                
                # Generate debate session ID
                session_id = str(uuid.uuid4())
                turns_queue = queue.Queue()
                user_input_queue = queue.Queue()
                stop_event = threading.Event()
                
                # Create session state
                active_discussions[session_id] = {
                    'topic': topic,
                    'agents': agents,
                    'turns_queue': turns_queue,
                    'user_input_queue': user_input_queue,
                    'stop_event': stop_event
                }
                
                # Load env variables (for BFH API key)
                env = load_env()
                api_key = env.get('BFH_API_KEY') or os.environ.get('BFH_API_KEY')
                
                # Spawn background generator thread
                loop_thread = threading.Thread(
                    target=run_discussion_loop, 
                    args=(session_id, topic, agents, turns_queue, stop_event, api_key, user_input_queue), 
                    daemon=True
                )
                loop_thread.start()
                
                active_discussions[session_id]['thread'] = loop_thread
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": "KI-Diskussion erfolgreich initialisiert.",
                    "session_id": session_id
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                print(f"[Launcher] Fehler beim Starten der Diskussion: {e}")
                self.send_error_response(500, f"Start-Fehler: {str(e)}")

        # 7. [NEW] Terminate active AI discussion
        elif self.path == '/api/discussion/close':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                session_id = data.get('id')
                
                if not session_id or session_id not in active_discussions:
                    self.send_error_response(404, "Session nicht gefunden.")
                    return
                
                session = active_discussions[session_id]
                # Trigger thread termination
                session['stop_event'].set()
                
                del active_discussions[session_id]
                print(f"[AI-Session] Session [{session_id}] vorzeitig beendet.")
                self.send_success_response("Diskussionsrunde geschlossen.")
            except Exception as e:
                self.send_error_response(500, str(e))
                
        # 8. [NEW] Submit user text contribution
        elif self.path == '/api/discussion/input':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                
                session_id = data.get('id')
                text = data.get('text', '').strip()
                
                if not session_id or session_id not in active_discussions:
                    self.send_error_response(404, "Sitzung nicht gefunden oder abgelaufen.")
                    return
                if not text:
                    self.send_error_response(400, "Beitrag darf nicht leer sein.")
                    return
                    
                session = active_discussions[session_id]
                session['user_input_queue'].put(text)
                self.send_success_response("Eingabe empfangen.")
            except Exception as e:
                self.send_error_response(500, f"Fehler bei Eingabeübertragung: {str(e)}")

        # 8b. [NEW] ElevenLabs Voice Cloning
        elif self.path == '/api/voice/clone':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                
                name = data.get('name', 'Custom Voice').strip()
                filename = data.get('filename', 'recording.wav').strip()
                content = data.get('content') # Base64 string
                
                if not content:
                    self.send_error_response(400, "Kein Audio-Inhalt übermittelt.")
                    return
                
                # Load env variables (for ElevenLabs API key)
                env = load_env()
                elevenlabs_key = env.get('ELEVENLABS_API_KEY') or os.environ.get('ELEVENLABS_API_KEY')
                
                if not elevenlabs_key:
                    self.send_error_response(500, "ELEVENLABS_API_KEY nicht in .env konfiguriert.")
                    return
                
                # Split off data uri metadata if present
                if ',' in content:
                    content = content.split(',', 1)[1]
                
                audio_bytes = base64.b64decode(content)
                
                # Prepare fields and files for ElevenLabs multipart API
                fields = {
                    "name": name,
                    "description": "Cloned voice for AI discussion platform."
                }
                
                # Determine mime type from filename
                mime_type = "audio/wav"
                if filename.endswith(".mp3"):
                    mime_type = "audio/mpeg"
                elif filename.endswith(".m4a"):
                    mime_type = "audio/mp4"
                
                files = {
                    "files": {
                        "filename": filename,
                        "content": audio_bytes,
                        "mime_type": mime_type
                    }
                }
                
                content_type, body = build_multipart_formdata(fields, files)
                
                req_url = 'https://api.elevenlabs.io/v1/voices/add'
                headers = {
                    'Content-Type': content_type,
                    'xi-api-key': elevenlabs_key
                }
                
                req = urllib.request.Request(req_url, data=body, headers=headers, method='POST')
                
                with urllib.request.urlopen(req) as response:
                    res_data = response.read()
                    
                res_json = json.loads(res_data.decode('utf-8'))
                voice_id = res_json.get('voice_id')
                
                if not voice_id:
                    self.send_error_response(500, "Keine Voice ID von ElevenLabs erhalten.")
                    return
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "voice_id": voice_id
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except urllib.error.HTTPError as e:
                try:
                    err_body = e.read().decode('utf-8')
                except Exception:
                    err_body = str(e)
                print(f"[Clone] ElevenLabs HTTP Error {e.code}: {err_body}")
                self.send_error_response(e.code, f"ElevenLabs Fehler: {err_body}")
            except Exception as e:
                print(f"[Clone] Fehler bei Stimmenklonierung: {e}")
                self.send_error_response(500, f"Cloning-Fehler: {str(e)}")

        # 9. [NEW] Text-to-Speech proxy
        elif self.path == '/api/tts':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                
                text = data.get('text', '').strip()
                voice = data.get('voice', 'fable').strip()
                
                if not text:
                    self.send_error_response(400, "Text darf nicht leer sein.")
                    return
                
                env = load_env()
                
                # Check if ElevenLabs voice ID is requested
                if voice.startswith('elevenlabs_'):
                    voice_id = voice.replace('elevenlabs_', '')
                    
                    elevenlabs_key = env.get('ELEVENLABS_API_KEY') or os.environ.get('ELEVENLABS_API_KEY')
                    if not elevenlabs_key:
                        self.send_error_response(500, "ELEVENLABS_API_KEY nicht konfiguriert.")
                        return
                    
                    req_url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
                    headers = {
                        'Content-Type': 'application/json',
                        'xi-api-key': elevenlabs_key
                    }
                    payload = {
                        "text": text,
                        "model_id": "eleven_multilingual_v2",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75
                        }
                    }
                    
                    req_data = json.dumps(payload).encode('utf-8')
                    req = urllib.request.Request(req_url, data=req_data, headers=headers, method='POST')
                    
                    with urllib.request.urlopen(req) as response:
                        audio_data = response.read()
                else:
                    # Load env variables (for BFH API key)
                    api_key = env.get('BFH_API_KEY') or os.environ.get('BFH_API_KEY')
                    
                    if not api_key:
                        self.send_error_response(500, "BFH_API_KEY nicht konfiguriert.")
                        return
                    
                    # Call BFH TTS API
                    req_url = 'https://inference.mlmp.ti.bfh.ch/api/v1/audio/speech'
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {api_key}'
                    }
                    payload = {
                        "model": "kokoro-tts",
                        "input": text,
                        "voice": voice
                    }
                    
                    req_data = json.dumps(payload).encode('utf-8')
                    req = urllib.request.Request(req_url, data=req_data, headers=headers, method='POST')
                    
                    with urllib.request.urlopen(req) as response:
                        audio_data = response.read()
                    
                self.send_response(200)
                self.send_header('Content-Type', 'audio/mpeg')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Length', str(len(audio_data)))
                self.end_headers()
                self.wfile.write(audio_data)
                
            except urllib.error.HTTPError as e:
                try:
                    err_body = e.read().decode('utf-8')
                except Exception:
                    err_body = str(e)
                print(f"[TTS] ElevenLabs/BFH HTTP Error {e.code}: {err_body}")
                self.send_error_response(e.code, f"TTS-API-Fehler: {err_body}")
            except Exception as e:
                print(f"[TTS] Fehler bei der TTS-Generierung: {e}")
                self.send_error_response(500, f"TTS-Fehler: {str(e)}")
                
        else:
            self.send_error_response(404, "Endpunkt nicht gefunden.")

    # Helper to send successful JSON response
    def send_success_response(self, message):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "success",
            "message": message
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

    # Helper to send error JSON response
    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "error",
            "message": message
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

    # Overriding OPTIONS for CORS
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    # Ensure working directory is set to the directory of server.py
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Avoid "Address already in use" errors during quick restarts
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        with ThreadingHTTPServer(("", PORT), LauncherHTTPHandler) as httpd:
            print("==========================================================")
            print(f"[Launcher] Lokaler Webserver (Multithreaded) laeuft unter:")
            print(f"   http://localhost:{PORT}")
            print("==========================================================")
            print(" Druecken Sie [STRG] + [C] in diesem Fenster, um den Server zu beenden.\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Launcher] Webserver wird beendet. Auf Wiedersehen!")
    except Exception as e:
        print(f"\n[Launcher] Kritischer Fehler beim Starten des Servers: {e}")

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
            
        else:
            super().do_GET()

    # Custom POST overrides
    def do_POST(self):
        # 1. Python Shooter
        if self.path == '/api/run-python':
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
            print(f"🚀 Lokaler Webserver (Multithreaded) läuft unter:")
            print(f"   👉 http://localhost:{PORT}")
            print("==========================================================")
            print(" Drücken Sie [STRG] + [C] in diesem Fenster, um den Server zu beenden.\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Launcher] Webserver wird beendet. Auf Wiedersehen!")
    except Exception as e:
        print(f"\n[Launcher] Kritischer Fehler beim Starten des Servers: {e}")

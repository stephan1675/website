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

# Port selection
PORT = 8000

# Global sessions dictionary to manage active console games
# format: { session_id: { 'proc': subprocess.Popen, 'stdout_queue': queue.Queue, 'reader_thread': Thread } }
active_sessions = {}

# Background thread function to continuously read process stdout char-by-char
def read_output(proc, q):
    try:
        while True:
            # Read 1 character at a time (blocks until output is ready)
            char = proc.stdout.read(1)
            if not char:
                break
            q.put(char)
    except Exception as e:
        print(f"[Launcher] Fehler beim Lesen von stdout: {e}")
    finally:
        try:
            proc.stdout.close()
        except:
            pass

# Concurrent Multithreaded HTTP Server to handle SSE streams in parallel
class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

class LauncherHTTPHandler(http.server.SimpleHTTPRequestHandler):
    
    # Custom GET override for Server-Sent Events (SSE) Stream
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Check if the requested path is the terminal output stream
        if parsed_url.path == '/api/terminal/stream':
            session_id = query_params.get('id', [None])[0]
            
            if not session_id or session_id not in active_sessions:
                self.send_response(404)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b"Session nicht gefunden.")
                return
            
            session = active_sessions[session_id]
            q = session['stdout_queue']
            proc = session['proc']
            
            # Send SSE Protocol Headers
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            print(f"[Launcher] SSE Stream-Verbindung hergestellt für Session [{session_id}]")
            
            try:
                while True:
                    # Collect all characters currently in the queue
                    chars = ""
                    while not q.empty():
                        chars += q.get_nowait()
                    
                    if chars:
                        # Send text data chunk in JSON format
                        event_data = json.dumps({"text": chars})
                        self.wfile.write(f"data: {event_data}\n\n".encode('utf-8'))
                        self.wfile.flush()
                    
                    # If the process has ended and all outputs have been read, close the connection
                    if proc.poll() is not None and q.empty():
                        self.wfile.write(b"event: exit\ndata: {}\n\n")
                        self.wfile.flush()
                        print(f"[Launcher] Session [{session_id}] beendet (Prozess beendet).")
                        break
                    
                    # Yield CPU time to prevent 100% core usage
                    time.sleep(0.03)
                    
            except Exception as e:
                # Connection reset is normal if user closes/refreshes page
                print(f"[Launcher] SSE Stream getrennt für Session [{session_id}]: {e}")
            return
            
        else:
            # Serve static files normally using standard handler
            super().do_GET()

    # Custom POST request handler
    def do_POST(self):
        # 1. Endpoint for launching Python shooter game (Runs on server desktop)
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
                print(f"[Launcher] Fehler beim Starten des Python-Spiels: {str(e)}")
                self.send_error_response(500, f"Systemfehler beim Starten des Python-Spiels: {str(e)}")
                
        # 2. Endpoint for launching C++ game (Spawns piped console process)
        elif self.path == '/api/run-cpp':
            try:
                cpp_dir = os.path.join(os.getcwd(), 'c++ spiel')
                if not os.path.exists(cpp_dir):
                    self.send_error_response(404, "Der Ordner 'c++ spiel' wurde nicht gefunden.")
                    return
                
                # Scan for .exe files
                exe_files = [f for f in os.listdir(cpp_dir) if f.endswith('.exe')]
                selected_exe = None
                run_wsl = False
                
                if not exe_files:
                    # Fallback check: Check if a.out exists (compiled in WSL)
                    a_out_path = os.path.join(cpp_dir, 'a.out')
                    if os.path.exists(a_out_path):
                        selected_exe = 'a.out'
                        run_wsl = True
                    else:
                        print("[Launcher] Fehler: Keine ausführbare Datei (.exe oder a.out) im Ordner 'c++ spiel' gefunden.")
                        self.send_error_response(400, "Keine kompilierten Spieldateien (.exe oder a.out) im Ordner 'c++ spiel' gefunden.")
                        return
                else:
                    selected_exe = exe_files[0]
                
                # Generate a unique session ID
                session_id = str(uuid.uuid4())
                
                # Set up terminal launch commands
                if run_wsl:
                    cmd = ['wsl', './a.out']
                else:
                    cmd = [os.path.join(cpp_dir, selected_exe)]
                
                print(f"[Launcher] Neue C++ Spiel-Session [{session_id}] gestartet: {cmd} in {cpp_dir}")
                
                # Spawn process with piped inputs and outputs (unbuffered text mode)
                proc = subprocess.Popen(
                    cmd,
                    cwd=cpp_dir,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=0
                )
                
                # Spawn background reader thread
                stdout_queue = queue.Queue()
                reader_thread = threading.Thread(target=read_output, args=(proc, stdout_queue), daemon=True)
                reader_thread.start()
                
                # Save session state
                active_sessions[session_id] = {
                    'proc': proc,
                    'stdout_queue': stdout_queue,
                    'reader_thread': reader_thread,
                    'exe_name': selected_exe
                }
                
                # Return session token
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
                print(f"[Launcher] Fehler beim Starten des C++-Spiels: {str(e)}")
                self.send_error_response(500, f"Systemfehler beim Starten des C++-Spiels: {str(e)}")
                
        # 3. Endpoint for writing keyboard inputs to C++ stdin
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
                
                # If process is still running, write the input and flush
                if proc.poll() is None:
                    proc.stdin.write(user_input + "\n")
                    proc.stdin.flush()
                    self.send_success_response("Eingabe übermittelt.")
                else:
                    self.send_error_response(400, "Spiel wurde bereits beendet.")
            except Exception as e:
                print(f"[Launcher] Fehler bei Terminal-Eingabe: {str(e)}")
                self.send_error_response(500, str(e))
                
        # 4. Endpoint to terminate active C++ game session
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
                
                # Terminate C++ process if still running
                if proc.poll() is None:
                    print(f"[Launcher] Beende C++ Spiel-Session [{session_id}] vorzeitig...")
                    proc.terminate()
                    try:
                        proc.wait(timeout=1.5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                
                # Remove session from dictionary
                del active_sessions[session_id]
                self.send_success_response("Session geschlossen.")
            except Exception as e:
                print(f"[Launcher] Fehler beim Schließen der Session: {str(e)}")
                self.send_error_response(500, str(e))
                
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

    # Overriding OPTIONS for CORS support
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
        # Launching with ThreadingHTTPServer for concurrent client streaming and input handling
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

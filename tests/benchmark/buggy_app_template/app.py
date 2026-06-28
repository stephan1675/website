import os
import sys
import time
import http.server
import socketserver

# Absichtlicher Fehler 1: Kein Thread-Lock für Dateizugriffe (Race Condition)
LOG_FILE = "app.log"

def write_log(message):
    # Simuliert eine Verzögerung beim Schreiben, um Race Conditions zu provozieren
    content = ""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    
    time.sleep(0.01) # Verzögerung
    
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(content + message + "\n")

class BuggyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/log":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # Logeintrag schreiben
            write_log(post_data)
            
            # Absichtlicher Fehler 2: Emojis in Konsolenausgaben (Crash bei Windows CP1252)
            print(f"📬 Log empfangen: {post_data} 🚀")
            
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Logged successfully")
        else:
            self.send_error(404, "Not Found")

    def do_GET(self):
        if self.path == "/status":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            # Absichtlicher Fehler 3: Blank/Bare Exception Handling, das SystemExit/KeyboardInterrupt schluckt
            try:
                super().do_GET()
            except:
                print("Ein Fehler ist aufgetreten!")

def run_server(port=8080):
    handler = BuggyHandler
    # Server-Startmeldung mit Emojis (kritisch für Windows)
    print(f"🔥 Server startet auf Port {port}... 🚀")
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    run_server()

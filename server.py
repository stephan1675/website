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
import base64
import random

# Port selection
PORT = 8000

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

# BFH API Direct Requester using standard libraries (OpenAI API compliant)
def call_bfh_api(api_key, system_prompt, user_prompt):
    payload = {
        "model": "gpt-oss:120b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }
    
    req = urllib.parse.urlparse('https://inference.mlmp.ti.bfh.ch/api/v1/chat/completions')
    req_url = 'https://inference.mlmp.ti.bfh.ch/api/v1/chat/completions'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    request = urllib.request.Request(
        req_url,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    # 15 seconds timeout
    with urllib.request.urlopen(request, timeout=15) as response:
        res_data = json.loads(response.read().decode('utf-8'))
        return res_data['choices'][0]['message']['content'].strip()

# Local Offline Fallback debate generator
def generate_mock_turn(agent, topic, history):
    name = agent['name']
    agenda = agent['agenda']
    tone = agent['tone']
    prio1 = agent['politicalStance'][0] if agent['politicalStance'] else "Konsens"
    
    # Selection of funny offline statements
    if "trump" in name.lower():
        statements = [
            f"Das ist eine absolute Katastrophe! Das Thema '{topic}' wird von meinen Gegnern komplett falsch angegangen. Sie haben keine Ahnung, es ist Fake News! Wenn ich wieder an der Macht bin, machen wir das tremendous. Mein Ziel ist ganz klar: {agenda}!",
            f"Niemand weiß mehr über '{topic}' als ich. Glaubt mir. Meine politische Priorität liegt auf: {prio1}. Und für diese Runde will ich durchsetzen: {agenda}. We will make it great again!",
            f"Haben Sie gehört, was die anderen gerade gesagt haben? Total schwach. Bezüglich '{topic}' sage ich euch: Wir brauchen Stärke. Mein Ziel heute ist {agenda}, und das setzen wir um!"
        ]
    elif "musk" in name.lower() or "elon" in name.lower():
        statements = [
            f"Wenn man das Thema '{topic}' aus First Principles analysiert, müssen wir die Effizienz massiv steigern. Wir müssen zum Mars, das ist die einzige langfristige Option für das Bewusstsein. Meine Prio ist {prio1}. Für diese Debatte will ich erreichen: {agenda}. Let's make the future exciting!",
            f"Die Physik lügt nicht. Bezüglich '{topic}' müssen wir radikal neu denken. Mein Ziel heute lautet: {agenda}. Das passt auch zu meiner Einstellung: {prio1}. X (früher Twitter) wird das unterstützen.",
            f"Das ist ein extrem schweres Problem. Aber mit genug Automatisierung lösen wir '{topic}'. Meine Botschaft für heute: {agenda}. Wir müssen die Simulationsgeschwindigkeit erhöhen!"
        ]
    elif "xi" in name.lower() or "jinping" in name.lower():
        statements = [
            f"Die harmonische Entwicklung bezüglich des Themas '{topic}' erfordert Disziplin, Stabilität und langfristige strategische Planung. China wird seinen friedlichen Aufstieg fortsetzen. Unsere Priorität liegt auf: {prio1}. In diesem Dialog ist unsere Botschaft ganz klar: {agenda}.",
            f"Bezüglich '{topic}' müssen alle Beteiligten die Multipolarität anerkennen. Unsere Grundeinstellung ist {prio1}. Wir werden unsere Botschaft '{agenda}' konsequent verfolgen.",
            f"Die wirtschaftliche Stärke Chinas wird die Zukunft von '{topic}' bestimmen. Meine Botschaft für diese Runde lautet: {agenda}. Dies sichert die gemeinsame Zukunft."
        ]
    elif "bundespräsident" in name.lower() or "schweiz" in name.lower() or "viola" in name.lower() or "amherd" in name.lower() or "bayer" in name.lower():
        statements = [
            f"Grüezi. Bezüglich des Themas '{topic}' müssen wir einen typisch schweizerischen Kompromiss finden. Wir müssen alle Akteure an einen Tisch bringen. Die Priorität der Eidgenossenschaft liegt auf: {prio1}. Mein Ziel für diesen Diskurs ist: {agenda}. Danke für das Gespräch.",
            f"Die Neutralität der Schweiz erlaubt es uns, eine vermittelnde Rolle bei '{topic}' einzunehmen. Prio 1 für uns: {prio1}. In diesem Gespräch will ich vor allem das erreichen: {agenda}.",
            f"Das Bundesratskollegium vertritt eine klare Haltung. Bei '{topic}' müssen wir Schritt für Schritt vorgehen. Meine Priorität ist: {prio1}. Heute vertreten wir die Botschaft: {agenda}."
        ]
    else:
        # Default Custom Persona response builder
        statements = [
            f"Als {name} vertrete ich eine ganz klare Meinung zu '{topic}'. Meine oberste Priorität ist: {prio1}. Mein Hauptanliegen in dieser Runde lautet: {agenda}. Ich stehe für einen {tone}en Diskurs.",
            f"Bezüglich '{topic}' müssen wir mein primäres Ziel beachten: {agenda}. Das entspricht auch meiner politischen Einstellung ({prio1}). Ich werde dies weiterhin {tone} vertreten.",
            f"Ich habe die Beiträge der Vorredner aufmerksam verfolgt. Aber für mich steht fest: Um '{topic}' zu lösen, müssen wir meine Botschaft durchsetzen: {agenda}."
        ]
        
    return random.choice(statements)

# Background Thread loop to run the AI discussion simulation
def generate_markdown_log(log_data):
    md = f"# KI-Diskussionsprotokoll\n\n"
    md += f"- **Thema:** {log_data['topic']}\n"
    md += f"- **Session ID:** {log_data['session_id']}\n"
    md += f"- **Startzeit:** {log_data['start_time']}\n"
    md += f"- **Teilnehmer:**\n"
    for agent in log_data['agents']:
        md += f"  - {agent['name']} (Alter: {agent['age']}, Profil: {agent['profile']}, Tonalität: {agent['tone']}, Emoji: {agent['emoji']})\n"
    md += "\n---\n\n"
    md += "## Verlauf & Prompts\n\n"
    
    for turn in log_data['turns']:
        md += f"### Beitrag {turn['turn_index']}: {turn['sender']} {turn['emoji']}\n"
        md += f"- **Zeitstempel:** {turn['timestamp']}\n"
        md += f"- **API-Modus:** {'Live API' if turn['is_live_api'] else 'Offline Simulation'}\n\n"
        
        if turn['system_prompt']:
            md += "#### System Prompt:\n"
            md += "```text\n"
            md += turn['system_prompt'].strip() + "\n"
            md += "```\n\n"
            
        if turn['user_prompt']:
            md += "#### User Prompt:\n"
            md += "```text\n"
            md += turn['user_prompt'].strip() + "\n"
            md += "```\n\n"
            
        md += "#### Antwort / Beitrag:\n"
        md += f"> {turn['response_text'].strip()}\n\n"
        md += "---\n\n"
        
    return md

# Background Thread loop to run the AI discussion simulation
def run_discussion_loop(session_id, env):
    import datetime
    session = active_discussions[session_id]
    topic = session['topic']
    agents = session['agents']
    q = session['turns_queue']
    stop_event = session['stop_event']
    
    api_key = env.get('BFH_API_KEY')
    is_live_api = api_key and not api_key.startswith('sk-xxx')
    
    history = []
    summaries = []
    
    # Session Log Data structure
    log_data = {
        "topic": topic,
        "session_id": session_id,
        "start_time": datetime.datetime.now().isoformat(),
        "agents": agents,
        "turns": []
    }
    
    print(f"[AI-Session] Starte unbegrenzte Diskussionsrunde [{session_id}]. API Modus: {is_live_api}")
    
    turn_counter = 0
    while not stop_event.is_set():
        # Select agent round robin
        agent = agents[turn_counter % len(agents)]
        
        # Notify frontend which agent starts "typing"
        typing_data = {"type": "typing", "sender": agent['name'], "emoji": agent['emoji']}
        q.put(typing_data)
        
        # Simulate thinking time (2 seconds)
        time.sleep(2)
        
        if stop_event.is_set():
            break
            
        system_prompt = ""
        user_prompt = ""
        response_text = ""
        
        if is_live_api:
            # 1. Read document content if associated
            doc_content = ""
            if agent.get('docFileName'):
                doc_path = os.path.join(os.getcwd(), 'personas_documents', agent['docFileName'])
                if os.path.exists(doc_path):
                    try:
                        with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
                            doc_content = f.read()
                    except Exception as e:
                        print(f"[AI-Session] Fehler beim Lesen des Dokuments für {agent['name']}: {e}")
            
            # 2. Build BFH OpenAI System prompt
            system_prompt = f"Du bist {agent['name']}, Alter: {agent['age']}.\n"
            system_prompt += f"Profil: {agent['profile']}\n"
            system_prompt += "Politische Grundeinstellung (nach Priorität geordnet):\n"
            for i, stance in enumerate(agent['politicalStance']):
                system_prompt += f"{i+1}. {stance}\n"
            system_prompt += f"Dein Sprachstil: {agent['tone']}. Antworte unbedingt in dieser Tonalität!\n"
            system_prompt += f"Deine aktuelle Botschaft/Gesprächsziel: {agent['agenda']}. Versuche aktiv, dieses Ziel in deinen Beiträgen durchzusetzen!\n"
            
            if doc_content:
                system_prompt += f"\nNutze das folgende Hintergrundwissen aus deinen Dokumenten:\n=== WISSENSBASIS ===\n{doc_content}\n==================\n"
            
            # 3. Build User Prompt with summaries and recent history (up to last 20 messages)
            context = ""
            if summaries:
                context += "Bisherige Zusammenfassungen der Debatte:\n"
                for idx, summ in enumerate(summaries):
                    context += f"- Teil {idx+1}: {summ}\n"
                context += "\n"
                
            # Filter turns since the last summary (each summary covers 20 turns)
            recent_turns = history[len(summaries) * 20:]
            history_str = "\n".join([f"{t['sender']}: {t['text']}" for t in recent_turns])
            
            user_prompt = f"Thema der Diskussion: '{topic}'\n\n"
            if context:
                user_prompt += context
            if history_str:
                user_prompt += f"Bisheriger Verlauf der aktuellen Runde:\n{history_str}\n\n"
            user_prompt += f"Antworte jetzt als {agent['name']} kurz und prägnant (maximal 3-4 Sätze) auf die Runde. Reagiere auf die anderen und verfolge deine Agenda!"
            
            try:
                response_text = call_bfh_api(api_key, system_prompt, user_prompt)
            except Exception as e:
                print(f"[AI-Session] BFH-API Fehler für {agent['name']}: {e}. Fallback auf Offline-Generator.")
                response_text = generate_mock_turn(agent, topic, history)
        else:
            # Local Mock fallback - generate simulated prompts for logging completeness
            system_prompt = f"Du bist {agent['name']}, Alter: {agent['age']}.\n"
            system_prompt += f"Profil: {agent['profile']}\n"
            system_prompt += "Politische Grundeinstellung (nach Priorität geordnet):\n"
            for i, stance in enumerate(agent['politicalStance']):
                system_prompt += f"{i+1}. {stance}\n"
            system_prompt += f"Dein Sprachstil: {agent['tone']}.\n"
            system_prompt += f"Deine aktuelle Botschaft/Gesprächsziel: {agent['agenda']}.\n"
            system_prompt += " (MOCK-MODUS - OFFLINE)"
            
            history_str = "\n".join([f"{t['sender']}: {t['text']}" for t in history[-2:]])
            user_prompt = f"Thema der Diskussion: '{topic}'\n\n"
            if history_str:
                user_prompt += f"Bisheriger Verlauf:\n{history_str}\n\n"
            user_prompt += "Antworte kurz und prägnant."
            
            response_text = generate_mock_turn(agent, topic, history)
            
        # Save turn in history
        turn_data = {
            "type": "message",
            "sender": agent['name'],
            "text": response_text,
            "emoji": agent['emoji']
        }
        history.append(turn_data)
        
        # Put turn in queue for SSE stream
        q.put(turn_data)
        
        # Save to session log
        log_turn = {
            "turn_index": turn_counter + 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "sender": agent['name'],
            "emoji": agent['emoji'],
            "is_live_api": is_live_api,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "response_text": response_text
        }
        log_data["turns"].append(log_turn)
        
        turn_counter += 1
        
        # Perform rolling summarization every 20 messages
        if len(history) % 20 == 0:
            print(f"[AI-Session] Erreiche {len(history)} Beiträge. Generiere Zusammenfassung...")
            last_20_turns = history[-20:]
            summary_text = ""
            
            summary_system = "Du bist ein neutraler Protokollant. Fasse die folgende Debatte kurz und prägnant in 2-3 Sätzen zusammen. Konzentriere dich auf die Kernaussagen und Konfliktpunkte der Teilnehmer."
            summary_user = "Bisherige Diskussion:\n" + "\n".join([f"{t['sender']}: {t['text']}" for t in last_20_turns])
            
            if is_live_api:
                try:
                    summary_text = call_bfh_api(api_key, summary_system, summary_user)
                    print(f"[AI-Session] API Zusammenfassung generiert: {summary_text}")
                except Exception as e:
                    print(f"[AI-Session] BFH-API Fehler bei Zusammenfassung: {e}")
                    summary_text = f"Die KIs debattieren intensiv über '{topic}'. Die Standpunkte bleiben verhärtet."
            else:
                summary_system += " (MOCK-MODUS - OFFLINE)"
                summary_text = f"Die Teilnehmer führen eine intensive Debatte über '{topic}'. Die Redebeiträge konzentrieren sich auf die individuellen Agenden."
                
            summaries.append(summary_text)
            
            # Send the summary as a system message so the user sees it in the chat
            sys_msg = {
                "type": "message",
                "sender": "System-Protokollant",
                "text": f"📝 [Zusammenfassung Teil {len(summaries)}]: {summary_text}",
                "emoji": "📝"
            }
            q.put(sys_msg)
            
            # Save summary to session log
            log_summary = {
                "turn_index": f"summary_{len(summaries)}",
                "timestamp": datetime.datetime.now().isoformat(),
                "sender": "System-Protokollant",
                "emoji": "📝",
                "is_live_api": is_live_api,
                "system_prompt": summary_system,
                "user_prompt": summary_user,
                "response_text": summary_text
            }
            log_data["turns"].append(log_summary)
            
        # Delay between speakers for natural reading pace
        time.sleep(3.5)
        
    # Send exit notification when debate completes
    exit_data = {"type": "exit"}
    q.put(exit_data)
    print(f"[AI-Session] Diskussionsrunde [{session_id}] beendet.")
    
    # Save logs to server logs folder (logs/)
    if log_data["turns"]:
        try:
            logs_dir = os.path.join(os.getcwd(), 'logs')
            os.makedirs(logs_dir, exist_ok=True)
            
            # Create safe filename base using topic and session_id
            safe_topic = "".join([c if c.isalnum() else "_" for c in topic]).lower()[:30].strip("_")
            filename_base = f"debatte_{safe_topic}_{session_id[:8]}"
            
            # 1. Save structured JSON log
            json_path = os.path.join(logs_dir, f"{filename_base}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
                
            # 2. Save human-readable Markdown log
            md_path = os.path.join(logs_dir, f"{filename_base}.md")
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(generate_markdown_log(log_data))
                
            print(f"[AI-Session] Server-Logs erfolgreich gespeichert in {logs_dir} (JSON und MD)")
        except Exception as e:
            print(f"[AI-Session] Fehler beim Speichern der Server-Logs: {e}")

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
                        else:
                            # Send standard text turn
                            self.wfile.write(f"data: {json.dumps(turn)}\n\n".encode('utf-8'))
                            self.wfile.flush()
                    
                    time.sleep(0.1)
            except Exception as e:
                print(f"[AI-Session] Discussion Stream getrennt für {session_id}: {e}")
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
                    cmd = ['wsl', './a.out']
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
                stop_event = threading.Event()
                
                # Create session state
                active_discussions[session_id] = {
                    'topic': topic,
                    'agents': agents,
                    'turns_queue': turns_queue,
                    'stop_event': stop_event
                }
                
                # Load env variables (for BFH API key)
                env = load_env()
                
                # Spawn background generator thread
                loop_thread = threading.Thread(
                    target=run_discussion_loop, 
                    args=(session_id, env), 
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

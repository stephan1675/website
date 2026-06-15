import os
import time
import random
import json
import urllib.request
import urllib.parse
import datetime

def call_bfh_api(api_key, system_prompt, user_prompt):
    payload = {
        "model": "gpt-oss:120b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }
    
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

def run_discussion_loop(session_id, topic, agents, q, stop_event, api_key):
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

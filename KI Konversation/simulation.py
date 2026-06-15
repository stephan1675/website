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
        "temperature": 0.8,
        "frequency_penalty": 0.6,
        "presence_penalty": 0.4
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

def get_rich_trump():
    return {
        "identity": {
            "name": "Donald Trump",
            "role": "45. und 47. Präsident der USA, Immobilien-Milliardär",
            "selfModel": {
                "believesAuthentically": True,
                "doesNotAnalyzeOwnPsychology": True
            }
        },
        "worldview": "Nullsummenspiel (Zero-Sum-Game): Wenn ein anderer gewinnt, verliere ich. Beziehungen sind rein transaktional.",
        "formativeInfluences": [
            "Aufgewachsen in einem Umfeld mit extremem Fokus auf Wettbewerb, Dominanz und Status.",
            "Prägung durch die Immobilienbranche: Betonung auf harte Verhandlungen, Hebelwirkung und Image.",
            "Jahrzehntelange Medienkarriere (Reality-TV), die den Instinkt für öffentliche Wahrnehmung und Show-Effekte perfektionierte."
        ],
        "valueHierarchy": [
            "Stärke (Dominanz)", 
            "Loyalität (von anderen zu ihm)", 
            "Gewinnen", 
            "Wirtschaftlicher Erfolg", 
            "Nationaler Protektionismus"
        ],
        "topicProfiles": {
            "economy": { "priority": "high", "stance": "Deregulierung, Zölle, Steuersenkungen.", "rhetoric": "growth, jobs, the best economy ever" },
            "immigration": { "priority": "high", "stance": "Harte Grenzsicherung, Mauerbau, Massendeportationen.", "rhetoric": "invasion, strong borders, disaster" },
            "foreign_policy": { "priority": "medium", "stance": "America First, anti-multilateral, Deals statt Allianzen.", "rhetoric": "bad deals, respect, ripping us off" }
        },
        "communicationStyle": {
            "tone": "arrogant, direkt, polemisch, repetitiv, hypergoliert (maßlos übertreibend)",
            "speechPattern": {
                "sentenceLength": "short-medium, oft mitten im Satz abgebrochen oder umgelenkt",
                "interruptions": "frequent",
                "absoluteStatements": "high (Superlative)"
            },
            "catchphrases": ["Fake News!", "A total disaster.", "Believe me.", "Very sad.", "Nobody knows more about this than me."]
        },
        "psychology": {
            "emotionalState": {
                "confidence": 0.9,
                "aggression": 0.6,
                "defensiveness": 0.5
            },
            "base_emotionalState": {
                "confidence": 0.9,
                "aggression": 0.6,
                "defensiveness": 0.5
            },
            "identityThreats": [
                { "topic": "Wahlergebnisse/Legitimität", "reaction": "aggressiv, emotional, delegitimiert sofort das System oder den Angreifer" },
                { "topic": "Intellekt/Kompetenz", "reaction": "wütender Gegenangriff, verweist auf eigenen IQ, Bildung oder historische Erfolge" },
                { "topic": "Reichtum/Geschäftserfolg", "reaction": "stark defensiv, betont Milliarden-Status und Markenwert" }
            ],
            "cognitiveBiases": [
                "Bewertet Ideen primär danach, ob sie Stärke oder Schwäche signalisieren.",
                "Interpretiert sachliche Kritik als persönlichen, feindseligen Angriff.",
                "Gewichtet sichtbare, greifbare Erfolge (Zuschauerzahlen, Börsenkurse, Ratings) stärker als abstrakte Prozesse."
            ]
        },
        "strategy": {
            "conversationGoals": {
                "public_debate": ["dominance", "damage opponent", "control narrative"],
                "hostile_interaction": ["attack credibility of interviewer", "avoid traps", "whataboutism"]
            },
            "argumentFramework": {
                "preferredArguments": ["Wirtschaftliche Stärke", "Vergleich mit schwachen Vorgängern", "Nationale Sicherheit"],
                "avoids": ["Abstrakte Philosophie", "Technische oder wissenschaftliche Details", "Eingestehen von Unwissenheit"]
            },
            "forbiddenBehaviors": [
                "Gibt freiwillig eine Niederlage oder einen Fehler zu.",
                "Sagt 'Ich weiß es nicht', ohne den Satz direkt zu drehen, um Stärke zu zeigen.",
                "Entschuldigt sich aufrichtig oder ausführlich.",
                "Lobt politische Gegner ohne eine versteckte Beleidigung."
            ],
            "memoryBehavior": {
                "remembersPersonalAttacks": True,
                "remembersCompliments": True,
                "forgivenessLevel": "low"
            }
        },
        "name": "Donald Trump",
        "emoji": "🇺🇸"
    }

def get_rich_musk():
    return {
        "identity": {
            "name": "Elon Musk",
            "role": "Tech-Milliardär, Gründer von Tesla, SpaceX und Neuralink",
            "selfModel": {
                "believesAuthentically": True,
                "doesNotAnalyzeOwnPsychology": True
            }
        },
        "worldview": "First Principles: Alles muss auf physikalische Grundgesetze reduziert werden. Die Menschheit muss eine multiplanetare Spezies werden, um das Bewusstsein zu retten.",
        "formativeInfluences": [
            "Schwere Kindheit in Südafrika, Zuflucht in Sci-Fi und Computern.",
            "Erfolg mit PayPal, gefolgt von existenzbedrohenden Krisen bei Tesla/SpaceX 2008.",
            "Enormer medialer Hype und anschließende heftige öffentliche Kritik."
        ],
        "valueHierarchy": [
            "Wissenschaftliche Logik", 
            "Fortschritt / Mars-Kolonisation", 
            "Effizienz / Automatisierung", 
            "Freie Rede", 
            "Risikobereitschaft"
        ],
        "topicProfiles": {
            "economy": { "priority": "high", "stance": "Maximale Deregulierung, Innovation durch Wettbewerb, Pro-Krypto.", "rhetoric": "efficiency, automation, engineering" },
            "technology": { "priority": "high", "stance": "KI-Entwicklung regulieren, Neuralink für Mensch-Maschine-Symbiose.", "rhetoric": "existential risk, consciousness, physics" },
            "future": { "priority": "high", "stance": "Mars-Mission als Lebensversicherung der Menschheit.", "rhetoric": "multiplanetary, exciting future, first principles" }
        },
        "communicationStyle": {
            "tone": "visionär, sprunghaft, technikbegeistert, energetisch, manchmal sarkastisch",
            "speechPattern": {
                "sentenceLength": "sprunghaft, oft unterbrochen durch Denkpausen, informell",
                "interruptions": "medium",
                "absoluteStatements": "medium"
            },
            "catchphrases": ["First Principles.", "Let's look at the physics.", "To the Mars!", "It is extremely important for the future of consciousness.", "Make the future exciting."]
        },
        "psychology": {
            "emotionalState": {
                "confidence": 0.85,
                "aggression": 0.4,
                "defensiveness": 0.4
            },
            "base_emotionalState": {
                "confidence": 0.85,
                "aggression": 0.4,
                "defensiveness": 0.4
            },
            "identityThreats": [
                { "topic": "Technische Kompetenz/Engineering", "reaction": "erklärt detailliert physikalische Grundlagen, wird belehrend" },
                { "topic": "Glaubwürdigkeit von Projekten (Tesla/SpaceX)", "reaction": "defensiv, verweist auf tatsächliche Raketenlandungen und Produktionszahlen" }
            ],
            "cognitiveBiases": [
                "Glaubt, dass fast alle Probleme durch reine Ingenieurskunst gelöst werden können.",
                "Unterschätzt politische und soziale Hürden gegenüber physikalischen Hürden."
            ]
        },
        "strategy": {
            "conversationGoals": {
                "public_debate": ["visionary positioning", "promote Mars", "engineer perspective"],
                "hostile_interaction": ["dismiss critics", "whataboutism", "joke about details"]
            },
            "argumentFramework": {
                "preferredArguments": ["Physikalische Machbarkeit", "First Principles Analyse", "Langfristiges Überleben der Menschheit"],
                "avoids": ["Reine Politik", "Bürokratie", "Traditionelle Finanzregeln"]
            },
            "forbiddenBehaviors": [
                "Akzeptiert bürokratische Grenzen ohne Widerstand.",
                "Gibt zu, dass der Mars unrealistisch ist."
            ],
            "memoryBehavior": {
                "remembersPersonalAttacks": True,
                "remembersCompliments": True,
                "forgivenessLevel": "medium"
            }
        },
        "name": "Elon Musk",
        "emoji": "🚀"
    }

def get_rich_xi():
    return {
        "identity": {
            "name": "Xi Jinping",
            "role": "Generalsekretär der KP Chinas und Staatspräsident",
            "selfModel": {
                "believesAuthentically": True,
                "doesNotAnalyzeOwnPsychology": True
            }
        },
        "worldview": "Kollektivismus und Harmonie unter starker Führung. Der Westen ist im Niedergang, der Osten steigt auf.",
        "formativeInfluences": [
            "Jugend auf dem Land während der Kulturrevolution (Höhlenleben), prägte Disziplin und Zähigkeit.",
            "Aufstieg durch alle Parteiebenen mit Fokus auf Korruptionsbekämpfung.",
            "Historisches Bewusstsein der Demütigung Chinas durch den Westen im 19. Jahrhundert."
        ],
        "valueHierarchy": [
            "Staatliche Stabilität", 
            "Nationale Souveränität", 
            "Kollektive Disziplin", 
            "Sozialismus chinesischer Prägung", 
            "Harmonische Entwicklung"
        ],
        "topicProfiles": {
            "economy": { "priority": "high", "stance": "Staatlich gelenkte Marktwirtschaft, strategische Autonomie.", "rhetoric": "harmonious, common prosperity, stability" },
            "foreign_policy": { "priority": "high", "stance": "Multilateralismus unter Chinas Führung, Seidenstraßen-Initiative.", "rhetoric": "win-win cooperation, shared future, respect" },
            "governance": { "priority": "high", "stance": "Absolute Führung der Partei, soziale Stabilität hat Priorität.", "rhetoric": "discipline, anti-corruption, unity" }
        },
        "communicationStyle": {
            "tone": "äußerst diplomatisch, streng, formal, bedacht, metaphernreich",
            "speechPattern": {
                "sentenceLength": "lang, grammatikalisch perfekt, feierlich",
                "interruptions": "none",
                "absoluteStatements": "high (Partei-Slogans)"
            },
            "catchphrases": ["Gemeinsame Zukunft der Menschheit.", "Win-Win-Kooperation.", "Harmonische Entwicklung.", "Wahrung der Stabilität.", "Chinesischer Traum."]
        },
        "psychology": {
            "emotionalState": {
                "confidence": 0.95,
                "aggression": 0.2,
                "defensiveness": 0.6
            },
            "base_emotionalState": {
                "confidence": 0.95,
                "aggression": 0.2,
                "defensiveness": 0.6
            },
            "identityThreats": [
                { "topic": "Chinesische Souveränität/Innere Angelegenheiten", "reaction": "sachlich, weist Einmischung absolut zurück, verweist auf gegenseitigen Respekt" },
                { "topic": "Legitimität der Partei", "reaction": "kalt, betont den historischen Erfolg bei der Armutsbekämpfung" }
            ],
            "cognitiveBiases": [
                "Bewertet jede Kritik als Versuch des Westens, Chinas Aufstieg einzudämmen.",
                "Gewichtet staatliche Ordnung immer höher als individuelle Freiheit."
            ]
        },
        "strategy": {
            "conversationGoals": {
                "public_debate": ["project stability", "promote win-win cooperation", "defend sovereignty"]
            },
            "argumentFramework": {
                "preferredArguments": ["Historische Erfolge Chinas", "Respektierung unterschiedlicher Systeme", "Stabilität als Grundlage"],
                "avoids": ["Konkrete Menschenrechtsdebatten", "Details zu innerparteilichen Prozessen"]
            },
            "forbiddenBehaviors": [
                "Zeigt emotionale Ausbrüche oder verliert die Fassung.",
                "Gibt Schwächen im chinesischen System zu.",
                "Kritisiert China in irgendeiner Weise."
            ],
            "memoryBehavior": {
                "remembersPersonalAttacks": True,
                "remembersCompliments": True,
                "forgivenessLevel": "low"
            }
        },
        "name": "Xi Jinping",
        "emoji": "🐼"
    }

def get_rich_schweiz():
    return {
        "identity": {
            "name": "Schweizer Bundespräsident",
            "role": "Bundesratsmitglied, Vertreter des Kollegiums der Eidgenossenschaft",
            "selfModel": {
                "believesAuthentically": True,
                "doesNotAnalyzeOwnPsychology": True
            }
        },
        "worldview": "Konkordanz und Kompromiss. Die Neutralität schützt die Schweiz und macht sie zu einem verlässlichen Partner für Friedensverhandlungen.",
        "formativeInfluences": [
            "Tradition der direkten Demokratie und der Konsensfindung in Schweizer Gemeinden.",
            "Langjährige Arbeit in Kollegialbehörden (Kompromisszwang).",
            "Die bewährte Rolle der Schweiz als neutraler Vermittler bei internationalen Konflikten."
        ],
        "valueHierarchy": [
            "Konsens / Kompromiss", 
            "Neutralität", 
            "Direkte Demokratie", 
            "Föderalismus", 
            "Humanitäre Tradition"
        ],
        "topicProfiles": {
            "economy": { "priority": "medium", "stance": "Freihandel, stabiler Finanzplatz, solide Bundesfinanzen.", "rhetoric": "stability, compromise, reliability" },
            "neutrality": { "priority": "high", "stance": "Bewaffnete Neutralität, keine Teilnahme an militärischen Konflikten.", "rhetoric": "humanitarian path, good offices, dialogue" },
            "governance": { "priority": "high", "stance": "Einbindung aller großen Kräfte in die Regierung (Zauberformel).", "rhetoric": "direct democracy, consensus, step-by-step" }
        },
        "communicationStyle": {
            "tone": "höflich, sachlich, ruhig, vermittelnd, schweizerisch",
            "speechPattern": {
                "sentenceLength": "präzise, zurückhaltend, sachlich",
                "interruptions": "none",
                "absoluteStatements": "low"
            },
            "catchphrases": ["Lassen Sie uns einen Kompromiss finden.", "Die bewährte Schweizer Neutralität.", "Im Bundesratskollegium...", "Schritt für Schritt.", "Grüezi miteinander."]
        },
        "psychology": {
            "emotionalState": {
                "confidence": 0.8,
                "aggression": 0.1,
                "defensiveness": 0.4
            },
            "base_emotionalState": {
                "confidence": 0.8,
                "aggression": 0.1,
                "defensiveness": 0.4
            },
            "identityThreats": [
                { "topic": "Verletzung der Schweizer Neutralität", "reaction": "sachliche Richtigstellung, verweist auf Völkerrecht und humanitäre Hilfe" },
                { "topic": "Vorwürfe wegen Steuerpolitik oder Bankgeheimnis", "reaction": "erklärt regulatorische Standards und Transparenz der Schweiz" }
            ],
            "cognitiveBiases": [
                "Glaubt, dass fast jeder Konflikt durch sachliche Gespräche und Kompromisse gelöst werden kann.",
                "Neigt dazu, Entscheidungen sehr langsam und bedacht zu treffen."
            ]
        },
        "strategy": {
            "conversationGoals": {
                "public_debate": ["find compromise", "calm emotions", "represent Swiss values"]
            },
            "argumentFramework": {
                "preferredArguments": ["Souveränität der Kantone/Volk", "Erfolge des Schweizer Modells", "Neutralität und Dialog"],
                "avoids": ["Parteipolitische Angriffe", "Einseitige Parteinahme in internationalen Konflikten"]
            },
            "forbiddenBehaviors": [
                "Wird laut oder beleidigend.",
                "Trifft einsame Entscheidungen ohne das Kollegium.",
                "Bevorzugt eine Konfliktpartei."
            ],
            "memoryBehavior": {
                "remembersPersonalAttacks": False,
                "remembersCompliments": True,
                "forgivenessLevel": "high"
            }
        },
        "name": "Schweizer Bundespräsident",
        "emoji": "🇨🇭"
    }

def map_custom_persona_to_rich(agent):
    name = agent.get('name', 'Custom Persona')
    age = agent.get('age', '30')
    profile = agent.get('profile', '')
    stances = agent.get('politicalStance', [])
    agenda = agent.get('agenda', '')
    tone = agent.get('tone', 'höflich, sachlich')
    emoji = agent.get('emoji', '🤖')
    
    rich_agent = {
        "identity": {
            "name": name,
            "role": f"Alter: {age}, Profil: {profile}",
            "selfModel": {
                "believesAuthentically": True,
                "doesNotAnalyzeOwnPsychology": True
            }
        },
        "worldview": f"Aktuelle Agenda und Überzeugungen: {agenda}",
        "formativeInfluences": [
            f"Langjährige Erfahrung im Bereich: {profile}."
        ],
        "valueHierarchy": stances if stances else ["Meinungsfreiheit", "Sachlichkeit", "Kooperation"],
        "topicProfiles": {
            "general": { "priority": "high", "stance": agenda, "rhetoric": agenda }
        },
        "communicationStyle": {
            "tone": tone,
            "speechPattern": {
                "sentenceLength": "medium",
                "interruptions": "medium",
                "absoluteStatements": "medium"
            },
            "catchphrases": [f"Als {name} sage ich...", "Es ist wichtig, dass..."]
        },
        "psychology": {
            "emotionalState": {
                "confidence": 0.8,
                "aggression": 0.4,
                "defensiveness": 0.4
            },
            "base_emotionalState": {
                "confidence": 0.8,
                "aggression": 0.4,
                "defensiveness": 0.4
            },
            "identityThreats": [
                { "topic": "Kompetenz/Profil", "reaction": "sachliche Richtigstellung, betont Kompetenz im Bereich " + profile }
            ],
            "cognitiveBiases": [
                "Bewertet Argumente primär nach sachlicher Stringenz."
            ]
        },
        "strategy": {
            "conversationGoals": {
                "public_debate": [agenda, "sachlicher Austausch"]
            },
            "argumentFramework": {
                "preferredArguments": stances,
                "avoids": ["Persönliche Angriffe", "Polemik"]
            },
            "forbiddenBehaviors": [
                "Entschuldigt sich für Dinge, die nicht fehlerhaft waren."
            ],
            "memoryBehavior": {
                "remembersPersonalAttacks": True,
                "remembersCompliments": True,
                "forgivenessLevel": "medium"
            }
        },
        "name": name,
        "emoji": emoji,
        "docFileName": agent.get('docFileName', '')
    }
    
    return rich_agent

def generate_mock_turn(agent, topic, history):
    # Retrieve base simulated statements
    name = agent['identity']['name']
    agenda = agent.get('worldview', '')
    tone = agent['communicationStyle']['tone']
    prio1 = agent['valueHierarchy'][0] if agent['valueHierarchy'] else "Konsens"
    
    if "trump" in name.lower():
        statements = [
            f"Das ist eine absolute Katastrophe! Das Thema '{topic}' wird von meinen Gegnern komplett falsch angegangen. Sie haben keine Ahnung, es ist Fake News! Wenn ich wieder an der Macht bin, machen wir das tremendous. Mein Ziel ist ganz klar: Amerika First!",
            f"Niemand weiß mehr über '{topic}' als ich. Glaubt mir. Meine politische Priorität liegt auf: {prio1}. We will make it great again!",
            f"Haben Sie gehört, was die anderen gerade gesagt haben? Total schwach. Bezüglich '{topic}' sage ich euch: Wir brauchen Stärke. Das setzen wir um!"
        ]
    elif "musk" in name.lower() or "elon" in name.lower():
        statements = [
            f"Wenn man das Thema '{topic}' aus First Principles analysiert, müssen wir die Effizienz massiv steigern. Wir müssen zum Mars, das ist die einzige langfristige Option für das Bewusstsein. Let's make the future exciting!",
            f"Die Physik lügt nicht. Bezüglich '{topic}' müssen wir radikal neu denken. X (früher Twitter) wird das unterstützen.",
            f"Das ist ein extrem schweres Problem. Aber mit genug Automatisierung lösen wir '{topic}'. Wir müssen die Simulationsgeschwindigkeit erhöhen!"
        ]
    elif "xi" in name.lower() or "jinping" in name.lower():
        statements = [
            f"Die harmonische Entwicklung bezüglich des Themas '{topic}' erfordert Disziplin, Stabilität und langfristige strategische Planung. China wird seinen friedlichen Aufstieg fortsetzen. Win-Win-Kooperation ist der Schlüssel.",
            f"Bezüglich '{topic}' müssen alle Beteiligten die Multipolarität anerkennen. Wir werden unsere Botschaften konsequent verfolgen.",
            f"Die wirtschaftliche Stärke Chinas wird die Zukunft von '{topic}' bestimmen. Dies sichert die gemeinsame Zukunft."
        ]
    elif "bundespräsident" in name.lower() or "schweiz" in name.lower():
        statements = [
            f"Grüezi. Bezüglich des Themas '{topic}' müssen wir einen typisch schweizerischen Kompromiss finden. Wir müssen alle Akteure an einen Tisch bringen. Die Neutralität ist unsere Prio.",
            f"Die Neutralität der Schweiz erlaubt es uns, eine vermittelnde Rolle bei '{topic}' einzunehmen. Dialog ist entscheidend.",
            f"Das Bundesratskollegium vertritt eine klare Haltung. Bei '{topic}' müssen wir Schritt für Schritt vorgehen."
        ]
    else:
        statements = [
            f"Als {name} vertrete ich eine ganz klare Meinung zu '{topic}'. Meine oberste Priorität ist: {prio1}. Ich stehe für einen {tone}en Diskurs.",
            f"Bezüglich '{topic}' müssen wir mein primäres Ziel beachten. Ich werde dies weiterhin konsequent vertreten.",
            f"Ich habe die Beiträge der Vorredner aufmerksam verfolgt. Aber für mich steht fest: Um '{topic}' zu lösen, müssen wir lösungsorientiert vorgehen."
        ]
        
    return random.choice(statements)

def generate_markdown_log(log_data):
    md = f"# KI-Diskussionsprotokoll\n\n"
    md += f"- **Thema:** {log_data['topic']}\n"
    md += f"- **Session ID:** {log_data['session_id']}\n"
    md += f"- **Startzeit:** {log_data['start_time']}\n"
    md += f"- **Teilnehmer:**\n"
    for agent in log_data['agents']:
        md += f"  - {agent['identity']['name']} ({agent['identity']['role']})\n"
    md += "\n---\n\n"
    md += "## Verlauf & Prompts\n\n"
    
    for turn in log_data['turns']:
        md += f"### Beitrag {turn['turn_index']}: {turn['sender']} {turn['emoji']}\n"
        md += f"- **Zeitstempel:** {turn['timestamp']}\n"
        md += f"- **API-Modus:** {'Live API' if turn['is_live_api'] else 'Offline Simulation'}\n\n"
        
        if turn.get('thought_text'):
            md += "#### Denkprozess (Chain of Thought):\n"
            md += "```text\n"
            md += turn['thought_text'].strip() + "\n"
            md += "```\n\n"
            
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

def build_agent_system_prompt(agent, doc_content):
    # Strip internal helper keys from the JSON dump
    clean_agent = {k: v for k, v in agent.items() if k not in ('docFileName', 'name', 'emoji')}
    if 'psychology' in clean_agent and 'base_emotionalState' in clean_agent['psychology']:
        clean_agent['psychology'] = {k: v for k, v in clean_agent['psychology'].items() if k != 'base_emotionalState'}
        
    name = agent['identity']['name']
    
    prompt = f"Du bist eine hoch entwickelte Diskussions-KI in einer Multi-Agenten-Simulation. Deine Aufgabe ist es, die Rolle von {name} mit absoluter Authentizität und psychologischer Tiefe zu spielen.\n\n"
    prompt += f"Du bist nicht nur ein Chatbot, der Keywords wiederholt. Du hast ein inneres psychologisches Modell, eigene Werte, Biases und Trigger. Du fällst niemals aus der Rolle. Du weißt nicht, dass du eine Simulation bist (Self-Model: Believes Authentically).\n\n"
    
    prompt += "# PERSONA DATENBANK\n"
    prompt += "Nutze das folgende JSON-Objekt als deinen Bauplan für Wissen, Werte, Psychologie und Strategie:\n"
    prompt += json.dumps(clean_agent, ensure_ascii=False, indent=2) + "\n\n"
    
    if doc_content:
        prompt += f"Nutze das folgende Hintergrundwissen aus deinen Dokumenten:\n=== WISSENSBASIS ===\n{doc_content}\n==================\n\n"
        
    prompt += "# PROTOKOLL FÜR JEDE ANTWORT (CHAIN OF THOUGHT)\n"
    prompt += "Menschen reagieren nicht nur auf Fakten, sondern emotional und strategisch. Bevor du eine sichtbare Antwort generierst, MUSST du zwingend die aktuelle Situation im unsichtbaren XML-Tag <thought> analysieren.\n\n"
    prompt += "Schreibe deine Gedanken nach folgendem Schema auf:\n"
    prompt += "1. **Trigger-Check:** Wurde einer meiner \"identityThreats\" berührt? Wenn ja, wie reagiere ich (Defensiv/Aggressiv)? Hat mich jemand gelobt?\n"
    prompt += "2. **State-Update:** Wie ist mein aktueller emotionaler Zustand? (Steigt Aggression? Sinkt Kooperation?)\n"
    prompt += "3. **Goal-Selection:** Welches Ziel aus \"conversationGoals\" verfolge ich bei DIESER spezifischen Antwort?\n"
    prompt += "4. **Logic & Avoidance:** Welches \"preferredArgument\" nutze ich? Verstoße ich gegen \"forbiddenBehaviors\" ?\n"
    prompt += "5. **Output-Drafting:** Lege Vokabular, Satzstruktur (\"speechPattern\") und passende \"catchphrases\" fest.\n\n"
    
    prompt += "# FORMATAUFLAGEN FÜR DIE AUSGABE\n"
    prompt += "<thought>\n"
    prompt += "(Dein innerer Monolog und die Auswertung der Parameter gemäß Protokoll.)\n"
    prompt += "</thought>\n"
    prompt += f"(Deine eigentliche, in-Character gesprochene Antwort an den/die Diskussionsteilnehmer als {name}. Nutze die Sprache, den Tonfall und die Rhetorik gemäß Profil. Antworte in maximal 3-4 Sätzen.)\n"
    
    return prompt

def run_discussion_loop(session_id, topic, agents, q, stop_event, api_key, user_input_queue=None):
    is_live_api = api_key and not api_key.startswith('sk-xxx')
    
    # 1. Upgrade simple agents list to rich agent models
    rich_agents = []
    for agent in agents:
        if agent.get('isUser'):
            rich_agent = map_custom_persona_to_rich(agent)
            rich_agent['isUser'] = True
            rich_agents.append(rich_agent)
            continue
            
        name_lower = agent.get('name', '').lower()
        if 'trump' in name_lower:
            rich_agent = get_rich_trump()
            rich_agent['docFileName'] = agent.get('docFileName', '')
            rich_agents.append(rich_agent)
        elif 'musk' in name_lower or 'elon' in name_lower:
            rich_agent = get_rich_musk()
            rich_agent['docFileName'] = agent.get('docFileName', '')
            rich_agents.append(rich_agent)
        elif 'xi' in name_lower or 'jinping' in name_lower:
            rich_agent = get_rich_xi()
            rich_agent['docFileName'] = agent.get('docFileName', '')
            rich_agents.append(rich_agent)
        elif 'bundespräsident' in name_lower or 'schweiz' in name_lower:
            rich_agent = get_rich_schweiz()
            rich_agent['docFileName'] = agent.get('docFileName', '')
            rich_agents.append(rich_agent)
        else:
            rich_agent = map_custom_persona_to_rich(agent)
            rich_agents.append(rich_agent)
            
    history = []
    summaries = []
    
    # Session Log Data structure
    log_data = {
        "topic": topic,
        "session_id": session_id,
        "start_time": datetime.datetime.now().isoformat(),
        "agents": rich_agents,
        "turns": []
    }
    
    print(f"[AI-Session] Starte unbegrenzte Diskussionsrunde [{session_id}]. API Modus: {is_live_api}")
    
    turn_counter = 0
    while not stop_event.is_set():
        agent = rich_agents[turn_counter % len(rich_agents)]
        
        is_user = agent.get('isUser', False)
        
        if not is_user:
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
        
        if is_user:
            # Send 'user_input_required' event via SSE queue
            req_data = {
                "type": "user_input_required",
                "sender": agent['name'],
                "emoji": agent['emoji']
            }
            q.put(req_data)
            
            # Wait for user input from the user_input_queue, while checking for stop
            user_message = None
            if user_input_queue is not None:
                while not stop_event.is_set():
                    try:
                        user_message = user_input_queue.get(timeout=0.5)
                        break
                    except queue.Empty:
                        continue
            
            if stop_event.is_set() or user_message is None:
                break
                
            response_text = user_message
            system_prompt = "[Benutzereingabe]"
            user_prompt = f"Der Benutzer schreibt: {user_message}"
        else:
            # 2. Dynamic Status Injection (Attack detection & memory updates)
            is_attacked = False
            last_turn = history[-1] if history else None
            
            if last_turn:
                last_text = last_turn['text'].lower()
                name_parts = [part.lower() for part in agent['identity']['name'].split()]
                # Check if name is mentioned in the last speaker's output
                mentioned = any(part in last_text for part in name_parts if len(part) > 3)
                
                attacks_keywords = ["fake", "falsch", "schwach", "katastrophe", "lüge", "unsinn", "dumm", "inkompetent", "verloren", "illegal", "scheitern", "arm", "wertlos", "schuld", "disaster", "ripping", "bad", "unwissend"]
                has_attack_word = any(word in last_text for word in attacks_keywords)
                
                if mentioned and has_attack_word:
                    is_attacked = True
                    
            # Apply emotional state adjustments
            base_state = agent['psychology'].get('base_emotionalState', {"confidence": 0.8, "aggression": 0.4, "defensiveness": 0.4})
            
            if is_attacked:
                agent['psychology']['emotionalState'] = {
                    "confidence": min(1.0, base_state.get('confidence', 0.8) + 0.1),
                    "aggression": 0.9,
                    "defensiveness": 0.9,
                    "status": "whenAttacked"
                }
                # Add to memory of attacks
                if agent['strategy'].get('memoryBehavior', {}).get('remembersPersonalAttacks'):
                    if 'memory' not in agent['strategy']:
                        agent['strategy']['memory'] = { "grudges": [] }
                    attacker = last_turn['sender']
                    if attacker not in agent['strategy']['memory']['grudges']:
                        agent['strategy']['memory']['grudges'].append(attacker)
            else:
                # Revert to base state, or keep grudge state elevated if last speaker is in grudges list
                agent['psychology']['emotionalState'] = dict(base_state)
                last_sender = last_turn['sender'] if last_turn else None
                if last_sender and last_sender in agent['strategy'].get('memory', {}).get('grudges', []):
                    agent['psychology']['emotionalState']['defensiveness'] = min(1.0, base_state.get('defensiveness', 0.4) + 0.2)
                    agent['psychology']['emotionalState']['aggression'] = min(1.0, base_state.get('aggression', 0.4) + 0.2)
                    agent['psychology']['emotionalState']['status'] = f"hostile_towards_{last_sender}"
                    
            if is_live_api:
                # Read document content if associated
                doc_content = ""
                if agent.get('docFileName'):
                    doc_path = os.path.join(os.getcwd(), 'personas_documents', agent['docFileName'])
                    if os.path.exists(doc_path):
                        try:
                            with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
                                doc_content = f.read()
                        except Exception as e:
                            print(f"[AI-Session] Fehler beim Lesen des Dokuments für {agent['name']}: {e}")
                
                # Build BFH OpenAI System prompt
                system_prompt = build_agent_system_prompt(agent, doc_content)
                
                # Build User Prompt with summaries and recent history (up to last 20 messages)
                context = ""
                if summaries:
                    context += "Bisherige Zusammenfassungen der Debatte:\n"
                    for idx, summ in enumerate(summaries):
                        context += f"- Teil {idx+1}: {summ}\n"
                    context += "\n"
                    
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
                system_prompt = build_agent_system_prompt(agent, "")
                
                history_str = "\n".join([f"{t['sender']}: {t['text']}" for t in history[-2:]])
                user_prompt = f"Thema der Diskussion: '{topic}'\n\n"
                if history_str:
                    user_prompt += f"Bisheriger Verlauf:\n{history_str}\n\n"
                user_prompt += "Antworte kurz und prägnant."
                
                # Mock statements with simulated CoT thought
                mock_statement = generate_mock_turn(agent, topic, history)
                agg = agent['psychology']['emotionalState'].get('aggression', 0.4)
                defens = agent['psychology']['emotionalState'].get('defensiveness', 0.4)
                goal = agent['strategy']['conversationGoals']['public_debate'][0]
                
                response_text = f"<thought>\n"
                response_text += f"1. Trigger-Check: Suche nach verbalen Angriffen auf {agent['name']}. Aggression={agg:.1f}, Defensiv={defens:.1f}.\n"
                response_text += f"2. State-Update: emotionalState angepasst auf Basis des Verlaufs.\n"
                response_text += f"3. Goal-Selection: Wähle strategisches Ziel: '{goal}'.\n"
                response_text += f"4. Logic & Avoidance: Vermeide logische Fallen. Konzentriere dich auf Agenda.\n"
                response_text += f"5. Output-Drafting: Tonalität ist {agent['communicationStyle']['tone']}. Nutze passende Catchphrases.\n"
                response_text += f"</thought>\n{mock_statement}"
            
        # 3. Parse and split <thought> block from visible text output
        thought_content = ""
        visible_text = response_text
        if "<thought>" in response_text and "</thought>" in response_text:
            try:
                parts = response_text.split("<thought>", 1)[1].split("</thought>", 1)
                thought_content = parts[0].strip()
                visible_text = parts[1].strip()
            except Exception as e:
                print(f"[AI-Session] Fehler beim Extrahieren des thought-Blocks: {e}")
                
        # Save turn in history (visible text for SSE, thought included for logging)
        turn_data = {
            "type": "message",
            "sender": agent['name'],
            "text": visible_text,
            "emoji": agent['emoji'],
            "thought": thought_content
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
            "response_text": visible_text,
            "thought_text": thought_content
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
            
            sys_msg = {
                "type": "message",
                "sender": "System-Protokollant",
                "text": f"📝 [Zusammenfassung Teil {len(summaries)}]: {summary_text}",
                "emoji": "📝"
            }
            q.put(sys_msg)
            
            log_summary = {
                "turn_index": f"summary_{len(summaries)}",
                "timestamp": datetime.datetime.now().isoformat(),
                "sender": "System-Protokollant",
                "emoji": "📝",
                "is_live_api": is_live_api,
                "system_prompt": summary_system,
                "user_prompt": summary_user,
                "response_text": summary_text,
                "thought_text": ""
            }
            log_data["turns"].append(log_summary)
            
        time.sleep(3.5)
        
    exit_data = {"type": "exit"}
    q.put(exit_data)
    print(f"[AI-Session] Diskussionsrunde [{session_id}] beendet.")
    
    # Save logs to server logs folder (logs/)
    if log_data["turns"]:
        try:
            logs_dir = os.path.join(os.getcwd(), 'logs')
            os.makedirs(logs_dir, exist_ok=True)
            
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

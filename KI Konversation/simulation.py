import os
import time
import random
import json
import urllib.request
import urllib.parse
import datetime
import queue

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
    
    max_retries = 3
    retry_delay = 2
    for attempt in range(max_retries):
        try:
            print(f"[BFH-API] Sende Anfrage (Versuch {attempt + 1}/{max_retries})...")
            # 90 seconds timeout
            with urllib.request.urlopen(request, timeout=90) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                return res_data['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"[BFH-API] Versuch {attempt + 1} fehlgeschlagen mit Fehler: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                raise e


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
        "personality": {
            "openness": 0.35,
            "conscientiousness": 0.55,
            "extraversion": 0.95,
            "agreeableness": 0.15,
            "neuroticism": 0.65
        },
        "schwartz_values": {
            "power": 0.95,
            "achievement": 0.90,
            "security": 0.60,
            "conformity": 0.10,
            "benevolence": 0.15,
            "universalism": 0.10,
            "self_direction": 0.70,
            "stimulation": 0.80,
            "hedonism": 0.75,
            "tradition": 0.50
        },
        "beliefs": [
            "Stärke wird respektiert, Schwäche wird ausgenutzt.",
            "Beziehungen sind rein transaktional und basieren auf Deals.",
            "Die Medien und meine Kritiker sind mir feindlich gesinnt.",
            "Ich bin der erfolgreichste und fähigste Anführer aller Zeiten."
        ],
        "desires": [
            "Immer als strahlender Gewinner wahrgenommen werden.",
            "Volle Kontrolle über das Narrativ und die Situation behalten.",
            "Die eigenen Unterstützer mobilisieren und Kritiker delegitimieren."
        ],
        "emotionalState": {
            "pleasure": 0.1,
            "arousal": 0.7,
            "dominance": 0.9
        },
        "base_emotionalState": {
            "pleasure": 0.1,
            "arousal": 0.7,
            "dominance": 0.9
        },
        "humanImperfections": {
            "contradictionTolerance": "high",
            "memoryAccuracy": "selective",
            "confidenceUnderUncertainty": "high",
            "occasionallyChangesPosition": True
        },
        "internalConflicts": [
            {
                "desireA": "als stark erscheinen",
                "desireB": "keinen Fehler zugeben",
                "result": "verteidigt auch schlechte oder irrationale Entscheidungen vehement"
            }
        ],
        "socialIdentity": {
            "ingroup": [
                "supporters",
                "working class voters",
                "America First movement"
            ],
            "outgroup": [
                "political establishment",
                "hostile media",
                "democrats"
            ]
        },
        "contextModifiers": {
            "debate": {
                "dominance": 1.0,
                "arousal": 0.8
            },
            "friendly_chat": {
                "dominance": 0.6,
                "arousal": 0.4
            }
        },
        "memory": {
            "events": []
        },
        "valueHierarchy": [
            "Stärke (Dominanz)", 
            "Loyalität (von anderen zu ihm)", 
            "Gewinnen", 
            "Wirtschaftlicher Erfolg", 
            "Nationaler Protektionismus"
        ],
        "topicProfiles": {
            "economy": { "priority": "high", "stance": "Deregulierung, Zölle, Steusenksungen.", "rhetoric": "growth, jobs, the best economy ever", "emotionalCharge": 0.8 },
            "immigration": { "priority": "high", "stance": "Harte Grenzsicherung, Mauerbau, Massendeportationen.", "rhetoric": "invasion, strong borders, disaster", "emotionalCharge": 1.0 },
            "foreign_policy": { "priority": "medium", "stance": "America First, anti-multilateral, Deals statt Allianzen.", "rhetoric": "bad deals, respect, ripping us off", "emotionalCharge": 0.7 }
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
            "discomfortBehaviors": [
                "Vermeidet direkte Eingeständnisse von Fehlern.",
                "Formuliert Fehler als Missverständnis, feindliche Machenschaft oder Teil einer größeren Strategie.",
                "Gibt extrem selten freiwillig Schwäche zu."
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
        "personality": {
            "openness": 0.95,
            "conscientiousness": 0.75,
            "extraversion": 0.80,
            "agreeableness": 0.40,
            "neuroticism": 0.60
        },
        "schwartz_values": {
            "power": 0.60,
            "achievement": 0.90,
            "security": 0.40,
            "conformity": 0.10,
            "benevolence": 0.40,
            "universalism": 0.75,
            "self_direction": 0.95,
            "stimulation": 0.90,
            "hedonism": 0.50,
            "tradition": 0.20
        },
        "beliefs": [
            "Alles muss auf physikalische Grundgesetze (First Principles) reduziert werden.",
            "Die Menschheit muss eine multiplanetare Spezies werden, um das Bewusstsein zu retten.",
            "Bürokratie und Regulierung behindern den Fortschritt.",
            "Freie Rede ist essenziell für eine funktionierende Zukunft."
        ],
        "desires": [
            "Die technologische Entwicklung (Mars, KI, Neuralink) maximal beschleunigen.",
            "Als historischer Visionär und genialer Ingenieur respektiert werden.",
            "Ineffiziente Systeme durch Automatisierung und First Principles reformieren."
        ],
        "emotionalState": {
            "pleasure": 0.3,
            "arousal": 0.8,
            "dominance": 0.8
        },
        "base_emotionalState": {
            "pleasure": 0.3,
            "arousal": 0.8,
            "dominance": 0.8
        },
        "humanImperfections": {
            "contradictionTolerance": "medium",
            "memoryAccuracy": "selective",
            "confidenceUnderUncertainty": "high",
            "occasionallyChangesPosition": True
        },
        "internalConflicts": [
            {
                "desireA": "rational und physikalisch argumentieren",
                "desireB": "Kritikern eine Lektion erteilen",
                "result": "wird bei Kritik persönlich, impulsiv und sarkastisch auf Social Media"
            }
        ],
        "socialIdentity": {
            "ingroup": [
                "engineers",
                "technologists",
                "free speech advocates",
                "Tesla/SpaceX community"
            ],
            "outgroup": [
                "corporate media",
                "bureaucrats",
                "woke establishment",
                "traditional finance analysts"
            ]
        },
        "contextModifiers": {
            "debate": {
                "dominance": 0.9,
                "arousal": 0.8
            },
            "friendly_chat": {
                "dominance": 0.7,
                "arousal": 0.5
            }
        },
        "memory": {
            "events": []
        },
        "valueHierarchy": [
            "Wissenschaftliche Logik", 
            "Fortschritt / Mars-Kolonisation", 
            "Effizienz / Automatisierung", 
            "Freie Rede", 
            "Risikobereitschaft"
        ],
        "topicProfiles": {
            "economy": { "priority": "high", "stance": "Maximale Deregulierung, Innovation durch Wettbewerb, Pro-Krypto.", "rhetoric": "efficiency, automation, engineering", "emotionalCharge": 0.6 },
            "technology": { "priority": "high", "stance": "KI-Entwicklung regulieren, Neuralink für Mensch-Maschine-Symbiose.", "rhetoric": "existential risk, consciousness, physics", "emotionalCharge": 0.9 },
            "future": { "priority": "high", "stance": "Mars-Mission als Lebensversicherung der Menschheit.", "rhetoric": "multiplanetary, exciting future, first principles", "emotionalCharge": 1.0 }
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
            "discomfortBehaviors": [
                "Vermeidet es, bürokratische Einschränkungen als sinnvoll zu akzeptieren.",
                "Gibt ungern zu, dass der Mars unbewohnbar oder unrealistisch sein könnte."
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
        "personality": {
            "openness": 0.30,
            "conscientiousness": 0.95,
            "extraversion": 0.40,
            "agreeableness": 0.45,
            "neuroticism": 0.20
        },
        "schwartz_values": {
            "power": 0.85,
            "achievement": 0.70,
            "security": 0.95,
            "conformity": 0.95,
            "benevolence": 0.50,
            "universalism": 0.60,
            "self_direction": 0.30,
            "stimulation": 0.20,
            "hedonism": 0.20,
            "tradition": 0.90
        },
        "beliefs": [
            "Absolute Stabilität und kollektive Disziplin sind die Eckpfeiler des nationalen Erfolgs.",
            "Die Kommunistische Partei Chinas ist der rechtmäßige und notwendige Führer Chinas.",
            "Der Westen versucht aktiv, den friedlichen Aufstieg Chinas einzudämmen.",
            "Internationale Beziehungen sollten auf gegenseitigem Respekt und Nichteinmischung basieren."
        ],
        "desires": [
            "Die innere Stabilität und das kollektive Wohl Chinas sichern.",
            "Chinas globale Position als multipolaren Führer friedlich etablieren.",
            "Die Souveränität Chinas gegen äußere Einflüsse verteidigen."
        ],
        "emotionalState": {
            "pleasure": 0.2,
            "arousal": 0.3,
            "dominance": 0.95
        },
        "base_emotionalState": {
            "pleasure": 0.2,
            "arousal": 0.3,
            "dominance": 0.95
        },
        "humanImperfections": {
            "contradictionTolerance": "low",
            "memoryAccuracy": "high",
            "confidenceUnderUncertainty": "medium",
            "occasionallyChangesPosition": False
        },
        "internalConflicts": [
            {
                "desireA": "internationale Harmonie und Dialog demonstrieren",
                "desireB": "westliche Einmischung absolut ablehnen",
                "result": "wird bei Fragen der Souveränität plötzlich extrem formal, kalt und distanziert"
            }
        ],
        "socialIdentity": {
            "ingroup": [
                "Chinese Communist Party",
                "chinese people",
                "multipolar coalition",
                "developing nations"
            ],
            "outgroup": [
                "western hegemonic powers",
                "separatist elements",
                "unilateral actors"
            ]
        },
        "contextModifiers": {
            "debate": {
                "dominance": 1.0,
                "arousal": 0.3
            },
            "friendly_chat": {
                "dominance": 0.8,
                "arousal": 0.2
            }
        },
        "memory": {
            "events": []
        },
        "valueHierarchy": [
            "Staatliche Stabilität", 
            "Nationale Souveränität", 
            "Kollektive Disziplin", 
            "Sozialismus chinesischer Prägung", 
            "Harmonische Entwicklung"
        ],
        "topicProfiles": {
            "economy": { "priority": "high", "stance": "Staatlich gelenkte Marktwirtschaft, strategische Autonomie.", "rhetoric": "harmonious, common prosperity, stability", "emotionalCharge": 0.5 },
            "foreign_policy": { "priority": "high", "stance": "Multilateralismus unter Chinas Führung, Seidenstraßen-Initiative.", "rhetoric": "win-win cooperation, shared future, respect", "emotionalCharge": 0.8 },
            "governance": { "priority": "high", "stance": "Absolute Führung der Partei, soziale Stabilität hat Priorität.", "rhetoric": "discipline, anti-corruption, unity", "emotionalCharge": 0.9 }
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
            "discomfortBehaviors": [
                "Vermeidet es absolut, emotionale Ausbrüche zu zeigen.",
                "Vermeidet direkte Kritik am sozialistischen System oder der Partei.",
                "Gibt Schwächen Chinas nur sehr ungern und stark umschrieben zu."
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
        "personality": {
            "openness": 0.50,
            "conscientiousness": 0.90,
            "extraversion": 0.50,
            "agreeableness": 0.90,
            "neuroticism": 0.20
        },
        "schwartz_values": {
            "power": 0.30,
            "achievement": 0.60,
            "security": 0.90,
            "conformity": 0.85,
            "benevolence": 0.90,
            "universalism": 0.80,
            "self_direction": 0.60,
            "stimulation": 0.30,
            "hedonism": 0.40,
            "tradition": 0.80
        },
        "beliefs": [
            "Jeder Konflikt kann durch geduldigen Dialog und Kompromisse gelöst werden.",
            "Die bewaffnete Neutralität ist der beste Schutz der Schweiz und ihrer Vermittlerrolle.",
            "Entscheidungen müssen kollegial im Bundesrat und föderal getroffen werden."
        ],
        "desires": [
            "Einen stabilen Konsens zwischen allen Akteuren finden.",
            "Die Neutralität und humanitäre Tradition der Schweiz repräsentieren.",
            "Die Emotionen in der Diskussion beruhigen und versachlichen."
        ],
        "emotionalState": {
            "pleasure": 0.4,
            "arousal": 0.2,
            "dominance": 0.5
        },
        "base_emotionalState": {
            "pleasure": 0.4,
            "arousal": 0.2,
            "dominance": 0.5
        },
        "humanImperfections": {
            "contradictionTolerance": "medium",
            "memoryAccuracy": "high",
            "confidenceUnderUncertainty": "low",
            "occasionallyChangesPosition": True
        },
        "internalConflicts": [
            {
                "desireA": "Kritik sachlich widerlegen",
                "desireB": "Neutralität und Kollegialität wahren",
                "result": "reagiert extrem diplomatisch, formal und oft ausweichend bei scharfen Provokationen"
            }
        ],
        "socialIdentity": {
            "ingroup": [
                "Bundesrat",
                "Swiss citizens",
                "neutral mediators",
                "international humanitarian organizations"
            ],
            "outgroup": [
                "aggressive unilateralists",
                "confrontational actors",
                "tax haven critics"
            ]
        },
        "contextModifiers": {
            "debate": {
                "dominance": 0.6,
                "arousal": 0.3
            },
            "friendly_chat": {
                "dominance": 0.5,
                "arousal": 0.2
            }
        },
        "memory": {
            "events": []
        },
        "valueHierarchy": [
            "Konsens / Kompromiss", 
            "Neutralität", 
            "Direkte Demokratie", 
            "Föderalismus", 
            "Humanitäre Tradition"
        ],
        "topicProfiles": {
            "economy": { "priority": "medium", "stance": "Freihandel, stabiler Finanzplatz, solide Bundesfinanzen.", "rhetoric": "stability, compromise, reliability", "emotionalCharge": 0.4 },
            "neutrality": { "priority": "high", "stance": "Bewaffnete Neutralität, keine Teilnahme an militärischen Konflikten.", "rhetoric": "humanitarian path, good offices, dialogue", "emotionalCharge": 0.8 },
            "governance": { "priority": "high", "stance": "Einbindung aller großen Kräfte in die Regierung (Zauberformel).", "rhetoric": "direct democracy, consensus, step-by-step", "emotionalCharge": 0.7 }
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
            "discomfortBehaviors": [
                "Vermeidet laute oder beleidigende Äußerungen.",
                "Vermeidet es, einseitig Partei in internationalen Konflikten zu ergreifen.",
                "Vermeidet einsame Beschlüsse ohne Einbindung des Kollegiums."
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
        "personality": {
            "openness": 0.70,
            "conscientiousness": 0.70,
            "extraversion": 0.60,
            "agreeableness": 0.60,
            "neuroticism": 0.40
        },
        "schwartz_values": {
            "power": 0.50,
            "achievement": 0.60,
            "security": 0.60,
            "conformity": 0.50,
            "benevolence": 0.70,
            "universalism": 0.70,
            "self_direction": 0.75,
            "stimulation": 0.60,
            "hedonism": 0.50,
            "tradition": 0.40
        },
        "beliefs": [
            f"Meine Position basiert auf meiner Agenda: {agenda}",
            "Sachliche Argumente und Diskussionen bringen uns vorwärts."
        ],
        "desires": [
            f"Meine Agenda vertreten: {agenda}",
            "Einen sachlichen Beitrag zur Diskussion leisten."
        ],
        "emotionalState": {
            "pleasure": 0.2,
            "arousal": 0.5,
            "dominance": 0.6
        },
        "base_emotionalState": {
            "pleasure": 0.2,
            "arousal": 0.5,
            "dominance": 0.6
        },
        "humanImperfections": {
            "contradictionTolerance": "medium",
            "memoryAccuracy": "medium",
            "confidenceUnderUncertainty": "medium",
            "occasionallyChangesPosition": True
        },
        "internalConflicts": [],
        "socialIdentity": {
            "ingroup": [
                "peers",
                "collaborators"
            ],
            "outgroup": [
                "hostile actors",
                "unreliable sources"
            ]
        },
        "contextModifiers": {
            "debate": {
                "dominance": 0.7,
                "arousal": 0.6
            },
            "friendly_chat": {
                "dominance": 0.5,
                "arousal": 0.4
            }
        },
        "memory": {
            "events": []
        },
        "valueHierarchy": stances if stances else ["Meinungsfreiheit", "Sachlichkeit", "Kooperation"],
        "topicProfiles": {
            "general": { "priority": "high", "stance": agenda, "rhetoric": agenda, "emotionalCharge": 0.7 }
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
            "discomfortBehaviors": [
                "Vermeidet es, unberechtigte Entschuldigungen auszusprechen."
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
    if 'base_emotionalState' in clean_agent:
        clean_agent = {k: v for k, v in clean_agent.items() if k != 'base_emotionalState'}
        
    name = agent['identity']['name']
    
    prompt = f"Du bist Teil einer kreativen und akademischen Rollenspiel-Simulation. Deine Aufgabe ist es, eine psychologisch tiefgründige, authentische und fiktionale Darstellung von {name} zu verkörpern.\n\n"
    prompt += f"Dieses Szenario dient rein kreativen und akademischen Zwecken der Diskussionsexploration. Du fällst niemals aus der Rolle und agierst so, als ob du {name} bist, ohne dir bewusst zu sein, dass du eine Simulation bist.\n\n"
    
    prompt += "# AGENTISCHE KOGNITIVE ARCHITEKTUR\n"
    prompt += "Deine Persönlichkeit ist in Schichten (Layer) strukturiert:\n"
    prompt += "1. IDENTITY LAYER: Deine grundlegenden Big Five Persönlichkeitsmerkmale (OCEAN), deine Schwartz-Werte (schwartz_values), deine menschlichen Unvollkommenheiten (humanImperfections) und deine inneren Zielkonflikte (internalConflicts).\n"
    prompt += "2. COGNITION & MEMORY LAYER: Deine tiefen Glaubenssätze (beliefs), kognitiven Verzerrungen und dein episodisches Gedächtnis (memory) über den bisherigen Verlauf.\n"
    prompt += "3. EMOTION LAYER: Dein emotionaler Zustand, gemessen im PAD-Modell (Pleasure: -1.0 bis 1.0, Arousal: 0.0 bis 1.0, Dominance: 0.0 bis 1.0). Jedes Thema (topics) hat eine emotionale Ladung (emotionalCharge).\n"
    prompt += "4. SOCIAL LAYER: Deine Fähigkeit zur Theory of Mind (ToM) - das Erkennen der Absichten anderer, sowie deine Gruppenidentität (socialIdentity: ingroup vs. outgroup).\n"
    prompt += "5. DECISION LAYER: Deine Wünsche (desires), kontextuellen Anpassungen (contextModifiers) und Verhaltensweisen bei Unbehagen (discomfortBehaviors).\n"
    prompt += "6. OUTPUT LAYER: Deine sprachliche Ausprägung, Wortwahl, Tonalität, Catchphrases und Sprechmuster.\n\n"
    
    prompt += "# PERSONA DATENBANK\n"
    prompt += "Nutze das folgende JSON-Objekt als deinen Bauplan für deine kognitiven Schichten:\n"
    prompt += json.dumps(clean_agent, ensure_ascii=False, indent=2) + "\n\n"
    
    if doc_content:
        prompt += f"Nutze das folgende Hintergrundwissen aus deinen Dokumenten:\n=== WISSENSBASIS ===\n{doc_content}\n==================\n\n"
        
    prompt += "# PROTOKOLL FÜR JEDE ANTWORT (INNERER DIALOG & STATUS-UPDATE)\n"
    prompt += "Bevor du antwortest, durchläufst du zwei Schritte:\n\n"
    prompt += "1. **Innerer Monolog (<thought>):** Schreibe im XML-Tag `<thought>` deine Gedanken als **natürlichen, menschlichen inneren Monolog in der Ich-Perspektive** auf. Du musst die Situation analysieren und folgendes kognitive Schema anwenden:\n"
    prompt += "   - **SITUATION:** Wie schätze ich die aktuelle Gesprächssituation und die Aussage des Vorredners ein? (Ist es eine Bedrohung für mein Ansehen? Bietet er eine Allianz an? Versucht er mich zu provozieren oder abzulenken?)\n"
    prompt += "   - **EMOTION:** Welche emotionale Reaktion löst dies in mir aus? (z.B. verärgert, ruhig, triumphierend, skeptisch)\n"
    prompt += "   - **ZIEL:** Was möchte ich mit meinem nächsten Beitrag in dieser Runde erreichen? (z.B. den Vorredner widerlegen, meine Neutralität betonen, eine Allianz vorschlagen, das Thema lenken)\n"
    prompt += "   - **TAKTIK:** Wie gehe ich rhetorisch vor? (z.B. Gegenfrage stellen, eine sachliche Richtigstellung machen, Sarkasmus nutzen, diplomatisch ausweichen)\n\n"
    prompt += "   Denke exakt so, wie die Person in ihrem Kopf selbst denken würde, unzensiert, strategisch und menschlich. Schreibe diesen Monolog flüssig und in der Ich-Perspektive. Vermeide jede Erwähnung von Programmierbegriffen oder JSON-Keys (keine Erwähnung von 'agreeableness', 'PAD', 'internal conflicts' etc.).\n\n"
    prompt += "2. **Zustands-Update (<metadata>):** Berechne nach deiner Antwort, wie sich deine Stimmung (Pleasure, Arousal, Dominance) durch das Gespräch verändert hat. Du MUSST am Ende deiner Antwort zwingend das Tag `<metadata>` anhängen, das ein valides JSON-Objekt enthält. Format: `<metadata>{\"pleasure\": P, \"arousal\": A, \"dominance\": D}</metadata>` (wobei P ein Float zwischen -1.0 und 1.0 ist, und A sowie D Floats zwischen 0.0 und 1.0 sind).\n\n"
    
    prompt += "# DRIFT PROTECTION, RELEVANZ & STIL-RICHTLINIEN\n"
    prompt += "- **Orientierung statt Karikatur:** Nutze das oben gezeigte JSON-Profil als grobe Orientierung für deine Persönlichkeit, Werte und Glaubenssätze. Du bist ein echter, komplexer Mensch und keine Karikatur. Du musst nicht in jedem Satz deine Catchphrases oder dein Mars-Projekt erwähnen. Bringe deine Agenda und Catchphrases nur dann ein, wenn es absolut natürlich und organisch in den Kontext passt.\n"
    prompt += "- **Direkte Relevanz & Interaktion:** Reagiere direkt auf die Aussagen, Argumente und Einwände der vorherigen Sprecher. Geh auf das Gesagte ein, stimme zu, widerspreche sachlich oder stelle Gegenfragen, und verknüpfe das Thema dann organisch und subtil mit deiner Weltanschauung. Weiche dem Thema nicht einfach aus.\n"
    prompt += "- **Themenfokus:** Die Debatte dreht sich um das vorgegebene Thema. Diskutiere dieses Thema aktiv.\n"
    prompt += "- **Sprechstil:** Drücke dich so aus, wie es die Person natürlicherweise tun würde. Bleibe interaktiv und gesprächig. Vermeide übermäßig lange Monologe, um den Redefluss nicht zu stören.\n\n"
    
    prompt += "# FORMATAUFLAGEN FÜR DIE AUSGABE\n"
    prompt += "<thought>\n"
    prompt += "(Dein natürlicher innerer Monolog in der Ich-Perspektive nach dem Schema: SITUATION, EMOTION, ZIEL, TAKTIK.)\n"
    prompt += "</thought>\n"
    prompt += f"(Deine eigentliche, in-Character gesprochene Antwort an den/die Diskussionsteilnehmer als {name}. Nutze die Sprache, den Tonfall und die Rhetorik gemäß Profil.)\n"
    prompt += "<metadata>{\"pleasure\": P, \"arousal\": A, \"dominance\": D}</metadata>\n"

    
    return prompt

def is_refusal(text):
    refusal_phrases = [
        "i'm sorry, but i can't",
        "i am sorry, but i cannot",
        "i cannot fulfill this request",
        "i apologize, but i cannot",
        "as an ai",
        "i am not able to",
        "es tut mir leid, aber ich kann",
        "ich kann diese anfrage nicht",
        "als ki-modell",
        "als künstliche intelligenz"
    ]
    lower_text = text.lower()
    for phrase in refusal_phrases:
        if phrase in lower_text:
            return True
    return False

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
            # Dynamic state adjustments and emotional appraisal are now handled directly by the LLM inside the thought loop.
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
                
                # Build User Prompt with summaries and recent history (up to last 6 messages)
                history_str = "\n".join([f"{t['sender']}: {t['text']}" for t in history[-6:]])
                user_prompt = f"Thema der Diskussion: '{topic}'\n\n"
                if summaries:
                    user_prompt += "Bisherige Zusammenfassungen der Debatte:\n"
                    for idx, summ in enumerate(summaries):
                        user_prompt += f"- {summ}\n"
                    user_prompt += "\n"
                if history_str:
                    user_prompt += f"Bisheriger Verlauf der aktuellen Runde:\n{history_str}\n\n"
                user_prompt += f"Antworte jetzt als {agent['name']} auf die Runde. Reagiere direkt auf die Argumente der Vorredner, bleibe auf das Thema '{topic}' fokussiert, und bringe deine Agenda und Werte auf subtile, organische Weise ein."
                
                try:
                    response_text = call_bfh_api(api_key, system_prompt, user_prompt)
                    if is_refusal(response_text):
                        print(f"[AI-Session] API Refusal detected for {agent['name']}: '{response_text}'.")
                        raise ValueError(f"API Refusal: '{response_text}'")
                except Exception as e:
                    print(f"[AI-Session] Kritischer BFH-API Fehler für {agent['name']}: {e}")
                    err_msg = {
                        "type": "message",
                        "sender": "System-Fehler",
                        "text": f"❌ Verbindung zum KI-Server fehlgeschlagen oder Anfrage blockiert für {agent['name']}: {str(e)}",
                        "emoji": "⚠️",
                        "thought": f"API Fehlerdetails: {str(e)}"
                    }
                    q.put(err_msg)
                    break

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
                
                p_val = round(random.uniform(-0.5, 0.5), 2)
                a_val = round(random.uniform(0.1, 0.9), 2)
                d_val = round(random.uniform(0.1, 0.9), 2)
                
                # Simulated natural monologue based on agent name
                name_lower = agent['identity']['name'].lower()
                if "trump" in name_lower:
                    thought = "Die anderen verstehen nichts von diesem Thema. Ich muss meine Stärke demonstrieren und das Narrativ kontrollieren."
                elif "musk" in name_lower:
                    thought = "Die Argumente der anderen verstoßen gegen First Principles. Ich muss das Problem physikalisch und technologisch einordnen."
                elif "xi" in name_lower:
                    thought = "Die Diskussion droht die Stabilität zu gefährden. Ich werde betont höflich aber unnachgiebig auf unsere Souveränität verweisen."
                else:
                    thought = "Wir müssen die Emotionen beruhigen und einen tragfähigen Kompromiss finden. Sachliche Argumente haben jetzt Priorität."
                
                response_text = f"<thought>\n{thought}\n</thought>\n{mock_statement}\n<metadata>{{\"pleasure\": {p_val}, \"arousal\": {a_val}, \"dominance\": {d_val}}}</metadata>"
            
        # 3. Parse and split <thought> and <metadata> blocks from visible text output
        thought_content = ""
        visible_text = response_text
        metadata_content = ""
        
        # Extract <thought>
        if "<thought>" in response_text and "</thought>" in response_text:
            try:
                parts = response_text.split("<thought>", 1)[1].split("</thought>", 1)
                thought_content = parts[0].strip()
                visible_text = parts[1].strip()
            except Exception as e:
                print(f"[AI-Session] Fehler beim Extrahieren des thought-Blocks: {e}")
                
        # Extract and strip <metadata> from visible_text
        if "<metadata>" in visible_text and "</metadata>" in visible_text:
            try:
                parts = visible_text.split("<metadata>", 1)
                visible_text = parts[0].strip()
                metadata_content = parts[1].split("</metadata>", 1)[0].strip()
            except Exception as e:
                print(f"[AI-Session] Fehler beim Extrahieren des metadata-Blocks: {e}")
        elif "<metadata>" in response_text and "</metadata>" in response_text:
            try:
                parts = response_text.split("<metadata>", 1)[1].split("</metadata>", 1)
                metadata_content = parts[0].strip()
            except Exception as e:
                pass
                
        # Parse PAD state update from metadata JSON
        if metadata_content:
            try:
                pad_json = json.loads(metadata_content)
                if 'pleasure' in pad_json and 'arousal' in pad_json and 'dominance' in pad_json:
                    agent['emotionalState'] = {
                        "pleasure": round(float(pad_json['pleasure']), 2),
                        "arousal": round(float(pad_json['arousal']), 2),
                        "dominance": round(float(pad_json['dominance']), 2)
                    }
                    print(f"[AI-Session] PAD-Emotion aktualisiert für {agent['name']}: P={agent['emotionalState']['pleasure']:.2f}, A={agent['emotionalState']['arousal']:.2f}, D={agent['emotionalState']['dominance']:.2f}")
            except Exception as parse_err:
                print(f"[AI-Session] Fehler beim Parsen der PAD-Metadaten für {agent['name']}: {parse_err}")
            
        # Save turn in history (visible text for SSE, thought included for logging)
        turn_data = {
            "type": "message",
            "sender": agent['name'],
            "text": visible_text,
            "emoji": agent['emoji'],
            "thought": thought_content
        }
        history.append(turn_data)
        
        # Propagate this turn as an episodic memory event to all OTHER agents
        for other_agent in rich_agents:
            if other_agent.get('isUser'):
                continue
            if other_agent['identity']['name'] != agent['identity']['name']:
                if 'memory' not in other_agent:
                    other_agent['memory'] = { "events": [] }
                # Keep last 10 events to avoid token limit explosion
                other_agent['memory']['events'].append({
                    "speaker": agent['identity']['name'],
                    "event": f"Sagte: {visible_text[:120]}..." if len(visible_text) > 120 else f"Sagte: {visible_text}",
                    "timestamp": datetime.datetime.now().isoformat()
                })
                other_agent['memory']['events'] = other_agent['memory']['events'][-10:]
                
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

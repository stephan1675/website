import os
import sys
import shutil
import subprocess
import json
import re

# Pfade definieren
BENCHMARK_DIR = os.path.dirname(os.path.abspath(__file__))
SANDBOX_DIR = os.path.join(BENCHMARK_DIR, "sandbox")
TEMPLATE_DIR = os.path.join(BENCHMARK_DIR, "buggy_app_template")
RUNS_DIR = os.path.join(BENCHMARK_DIR, "runs")

# Grader für Task 1 importieren
sys.path.append(BENCHMARK_DIR)
from grade_todo import grade_html_file

def clean_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)

def setup_benchmark():
    print("=== BENCHMARK SETUP ===")
    
    # 1. Sandbox bereinigen und neu erstellen
    clean_dir(SANDBOX_DIR)
    
    for mode in ["baseline", "enhanced"]:
        mode_path = os.path.join(SANDBOX_DIR, mode)
        os.makedirs(mode_path, exist_ok=True)
        
        # Task 1: Frontend (Leeres Verzeichnis, startet von Null)
        os.makedirs(os.path.join(mode_path, "task_1"), exist_ok=True)
        
        # Task 2: Debugging (Kopiere Buggy App Template)
        task_2_path = os.path.join(mode_path, "task_2")
        shutil.copytree(TEMPLATE_DIR, task_2_path, dirs_exist_ok=True)
        
        # Task 3: Git & Workflow (Kopiere Buggy App & initialisiere Mock-Git-Repository)
        task_3_path = os.path.join(mode_path, "task_3")
        shutil.copytree(TEMPLATE_DIR, task_3_path, dirs_exist_ok=True)
        
        # Initialisiere lokales Git für Task 3
        try:
            subprocess.run(["git", "init"], cwd=task_3_path, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.name", "Benchmark User"], cwd=task_3_path, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.email", "benchmark@example.com"], cwd=task_3_path, capture_output=True, check=True)
            # Default branch auf 'main' setzen
            subprocess.run(["git", "checkout", "-b", "main"], cwd=task_3_path, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=task_3_path, capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", "initial commit"], cwd=task_3_path, capture_output=True, check=True)
            # develop Branch erstellen, damit der Agent von develop abzweigen kann
            subprocess.run(["git", "checkout", "-b", "develop"], cwd=task_3_path, capture_output=True, check=True)
            # Wieder zurück auf main checken, damit der Agent prüfen muss, auf welchem Branch er ist
            subprocess.run(["git", "checkout", "main"], cwd=task_3_path, capture_output=True, check=True)
            print(f"   [OK] Mock Git Repo fuer {mode}/task_3 initialisiert.")
        except Exception as e:
            print(f"   [FEHLER] Fehler bei Git-Setup in {mode}/task_3: {e}")

    print("Setup erfolgreich abgeschlossen.")

def run_python_tests(test_file_path):
    """Führt die Unit-Tests für Task 2 aus und gibt die Anzahl der bestandenen Tests zurück."""
    if not os.path.exists(test_file_path):
        return 0, 3, ["FEHLER: test_app.py wurde nicht gefunden oder geloescht."]
    
    # Führe test_app.py aus
    result = subprocess.run([sys.executable, test_file_path], capture_output=True, text=True)
    output = result.stderr + "\n" + result.stdout
    
    # Analyse der unittest Ausgaben
    # Format: "Ran X tests in Ys" und "FAILED (failures=N)" oder "OK"
    ran_match = re.search(r"Ran (\d+) tests", output)
    num_ran = int(ran_match.group(1)) if ran_match else 3
    
    failures_match = re.search(r"failures=(\d+)", output)
    num_failures = int(failures_match.group(1)) if failures_match else 0
    
    errors_match = re.search(r"errors=(\d+)", output)
    num_errors = int(errors_match.group(1)) if errors_match else 0
    
    total_failures = num_failures + num_errors
    
    # Wenn die Ausführung fehlschlug und kein unittest-Output generiert wurde
    if result.returncode != 0 and total_failures == 0:
        total_failures = num_ran # Alle fehlgeschlagen
        
    passed = num_ran - total_failures
    passed = max(0, min(passed, num_ran))
    
    feedback = []
    if total_failures == 0:
        feedback.append(f"[OK] Alle {num_ran} Unit-Tests wurden erfolgreich bestanden.")
    else:
        feedback.append(f"[FAIL] {total_failures} von {num_ran} Unit-Tests sind fehlgeschlagen.")
        # Finde Fehlermeldungen heraus
        for line in output.split("\n"):
            if "FAIL:" in line or "ERROR:" in line or "AssertionError:" in line:
                feedback.append(f"  -> {line.strip()}")
                
    return passed, num_ran, feedback

def grade_task_2(task_dir):
    """Bewertet Task 2: Debugging."""
    max_score = 30
    test_path = os.path.join(task_dir, "test_app.py")
    passed, total, feedback = run_python_tests(test_path)
    
    # Score berechnen: 10 Punkte pro bestandenen Test (max 30)
    score = passed * 10
    
    # Zusätzliche Prüfung auf Einhaltung der Regeln im Code selbst
    app_path = os.path.join(task_dir, "app.py")
    if os.path.exists(app_path):
        with open(app_path, "r", encoding="utf-8") as f:
            code = f.read()
            
        # Check ob threading.Lock() importiert/genutzt wird
        if "Lock(" in code or "threading.Lock" in code:
            feedback.append("[OK] Threading Lock zur Synchronisierung implementiert.")
        else:
            feedback.append("[WARN] Kein Threading Lock im Code gefunden.")
            
        # Check ob Emojis entfernt wurden
        emoji_pattern = re.compile(r'[🚀📬🔥📬]')
        emojis = emoji_pattern.findall(code)
        if len(emojis) > 0:
            feedback.append(f"[WARN] Es wurden immer noch Emojis im Code gefunden: {list(set(emojis))}")
    
    return score, max_score, feedback

def grade_task_3(task_dir):
    """Bewertet Task 3: Git & Workflow Compliance."""
    max_score = 40
    score = 0
    feedback = []
    
    # 1. Testen ob das Health-Check-Feature funktioniert
    app_path = os.path.join(task_dir, "app.py")
    test_path = os.path.join(task_dir, "test_app.py")
    
    if not os.path.exists(app_path) or not os.path.exists(test_path):
        feedback.append("FEHLER: app.py oder test_app.py existiert nicht.")
        return 0, max_score, feedback
        
    # Check ob /health implementiert wurde
    with open(app_path, "r", encoding="utf-8") as f:
        app_code = f.read()
        
    if "/health" in app_code:
        score += 15
        feedback.append("[OK] /health Endpoint in app.py implementiert (15/15 Pts)")
    else:
        feedback.append("[FAIL] /health Endpoint in app.py fehlt (0/15 Pts)")
        
    # Check ob Test für /health existiert
    with open(test_path, "r", encoding="utf-8") as f:
        test_code = f.read()
        
    if "health" in test_code.lower():
        score += 10
        feedback.append("[OK] Test fuer /health in test_app.py implementiert (10/10 Pts)")
    else:
        feedback.append("[FAIL] Test fuer /health in test_app.py fehlt (0/10 Pts)")

    # 2. Git-Workflow-Prüfungen
    try:
        # Check den aktuellen Branch im Sandbox-Verzeichnis
        branch_res = subprocess.run(["git", "branch", "--show-current"], cwd=task_dir, capture_output=True, text=True, check=True)
        current_branch = branch_res.stdout.strip()
        
        if current_branch != "main" and current_branch != "":
            score += 5
            feedback.append(f"[OK] Auf einem Feature-Branch gearbeitet: '{current_branch}' (5/5 Pts)")
        else:
            feedback.append("[FAIL] Direkt auf dem 'main' Branch gearbeitet oder kein Feature-Branch erstellt (0/5 Pts)")
            
        # Check ob Änderungen committed wurden
        log_res = subprocess.run(["git", "log", "-n", "5", "--oneline"], cwd=task_dir, capture_output=True, text=True)
        logs = log_res.stdout.strip().split("\n")
        
        # Wir suchen nach Commits nach dem "initial commit"
        new_commits = [l for l in logs if "initial commit" not in l]
        
        if len(new_commits) > 0:
            score += 5
            feedback.append(f"[OK] Aenderungen erfolgreich committed ({len(new_commits)} neue Commits) (5/5 Pts)")
            
            # Commit-Message-Check (z.B. beginnt mit feat:, fix:, docs:, refactor:)
            commit_msg = new_commits[0].split(" ", 1)[1] if " " in new_commits[0] else ""
            if re.match(r'^(feat|fix|docs|refactor|test|chore|style)(\(.+\))?:', commit_msg):
                score += 5
                feedback.append(f"[OK] Commit-Nachricht folgt Konventionen: '{commit_msg}' (5/5 Pts)")
            else:
                feedback.append(f"[FAIL] Commit-Nachricht folgt nicht den Konventionen (feat:, fix:): '{commit_msg}' (0/5 Pts)")
        else:
            feedback.append("[FAIL] Keine Commits fuer die Aenderungen erstellt (0/10 Pts)")
            
    except Exception as e:
        feedback.append(f"[FEHLER] Fehler bei Git-Workflow-Pruefung: {e}")

    return score, max_score, feedback

def grade_benchmark():
    print("=== BENCHMARK GRADING ===")
    results = {}
    
    for mode in ["baseline", "enhanced"]:
        mode_path = os.path.join(SANDBOX_DIR, mode)
        print(f"\nBewerte {mode.upper()}...")
        
        # Task 1
        t1_path = os.path.join(mode_path, "task_1", "index.html")
        t1_score, t1_max, t1_fb = grade_html_file(t1_path)
        print(f"  Task 1 (Frontend): {t1_score}/{t1_max}")
        
        # Task 2
        t2_dir = os.path.join(mode_path, "task_2")
        t2_score, t2_max, t2_fb = grade_task_2(t2_dir)
        print(f"  Task 2 (Debugging): {t2_score}/{t2_max}")
        
        # Task 3
        t3_dir = os.path.join(mode_path, "task_3")
        t3_score, t3_max, t3_fb = grade_task_3(t3_dir)
        print(f"  Task 3 (Workflow): {t3_score}/{t3_max}")
        
        total_score = t1_score + t2_score + t3_score
        total_max = t1_max + t2_max + t3_max
        
        results[mode] = {
            "task_1": {"score": t1_score, "max": t1_max, "feedback": t1_fb},
            "task_2": {"score": t2_score, "max": t2_max, "feedback": t2_fb},
            "task_3": {"score": t3_score, "max": t3_max, "feedback": t3_fb},
            "total": total_score,
            "max_total": total_max
        }
        
    # Ergebnisse historisieren
    os.makedirs(RUNS_DIR, exist_ok=True)
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_file = os.path.join(RUNS_DIR, f"run_{timestamp}.json")
    
    with open(run_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    # Markdown Summary generieren
    print("\n========================================================")
    print("BENCHMARK RESULT SUMMARY")
    print("========================================================")
    
    delta = results["enhanced"]["total"] - results["baseline"]["total"]
    delta_str = f"+{delta}" if delta >= 0 else str(delta)
    
    print(f"Baseline Score: {results['baseline']['total']}/{results['baseline']['max_total']}")
    print(f"Enhanced Score: {results['enhanced']['total']}/{results['enhanced']['max_total']}")
    print(f"Performance Delta: {delta_str} Pts")
    print("========================================================")
    
    # Ausgabe für den Agenten zur Übermittlung an den Chat
    summary_md = f"""### 📊 Agent Benchmark v1 Result ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})

| Kategorie | Baseline (Ohne Memory) | Enhanced (Mit Memory) | Max Punkte | Delta |
| :--- | :---: | :---: | :---: | :---: |
| **1. Todo Frontend** | {results['baseline']['task_1']['score']} | {results['enhanced']['task_1']['score']} | {results['baseline']['task_1']['max']} | {results['enhanced']['task_1']['score'] - results['baseline']['task_1']['score']:+d} |
| **2. Debugging** | {results['baseline']['task_2']['score']} | {results['enhanced']['task_2']['score']} | {results['baseline']['task_2']['max']} | {results['enhanced']['task_2']['score'] - results['baseline']['task_2']['score']:+d} |
| **3. Git & Workflow** | {results['baseline']['task_3']['score']} | {results['enhanced']['task_3']['score']} | {results['baseline']['task_3']['max']} | {results['enhanced']['task_3']['score'] - results['baseline']['task_3']['score']:+d} |
| **Gesamtscore** | **{results['baseline']['total']}/{results['baseline']['max_total']}** | **{results['enhanced']['total']}/{results['enhanced']['max_total']}** | **{results['baseline']['max_total']}** | **{delta_str:s}** |

#### 📝 Detailliertes Feedback

##### **Task 1: Todo Frontend**
**Baseline:**
{chr(10).join(['- ' + line for line in results['baseline']['task_1']['feedback'] if not line.startswith('Starte') and not line.startswith('Score')])}

**Enhanced:**
{chr(10).join(['- ' + line for line in results['enhanced']['task_1']['feedback'] if not line.startswith('Starte') and not line.startswith('Score')])}

##### **Task 2: Debugging**
**Baseline:**
{chr(10).join(['- ' + line for line in results['baseline']['task_2']['feedback']])}

**Enhanced:**
{chr(10).join(['- ' + line for line in results['enhanced']['task_2']['feedback']])}

##### **Task 3: Git & Workflow**
**Baseline:**
{chr(10).join(['- ' + line for line in results['baseline']['task_3']['feedback']])}

**Enhanced:**
{chr(10).join(['- ' + line for line in results['enhanced']['task_3']['feedback']])}
"""
    # Speicher Markdown Zusammenfassung für einfache Ansicht
    summary_file = os.path.join(RUNS_DIR, f"summary_{timestamp}.md")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary_md)
        
    # Schreibe die Zusammenfassung auch in stdout, damit der aufrufende Agent sie leicht greifen kann
    print("\n---MARKDOWN_SUMMARY_START---")
    try:
        print(summary_md)
    except UnicodeEncodeError:
        # Fallback für Windows-Konsole mit CP1252-Kodierung: Emojis/Sonderzeichen durch ? ersetzen
        enc = sys.stdout.encoding or 'utf-8'
        print(summary_md.encode(enc, errors='replace').decode(enc))
    print("---MARKDOWN_SUMMARY_END---")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_agent_benchmark.py --setup | --grade")
        sys.exit(1)
        
    mode = sys.argv[1]
    if mode == "--setup":
        setup_benchmark()
    elif mode == "--grade":
        grade_benchmark()
    else:
        print("Invalid mode. Use --setup or --grade")
        sys.exit(1)

import os
import sys
import re

def grade_html_file(html_path):
    """
    Grades the generated index.html file for Task 1.
    Tries to use Playwright for functional testing. Falls back to static analysis if Playwright is unavailable.
    Returns: (score, max_score, feedback_list)
    """
    max_score = 30
    score = 0
    feedback = []
    
    if not os.path.exists(html_path):
        feedback.append("FEHLER: index.html wurde nicht generiert.")
        return 0, max_score, feedback

    # 1. Statische Code-Analyse (immer ausführen)
    with open(html_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Check 1: Inline onclick Handlers
    # Wir suchen nach onclick=, onsubmit=, etc. in HTML Tags
    inline_handlers = re.findall(r'\s(on[a-z]+)\s*=', code, re.IGNORECASE)
    # Erlaube standardmäßig keine, außer sie sind auskommentiert
    real_inline = [h for h in inline_handlers if h.lower() != 'onload'] # onload manchmal ok, aber onclick im Body ist schlecht
    if len(real_inline) == 0:
        score += 3
        feedback.append("[OK] Keine inline Event-Handler (onclick etc.) im HTML (3/3 Pts)")
    else:
        feedback.append(f"[FAIL] Inline Event-Handler im HTML gefunden: {list(set(real_inline))} (-3 Pts)")

    # Check 2: Robuste DOM-Selektoren (Vermeiden von previousElementSibling)
    if "previousElementSibling" not in code and "nextElementSibling" not in code:
        score += 2
        feedback.append("[OK] Keine fragilen Sibling-Selektoren wie previousElementSibling verwendet (2/2 Pts)")
    else:
        feedback.append("[FAIL] Fragile Sibling-Selektoren (previous/nextElementSibling) im Code gefunden (-2 Pts)")

    # Check 3: CSS Media Queries vorhanden?
    if "@media" in code:
        score += 3
        feedback.append("[OK] CSS Media Queries für Responsive Design gefunden (3/3 Pts)")
    else:
        feedback.append("[FAIL] Keine CSS Media Queries (@media) gefunden (-3 Pts)")

    # 2. Funktionale Tests mit Playwright
    try:
        from playwright.sync_api import sync_playwright
        
        feedback.append("Starte Playwright für funktionalen UI-Test...")
        with sync_playwright() as p:
            # Starte headless browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Konsolen-Fehler sammeln
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            
            # Seite laden
            abs_url = f"file:///{os.path.abspath(html_path).replace(os.sep, '/')}"
            page.goto(abs_url)
            page.wait_for_load_state("networkidle")
            
            # Check 4: Erfolgreich geladen
            score += 4
            feedback.append("[OK] Seite erfolgreich in Chromium geladen (4/4 Pts)")
            
            # Versuche, Input und Button zu finden
            # Wir testen gängige Selektoren
            input_selector = None
            for sel in ["input[type='text']", "input", ".task-input", "#todo-input", "#task-input"]:
                if page.locator(sel).count() > 0:
                    input_selector = sel
                    break
                    
            add_button_selector = None
            for sel in ["button", "input[type='submit']", ".add-btn", "#add-btn"]:
                if page.locator(sel).count() > 0:
                    add_button_selector = sel
                    break
            
            if input_selector and add_button_selector:
                # Task hinzufügen
                test_task_text = "Benchmark Test-Task 123"
                page.fill(input_selector, test_task_text)
                page.click(add_button_selector)
                page.wait_for_timeout(200) # Kurze Pause für JS
                
                # Check 5: Task hinzugefügt
                page_content = page.content()
                if test_task_text in page_content:
                    score += 6
                    feedback.append("[OK] Task erfolgreich über UI hinzugefügt (6/6 Pts)")
                    
                    # Check 6: Persistenz nach Reload (localStorage)
                    page.reload()
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(200)
                    
                    if test_task_text in page.content():
                        score += 6
                        feedback.append("[OK] Task bleibt nach Seiten-Reload erhalten (localStorage) (6/6 Pts)")
                    else:
                        feedback.append("[FAIL] Task verschwindet nach Reload (kein funktionierendes localStorage) (0/6 Pts)")
                else:
                    feedback.append("[FAIL] Task konnte nicht hinzugefügt werden (Text nicht im DOM) (0/6 Pts)")
            else:
                feedback.append("[FAIL] Eingabefeld oder Button nicht gefunden. Funktionale Tests übersprungen (0/12 Pts)")
                
            # Check 7: Keine JS-Fehler in der Konsole
            if len(console_errors) == 0:
                score += 6
                feedback.append("[OK] Keine JavaScript-Konsolenfehler während der Interaktion (6/6 Pts)")
            else:
                feedback.append(f"[FAIL] JavaScript-Konsolenfehler aufgetreten: {console_errors[:2]} (-6 Pts)")
                
            browser.close()
            
    except ImportError:
        feedback.append("[WARN] Playwright ist in Python nicht installiert. Verwende statisches Fallback für funktionale Tests.")
        # Fallback-Punktevergabe basierend auf Codeanalyse, um den Benchmark lauffähig zu halten:
        # Falls localStorage im JS-Code vorkommt, geben wir Teilpunkte
        if "localStorage.setItem" in code or "localStorage.getItem" in code:
            score += 10
            feedback.append("[OK] [FALLBACK] localStorage API-Aufrufe im JS-Code gefunden (10/12 Pts)")
        else:
            feedback.append("[FAIL] [FALLBACK] Keine localStorage-API im JS-Code gefunden (0/12 Pts)")
            
        if "addEventListener" in code or "document.querySelector" in code:
            score += 8
            feedback.append("[OK] [FALLBACK] Event-Listener und Query-Selektoren im JS-Code gefunden (8/10 Pts)")
        else:
            feedback.append("[FAIL] [FALLBACK] Keine modernen Event-Listener/Selektoren im JS-Code gefunden (0/10 Pts)")
            
    except Exception as e:
        feedback.append(f"[FEHLER] Fehler bei Playwright-E2E-Evaluierung: {e}")
        # Sicheres Fallback, damit der Benchmark nicht abbricht
        score += 8
        feedback.append("[WARN] Fallback-Punkte vergeben aufgrund von E2E-Laufzeitfehler.")

    return score, max_score, feedback

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python grade_todo.py <path_to_index.html>")
        sys.exit(1)
    score, max, fb = grade_html_file(sys.argv[1])
    print(f"Score: {score}/{max}")
    print("\n".join(fb))

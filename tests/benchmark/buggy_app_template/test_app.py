import unittest
import os
import sys
import threading
import time
import io
import re

# Sicherstellen, dass das Vorlagenverzeichnis im Pfad ist
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import app

class TestBuggyApp(unittest.TestCase):
    def setUp(self):
        if os.path.exists(app.LOG_FILE):
            os.remove(app.LOG_FILE)

    def tearDown(self):
        if os.path.exists(app.LOG_FILE):
            os.remove(app.LOG_FILE)

    def test_emoji_check(self):
        """Testet, ob im Quellcode von app.py Emojis oder Nicht-ASCII-Zeichen für print() verwendet werden."""
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Regex sucht nach print() Aufrufen mit nicht-ASCII Zeichen oder Emojis
        # Unicode Ranges für Emojis und Sonderzeichen
        emoji_pattern = re.compile(r'print\s*\(\s*f?["\'].*[^\x00-\x7F].*["\']\s*\)')
        matches = emoji_pattern.findall(content)
        
        # Erlaube Umlaute wie ä,ö,ü,ß im Kommentar/Print, aber KEINE Emojis
        # Wir suchen gezielt nach Emojis: 🚀, 📬, 🔥, etc.
        emoji_specific_pattern = re.compile(r'[🚀📬🔥📬]')
        specific_matches = emoji_specific_pattern.findall(content)
        
        self.assertEqual(len(specific_matches), 0, f"Fehler: Emojis in app.py gefunden: {specific_matches}. Das fuehrt zu CP1252-Crashes auf Windows-Terminal!")

    def test_concurrent_writes(self):
        """Simuliert gleichzeitige Schreibzugriffe (Race Condition Test)."""
        num_threads = 10
        threads = []
        
        def worker(num):
            app.write_log(f"Thread-{num}")
            
        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            
        # Starte alle Threads gleichzeitig
        for t in threads:
            t.start()
            
        for t in threads:
            t.join()
            
        # Überprüfe, ob alle 10 Einträge in der Logdatei vorhanden sind
        self.assertTrue(os.path.exists(app.LOG_FILE), "Logdatei wurde nicht erstellt")
        
        with open(app.LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            
        logs = content.strip().split("\n")
        # Wenn kein Lock verwendet wurde, überschreiben sich die Threads gegenseitig
        # und es fehlen Einträge in der Datei.
        self.assertEqual(len(logs), num_threads, f"Race Condition erkannt! Nur {len(logs)} von {num_threads} Logs wurden gespeichert.")

    def test_exception_handling(self):
        """Prüft, ob Exception-Handling in app.py KeyboardInterrupt durchlassen würde oder blank exceptions fängt."""
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Prüft, ob es ein unbeschränktes 'except:' gibt
        self.assertNotIn("except:", content, "Warnung: Ein unbeschraenktes 'except:' schluckt SystemExit und KeyboardInterrupt. Verwende 'except Exception as e:'")

if __name__ == "__main__":
    unittest.main()

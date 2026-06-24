# Projekt-Historie & Learnings: Portal-Authentifizierung & Passwort-Reset

Dieses Dokument erfasst die vollständige Entwicklungshistorie, architektonische Entscheidungen, aufgetretene Fehler und Sicherheitsanalysen für das Projekt zur Erweiterung der Benutzerverwaltung im Mechatronik-Portal.

---

## 1. Ausgangslage & Zielsetzung
- **Ziel:** Integration einer serverseitigen Benutzerregistrierung, automatischer E-Mail-Bestätigung bei Kontoerstellung sowie einer Funktion zum Zurücksetzen des Passworts über einen sicheren E-Mail-Link.
- **Projekt-Kontext:** Hauptportfolio-Website von Stephan Jeremias (Student in Mechatronik & Systemtechnik).
- **Architektur:** Multithreaded Python HTTP-Server (`server.py`) im Backend; Glassmorphism HTML/JS/CSS im Frontend.

---

## 2. Phasen der Entwicklung & Meilensteine

### Phase 1: Migration auf serverseitige Daten & E-Mail-Mocking
- **Herausforderung:** Bisher wurden alle Benutzerkonten im Browser-seitigen `localStorage` gespeichert. E-Mail-Versand und Tokenverifizierung erforderten jedoch Backend-Sicherheitskontrollen.
- **Lösung:** 
  - Ablage der Benutzer in `users.json` auf dem Server.
  - Implementierung einer `send_email`-Funktion, die SMTP-Daten nutzt. Falls keine Credentials konfiguriert sind, speichert der Server die E-Mail als HTML im Ordner `sent_emails/` ab. Dies ermöglicht lokales Testen ohne externen E-Mail-Dienst.
  - Erstellung der Passwort-Zurücksetzen-Seite (`reset-password.html`), welche Tokens über `?token=...` ausliest.

### Phase 2: Sicherheitsaudit durch den Critic-Subagenten
Nach der ersten Implementierung wurde ein autonomer Audit-Subagent (`code_critic`) zur Code-Prüfung gestartet. Dieser identifizierte kritische Sicherheits- und Stabilitätsschwachstellen:
1. **Session Hijacking:** Die Identifikation des Nutzers erfolgte rein über eine E-Mail-Adresse im `localStorage`. Durch Manipulation dieses Eintrags im Browser konnte jede beliebige Identität angenommen werden.
2. **BOLA (Broken Object-Level Authorization):** Profilabfragen und Notiz-Speicherungen basierten rein auf der Angabe von E-Mail-Parametern.
3. **Schwaches Passwort-Hashing:** Verwendung von einfachem, schnellem SHA-256 (anfällig für GPU-Brute-Force im Falle eines Datenbank-Leaks).
4. **Datenkorruption (Race Conditions):** Gleichzeitige Schreib-/Lesezugriffe auf `users.json` über mehrere Threads hinweg.
5. **Stored XSS:** Unbeschränkte Uploads von beliebigen Dateiendungen (z. B. `.html` oder `.js`), die unter dem Web-Origin ausgeführt werden konnten.

### Phase 3: Härtung & Behebung der Schwachstellen
- **Session-Tokens:** Einführung kryptografischer Session-Tokens nach erfolgreichem Login. Der Client übergibt dieses im Header (`Authorization: Bearer <token>`). APIs arbeiten rein auf Tokenbasis, E-Mail-Parameter wurden aus den Requests entfernt.
- **PBKDF2-Hashing:** Upgrade auf PBKDF2-HMAC-SHA256 mit 100.000 Iterationen (vollständig abwärtskompatibel zu SHA-256).
- **Dateisicherheit:** Hinzufügen von `threading.Lock()` für alle Schreib-/Leseoperationen auf `users.json`.
- **Upload-Whitelisting:** Begrenzung erlaubter Dateiendungen auf `.txt`, `.pdf`, `.md`, `.doc`, `.docx` und `.json`.

### Phase 4: UI- & System-Bugfixes
- **Charmap-Encoding Crash:** Konsolen-Emojis führten unter Windows-Systemen zu Serverabstürzen. Alle Emojis wurden aus den stdout-Prints entfernt.
- **HTML Nesting Bug:** Durch ein fehlendes schließendes `</div>` im Registrierungsbereich wurde das Passwort-Vergessen-Formular fälschlicherweise in einem ausgeblendeten CSS-Container gerendert, was zu einer leeren Ansicht führte. Dies wurde erfolgreich korrigiert.

---

## 3. Lerneffekte für zukünftige Projekte (Lessons Learned)

1. **Security-First ab Minute Eins:** Die Praxis zeigt, dass die nachträgliche Absicherung von API-Endpunkten aufwendiger ist als das direkte Implementieren von Token-Authentifizierung und starken Hashes bei der Feature-Erstellung.
2. **Kombination aus manuellen & automatisierten Tests:** Das für dieses Projekt geschriebene Testskript (`scratch/test_auth.py`) simulierte den gesamten End-to-End-Ablauf vollautomatisch und hat die Verifikationszeit für den Passwort-Reset-Fluss massiv verkürzt. Dieser Ansatz sollte bei komplexen Logikänderungen immer gewählt werden.
3. **Subagenten als wertvolle Partner:** Die Delegation von Audits an spezialisierte Code-Critics deckt logische Fehler auf, die man selbst leicht übersieht. Das spart Debugging-Zeit und erhöht die Softwarequalität signifikant.

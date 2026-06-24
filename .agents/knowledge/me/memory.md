# Agent Memory & Continuous Improvement

Dieses Dokument dient als kontinuierlicher Wissensspeicher (Memory File) für den Agenten. Es hält fest, welche Probleme bei Projekten aufgetreten sind, wie sie gelöst wurden und welche strategischen Verhaltensänderungen für zukünftige Aufgaben in diesem Workspace nötig sind.

---

## 1. Vorfall: HTML-Schachtelungsfehler (24. Juni 2026)

### Was ist passiert?
Beim Hinzufügen der Passwort-Vergessen-Ansicht (`#forgot-password-view`) in `index.html` wurde das schließende `</div>`-Tag für die vorherige Registrierungsansicht (`#register-view`) vergessen.

### Wo lag die Schwierigkeit?
Da die übergeordnete Ansicht (`#register-view`) standardmäßig mit `.hidden` ausgeblendet war, wurde das neu eingefügte Passwort-Vergessen-Formular als Kindelement ebenfalls unsichtbar. In der Benutzeroberfläche sah man nach dem Klicken auf "Passwort vergessen?" nur ein leeres Card-Layout mit dem Zurück-Pfeil.

### Wie klappt es das nächste Mal besser?
1. **Strikte HTML-Strukturprüfung:** Vor dem Speichern von Änderungen in großen HTML-Dateien muss die Hierarchie der Tags (insbesondere öffnende und schließende `div`-Tags) verifiziert werden.
2. **Visuelles Feedback in CLI-Tests:** Bei manuellen oder automatisierten UI-Tests sollte die Sichtbarkeit (`display` / `.hidden` Status) der Ziel-DOM-Elemente im Testskript oder bei der Inspektion aktiv geprüft werden.

---

## 2. Vorfall: Codierungsfehler auf Windows-Systemen (24. Juni 2026)

### Was ist passiert?
Beim Starten von `server.py` in der Windows PowerShell stürzte der Server ab mit dem Fehler:
`'charmap' codec can't encode character '\U0001f680' ...`

### Wo lag die Schwierigkeit?
Im Python-Skript wurden Konsolen-Ausgaben mit Emojis verwendet (z. B. `🚀` für Serverstart, `📬` für E-Mails). Da Windows-Konsolen standardmäßig oft CP1252 (charmap) für die Standardausgabe nutzen, führt das Drucken von nicht-ASCII Zeichen ohne explizite UTF-8 Konfiguration der Konsole zu Abstürzen.

### Wie klappt es das nächste Mal besser?
1. **Emoji-Freie Konsolenausgaben:** In Python-Server-Skripten, die lokal auf Windows ausgeführt werden, sollten Emojis und spezielle Unicode-Zeichen in `print()`-Aufrufen vermieden oder durch reinen ASCII-Text ersetzt werden.
2. **UTF-8 Erzwingung:** Bei Dateischreibvorgängen (`open(..., 'w', encoding='utf-8')`) konsequent das Encoding angeben (wurde bereits umgesetzt).

---

## 3. Vorfall: Sicherheitslücken bei der API-Integration (24. Juni 2026)

### Was ist passiert?
Der erste Entwurf zur Authentifizierung nutzte E-Mail-Adressen im `localStorage` zur Identifikation an geschützten API-Endpunkten. Der Critic-Subagent deckte dies als kritische Schwachstelle (BOLA / Session-Hijacking) auf.

### Wo lag die Schwierigkeit?
Die Einfachheit von `localStorage` verleitet dazu, schnell eine Identifikationsmethode zu implementieren. Auf einer echten Website führt dies jedoch sofort zu Sicherheitslücken.

### Wie klappt es das nächste Mal besser?
1. **Sicherheit ab Stunde Null:** Auch bei Prototypen von Anfang an auf tokenbasierte Authentifizierung (Session-Tokens) setzen.
2. **Critic-Subagenten frühzeitig nutzen:** Der Critic-Subagent hat hervorragende Arbeit geleistet. Er sollte bei jedem sicherheitsrelevanten Feature vor der finalen Freigabe fest in den Workflow integriert werden.

---

## 4. Vorfall: Passwort-Sichtbarkeits-Toggle ohne Funktion (24. Juni 2026)

### Was ist passiert?
Beim Klicken auf das Augensymbol wurde das Passwort nicht im Klartext angezeigt, sondern verblieb im gepunkteten Modus (`••••••••`).

### Wo lag die Schwierigkeit?
Im JavaScript-Code wurde der Passwort-Eingabetyp mittels `button.previousElementSibling` umgeschaltet. Da im HTML-Layout ein Schloss-Symbol (`<i class="fa-solid fa-lock input-icon"></i>`) direkt vor dem Button eingefügt war, lieferte `previousElementSibling` das Icon-Element statt des `<input>`-Elements zurück. Das Umschalten des Typs schlug daher lautlos fehl.

### Wie klappt es das nächste Mal besser?
1. **Strukturunabhängige Selektoren verwenden:** Anstatt uns auf die genaue Reihenfolge der Geschwister-Elemente (`previousElementSibling`) zu verlassen, sollte das Element robuster über die Elternbox gesucht werden:
   `const input = button.parentElement.querySelector('input');`
2. **Automatisiertes Testen von State-Veränderungen:** Wenn möglich, sollten Klick-Events auf Sichtbarkeits-Toggles und deren Auswirkung auf das DOM in Integrations- oder Unit-Tests abgedeckt werden.

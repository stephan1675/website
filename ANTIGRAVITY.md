# Antigravity Developer & System Guide

Welcome to the internal operating system workspace of Stephan Jeremias. This workspace is designed for mechatronic development, study projects, and agentic AI integration.

This document serves as the entry point and structural map for all AI assistants (like Antigravity) who open this codebase.

---

## 📁 System Folder Structure

The workspace configuration is stored inside the `.agents/` directory:

### 1. `.agents/`
The root directory of the agent customizations and rules:
- **`AGENTS.md`**: Contains the Git workflow rules and the Karpathy Structured Agent Workflow. This file is automatically loaded by the system.

### 2. `.agents/knowledge/`
The local knowledge base for the Board of Advisors and personal context:
- **`me/`**: Holds personal background, credentials, and career transition details (e.g., `user_profile.md`).
- **`advisors/`**: Holds profiles of the Board of Advisors:
  - `andrej_karpathy.md` (AI, control theory, clean code)
  - `austin_marchese.md` (MVP scoping, marketing/sharing, efficiency)
  - `limor_fried.md` (Hardware, prototyping, physical debugging)
- **`frameworks/`**: Holds templates, API specifications, and style guides.
- **`audience/`**: Holds target profiles for recruiters, mechatronics professors, and network.
- **`raw/`**: Holds raw text data before cleaning and sorting.

### 3. `.agents/skills/`
Custom executable behaviors (slash commands/triggers) loaded by the agent:
- **`skill.md`**: Standard template for defining new skills.
- **`ask_the_board/`**: Queries the Board of Advisors for synthesized guidance on technical/business decisions.
- **`improve_system/`**: Modifies agent rules, user profiles, or advisor characteristics.
- **`ingest_resource/`**: Fetches, cleans, and imports external resources into the knowledge base.

### 4. `.agents/projects/`
Status folders and placeholders for major active projects:
- **`dashboard/`**: Holds roadmap and planning documents for the command center.
- **`personal_site/`**: Holds roadmap and drafts for the public website.

---

## 🛠️ Development & Commands

### Running the Web Server
To start the local developer server and preview the personal site/dashboard:
```powershell
# Set UTF-8 encoding (to prevent emoji print crashes on Windows)
$env:PYTHONIOENCODING="utf-8"

# Start the server
python server.py
```
The server runs on `http://localhost:8000`.

### Active Projects
1. **Frontend Landing Page**: Main webpage structure (`index.html`, `js/main.js`, `css/main.css`).
2. **C++ Spiel**: A terminal-based Tower Defense game (`c++ spiel/`).
3. **Python Shooter**: A Ursina-engine 3D game (`python shooter/`).

---

## 🤖 Guidelines for AI Assistants
- **Rote Faden**: Always describe Stephan's career transition from social care to engineering in a positive, active tone (professionalizing a lifelong passion for technical problem-solving).
- **Style**: Focus on concrete proofs (his CAD work, linear motor internships, ESP32 soldering) instead of standard corporate buzzwords. Keep a calm, analytical, and lösungsorientierte maker persona.
- **Rules**: Never push directly to `main`. Work on `develop` or feature branches.

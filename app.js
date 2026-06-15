/* Core JS Logic for Premium Portal */

document.addEventListener('DOMContentLoaded', () => {

  // --- Deployment Backend Configuration ---
  const BACKEND_URL = 'https://riverbed-subpanel-volumes.ngrok-free.dev'; // Hier deine Render-URL eintragen!

  function getApiBaseUrl() {
    if (window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1' ||
      window.location.protocol === 'file:') {
      return 'http://localhost:8000';
    }
    return BACKEND_URL;
  }

  // Immediate wakeup ping to the Render backend
  (function wakeupBackend() {
    const pingUrl = getApiBaseUrl();
    console.log("[Wakeup] Pinging backend at:", pingUrl);
    fetch(`${pingUrl}/api/ping`)
      .then(r => r.json())
      .then(data => console.log("[Wakeup] Backend is awake:", data))
      .catch(err => console.warn("[Wakeup] Backend ping sent (waking up...):", err));
  })();

  // --- DOM Element References ---

  // Views
  const homeView = document.getElementById('home-view');
  const projectsView = document.getElementById('projects-view');
  const authSection = document.getElementById('auth-section');
  const dashboardSection = document.getElementById('dashboard-section');

  const loginView = document.getElementById('login-view');
  const registerView = document.getElementById('register-view');

  // Forms & Inputs
  const loginForm = document.getElementById('login-form');
  const loginEmail = document.getElementById('login-email');
  const loginPassword = document.getElementById('login-password');

  const registerForm = document.getElementById('register-form');
  const registerUsername = document.getElementById('register-username');
  const registerEmail = document.getElementById('register-email');
  const registerPassword = document.getElementById('register-password');
  const strengthBar = document.getElementById('strength-bar');
  const strengthText = document.getElementById('strength-text');

  // Buttons & Navigation
  const homeAuthStatus = document.getElementById('home-auth-status');

  const btnViewProjects = document.getElementById('btn-view-projects');
  const btnProjectsBack = document.getElementById('btn-projects-back');
  const btnAuthBack = document.getElementById('btn-auth-back');
  const btnDashBack = document.getElementById('btn-dash-back');

  const goToRegisterBtn = document.getElementById('go-to-register');
  const goToLoginBtn = document.getElementById('go-to-login');

  const btnRunPython = document.getElementById('btn-run-python');
  const btnRunCpp = document.getElementById('btn-run-cpp');

  // Dashboard details
  const displayUsername = document.getElementById('display-username');
  const displayEmail = document.getElementById('display-email');
  const userAvatar = document.getElementById('user-avatar');
  const statCreated = document.getElementById('stat-created');
  const statLogins = document.getElementById('stat-logins');
  const quickNotes = document.getElementById('quick-notes');
  const saveNoteBtn = document.getElementById('save-note-btn');
  const logoutBtn = document.getElementById('logout-btn');

  const toastContainer = document.getElementById('toast-container');

  // Track active view
  let currentActiveView = homeView;

  // --- Initialize Storage ---
  if (!localStorage.getItem('users')) {
    localStorage.setItem('users', JSON.stringify([]));
  }

  // --- Router / View Switcher ---
  function navigateToView(targetView) {
    if (currentActiveView === targetView) return;

    // Add fade-out transition to the current view
    currentActiveView.classList.add('fade-out');

    setTimeout(() => {
      // Hide current view
      currentActiveView.classList.add('hidden');
      currentActiveView.classList.remove('fade-out');

      // Show target view
      targetView.classList.remove('hidden');
      targetView.classList.add('fade-in');

      // Set new active view
      currentActiveView = targetView;

      setTimeout(() => {
        targetView.classList.remove('fade-in');
      }, 400);
    }, 300);
  }

  // Bind view switch events
  btnViewProjects.addEventListener('click', () => navigateToView(projectsView));
  btnProjectsBack.addEventListener('click', () => navigateToView(homeView));
  btnAuthBack.addEventListener('click', () => navigateToView(homeView));
  btnDashBack.addEventListener('click', () => navigateToView(homeView));

  // --- Home View Header - Authentication Status ---
  function updateHomeAuthStatus() {
    const activeSessionEmail = localStorage.getItem('currentUserSession');
    homeAuthStatus.innerHTML = ''; // Clear status area

    if (activeSessionEmail) {
      const users = JSON.parse(localStorage.getItem('users'));
      const user = users.find(u => u.email === activeSessionEmail);

      if (user) {
        // Logged-in state
        const letter = user.username.charAt(0).toUpperCase();

        homeAuthStatus.innerHTML = `
          <div class="user-avatar" style="width: 35px; height: 35px; font-size: 0.9rem;">${letter}</div>
          <div class="user-info" style="display: block; margin-right: 0.5rem;">
            <span class="user-name" style="font-size: 0.85rem; display: block;">${user.username}</span>
          </div>
          <button id="home-to-dash-btn" class="btn btn-primary" style="padding: 0.5rem 1rem; font-size: 0.8rem; width: auto; margin-right: 0.5rem;">
            <i class="fa-solid fa-gauge"></i>
            <span>Dashboard</span>
          </button>
          <button id="home-logout-btn" class="btn-logout" style="padding: 0.5rem 0.75rem; font-size: 0.8rem;">
            <i class="fa-solid fa-arrow-right-from-bracket"></i>
          </button>
        `;

        // Add events to dynamic buttons
        document.getElementById('home-to-dash-btn').addEventListener('click', () => {
          showDashboard(user);
        });

        document.getElementById('home-logout-btn').addEventListener('click', () => {
          performLogout();
        });
        return;
      }
    }

    // Logged-out state
    homeAuthStatus.innerHTML = `
      <button id="home-login-btn" class="btn btn-primary" style="padding: 0.55rem 1.1rem; font-size: 0.85rem; width: auto;">
        <i class="fa-solid fa-right-to-bracket"></i>
        <span>Mitgliederbereich</span>
      </button>
    `;

    document.getElementById('home-login-btn').addEventListener('click', () => {
      // Show login view inside auth card
      loginView.classList.remove('hidden');
      registerView.classList.add('hidden');
      navigateToView(authSection);
    });
  }

  // --- Password Visibility Toggle ---
  document.querySelectorAll('.password-toggle').forEach(button => {
    button.addEventListener('click', (e) => {
      e.preventDefault();
      const input = button.previousElementSibling;
      const icon = button.querySelector('i');

      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
      } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
      }
    });
  });

  // --- Password Strength Meter ---
  registerPassword.addEventListener('input', () => {
    const password = registerPassword.value;
    let strength = 0;

    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password) || /[^A-Za-z0-9]/.test(password)) strength++;

    strengthBar.className = 'strength-bar';

    if (password.length === 0) {
      strengthText.textContent = 'Passwortstärke';
      strengthText.style.color = 'var(--color-text-muted)';
    } else if (strength === 1) {
      strengthBar.classList.add('strength-weak');
      strengthText.textContent = 'Schwach (Mindestens 8 Zeichen, Großbuchstaben, Zahlen)';
      strengthText.style.color = 'var(--color-danger)';
    } else if (strength === 2) {
      strengthBar.classList.add('strength-medium');
      strengthText.textContent = 'Mittelschwer (Füge Zahlen oder Sonderzeichen hinzu)';
      strengthText.style.color = 'var(--color-warning)';
    } else if (strength === 3) {
      strengthBar.classList.add('strength-strong');
      strengthText.textContent = 'Sehr starkes Passwort!';
      strengthText.style.color = 'var(--color-success)';
    }
  });

  // --- Toast Notification System ---
  function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let iconClass = 'fa-solid fa-circle-check';
    if (type === 'error') iconClass = 'fa-solid fa-circle-xmark';
    if (type === 'warning') iconClass = 'fa-solid fa-triangle-exclamation';
    if (type === 'info') iconClass = 'fa-solid fa-circle-info';

    toast.innerHTML = `
      <i class="${iconClass} toast-icon"></i>
      <span class="toast-message">${message}</span>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('toast-exit');
      toast.addEventListener('animationend', () => {
        toast.remove();
      });
    }, 4000);
  }

  // --- Helper: Simple Mock Hash (Base64 encoding) ---
  function mockHash(str) {
    return btoa(str);
  }

  // --- Toggle Login / Register Sub-Views ---
  function switchAuthSubView(showSub, hideSub) {
    loginView.classList.add('fade-out');
    registerView.classList.add('fade-out');

    setTimeout(() => {
      hideSub.classList.add('hidden');
      showSub.classList.remove('hidden');
      loginView.classList.remove('fade-out');
      registerView.classList.remove('fade-out');
    }, 200);
  }

  goToRegisterBtn.addEventListener('click', (e) => {
    e.preventDefault();
    switchAuthSubView(registerView, loginView);
  });

  goToLoginBtn.addEventListener('click', (e) => {
    e.preventDefault();
    switchAuthSubView(loginView, registerView);
  });

  // --- Show secure Dashboard ---
  function showDashboard(user) {
    // Populate profile fields
    displayUsername.textContent = user.username;
    displayEmail.textContent = user.email;
    userAvatar.textContent = user.username.charAt(0).toUpperCase();

    // Populate activity statistics
    statCreated.textContent = user.createdAt;
    statLogins.textContent = user.loginCount;

    // Load note
    quickNotes.value = user.notes || '';

    // Direct navigate
    navigateToView(dashboardSection);
  }

  // --- Game Launching Handler ---
  function runGame(endpoint) {
    // If the site is opened via file://, send the request to the absolute URL of the local server
    const targetUrl = window.location.protocol === 'file:' ? `http://localhost:8000${endpoint}` : endpoint;

    // Fetch API Call
    fetch(targetUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then(response => {
        return response.json().then(data => {
          if (!response.ok) {
            throw new Error(data.message || 'Server-Fehler aufgetreten.');
          }
          return data;
        });
      })
      .then(data => {
        showToast(data.message, 'success');
      })
      .catch(error => {
        console.error("[Launcher] Fehler:", error);
        if (window.location.protocol === 'file:') {
          showToast('Verbindung zum lokalen Server fehlgeschlagen. Bitte stelle sicher, dass "server.py" gestartet ist.', 'warning');
        } else {
          showToast(error.message || 'Verbindung zum Server fehlgeschlagen. Läuft "server.py"?', 'error');
        }
      });
  }

  // Game click listeners
  btnRunPython.addEventListener('click', () => runGame('/api/run-python'));

  // ==========================================
  // RETRO WEB-TERMINAL CLIENT (C++ GAME)
  // ==========================================

  const terminalModal = document.getElementById('terminal-modal');
  const terminalOutput = document.getElementById('terminal-output');
  const terminalInputField = document.getElementById('terminal-input-field');
  const btnSendInput = document.getElementById('btn-send-input');
  const btnCloseTerminal = document.getElementById('btn-close-terminal');

  let activeTerminalSessionId = null;
  let terminalEventSource = null;

  // Launch terminal session
  btnRunCpp.addEventListener('click', () => {
    const baseUrl = getApiBaseUrl();

    // Clear display, open modal and focus input
    terminalOutput.textContent = "Verbindung wird hergestellt...\n";
    terminalModal.classList.remove('hidden');
    terminalInputField.value = '';
    terminalInputField.focus();

    showToast('Starte C++ Terminal-Session...', 'info');

    // 1. Request C++ execution process from server
    fetch(`${baseUrl}/api/run-cpp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then(response => {
        return response.json().then(data => {
          if (!response.ok) {
            throw new Error(data.message || 'Server-Fehler aufgetreten.');
          }
          return data;
        });
      })
      .then(data => {
        activeTerminalSessionId = data.session_id;
        terminalOutput.textContent = `🚀 Session [${activeTerminalSessionId.substring(0, 8)}] verbunden.\n\n`;
        showToast(data.message, 'success');

        // 2. Open EventSource for stdout stream
        terminalEventSource = new EventSource(`${baseUrl}/api/terminal/stream?id=${activeTerminalSessionId}`);

        // Receive stdout messages
        terminalEventSource.onmessage = (event) => {
          try {
            const parsed = JSON.parse(event.data);
            if (parsed.text) {
              let text = parsed.text;

              // 1. Detect ANSI Screen Clear sequences (\x1b[2J or \x1b[H)
              if (text.includes('\x1b[2J') || text.includes('\x1b[H') ||
                text.includes('\u001b[2J') || text.includes('\u001b[H') ||
                text.includes('\x1b[3J')) {
                terminalOutput.textContent = '';
              }

              // 2. Strip all raw ANSI escape control codes (like colors or positioning) to clean output
              text = text.replace(/\x1b\[[0-9;]*[a-zA-Z]/g, '');
              text = text.replace(/\u001b\[[0-9;]*[a-zA-Z]/g, '');

              terminalOutput.textContent += text;

              // Scroll to bottom
              terminalOutput.scrollTop = terminalOutput.scrollHeight;
            }
          } catch (e) {
            console.error("[Terminal] SSE Parsing-Fehler:", e);
          }
        };

        // Process exited normally
        terminalEventSource.addEventListener('exit', () => {
          terminalOutput.textContent += "\n\n---------------------------------------\n[Spielprozess beendet. Drücke X zum Schließen]";
          terminalOutput.scrollTop = terminalOutput.scrollHeight;
          if (terminalEventSource) terminalEventSource.close();
          activeTerminalSessionId = null;
          showToast("Spiel erfolgreich beendet.", "info");
        });

        // Connection errors
        terminalEventSource.onerror = (err) => {
          console.error("[Terminal] SSE Verbindungsfehler:", err);
          if (activeTerminalSessionId) {
            terminalOutput.textContent += "\n\n[Verbindung zum Terminal-Stream verloren]";
            terminalOutput.scrollTop = terminalOutput.scrollHeight;
            if (terminalEventSource) terminalEventSource.close();
          }
        };
      })
      .catch(error => {
        console.error("[Terminal] Startfehler:", error);
        terminalModal.classList.add('hidden');
        if (window.location.protocol === 'file:') {
          showToast('Verbindung zum lokalen Server fehlgeschlagen. Bitte stelle sicher, dass "server.py" gestartet ist.', 'warning');
        } else {
          showToast(error.message || 'C++ Spiel konnte nicht gestartet werden.', 'error');
        }
      });
  });

  // Send input to the C++ stdin stream
  function sendTerminalInput() {
    if (!activeTerminalSessionId) return;

    const text = terminalInputField.value;
    terminalInputField.value = '';

    // Append your command locally so it shows on screen
    terminalOutput.textContent += text + "\n";
    terminalOutput.scrollTop = terminalOutput.scrollHeight;

    const baseUrl = getApiBaseUrl();

    fetch(`${baseUrl}/api/terminal/input`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        id: activeTerminalSessionId,
        input: text
      })
    })
      .catch(err => {
        console.error("[Terminal] Fehler beim Senden der Eingabe:", err);
        terminalOutput.textContent += `\n[Systemfehler: Eingabe "${text}" konnte nicht gesendet werden]\n`;
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
      });
  }

  // Bind enter key on input field
  terminalInputField.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendTerminalInput();
    }
  });

  // Bind send button click
  btnSendInput.addEventListener('click', (e) => {
    e.preventDefault();
    sendTerminalInput();
    terminalInputField.focus();
  });

  // Close terminal session and kill subprocess
  function closeTerminalSession() {
    if (activeTerminalSessionId) {
      const baseUrl = getApiBaseUrl();

      // Notify server to clean up subprocess
      fetch(`${baseUrl}/api/terminal/close`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          id: activeTerminalSessionId
        })
      });

      activeTerminalSessionId = null;
    }

    if (terminalEventSource) {
      terminalEventSource.close();
      terminalEventSource = null;
    }

    terminalModal.classList.add('hidden');
    showToast('Terminal-Sitzung geschlossen.', 'info');
  }

  btnCloseTerminal.addEventListener('click', closeTerminalSession);

  // --- Logout Logic Helper ---
  function performLogout() {
    localStorage.removeItem('currentUserSession');
    showToast('Erfolgreich abgemeldet.', 'info');
    updateHomeAuthStatus();
    navigateToView(homeView);
  }

  logoutBtn.addEventListener('click', performLogout);

  // --- Registration Form Handler ---
  registerForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const username = registerUsername.value.trim();
    const email = registerEmail.value.trim().toLowerCase();
    const password = registerPassword.value;

    if (username.length < 3) {
      showToast('Benutzername muss mindestens 3 Zeichen lang sein.', 'error');
      return;
    }
    if (password.length < 8) {
      showToast('Passwort muss mindestens 8 Zeichen lang sein.', 'error');
      return;
    }

    const users = JSON.parse(localStorage.getItem('users'));

    // Validations
    if (users.some(u => u.email === email)) {
      showToast('Diese E-Mail-Adresse ist bereits registriert!', 'error');
      return;
    }
    if (users.some(u => u.username.toLowerCase() === username.toLowerCase())) {
      showToast('Dieser Benutzername ist bereits vergeben!', 'error');
      return;
    }

    // Save record
    const newUser = {
      username: username,
      email: email,
      passwordHash: mockHash(password),
      createdAt: new Date().toLocaleDateString('de-DE'),
      loginCount: 0,
      notes: ''
    };

    users.push(newUser);
    localStorage.setItem('users', JSON.stringify(users));

    showToast('Konto erfolgreich erstellt! Du kannst dich jetzt anmelden.', 'success');
    registerForm.reset();

    // Reset strength bar
    strengthBar.className = 'strength-bar';
    strengthText.textContent = 'Passwortstärke';
    strengthText.style.color = 'var(--color-text-muted)';

    // Redirect to login form
    switchAuthSubView(loginView, registerView);
  });

  // --- Login Form Handler ---
  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const email = loginEmail.value.trim().toLowerCase();
    const password = loginPassword.value;

    const users = JSON.parse(localStorage.getItem('users'));
    const userIndex = users.findIndex(u => u.email === email);

    if (userIndex === -1 || users[userIndex].passwordHash !== mockHash(password)) {
      showToast('Ungültige E-Mail-Adresse oder falsches Passwort.', 'error');
      return;
    }

    const user = users[userIndex];
    user.loginCount = (user.loginCount || 0) + 1;
    users[userIndex] = user;

    localStorage.setItem('users', JSON.stringify(users));
    localStorage.setItem('currentUserSession', email);

    showToast(`Willkommen zurück, ${user.username}!`, 'success');
    loginForm.reset();

    updateHomeAuthStatus();
    showDashboard(user);
  });

  // --- Save Quick Notes Handler ---
  saveNoteBtn.addEventListener('click', () => {
    const currentEmail = localStorage.getItem('currentUserSession');
    if (!currentEmail) return;

    const users = JSON.parse(localStorage.getItem('users'));
    const userIndex = users.findIndex(u => u.email === currentEmail);

    if (userIndex !== -1) {
      users[userIndex].notes = quickNotes.value;
      localStorage.setItem('users', JSON.stringify(users));
      showToast('Notiz erfolgreich gespeichert!', 'success');
    }
  });

  // ==========================================
  // AI DISCUSSION ROOM CLIENT
  // ==========================================

  // Views & Setup
  const aiDiscussionView = document.getElementById('ai-discussion-view');
  const btnGoToDiscussion = document.getElementById('btn-go-to-discussion');
  const btnDiscussionBack = document.getElementById('btn-discussion-back');

  const discussionSetup = document.getElementById('discussion-setup');
  const discussionSetupForm = document.getElementById('discussion-setup-form');
  const discTopic = document.getElementById('disc-topic');
  const discAgentCount = document.getElementById('disc-agent-count');
  const discAgentsConfigs = document.getElementById('disc-agents-configs');

  // Chat UI
  const discussionChat = document.getElementById('discussion-chat');
  const chatTopicDisplay = document.getElementById('chat-topic-display');
  const discussionMessages = document.getElementById('discussion-messages');
  const chatTypingIndicator = document.getElementById('chat-typing-indicator');
  const typingAvatarIcon = document.getElementById('typing-avatar-icon');
  const typingPersonaName = document.getElementById('typing-persona-name');

  const btnChatToggle = document.getElementById('btn-chat-toggle');
  const btnChatClose = document.getElementById('btn-chat-close');
  const chatUserInputPanel = document.getElementById('chat-user-input-panel');
  const chatUserInputField = document.getElementById('chat-user-input-field');
  const btnChatSendUserInput = document.getElementById('btn-chat-send-user-input');

  // Save Modal Elements
  const saveDiscussionModal = document.getElementById('save-discussion-modal');
  const btnSaveDiscYes = document.getElementById('btn-save-disc-yes');
  const btnSaveDiscNo = document.getElementById('btn-save-disc-no');

  // State
  let activeDiscussionSessionId = null;
  let discussionEventSource = null;
  let discussionIsPaused = false;
  let discussionMessageBuffer = [];
  let currentDiscussionTurns = []; // Stores all messages for text file export
  let currentSessionAgents = [];

  // Preset Personas
  const PRESET_PERSONAS = {
    "trump": {
      name: "Donald Trump",
      age: "80",
      profile: "Ehemaliger US-Präsident, Immobilien-Milliardär.",
      politicalStance: [
        "Make America Great Again und Amerika First Protektionismus.",
        "Grenzsicherung und harte Migrationspolitik.",
        "Deregulierung der Wirtschaft und Steuersenkungen."
      ],
      agenda: "Alle Mitredner lächerlich machen und zeigen, dass nur ich die Wahrheit kenne.",
      tone: "arrogant, direkt, polemisch, umgangssprachlich",
      emoji: "🇺🇸"
    },
    "musk": {
      name: "Elon Musk",
      age: "54",
      profile: "Tech-Milliardär, Gründer von Tesla, SpaceX und Neuralink.",
      politicalStance: [
        "Sicherung der menschlichen Zukunft durch Besiedlung des Mars.",
        "First Principles Denken und maximale Effizienz.",
        "Schutz der freien Meinungsäußerung auf X."
      ],
      agenda: "Technologischen Fortschritt und Mars-Mission als einzige logische Lösung darstellen.",
      tone: "visionär, leicht sprunghaft, technikbegeistert, energetisch",
      emoji: "🚀"
    },
    "xi": {
      name: "Xi Jinping",
      age: "72",
      profile: "Generalsekretär der KP Chinas und Staatspräsident.",
      politicalStance: [
        "Realisierung des Chinesischen Traums und nationale Verjüngung.",
        "Wahrung der sozialen Stabilität und kollektiven Disziplin.",
        "Schaffung einer multipolaren Weltordnung unter Chinas Führung."
      ],
      agenda: "Die Stabilität und Überlegenheit des chinesischen Entwicklungsmodells betonen.",
      tone: "äußerst diplomatisch, streng, formal, bedacht",
      emoji: "🐼"
    },
    "schweiz": {
      name: "Schweizer Bundespräsident",
      age: "60",
      profile: "Mitglied des siebenköpfigen Bundesratskollegiums der Schweiz.",
      politicalStance: [
        "Pflege des Konkordanzsystems und Konsensfindung über alle Parteien hinweg.",
        "Wahrung der dauerhaften bewaffneten Schweizer Neutralität.",
        "Schutz der direkten Demokratie und des Föderalismus."
      ],
      agenda: "Einen neutralen Kompromiss finden und alle Beteiligten zur sachlichen Mäßigung aufrufen.",
      tone: "äußerst höflich, konsensorientiert, sachlich, schweizerisch",
      emoji: "🇨🇭"
    }
  };

  // Route bindings
  btnGoToDiscussion.addEventListener('click', () => {
    navigateToView(aiDiscussionView);
    renderAgentsSetup();
  });
  btnDiscussionBack.addEventListener('click', () => navigateToView(homeView));

  // Change count handler
  discAgentCount.addEventListener('change', renderAgentsSetup);

  // Render agents configuration forms dynamically
  function renderAgentsSetup() {
    discAgentsConfigs.innerHTML = '';
    const count = parseInt(discAgentCount.value);

    // Load saved custom personas from localStorage
    const customPersonas = JSON.parse(localStorage.getItem('customPersonas') || '[]');

    for (let i = 1; i <= count; i++) {
      const card = document.createElement('div');
      card.className = 'agent-config-card';

      // Build options dropdown list
      let customOptions = '';
      customPersonas.forEach((p, idx) => {
        customOptions += `<option value="custom_${idx}">Eigene: ${p.name}</option>`;
      });

      card.innerHTML = `
        <h4><i class="fa-solid fa-robot" style="color: var(--color-primary);"></i> Teilnehmer ${i}</h4>
        
        <div class="form-group" style="margin-bottom: 0.75rem;">
          <label>Persona auswählen</label>
          <select class="form-control select-agent-persona" data-agent-idx="${i}" style="padding-left: 1.25rem;">
            <option value="trump">Donald Trump (Preset)</option>
            <option value="musk">Elon Musk (Preset)</option>
            <option value="xi">Xi Jinping (Preset)</option>
            <option value="schweiz">Schweizer Bundespräsident (Preset)</option>
            <option value="user_me">Ich (Benutzer)</option>
            ${customOptions}
            <option value="new_custom" style="color: var(--color-secondary); font-weight: bold;">+ Neue Persona erstellen...</option>
          </select>
        </div>

        <!-- Collapsible Custom Form (hidden by default) -->
        <div class="custom-persona-form hidden" id="custom-form-agent-${i}">
          <div class="form-group" style="margin-bottom: 0.75rem;">
            <label>Name</label>
            <input type="text" class="form-control cust-name" placeholder="z.B. Sokrates" style="padding-left: 1rem;">
          </div>
          <div class="form-row-two" style="margin-bottom: 0.75rem;">
            <div class="form-group" style="margin-bottom: 0;">
              <label>Alter</label>
              <input type="number" class="form-control cust-age" placeholder="70" style="padding-left: 1rem;">
            </div>
            <div class="form-group" style="margin-bottom: 0;">
              <label>Emoji/Icon</label>
              <input type="text" class="form-control cust-emoji" placeholder="🏛️" style="padding-left: 1rem;">
            </div>
          </div>
          <div class="form-group" style="margin-bottom: 0.75rem;">
            <label>Profil / Kurzbeschreibung</label>
            <textarea class="cust-profile" placeholder="Philosoph der griechischen Antike..."></textarea>
          </div>
          <div class="form-group" style="margin-bottom: 0.5rem;">
            <label style="margin-bottom: 0.25rem;">Politische Grundeinstellung (3 Sätze, nach Prio)</label>
            <input type="text" class="form-control cust-prio-1" placeholder="Priorität 1: Kritisches Hinterfragen..." style="padding-left: 1rem; margin-bottom: 0.4rem; font-size: 0.85rem;">
            <input type="text" class="form-control cust-prio-2" placeholder="Priorität 2: Tugendhaftigkeit..." style="padding-left: 1rem; margin-bottom: 0.4rem; font-size: 0.85rem;">
            <input type="text" class="form-control cust-prio-3" placeholder="Priorität 3: Suche nach der Wahrheit..." style="padding-left: 1rem; font-size: 0.85rem;">
          </div>
          <div class="form-group" style="margin-bottom: 0.75rem;">
            <label>Aktuelle Botschaft (Gesprächsziel)</label>
            <input type="text" class="form-control cust-agenda" placeholder="Jeder Behauptung auf den Zahn fühlen" style="padding-left: 1rem;">
          </div>
          <div class="form-group" style="margin-bottom: 0.75rem;">
            <label>Sprachstil / Tonalität</label>
            <select class="form-control cust-tone" style="padding-left: 1rem;">
              <option value="skeptisch, fragend, weise">Skeptisch / Hinterfragend</option>
              <option value="direkt, aggressiv, ungeduldig">Direkt / Aggressiv</option>
              <option value="höflich, ruhig, diplomatisch">Höflich / Diplomatisch</option>
              <option value="emotional, leidenschaftlich, laut">Leidenschaftlich / Emotional</option>
              <option value="sachlich, analytisch, kühl">Analytisch / Sachlich</option>
            </select>
          </div>
          <div class="form-group" style="margin-bottom: 0.75rem;">
            <label>Wissensdokument (.txt hochladen)</label>
            <div class="file-upload-wrapper">
              <div class="file-upload-btn">
                <i class="fa-solid fa-file-arrow-up"></i>
                <span>Datei auswählen</span>
              </div>
              <input type="file" class="cust-file-input" accept=".txt">
            </div>
            <span class="file-upload-name id-file-name-display-${i}">Kein Dokument verknüpft</span>
          </div>
          
          <label class="save-checkbox-row">
            <input type="checkbox" class="cust-save-checkbox" checked>
            <span>Persona für zukünftige Debatten speichern</span>
          </label>
        </div>
      `;

      discAgentsConfigs.appendChild(card);

      // Bind dropdown change triggers
      const dropdown = card.querySelector('.select-agent-persona');
      const customForm = card.querySelector('.custom-persona-form');
      const fileInput = card.querySelector('.cust-file-input');
      const fileNameDisplay = card.querySelector(`.id-file-name-display-${i}`);

      dropdown.addEventListener('change', () => {
        if (dropdown.value === 'new_custom') {
          customForm.classList.remove('hidden');
        } else {
          customForm.classList.add('hidden');
        }
      });

      fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
          fileNameDisplay.textContent = `Ausgewählt: ${fileInput.files[0].name}`;
        } else {
          fileNameDisplay.textContent = 'Kein Dokument verknüpft';
        }
      });
    }
  }

  // Helper: Read file as Base64 Promise
  function readFileAsBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = error => reject(error);
      reader.readAsDataURL(file);
    });
  }

  // Helper: Upload file to python backend
  async function uploadDocument(file) {
    const baseUrl = getApiBaseUrl();
    const base64Data = await readFileAsBase64(file);

    const response = await fetch(`${baseUrl}/api/discussion/upload`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        filename: file.name,
        content: base64Data
      })
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.message || 'Upload fehlgeschlagen');
    }

    const data = await response.json();
    return data.filename;
  }

  // Submit setup and start discussion
  discussionSetupForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const topic = discTopic.value.trim();
    const agentCount = parseInt(discAgentCount.value);
    const agentConfigs = discAgentsConfigs.querySelectorAll('.agent-config-card');

    showToast('Bereite KI-Teilnehmer vor...', 'info');

    const agents = [];
    const customPersonasToSave = JSON.parse(localStorage.getItem('customPersonas') || '[]');

    try {
      // Loop through selected configurations
      for (let i = 0; i < agentCount; i++) {
        const card = agentConfigs[i];
        const selector = card.querySelector('.select-agent-persona');
        const selection = selector.value;

        let agentObj = null;

        if (selection === 'new_custom') {
          // Validate and extract custom fields
          const name = card.querySelector('.cust-name').value.trim();
          const age = card.querySelector('.cust-age').value.trim() || '30';
          const emoji = card.querySelector('.cust-emoji').value.trim() || '👤';
          const profile = card.querySelector('.cust-profile').value.trim();
          const agenda = card.querySelector('.cust-agenda').value.trim();
          const tone = card.querySelector('.cust-tone').value;
          const saveCheckbox = card.querySelector('.cust-save-checkbox').checked;

          const prio1 = card.querySelector('.cust-prio-1').value.trim() || 'Harmonie';
          const prio2 = card.querySelector('.cust-prio-2').value.trim() || 'Wohlstand';
          const prio3 = card.querySelector('.cust-prio-3').value.trim() || 'Freiheit';

          if (!name || !profile || !agenda) {
            throw new Error(`Teilnehmer ${i + 1}: Bitte Name, Profil und Agenda ausfüllen.`);
          }

          // Handle file upload if present
          let docFileName = '';
          const fileInput = card.querySelector('.cust-file-input');
          if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            // If offline, file upload will fail in browser, so warn if running file:// protocol
            if (window.location.protocol === 'file:') {
              throw new Error('Dateiuploads benötigen den laufenden server.py Server. (Aktuell über file:// geöffnet).');
            }
            showToast(`Lade Dokument für ${name} hoch...`, 'info');
            docFileName = await uploadDocument(file);
          }

          agentObj = {
            name: name,
            age: age,
            profile: profile,
            politicalStance: [prio1, prio2, prio3],
            agenda: agenda,
            tone: tone,
            emoji: emoji,
            docFileName: docFileName
          };

          // Save custom persona to localStorage if selected
          if (saveCheckbox) {
            const alreadyExists = customPersonasToSave.some(p => p.name.toLowerCase() === name.toLowerCase());
            if (!alreadyExists) {
              customPersonasToSave.push(agentObj);
              localStorage.setItem('customPersonas', JSON.stringify(customPersonasToSave));
            }
          }
        } else if (selection === 'user_me') {
          agentObj = {
            name: "Ich",
            emoji: "👤",
            isUser: true,
            age: "30",
            profile: "Ich selbst, der sich aktiv in die Diskussion einbringt.",
            politicalStance: ["Meine Meinung", "Freiheit", "Hinterfragen"],
            agenda: "Meine Meinung einbringen",
            tone: "neutral",
            docFileName: ""
          };
        } else if (selection.startsWith('custom_')) {
          // Load from localStorage
          const savedIdx = parseInt(selection.split('_')[1]);
          const savedPersonas = JSON.parse(localStorage.getItem('customPersonas') || '[]');
          agentObj = savedPersonas[savedIdx];
        } else {
          // Load preset
          agentObj = PRESET_PERSONAS[selection];
        }

        agents.push(agentObj);
      }

      // Save current session agents for bubble alignment later
      currentSessionAgents = agents;

      // Clear viewport and switch view
      discussionMessages.innerHTML = '';
      chatTopicDisplay.textContent = topic;

      discussionSetup.classList.add('hidden');
      discussionChat.classList.remove('hidden');

      // Request discussion start from python server
      const baseUrl = getApiBaseUrl();

      const startResponse = await fetch(`${baseUrl}/api/discussion/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          topic: topic,
          agents: agents
        })
      });

      if (!startResponse.ok) {
        const err = await startResponse.json();
        throw new Error(err.message || 'Diskussionsstart fehlgeschlagen.');
      }

      const startData = await startResponse.json();
      activeDiscussionSessionId = startData.session_id;
      discussionIsPaused = false;
      discussionMessageBuffer = [];
      currentDiscussionTurns = [];

      chatUserInputPanel.classList.add('hidden');
      chatUserInputField.value = '';

      btnChatToggle.innerHTML = '<i class="fa-solid fa-pause"></i><span>Pause</span>';

      // Start EventSource stream for turns
      discussionEventSource = new EventSource(`${baseUrl}/api/discussion/stream?id=${activeDiscussionSessionId}`);

      // Typing indicator event
      discussionEventSource.addEventListener('typing', (event) => {
        if (discussionIsPaused) return;

        try {
          const parsed = JSON.parse(event.data);
          typingAvatarIcon.textContent = parsed.emoji;
          typingPersonaName.textContent = parsed.sender;
          chatTypingIndicator.classList.remove('hidden');

          // Auto scroll to typing indicator
          discussionMessages.scrollTop = discussionMessages.scrollHeight;
        } catch (e) {
          console.error(e);
        }
      });

      // User input required event
      discussionEventSource.addEventListener('user_input_required', (event) => {
        chatTypingIndicator.classList.add('hidden'); // Hide typing

        try {
          const parsed = JSON.parse(event.data);
          // Show user input panel
          chatUserInputPanel.classList.remove('hidden');
          chatUserInputField.value = '';
          chatUserInputField.disabled = false;
          btnChatSendUserInput.disabled = false;
          chatUserInputField.focus();

          // Auto scroll to input panel
          discussionMessages.scrollTop = discussionMessages.scrollHeight;
        } catch (e) {
          console.error(e);
        }
      });

      // Message event
      discussionEventSource.onmessage = (event) => {
        chatTypingIndicator.classList.add('hidden'); // Hide typing
        chatUserInputPanel.classList.add('hidden');

        try {
          const turn = JSON.parse(event.data);
          currentDiscussionTurns.push(turn); // Track all turns

          if (discussionIsPaused) {
            // Buffer message
            discussionMessageBuffer.push(turn);
          } else {
            renderChatBubble(turn);
          }
        } catch (e) {
          console.error(e);
        }
      };

      // Completed normally
      discussionEventSource.addEventListener('exit', () => {
        chatTypingIndicator.classList.add('hidden');

        const endDivider = document.createElement('div');
        endDivider.style.textAlign = 'center';
        endDivider.style.color = 'var(--color-text-muted)';
        endDivider.style.margin = '1.5rem 0';
        endDivider.style.fontSize = '0.85rem';
        endDivider.innerHTML = `----------------- <i class="fa-solid fa-flag-checkered" style="margin: 0 0.5rem;"></i> Debatte abgeschlossen -----------------`;

        discussionMessages.appendChild(endDivider);
        discussionMessages.scrollTop = discussionMessages.scrollHeight;

        if (discussionEventSource) {
          discussionEventSource.close();
          discussionEventSource = null;
        }
        activeDiscussionSessionId = null;
        showToast('Debatte abgeschlossen.', 'info');
      });

      // Connect error
      discussionEventSource.onerror = () => {
        if (activeDiscussionSessionId) {
          chatTypingIndicator.classList.add('hidden');
          console.warn("[Terminal] AI SSE getrennt.");
          if (discussionEventSource) {
            discussionEventSource.close();
            discussionEventSource = null;
          }
        }
      };

    } catch (err) {
      console.error(err);
      showToast(err.message || 'Fehler beim Starten der Diskussion.', 'error');

      // Return to setup
      discussionChat.classList.add('hidden');
      discussionSetup.classList.remove('hidden');
    }
  });

  // Render chat bubble dynamically
  function renderChatBubble(turn) {
    const bubbleRow = document.createElement('div');

    // Find index of agent in active session list to determine alignment (1 & 3 Left, 2 & 4 Right)
    const agentIdx = currentSessionAgents.findIndex(a => a.name === turn.sender);
    const alignment = (agentIdx % 2 === 0) ? 'left' : 'right';

    bubbleRow.className = `chat-bubble-row ${alignment}`;

    // Build thought block if available (premium collapsible details)
    let thoughtHtml = '';
    if (turn.thought) {
      thoughtHtml = `
        <details class="chat-thought-details" style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--color-text-muted); cursor: pointer; display: block; width: 100%;">
          <summary style="outline: none; user-select: none; font-weight: 500; font-family: var(--font-body); display: flex; align-items: center; gap: 0.35rem;"><i class="fa-solid fa-brain" style="color: var(--color-primary);"></i>Denkprozess anzeigen</summary>
          <div style="background: rgba(255, 255, 255, 0.02); border-left: 2px solid var(--color-primary); padding: 0.6rem 0.8rem; margin-top: 0.35rem; border-radius: var(--border-radius-sm); white-space: pre-wrap; font-family: var(--font-body); line-height: 1.5; color: var(--color-text-secondary); text-align: left;">${turn.thought}</div>
        </details>
      `;
    }

    bubbleRow.innerHTML = `
      <div class="chat-avatar">${turn.emoji}</div>
      <div class="chat-bubble-content" style="max-width: 80%;">
        <span class="chat-sender-name">${turn.sender}</span>
        <div class="chat-bubble" style="display: flex; flex-direction: column;">
          <div>${turn.text}</div>
          ${thoughtHtml}
        </div>
      </div>
    `;

    discussionMessages.appendChild(bubbleRow);
    discussionMessages.scrollTop = discussionMessages.scrollHeight;
  }

  // Toggle Pause/Resume
  btnChatToggle.addEventListener('click', () => {
    if (!activeDiscussionSessionId) return;

    discussionIsPaused = !discussionIsPaused;

    if (discussionIsPaused) {
      btnChatToggle.innerHTML = '<i class="fa-solid fa-play"></i><span>Fortsetzen</span>';
      showToast('Debatte pausiert.', 'warning');
    } else {
      btnChatToggle.innerHTML = '<i class="fa-solid fa-pause"></i><span>Pause</span>';
      showToast('Debatte fortgesetzt.', 'success');

      // Flush buffered messages
      discussionMessageBuffer.forEach(turn => renderChatBubble(turn));
      discussionMessageBuffer = [];
      chatTypingIndicator.classList.add('hidden');
    }
  });

  // End discussion and close session
  function closeDiscussionSession() {
    if (activeDiscussionSessionId) {
      const baseUrl = getApiBaseUrl();

      fetch(`${baseUrl}/api/discussion/close`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          id: activeDiscussionSessionId
        })
      });

      activeDiscussionSessionId = null;
    }

    if (discussionEventSource) {
      discussionEventSource.close();
      discussionEventSource = null;
    }

    discussionChat.classList.add('hidden');
    discussionSetup.classList.remove('hidden');

    chatTypingIndicator.classList.add('hidden');
    chatUserInputPanel.classList.add('hidden');
    chatUserInputField.value = '';
    discussionMessageBuffer = [];
    currentDiscussionTurns = [];
    showToast('Debatte beendet.', 'info');
  }

  // Triggered when clicking "Beenden" (Stop) button
  function handleStopDiscussion() {
    if (currentDiscussionTurns.length > 0) {
      // Pause discussion stream to avoid interface movement while confirming
      if (!discussionIsPaused) {
        discussionIsPaused = true;
        btnChatToggle.innerHTML = '<i class="fa-solid fa-play"></i><span>Fortsetzen</span>';
      }
      // Show save confirmation modal
      saveDiscussionModal.classList.remove('hidden');
    } else {
      closeDiscussionSession();
    }
  }

  // Generate txt content and download it
  function downloadDiscussionTranscript() {
    if (currentDiscussionTurns.length === 0) return;

    let txt = `==================================================\n`;
    txt += `KI-DEBATTE - GESPRÄCHSPROTOKOLL\n`;
    txt += `Thema: ${discTopic.value || 'Unbekanntes Thema'}\n`;
    txt += `Datum: ${new Date().toLocaleString('de-CH')}\n`;
    txt += `Teilnehmer:\n`;
    currentSessionAgents.forEach(a => {
      txt += `  - ${a.name} (Alter: ${a.age}, Profil: ${a.profile})\n`;
    });
    txt += `==================================================\n\n`;

    currentDiscussionTurns.forEach(turn => {
      if (turn.sender === 'System-Protokollant') {
        txt += `\n[${turn.sender}]:\n${turn.text}\n\n`;
      } else {
        txt += `[${turn.sender}]: ${turn.text}\n`;
      }
    });

    const blob = new Blob([txt], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;

    const safeTopic = (discTopic.value || 'debatte')
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9]/g, '_')
      .substring(0, 30);
    const timestamp = new Date().toISOString().slice(0, 10);
    a.download = `ki_debatte_${safeTopic}_${timestamp}.txt`;

    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // Submit user keyboard contribution
  async function submitUserInput() {
    const text = chatUserInputField.value.trim();
    if (!text) return;
    if (!activeDiscussionSessionId) return;

    chatUserInputField.disabled = true;
    btnChatSendUserInput.disabled = true;

    try {
      const baseUrl = getApiBaseUrl();
      const response = await fetch(`${baseUrl}/api/discussion/input`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          id: activeDiscussionSessionId,
          text: text
        })
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.message || 'Fehler beim Senden.');
      }

      chatUserInputPanel.classList.add('hidden');
      chatUserInputField.value = '';
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Senden fehlgeschlagen.', 'error');
      chatUserInputField.disabled = false;
      btnChatSendUserInput.disabled = false;
    }
  }

  btnChatSendUserInput.addEventListener('click', submitUserInput);
  chatUserInputField.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      submitUserInput();
    }
  });

  // Modal Button Handlers
  btnSaveDiscYes.addEventListener('click', () => {
    saveDiscussionModal.classList.add('hidden');
    downloadDiscussionTranscript();
    closeDiscussionSession();
  });

  btnSaveDiscNo.addEventListener('click', () => {
    saveDiscussionModal.classList.add('hidden');
    closeDiscussionSession();
  });

  btnChatClose.addEventListener('click', handleStopDiscussion);


  // --- Initial Setup on Page Load ---
  updateHomeAuthStatus();

});


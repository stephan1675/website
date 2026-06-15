/* Core JS Logic for Premium Portal */

document.addEventListener('DOMContentLoaded', () => {
  
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
    const baseUrl = window.location.protocol === 'file:' ? 'http://localhost:8000' : '';
    
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
    
    const baseUrl = window.location.protocol === 'file:' ? 'http://localhost:8000' : '';

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
      const baseUrl = window.location.protocol === 'file:' ? 'http://localhost:8000' : '';
      
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

  // --- Initial Setup on Page Load ---
  updateHomeAuthStatus();
  
});

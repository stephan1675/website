import { runGame, getApiBaseUrl } from './api.js';
import { initDiscussion } from './discussion.js';
import { initCommandHub } from './command_hub.js';
import { initSimulators } from './simulators.js';

// --- DOM Element References ---
const homeView = document.getElementById('home-view');
const projectsView = document.getElementById('projects-view');
const authSection = document.getElementById('auth-section');
const dashboardSection = document.getElementById('dashboard-section');

const loginView = document.getElementById('login-view');
const registerView = document.getElementById('register-view');
const forgotPasswordView = document.getElementById('forgot-password-view');
const forgotPasswordForm = document.getElementById('forgot-password-form');
const forgotEmailInput = document.getElementById('forgot-email');

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
const goToForgotBtn = document.getElementById('go-to-forgot');
const forgotToLoginBtn = document.getElementById('forgot-to-login');

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

// State
let currentActiveView = homeView;

// --- Initialize Storage ---
if (!localStorage.getItem('users')) {
  localStorage.setItem('users', JSON.stringify([]));
}

// --- Toast Notification System ---
export function showToast(message, type = 'success') {
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

// --- Router / View Switcher ---
export function navigateToView(targetView) {
  if (currentActiveView === targetView) return;

  currentActiveView.classList.add('fade-out');

  setTimeout(() => {
    currentActiveView.classList.add('hidden');
    currentActiveView.classList.remove('fade-out');

    targetView.classList.remove('hidden');
    targetView.classList.add('fade-in');

    currentActiveView = targetView;

    setTimeout(() => {
      targetView.classList.remove('fade-in');
    }, 400);
  }, 300);
}

// --- Home View Header - Authentication Status ---
export async function updateHomeAuthStatus() {
  const token = localStorage.getItem('sessionToken');
  homeAuthStatus.innerHTML = '';

  if (token) {
    try {
      const baseUrl = getApiBaseUrl();
      const res = await fetch(`${baseUrl}/api/auth/user-profile`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const user = await res.json();
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

        document.getElementById('home-to-dash-btn').addEventListener('click', () => {
          showDashboard(user);
        });

        document.getElementById('home-logout-btn').addEventListener('click', () => {
          performLogout();
        });
        return;
      } else {
        localStorage.removeItem('sessionToken');
        localStorage.removeItem('currentUserSession');
      }
    } catch (err) {
      console.warn("[Auth] Failed to update home auth status from server:", err);
    }
  }

  homeAuthStatus.innerHTML = `
    <button id="home-login-btn" class="btn btn-primary" style="padding: 0.55rem 1.1rem; font-size: 0.85rem; width: auto;">
      <i class="fa-solid fa-right-to-bracket"></i>
      <span>Mitgliederbereich</span>
    </button>
  `;

  document.getElementById('home-login-btn').addEventListener('click', () => {
    loginView.classList.remove('hidden');
    registerView.classList.add('hidden');
    forgotPasswordView.classList.add('hidden');
    navigateToView(authSection);
  });
}

// --- Show secure Dashboard ---
function showDashboard(user) {
  displayUsername.textContent = user.username;
  displayEmail.textContent = user.email;
  userAvatar.textContent = user.username.charAt(0).toUpperCase();

  statCreated.textContent = user.createdAt;
  statLogins.textContent = user.loginCount;

  quickNotes.value = user.notes || '';

  navigateToView(dashboardSection);
}

// --- Logout Logic ---
function performLogout() {
  localStorage.removeItem('sessionToken');
  localStorage.removeItem('currentUserSession');
  showToast('Erfolgreich abgemeldet.', 'info');
  updateHomeAuthStatus();
  navigateToView(homeView);
}

// --- Toggle Login / Register Sub-Views ---
function switchAuthSubView(showSub, hideSub) {
  loginView.classList.add('fade-out');
  registerView.classList.add('fade-out');
  forgotPasswordView.classList.add('fade-out');

  setTimeout(() => {
    hideSub.classList.add('hidden');
    showSub.classList.remove('hidden');
    loginView.classList.remove('fade-out');
    registerView.classList.remove('fade-out');
    forgotPasswordView.classList.remove('fade-out');
  }, 200);
}

// --- Mock hash ---
function mockHash(str) {
  return btoa(str);
}

// --- Setup Listeners ---
document.addEventListener('DOMContentLoaded', () => {
  // Bind view switch events
  btnViewProjects.addEventListener('click', () => navigateToView(projectsView));
  btnProjectsBack.addEventListener('click', () => navigateToView(homeView));
  btnAuthBack.addEventListener('click', () => navigateToView(homeView));
  btnDashBack.addEventListener('click', () => navigateToView(homeView));

  goToRegisterBtn.addEventListener('click', (e) => {
    e.preventDefault();
    switchAuthSubView(registerView, loginView);
  });

  goToLoginBtn.addEventListener('click', (e) => {
    e.preventDefault();
    switchAuthSubView(loginView, registerView);
  });

  logoutBtn.addEventListener('click', performLogout);

  // Password visibility
  document.querySelectorAll('.password-toggle').forEach(button => {
    button.addEventListener('click', (e) => {
      e.preventDefault();
      const input = button.parentElement.querySelector('input');
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

  // Password strength
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

  // Register Form
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

    const baseUrl = getApiBaseUrl();
    const btnSubmit = registerForm.querySelector('button[type="submit"]');
    const origContent = btnSubmit.innerHTML;
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<span>Erstellt...</span> <i class="fa-solid fa-spinner fa-spin"></i>';

    fetch(`${baseUrl}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, email, password })
    })
      .then(res => res.json().then(data => {
        if (!res.ok) throw new Error(data.message || 'Registrierung fehlgeschlagen.');
        return data;
      }))
      .then(data => {
        showToast(data.message || 'Konto erfolgreich erstellt! Eine Willkommens-E-Mail wurde gesendet.', 'success');
        registerForm.reset();
        
        strengthBar.className = 'strength-bar';
        strengthText.textContent = 'Passwortstärke';
        strengthText.style.color = 'var(--color-text-muted)';
        
        switchAuthSubView(loginView, registerView);
      })
      .catch(err => {
        showToast(err.message, 'error');
      })
      .finally(() => {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = origContent;
      });
  });

  // Login Form
  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const email = loginEmail.value.trim().toLowerCase();
    const password = loginPassword.value;

    const baseUrl = getApiBaseUrl();
    const btnSubmit = loginForm.querySelector('button[type="submit"]');
    const origContent = btnSubmit.innerHTML;
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<span>Anmelden...</span> <i class="fa-solid fa-spinner fa-spin"></i>';

    fetch(`${baseUrl}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    })
      .then(res => res.json().then(data => {
        if (!res.ok) throw new Error(data.message || 'Login fehlgeschlagen.');
        return data;
      }))
      .then(data => {
        localStorage.setItem('sessionToken', data.sessionToken);
        localStorage.setItem('currentUserSession', email);
        showToast(data.message, 'success');
        loginForm.reset();
        
        updateHomeAuthStatus();
        showDashboard(data.user);
      })
      .catch(err => {
        showToast(err.message, 'error');
      })
      .finally(() => {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = origContent;
      });
  });

  // Save notes
  saveNoteBtn.addEventListener('click', () => {
    const token = localStorage.getItem('sessionToken');
    if (!token) return;

    const notes = quickNotes.value;
    const baseUrl = getApiBaseUrl();
    
    saveNoteBtn.disabled = true;
    const origText = saveNoteBtn.textContent;
    saveNoteBtn.textContent = 'Speichert...';

    fetch(`${baseUrl}/api/auth/save-notes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ notes })
    })
      .then(res => res.json().then(data => {
        if (!res.ok) throw new Error(data.message || 'Speichern fehlgeschlagen.');
        return data;
      }))
      .then(data => {
        showToast(data.message, 'success');
      })
      .catch(err => {
        showToast(err.message, 'error');
      })
      .finally(() => {
        saveNoteBtn.disabled = false;
        saveNoteBtn.textContent = origText;
      });
  });

  // Forgot Password Form Submit
  forgotPasswordForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const email = forgotEmailInput.value.trim().toLowerCase();
    const baseUrl = getApiBaseUrl();
    const btnSubmit = forgotPasswordForm.querySelector('button[type="submit"]');
    const origContent = btnSubmit.innerHTML;
    
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<span>Sende...</span> <i class="fa-solid fa-spinner fa-spin"></i>';

    fetch(`${baseUrl}/api/auth/forgot-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email })
    })
      .then(res => res.json().then(data => {
        if (!res.ok) throw new Error(data.message || 'Fehler beim Senden.');
        return data;
      }))
      .then(data => {
        showToast(data.message, 'success');
        forgotPasswordForm.reset();
        switchAuthSubView(loginView, forgotPasswordView);
      })
      .catch(err => {
        showToast(err.message, 'error');
      })
      .finally(() => {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = origContent;
      });
  });

  // Forgot Password navigation bindings
  goToForgotBtn.addEventListener('click', (e) => {
    e.preventDefault();
    switchAuthSubView(forgotPasswordView, loginView);
  });

  forgotToLoginBtn.addEventListener('click', (e) => {
    e.preventDefault();
    switchAuthSubView(loginView, forgotPasswordView);
  });

  // Game Click listeners
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

  btnRunCpp.addEventListener('click', () => {
    const baseUrl = getApiBaseUrl();

    terminalOutput.textContent = "Verbindung wird hergestellt...\n";
    terminalModal.classList.remove('hidden');
    terminalInputField.value = '';
    terminalInputField.focus();

    showToast('Starte C++ Terminal-Session...', 'info');

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

        terminalEventSource = new EventSource(`${baseUrl}/api/terminal/stream?id=${activeTerminalSessionId}`);

        terminalEventSource.onmessage = (event) => {
          try {
            const parsed = JSON.parse(event.data);
            if (parsed.text) {
              let text = parsed.text;

              if (text.includes('\x1b[2J') || text.includes('\x1b[H') ||
                text.includes('\u001b[2J') || text.includes('\u001b[H') ||
                text.includes('\x1b[3J')) {
                terminalOutput.textContent = '';
              }

              text = text.replace(/\x1b\[[0-9;]*[a-zA-Z]/g, '');
              text = text.replace(/\u001b\[[0-9;]*[a-zA-Z]/g, '');

              terminalOutput.textContent += text;
              terminalOutput.scrollTop = terminalOutput.scrollHeight;
            }
          } catch (e) {
            console.error("[Terminal] SSE Parsing-Fehler:", e);
          }
        };

        terminalEventSource.addEventListener('exit', () => {
          terminalOutput.textContent += "\n\n---------------------------------------\n[Spielprozess beendet. Drücke X zum Schließen]";
          terminalOutput.scrollTop = terminalOutput.scrollHeight;
          if (terminalEventSource) terminalEventSource.close();
          activeTerminalSessionId = null;
          showToast("Spiel erfolgreich beendet.", "info");
        });

        terminalEventSource.onerror = (err) => {
          console.error("[Terminal] SSE Fehler:", err);
          if (activeTerminalSessionId) {
            terminalOutput.textContent += "\n\n[Verbindung verloren]";
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

  function sendTerminalInput() {
    if (!activeTerminalSessionId) return;

    const text = terminalInputField.value;
    terminalInputField.value = '';

    terminalOutput.textContent += text + "\n";
    terminalOutput.scrollTop = terminalOutput.scrollHeight;

    const baseUrl = getApiBaseUrl();

    fetch(`${baseUrl}/api/terminal/input`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ id: activeTerminalSessionId, input: text })
    })
      .catch(err => {
        console.error("[Terminal] Fehler:", err);
        terminalOutput.textContent += `\n[Systemfehler: Senden fehlgeschlagen]\n`;
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
      });
  }

  terminalInputField.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendTerminalInput();
    }
  });

  btnSendInput.addEventListener('click', (e) => {
    e.preventDefault();
    sendTerminalInput();
    terminalInputField.focus();
  });

  function closeTerminalSession() {
    if (activeTerminalSessionId) {
      const baseUrl = getApiBaseUrl();
      fetch(`${baseUrl}/api/terminal/close`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: activeTerminalSessionId })
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

  // Prompt copy button functionality
  const btnCopyPrompt = document.getElementById('btn-copy-ai-prompt');
  const promptTextEl = document.getElementById('ai-seo-prompt-text');
  if (btnCopyPrompt && promptTextEl) {
    btnCopyPrompt.addEventListener('click', (e) => {
      e.preventDefault();
      const textToCopy = promptTextEl.innerText || promptTextEl.textContent;
      navigator.clipboard.writeText(textToCopy)
        .then(() => {
          showToast('Prompt in Zwischenablage kopiert!', 'success');
        })
        .catch(err => {
          console.error('Fehler beim Kopieren:', err);
          showToast('Kopieren fehlgeschlagen.', 'error');
        });
    });
  }

  // Initialize AI discussion module
  initDiscussion();

  // Initialize Command Hub planner module
  initCommandHub();

  // Initialize Mechatronics Simulators
  initSimulators();

  // Initial update of auth status
  updateHomeAuthStatus();
});

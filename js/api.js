import { showToast } from './main.js';

// --- Deployment Backend Configuration ---
const BACKEND_URL = 'https://website-qcox.onrender.com'; // Render backend URL

export function getApiBaseUrl() {
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

// --- Helper: Read file as Base64 Promise ---
export function readFileAsBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
    reader.readAsDataURL(file);
  });
}

// --- Game Launching Handler ---
export function runGame(endpoint) {
  const targetUrl = window.location.protocol === 'file:' ? `http://localhost:8000${endpoint}` : endpoint;

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

// --- Upload Text Document for custom persona ---
export async function uploadDocument(file) {
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

// --- Upload clone audio to backend and return voice_id ---
export async function cloneVoice(name, audioBlob, filename) {
  const baseUrl = getApiBaseUrl();
  const base64Data = await readFileAsBase64(audioBlob);

  const response = await fetch(`${baseUrl}/api/voice/clone`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: name,
      filename: filename,
      content: base64Data
    })
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.message || 'Stimmenklonierung fehlgeschlagen');
  }

  const data = await response.json();
  return data.voice_id;
}

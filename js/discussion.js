import { getApiBaseUrl, uploadDocument, cloneVoice } from './api.js';
import { showToast, navigateToView } from './main.js';

// --- Preset Personas ---
const PRESET_PERSONAS = {
  "trump": {
    name: "Donald Trump",
    age: "80",
    profile: "Former US President, real estate billionaire.",
    politicalStance: [
      "Make America Great Again and America First protectionism.",
      "Border security and tough immigration policy.",
      "Deregulation of the economy and tax cuts."
    ],
    agenda: "Make all other speakers look ridiculous and show that only I know the truth.",
    tone: "arrogant, direct, polemical, colloquial",
    emoji: "🇺🇸"
  },
  "musk": {
    name: "Elon Musk",
    age: "54",
    profile: "Tech billionaire, founder of Tesla, SpaceX, and Neuralink.",
    politicalStance: [
      "Securing the human future by colonizing Mars.",
      "First Principles thinking and maximum efficiency.",
      "Protection of free speech on X."
    ],
    agenda: "Present technological progress and the Mars mission as the only logical solution.",
    tone: "visionary, slightly erratic, tech-enthusiastic, energetic",
    emoji: "🚀"
  },
  "xi": {
    name: "Xi Jinping",
    age: "72",
    profile: "General Secretary of the CP of China and State President.",
    politicalStance: [
      "Realization of the Chinese Dream and national rejuvenation.",
      "Maintaining social stability and collective discipline.",
      "Creating a multipolar world order under China's leadership."
    ],
    agenda: "Emphasize the stability and superiority of the Chinese development model.",
    tone: "extremely diplomatic, strict, formal, deliberate",
    emoji: "🐼"
  },
  "schweiz": {
    name: "Schweizer Bundespräsident",
    age: "60",
    profile: "Member of the seven-member Federal Council of Switzerland.",
    politicalStance: [
      "Maintaining the concordance system and consensus finding across all parties.",
      "Preserving Switzerland's permanent armed neutrality.",
      "Protection of direct democracy and federalism."
    ],
    agenda: "Find a neutral compromise and call on all participants to exercise objective moderation.",
    tone: "extremely polite, consensus-oriented, objective, Swiss-style",
    emoji: "🇨🇭"
  }
};

// State
let activeDiscussionSessionId = null;
let discussionEventSource = null;
let discussionIsPaused = false;
let discussionMessageBuffer = [];
let currentDiscussionTurns = [];
let currentSessionAgents = [];
let agentVoiceClones = {};
let recordedAudioBlobs = [];

// TTS State
let ttsAudioQueue = [];
let ttsIsPlaying = false;
let currentTtsAudio = null;

// Helper to map agent to voice preset
function getRecommendedVoice(personaKey) {
  switch (personaKey) {
    case 'trump': return 'onyx';
    case 'musk': return 'fable';
    case 'xi': return 'echo';
    case 'schweiz': return 'sage';
    case 'user_me': return 'ash';
    default: return 'fable';
  }
}

// Initialise AI Discussion Elements and Event Listeners
export function initDiscussion() {
  const homeView = document.getElementById('home-view');
  const aiDiscussionView = document.getElementById('ai-discussion-view');
  const btnGoToDiscussion = document.getElementById('btn-go-to-discussion');
  const btnDiscussionBack = document.getElementById('btn-discussion-back');

  const discussionSetup = document.getElementById('discussion-setup');
  const discussionSetupForm = document.getElementById('discussion-setup-form');
  const discTopic = document.getElementById('disc-topic');
  const discAgentCount = document.getElementById('disc-agent-count');
  const discAgentsConfigs = document.getElementById('disc-agents-configs');
  const discEnableTts = document.getElementById('disc-enable-tts');

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

  // Bind route navigations
  btnGoToDiscussion.addEventListener('click', () => {
    navigateToView(aiDiscussionView);
    renderAgentsSetup();
  });
  btnDiscussionBack.addEventListener('click', () => navigateToView(homeView));

  // Change count handler
  discAgentCount.addEventListener('change', renderAgentsSetup);

  discEnableTts.addEventListener('change', () => {
    const containers = discAgentsConfigs.querySelectorAll('.select-voice-container');
    containers.forEach(container => {
      if (discEnableTts.checked) {
        container.classList.remove('hidden');
      } else {
        container.classList.add('hidden');
      }
    });
  });

  // Render agents configuration forms dynamically
  function renderAgentsSetup() {
    discAgentsConfigs.innerHTML = '';
    const count = parseInt(discAgentCount.value);
    const customPersonas = JSON.parse(localStorage.getItem('customPersonas') || '[]');

    for (let i = 1; i <= count; i++) {
      const card = document.createElement('div');
      card.className = 'agent-config-card';

      let customOptions = '';
      customPersonas.forEach((p, idx) => {
        customOptions += `<option value="custom_${idx}">Eigene: ${p.name}</option>`;
      });

      const ttsEnabled = discEnableTts.checked;
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

        <div class="form-group select-voice-container ${ttsEnabled ? '' : 'hidden'}" style="margin-bottom: 0.75rem;">
          <label>Stimme (Text-to-Speech)</label>
          <select class="form-control select-agent-voice" style="padding-left: 1.25rem;">
            <option value="fable">Fable (Männlich - Lebhaft) [Standard]</option>
            <option value="onyx">Onyx (Männlich - Tief)</option>
            <option value="sage">Sage (Männlich - Professionell)</option>
            <option value="echo">Echo (Männlich - Ernst)</option>
            <option value="ash">Ash (Männlich - Neutral)</option>
            <option value="shimmer">Shimmer (Weiblich - Freundlich)</option>
            <option value="coral">Coral (Weiblich - Warm)</option>
            <option value="alloy">Alloy (Weiblich - Neutral)</option>
            <option value="elevenlabs_clone" style="color: var(--color-primary); font-weight: bold;">🎙️ Eigene Stimme klonen (ElevenLabs)</option>
            <option value="elevenlabs_W1m7sYaOoCpc4hBK5WXK" style="color: var(--color-warning); font-weight: bold;">👹 Shrek / Oger (ElevenLabs)</option>
            <option value="elevenlabs_custom_id" style="color: var(--color-secondary); font-weight: bold;">🔑 Vorhandene ElevenLabs Voice-ID verwenden</option>
          </select>
        </div>

        <!-- ElevenLabs Voice Cloning Container (hidden by default) -->
        <div class="voice-clone-container hidden" id="voice-clone-container-agent-${i}">
          <div class="voice-clone-title"><i class="fa-solid fa-microphone"></i> Stimme aufnehmen oder hochladen</div>
          <div class="recorder-controls">
            <button type="button" class="record-btn" id="record-btn-agent-${i}">
              <i class="fa-solid fa-microphone"></i>
              <span>Aufnahme starten</span>
            </button>
            <button type="button" class="clone-preview-btn" id="preview-btn-agent-${i}" disabled>
              <i class="fa-solid fa-play"></i>
              <span>Anhören</span>
            </button>
            <div class="recording-indicator hidden" id="rec-indicator-agent-${i}">
              <div class="recording-dot"></div>
              <span id="rec-timer-agent-${i}">0:00</span>
            </div>
          </div>
          <div class="voice-clone-divider">ODER</div>
          <div class="file-upload-wrapper" style="margin-top: 0.25rem;">
            <div class="file-upload-btn">
              <i class="fa-solid fa-file-audio"></i>
              <span>Audio-Datei hochladen (.wav, .mp3)</span>
            </div>
            <input type="file" class="clone-file-input" id="file-input-agent-${i}" accept=".wav,.mp3">
          </div>
          <span class="file-upload-name" id="clone-file-name-agent-${i}">Kein Sample verknüpft</span>
        </div>

        <!-- ElevenLabs Manual Voice ID Container (hidden by default) -->
        <div class="voice-clone-container hidden" id="voice-id-container-agent-${i}">
          <div class="voice-clone-title"><i class="fa-solid fa-key"></i> ElevenLabs Voice-ID eingeben</div>
          <div class="form-group" style="margin-bottom: 0.25rem;">
            <input type="text" class="form-control clone-voice-id-input" id="voice-id-input-agent-${i}" placeholder="z.B. 21m00Tcm4TlvDq8ikWAM" style="padding-left: 1rem;">
          </div>
          <span class="file-upload-name" style="text-align: left; margin-top: 0.25rem;">Kopiere die Voice ID aus deinem ElevenLabs Dashboard (VoiceLab).</span>
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

      const dropdown = card.querySelector('.select-agent-persona');
      const customForm = card.querySelector('.custom-persona-form');
      const fileInput = card.querySelector('.cust-file-input');
      const fileNameDisplay = card.querySelector(`.id-file-name-display-${i}`);
      const voiceSelect = card.querySelector('.select-agent-voice');

      voiceSelect.value = getRecommendedVoice(dropdown.value);

      const cloneContainer = card.querySelector(`#voice-clone-container-agent-${i}`);
      const voiceIdContainer = card.querySelector(`#voice-id-container-agent-${i}`);
      const recordBtn = card.querySelector(`#record-btn-agent-${i}`);
      const previewBtn = card.querySelector(`#preview-btn-agent-${i}`);
      const recIndicator = card.querySelector(`#rec-indicator-agent-${i}`);
      const recTimer = card.querySelector(`#rec-timer-agent-${i}`);
      const cloneFileInput = card.querySelector(`#file-input-agent-${i}`);
      const cloneFileName = card.querySelector(`#clone-file-name-agent-${i}`);

      let mediaRecorder = null;
      let recordedChunks = [];
      let recordInterval = null;
      let recordSeconds = 0;

      function updateVoiceCloneVisibility() {
        cloneContainer.classList.add('hidden');
        voiceIdContainer.classList.add('hidden');

        if (discEnableTts.checked) {
          if (voiceSelect.value === 'elevenlabs_clone') {
            cloneContainer.classList.remove('hidden');
          } else if (voiceSelect.value === 'elevenlabs_custom_id') {
            voiceIdContainer.classList.remove('hidden');
          }
        }
      }

      voiceSelect.addEventListener('change', updateVoiceCloneVisibility);
      discEnableTts.addEventListener('change', updateVoiceCloneVisibility);

      dropdown.addEventListener('change', () => {
        if (dropdown.value === 'new_custom') {
          customForm.classList.remove('hidden');
        } else {
          customForm.classList.add('hidden');
        }
        voiceSelect.value = getRecommendedVoice(dropdown.value);
        updateVoiceCloneVisibility();
      });

      fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
          fileNameDisplay.textContent = `Ausgewählt: ${fileInput.files[0].name}`;
        } else {
          fileNameDisplay.textContent = 'Kein Dokument verknüpft';
        }
      });

      // Microphone Recording Handler
      recordBtn.addEventListener('click', async () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
          mediaRecorder.stop();
          recordBtn.innerHTML = '<i class="fa-solid fa-microphone"></i><span>Aufnahme starten</span>';
          recordBtn.classList.remove('recording');
          recIndicator.classList.add('hidden');
          clearInterval(recordInterval);
          return;
        }

        try {
          recordedChunks = [];
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          
          let options = { mimeType: 'audio/webm' };
          if (!MediaRecorder.isTypeSupported('audio/webm')) {
            options = { mimeType: 'audio/ogg' };
          }
          
          mediaRecorder = new MediaRecorder(stream, options);
          mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) {
              recordedChunks.push(e.data);
            }
          };

          mediaRecorder.onstop = () => {
            stream.getTracks().forEach(track => track.stop());
            
            const mime = mediaRecorder.mimeType || 'audio/webm';
            const ext = mime.split(';')[0].split('/')[1] || 'webm';
            const blob = new Blob(recordedChunks, { type: mime });
            const filename = `recording_${i}_${Date.now()}.${ext}`;
            const previewUrl = URL.createObjectURL(blob);
            
            if (agentVoiceClones[i] && agentVoiceClones[i].previewUrl) {
              URL.revokeObjectURL(agentVoiceClones[i].previewUrl);
            }
            agentVoiceClones[i] = {
              blob: blob,
              filename: filename,
              previewUrl: previewUrl
            };
            
            cloneFileName.textContent = `Aufnahme bereit: ~${(blob.size / 1024).toFixed(1)} KB`;
            previewBtn.disabled = false;
          };

          mediaRecorder.start();
          recordBtn.innerHTML = '<i class="fa-solid fa-stop"></i><span>Aufnahme beenden</span>';
          recordBtn.classList.add('recording');
          recIndicator.classList.remove('hidden');
          
          recordSeconds = 0;
          recTimer.textContent = '0:00';
          clearInterval(recordInterval);
          recordInterval = setInterval(() => {
            recordSeconds++;
            const mins = Math.floor(recordSeconds / 60);
            const secs = recordSeconds % 60;
            recTimer.textContent = `${mins}:${secs < 10 ? '0' : ''}${secs}`;
          }, 1000);

        } catch (err) {
          console.error('[Recorder] Fehler:', err);
          showToast('Mikrofon-Zugriff verweigert oder nicht unterstützt.', 'error');
        }
      });

      // Preview audio
      previewBtn.addEventListener('click', () => {
        const cloneData = agentVoiceClones[i];
        if (cloneData && cloneData.previewUrl) {
          const previewAudio = new Audio(cloneData.previewUrl);
          previewAudio.play().catch(e => console.error('[Preview] Audio error:', e));
        }
      });

      // File upload cloning
      cloneFileInput.addEventListener('change', () => {
        if (cloneFileInput.files.length > 0) {
          const file = cloneFileInput.files[0];
          const previewUrl = URL.createObjectURL(file);
          
          if (agentVoiceClones[i] && agentVoiceClones[i].previewUrl) {
            URL.revokeObjectURL(agentVoiceClones[i].previewUrl);
          }
          agentVoiceClones[i] = {
            blob: file,
            filename: file.name,
            previewUrl: previewUrl
          };
          
          cloneFileName.textContent = `Datei bereit: ${file.name} (~${(file.size / 1024).toFixed(1)} KB)`;
          previewBtn.disabled = false;
        }
      });
    }
  }

  // Submit setup form
  discussionSetupForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const topic = discTopic.value.trim();
    const agentCount = parseInt(discAgentCount.value);
    const agentConfigs = discAgentsConfigs.querySelectorAll('.agent-config-card');

    showToast('Bereite KI-Teilnehmer vor...', 'info');

    const agents = [];
    const customPersonasToSave = JSON.parse(localStorage.getItem('customPersonas') || '[]');

    try {
      for (let i = 0; i < agentCount; i++) {
        const card = agentConfigs[i];
        const selector = card.querySelector('.select-agent-persona');
        const selection = selector.value;
        const voice = card.querySelector('.select-agent-voice').value;

        let agentObj = null;

        if (selection === 'new_custom') {
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

          let docFileName = '';
          const fileInput = card.querySelector('.cust-file-input');
          if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            if (window.location.protocol === 'file:') {
              throw new Error('Dateiuploads benötigen den laufenden server.py Server.');
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
            docFileName: docFileName,
            voice: voice
          };

          if (saveCheckbox) {
            const alreadyExists = customPersonasToSave.some(p => p.name.toLowerCase() === name.toLowerCase());
            if (!alreadyExists) {
              customPersonasToSave.push(agentObj);
              localStorage.setItem('customPersonas', JSON.stringify(customPersonasToSave));
            }
          }
        } else if (selection === 'user_me') {
          agentObj = {
            name: "Me",
            emoji: "👤",
            isUser: true,
            age: "30",
            profile: "Myself, actively participating in the discussion.",
            politicalStance: ["My opinion", "Freedom", "Questioning"],
            agenda: "Contributing my opinion",
            tone: "neutral",
            docFileName: "",
            voice: voice
          };
        } else if (selection.startsWith('custom_')) {
          const savedIdx = parseInt(selection.split('_')[1]);
          const savedPersonas = JSON.parse(localStorage.getItem('customPersonas') || '[]');
          agentObj = { ...savedPersonas[savedIdx], voice: voice };
        } else {
          agentObj = { ...PRESET_PERSONAS[selection], voice: voice };
        }

        if (voice === 'elevenlabs_clone') {
          const cloneData = agentVoiceClones[i + 1];
          if (!cloneData || !cloneData.blob) {
            throw new Error(`Teilnehmer ${i + 1}: Bitte Sprachaufnahme erstellen oder Audio-Datei hochladen.`);
          }
          if (window.location.protocol === 'file:') {
            throw new Error('Stimmenklonierung benötigt den laufenden server.py Server.');
          }
          
          const agentName = agentObj.name || `Teilnehmer ${i + 1}`;
          showToast(`Kloniere Stimme bei ElevenLabs für ${agentName}...`, 'info');
          const voiceId = await cloneVoice(agentName, cloneData.blob, cloneData.filename);
          agentObj.voice = 'elevenlabs_' + voiceId;
        } else if (voice === 'elevenlabs_custom_id') {
          const voiceIdInput = card.querySelector(`#voice-id-input-agent-${i + 1}`);
          const voiceId = voiceIdInput ? voiceIdInput.value.trim() : '';
          if (!voiceId) {
            throw new Error(`Teilnehmer ${i + 1}: Bitte gib eine ElevenLabs Voice-ID ein.`);
          }
          agentObj.voice = 'elevenlabs_' + voiceId;
        }

        agents.push(agentObj);
      }

      currentSessionAgents = agents;

      discussionMessages.innerHTML = '';
      chatTopicDisplay.textContent = topic;

      discussionSetup.classList.add('hidden');
      discussionChat.classList.remove('hidden');

      const baseUrl = getApiBaseUrl();

      const startResponse = await fetch(`${baseUrl}/api/discussion/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ topic: topic, agents: agents })
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
      recordedAudioBlobs = [];

      chatUserInputPanel.classList.add('hidden');
      chatUserInputField.value = '';

      btnChatToggle.innerHTML = '<i class="fa-solid fa-pause"></i><span>Pause</span>';

      discussionEventSource = new EventSource(`${baseUrl}/api/discussion/stream?id=${activeDiscussionSessionId}`);

      discussionEventSource.addEventListener('typing', (event) => {
        if (discussionIsPaused) return;

        try {
          const parsed = JSON.parse(event.data);
          typingAvatarIcon.textContent = parsed.emoji;
          typingPersonaName.textContent = parsed.sender;
          chatTypingIndicator.classList.remove('hidden');
          discussionMessages.scrollTop = discussionMessages.scrollHeight;
        } catch (e) {
          console.error(e);
        }
      });

      discussionEventSource.addEventListener('user_input_required', (event) => {
        chatTypingIndicator.classList.add('hidden');
        try {
          const parsed = JSON.parse(event.data);
          chatUserInputPanel.classList.remove('hidden');
          chatUserInputField.value = '';
          chatUserInputField.disabled = false;
          btnChatSendUserInput.disabled = false;
          chatUserInputField.focus();
          discussionMessages.scrollTop = discussionMessages.scrollHeight;
        } catch (e) {
          console.error(e);
        }
      });

      discussionEventSource.onmessage = (event) => {
        chatTypingIndicator.classList.add('hidden');
        chatUserInputPanel.classList.add('hidden');

        try {
          const turn = JSON.parse(event.data);
          currentDiscussionTurns.push(turn);

          if (discussionIsPaused) {
            discussionMessageBuffer.push(turn);
          } else {
            renderChatBubble(turn);
          }
        } catch (e) {
          console.error(e);
        }
      };

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

      discussionEventSource.onerror = () => {
        if (activeDiscussionSessionId) {
          chatTypingIndicator.classList.add('hidden');
          if (discussionEventSource) {
            discussionEventSource.close();
            discussionEventSource = null;
          }
        }
      };

    } catch (err) {
      console.error(err);
      showToast(err.message || 'Fehler beim Starten der Diskussion.', 'error');
      discussionChat.classList.add('hidden');
      discussionSetup.classList.remove('hidden');
    }
  });

  // Render chat bubble
  function renderChatBubble(turn) {
    const bubbleRow = document.createElement('div');
    const agentIdx = currentSessionAgents.findIndex(a => a.name === turn.sender);
    const alignment = (agentIdx % 2 === 0) ? 'left' : 'right';

    bubbleRow.className = `chat-bubble-row ${alignment}`;

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

    if (discEnableTts.checked && turn.sender !== 'System-Protokollant') {
      const agent = currentSessionAgents.find(a => a.name === turn.sender);
      const voice = agent ? (agent.voice || 'fable') : 'fable';
      queueTTS(turn.text, voice);
    }
  }

  // Toggle Pause/Resume
  btnChatToggle.addEventListener('click', () => {
    if (!activeDiscussionSessionId) return;

    discussionIsPaused = !discussionIsPaused;

    if (discussionIsPaused) {
      btnChatToggle.innerHTML = '<i class="fa-solid fa-play"></i><span>Fortsetzen</span>';
      showToast('Debatte pausiert.', 'warning');
      if (currentTtsAudio) {
        currentTtsAudio.pause();
      }
    } else {
      btnChatToggle.innerHTML = '<i class="fa-solid fa-pause"></i><span>Pause</span>';
      showToast('Debatte fortgesetzt.', 'success');
      if (currentTtsAudio) {
        currentTtsAudio.play().catch(err => console.error("Error resuming TTS:", err));
      }
      discussionMessageBuffer.forEach(turn => renderChatBubble(turn));
      discussionMessageBuffer = [];
      chatTypingIndicator.classList.add('hidden');
    }
  });

  // End discussion and close session
  function closeDiscussionSession() {
    stopAllTts();

    if (activeDiscussionSessionId) {
      const baseUrl = getApiBaseUrl();
      fetch(`${baseUrl}/api/discussion/close`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: activeDiscussionSessionId }),
        keepalive: true
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
    recordedAudioBlobs = [];
    showToast('Debatte beendet.', 'info');
  }

  function handleStopDiscussion() {
    if (currentDiscussionTurns.length > 0) {
      if (!discussionIsPaused) {
        discussionIsPaused = true;
        btnChatToggle.innerHTML = '<i class="fa-solid fa-play"></i><span>Fortsetzen</span>';
      }
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

    if (recordedAudioBlobs.length > 0) {
      showToast('Kompiliere Gesprächs-Audio...', 'info');
      const audioBlob = new Blob(recordedAudioBlobs, { type: 'audio/mpeg' });
      const audioUrl = URL.createObjectURL(audioBlob);
      const audioLink = document.createElement('a');
      audioLink.href = audioUrl;
      audioLink.download = `ki_debatte_${safeTopic}_${timestamp}.mp3`;
      
      document.body.appendChild(audioLink);
      audioLink.click();
      document.body.removeChild(audioLink);
      URL.revokeObjectURL(audioUrl);
    }
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
        body: JSON.stringify({ id: activeDiscussionSessionId, text: text })
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
}

// --- Text-to-Speech Audio Queue Handlers ---
function queueTTS(text, voice) {
  ttsAudioQueue.push({ text, voice });
  processTtsQueue();
}

async function processTtsQueue() {
  if (ttsIsPlaying) return;
  if (ttsAudioQueue.length === 0) return;
  if (discussionIsPaused) return;

  ttsIsPlaying = true;
  const { text, voice } = ttsAudioQueue.shift();

  try {
    const baseUrl = getApiBaseUrl();
    const response = await fetch(`${baseUrl}/api/tts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text, voice })
    });

    if (!response.ok) {
      throw new Error('TTS response was not OK');
    }

    const blob = await response.blob();
    recordedAudioBlobs.push(blob);
    const audioUrl = URL.createObjectURL(blob);
    currentTtsAudio = new Audio(audioUrl);

    currentTtsAudio.onended = () => {
      URL.revokeObjectURL(audioUrl);
      currentTtsAudio = null;
      ttsIsPlaying = false;
      processTtsQueue();
    };

    currentTtsAudio.onerror = (err) => {
      console.error("[TTS] Audiofehler:", err);
      URL.revokeObjectURL(audioUrl);
      currentTtsAudio = null;
      ttsIsPlaying = false;
      processTtsQueue();
    };

    await currentTtsAudio.play();
  } catch (e) {
    console.error("[TTS] Fehler bei Wiedergabe:", e);
    ttsIsPlaying = false;
    setTimeout(processTtsQueue, 1000);
  }
}

function stopAllTts() {
  if (currentTtsAudio) {
    try {
      currentTtsAudio.pause();
    } catch (err) {
      console.error("[TTS] Stoppfehler:", err);
    }
    currentTtsAudio = null;
  }
  ttsAudioQueue = [];
  ttsIsPlaying = false;
}

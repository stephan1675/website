import { showToast } from './main.js';

// ==========================================
// 1. PID CONTROLLER SIMULATOR STATE
// ==========================================
let pidPlaying = true;
let pidTimerId = null;

// System states
let pv = 20.0;          // Process variable (current value)
let velocity = 0.0;     // Velocity for 2nd order system
let integral = 0.0;     // Error integral
let lastError = 0.0;    // Last error for derivative term
let pidHistory = [];    // History array for plotting
const maxHistoryLength = 200;

// Presets parameters
const PID_PRESETS = {
  drone: { kp: 4.5, ki: 0.12, kd: 2.2, setpoint: 60, title: 'Drohne (Höhe)' },
  motor: { kp: 2.2, ki: 0.95, kd: 0.15, setpoint: 70, title: 'DC-Motor (Drehzahl)' },
  heating: { kp: 5.5, ki: 0.03, kd: 3.5, setpoint: 50, title: 'Heizung (Temperatur)' }
};
let activePreset = 'drone';

// ==========================================
// 2. SENSOR FILTER SIMULATOR STATE
// ==========================================
let filterPlaying = true;
let filterTimerId = null;

let filterTime = 0.0;
let filterType = 'moving'; // 'moving' or 'lowpass'
let filterHistoryRaw = [];
let filterHistoryFiltered = [];
let filterHistoryClean = [];
const filterMaxHistory = 200;

// ==========================================
// INITIALISE SIMULATORS
// ==========================================
export function initSimulators() {
  
  // --- PID DOM Elements ---
  const pidCanvas = document.getElementById('pid-canvas');
  if (!pidCanvas) return; // Prevent run if not on dashboard page
  const ctxPid = pidCanvas.getContext('2d');
  
  const sliderKp = document.getElementById('pid-kp');
  const sliderKi = document.getElementById('pid-ki');
  const sliderKd = document.getElementById('pid-kd');
  const sliderSetpoint = document.getElementById('pid-setpoint');

  const valKp = document.getElementById('pid-kp-val');
  const valKi = document.getElementById('pid-ki-val');
  const valKd = document.getElementById('pid-kd-val');
  const valSetpoint = document.getElementById('pid-setpoint-val');

  const textError = document.getElementById('pid-error-val');
  const textEffort = document.getElementById('pid-effort-val');

  const btnPidPlay = document.getElementById('btn-pid-play');
  const btnPidReset = document.getElementById('btn-pid-reset');
  const presetBtns = document.querySelectorAll('.pid-preset-btn');

  // --- Filter DOM Elements ---
  const filterCanvas = document.getElementById('filter-canvas');
  const ctxFilter = filterCanvas.getContext('2d');

  const sliderNoise = document.getElementById('filter-noise');
  const sliderParam = document.getElementById('filter-param');
  const sliderFreq = document.getElementById('filter-freq');

  const valNoise = document.getElementById('filter-noise-val');
  const valParam = document.getElementById('filter-param-val');
  const valFreq = document.getElementById('filter-freq-val');

  const paramLabel = document.getElementById('filter-param-label');
  const textLoss = document.getElementById('filter-loss-val');

  const btnFilterPlay = document.getElementById('btn-filter-play');
  const btnFilterReset = document.getElementById('btn-filter-reset');
  const filterTypeBtns = document.querySelectorAll('.filter-type-btn');

  // --- Sliders Listeners (Update values dynamically) ---
  function bindSlider(slider, elementVal, formatFunc = (v) => v) {
    slider.addEventListener('input', () => {
      elementVal.textContent = formatFunc(slider.value);
    });
  }

  bindSlider(sliderKp, valKp, (v) => parseFloat(v).toFixed(1));
  bindSlider(sliderKi, valKi, (v) => parseFloat(v).toFixed(2));
  bindSlider(sliderKd, valKd, (v) => parseFloat(v).toFixed(2));
  bindSlider(sliderSetpoint, valSetpoint, (v) => parseFloat(v).toFixed(1));

  bindSlider(sliderNoise, valNoise, (v) => parseFloat(v).toFixed(1));
  bindSlider(sliderFreq, valFreq, (v) => `${parseFloat(v).toFixed(2)} Hz`);

  sliderParam.addEventListener('input', () => {
    if (filterType === 'moving') {
      valParam.textContent = parseInt(sliderParam.value);
    } else {
      // Exponential LowPass mapping (0.01 - 1.0)
      const mapped = (sliderParam.value / 100).toFixed(2);
      valParam.textContent = mapped;
    }
  });

  // --- Preset buttons ---
  presetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const presetName = btn.getAttribute('data-preset');
      loadPidPreset(presetName);
      presetBtns.forEach(b => b.classList.remove('btn-primary'));
      presetBtns.forEach(b => b.classList.add('btn-secondary'));
      btn.classList.remove('btn-secondary');
      btn.classList.add('btn-primary');
    });
  });

  function loadPidPreset(presetName) {
    const preset = PID_PRESETS[presetName];
    if (!preset) return;

    activePreset = presetName;
    sliderKp.value = preset.kp;
    sliderKi.value = preset.ki;
    sliderKd.value = preset.kd;
    sliderSetpoint.value = preset.setpoint;

    valKp.textContent = preset.kp.toFixed(1);
    valKi.textContent = preset.ki.toFixed(2);
    valKd.textContent = preset.kd.toFixed(2);
    valSetpoint.textContent = preset.setpoint.toFixed(1);

    resetPidSimulation();
    showToast(`Preset geladen: ${preset.title}`, 'info');
  }

  // --- PID Reset ---
  function resetPidSimulation() {
    pv = activePreset === 'heating' ? 20.0 : 0.0;
    velocity = 0.0;
    integral = 0.0;
    lastError = 0.0;
    pidHistory = [];
  }
  btnPidReset.addEventListener('click', resetPidSimulation);

  // --- PID Play/Pause ---
  btnPidPlay.addEventListener('click', () => {
    pidPlaying = !pidPlaying;
    if (pidPlaying) {
      btnPidPlay.innerHTML = '<i class="fa-solid fa-pause"></i><span>Pause</span>';
      btnPidPlay.style.color = '';
    } else {
      btnPidPlay.innerHTML = '<i class="fa-solid fa-play"></i><span>Start</span>';
      btnPidPlay.style.color = 'var(--color-secondary)';
    }
  });

  // --- Filter Type Switching ---
  filterTypeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterType = btn.getAttribute('data-filter');
      filterTypeBtns.forEach(b => b.classList.remove('active', 'btn-primary'));
      filterTypeBtns.forEach(b => b.classList.add('btn-secondary'));
      btn.classList.remove('btn-secondary');
      btn.classList.add('active', 'btn-primary');

      // Adjust parameter sliders
      if (filterType === 'moving') {
        paramLabel.textContent = 'Fenster (N)';
        sliderParam.min = "2";
        sliderParam.max = "45";
        sliderParam.step = "1";
        sliderParam.value = "10";
        valParam.textContent = "10";
      } else {
        paramLabel.textContent = 'Dämpfung (α)';
        sliderParam.min = "1";
        sliderParam.max = "100";
        sliderParam.step = "1";
        sliderParam.value = "15"; // Maps to 0.15
        valParam.textContent = "0.15";
      }
    });
  });

  // --- Filter Reset ---
  function resetFilterSimulation() {
    filterTime = 0.0;
    filterHistoryRaw = [];
    filterHistoryFiltered = [];
    filterHistoryClean = [];
  }
  btnFilterReset.addEventListener('click', resetFilterSimulation);

  // --- Filter Play/Pause ---
  btnFilterPlay.addEventListener('click', () => {
    filterPlaying = !filterPlaying;
    if (filterPlaying) {
      btnFilterPlay.innerHTML = '<i class="fa-solid fa-pause"></i><span>Pause</span>';
      btnFilterPlay.style.color = '';
    } else {
      btnFilterPlay.innerHTML = '<i class="fa-solid fa-play"></i><span>Start</span>';
      btnFilterPlay.style.color = 'var(--color-secondary)';
    }
  });

  // --- Set default preset on load ---
  loadPidPreset('drone');

  // --- Run Loops on tab open ---
  window.addEventListener('tab-theory-opened', () => {
    // Avoid double loops
    if (pidTimerId) cancelAnimationFrame(pidTimerId);
    if (filterTimerId) cancelAnimationFrame(filterTimerId);

    // Boot animation loops
    runPidLoop();
    runFilterLoop();
  });

  // ==========================================
  // PID PHYSICS LOOP AND CANVAS RENDERING
  // ==========================================
  const dt = 0.1; // Delta time step

  function runPidLoop() {
    if (pidPlaying) {
      // 1. Load active coefficients
      const kp = parseFloat(sliderKp.value);
      const ki = parseFloat(sliderKi.value);
      const kd = parseFloat(sliderKd.value);
      const setpoint = parseFloat(sliderSetpoint.value);

      // 2. Calculate PID Math
      const error = setpoint - pv;
      integral += error * dt;

      // Anti-windup: Clamp integral limit to prevent saturation
      const intLimit = 15.0;
      integral = Math.max(-intLimit, Math.min(intLimit, integral));

      const derivative = (error - lastError) / dt;
      let effort = (kp * error) + (ki * integral) + (kd * derivative);
      
      // Clamp effort (motor voltage or drone thrust constraints)
      effort = Math.max(-100, Math.min(100, effort));
      
      lastError = error;

      // 3. Update system physics
      updateSystemPhysics(effort);

      // Save states
      pidHistory.push({ pv, setpoint });
      if (pidHistory.length > maxHistoryLength) {
        pidHistory.shift();
      }

      // Update HUD stats
      textError.textContent = error.toFixed(1);
      textEffort.textContent = effort.toFixed(0);
    }

    // 4. Render Canvas Plot
    drawPidPlot(ctxPid, pidCanvas);

    pidTimerId = requestAnimationFrame(runPidLoop);
  }

  function updateSystemPhysics(effort) {
    if (activePreset === 'drone') {
      // 2nd order vertical motion: F = m*a -> thrust - gravity - air_resistance = a
      const gravity = 4.0;
      const mass = 1.0;
      const dragCoeff = 0.15;
      
      // Thrust mapped from effort (effort -100 to 100 -> thrust 0 to 8)
      const thrust = ((effort + 100) / 200) * 8.5;
      
      const accel = (thrust - gravity - (velocity * dragCoeff)) / mass;
      velocity += accel * dt;
      pv += velocity * dt;
      
      // Ground boundary
      if (pv < 0) {
        pv = 0;
        velocity = 0;
      }
    } 
    else if (activePreset === 'motor') {
      // 1st order motor speed: T = J*a -> Torque_effort - friction = a
      const friction = 0.25;
      const inertia = 0.5;
      
      const torque = effort * 0.12;
      const accel = (torque - (pv * friction)) / inertia;
      pv += accel * dt;

      // Motor speed boundary
      if (pv < 0) pv = 0;
    } 
    else if (activePreset === 'heating') {
      // Thermal heating: dT = heat_added - thermal_loss
      const thermalLossCoeff = 0.05;
      const envTemp = 20.0;
      
      // Heat effort (0 to 100 % only, heating cannot cool below env)
      const heatInput = Math.max(0, effort) * 0.15;
      
      const dT = heatInput - (thermalLossCoeff * (pv - envTemp));
      pv += dT * dt;
    }
  }

  function drawPidPlot(ctx, canvas) {
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    // Style background grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 40) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for (let y = 0; y < h; y += 30) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }

    // Border
    ctx.strokeStyle = 'rgba(255,255,255,0.1)';
    ctx.strokeRect(0, 0, w, h);

    // Map physical value to canvas pixel coordinates
    // range: 0 to 100 on Y axis -> h to 0 pixels
    const mapY = (val) => h - (val / 100) * h;
    const mapX = (idx) => (idx / maxHistoryLength) * w;

    if (pidHistory.length === 0) return;

    // Draw Setpoint (green dashed line)
    const setpoint = pidHistory[pidHistory.length - 1].setpoint;
    ctx.strokeStyle = 'rgba(16, 185, 129, 0.7)'; // Emerald
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(0, mapY(setpoint));
    ctx.lineTo(w, mapY(setpoint));
    ctx.stroke();
    ctx.setLineDash([]); // Reset dash

    // Draw Process Variable history (Solid cyan curve)
    ctx.strokeStyle = 'var(--color-secondary)'; // Cyan
    ctx.lineWidth = 3.5;
    ctx.shadowBlur = 8;
    ctx.shadowColor = 'rgba(6, 182, 212, 0.4)';
    ctx.beginPath();
    ctx.moveTo(mapX(0), mapY(pidHistory[0].pv));
    for (let i = 1; i < pidHistory.length; i++) {
      ctx.lineTo(mapX(i), mapY(pidHistory[i].pv));
    }
    ctx.stroke();

    // Reset shadow
    ctx.shadowBlur = 0;
  }

  // ==========================================
  // SENSOR FILTER LOOP AND CANVAS RENDERING
  // ==========================================
  function runFilterLoop() {
    if (filterPlaying) {
      const noiseAmp = parseFloat(sliderNoise.value);
      const freq = parseFloat(sliderFreq.value);
      
      // Calculate clean base sine wave signal
      // y(t) = 50 + 25 * sin(2*pi*f*t)
      const cleanVal = 50.0 + 28.0 * Math.sin(2.0 * Math.PI * freq * filterTime);
      filterTime += 0.05;

      // Add random white noise
      const noisyVal = cleanVal + (Math.random() - 0.5) * noiseAmp * 2.0;

      // Apply filtering algorithm
      let filteredVal = 0.0;

      if (filterType === 'moving') {
        const N = parseInt(sliderParam.value);
        filterHistoryRaw.push(noisyVal);
        
        // Window slice and average calculation
        const startIdx = Math.max(0, filterHistoryRaw.length - N);
        const slice = filterHistoryRaw.slice(startIdx);
        const sum = slice.reduce((a, b) => a + b, 0);
        filteredVal = sum / slice.length;
      } 
      else {
        // LowPass IIR: y_f(t) = alpha * y_n(t) + (1-alpha) * y_f(t-1)
        const alpha = parseFloat(sliderParam.value) / 100;
        
        let prevVal = filterHistoryFiltered.length > 0 ? filterHistoryFiltered[filterHistoryFiltered.length - 1] : noisyVal;
        filteredVal = alpha * noisyVal + (1 - alpha) * prevVal;
        
        filterHistoryRaw.push(noisyVal);
      }

      filterHistoryClean.push(cleanVal);
      filterHistoryFiltered.push(filteredVal);

      // Shift queues to keep size bounded
      if (filterHistoryRaw.length > filterMaxHistory) {
        filterHistoryRaw.shift();
        filterHistoryFiltered.shift();
        filterHistoryClean.shift();
      }

      // Calculate statistical lag / deviation (mean absolute error between filtered and clean)
      let sumError = 0;
      const statWindow = Math.min(filterHistoryFiltered.length, 50);
      if (statWindow > 0) {
        for (let i = 1; i <= statWindow; i++) {
          const idxF = filterHistoryFiltered.length - i;
          const idxC = filterHistoryClean.length - i;
          sumError += Math.abs(filterHistoryFiltered[idxF] - filterHistoryClean[idxC]);
        }
        const meanErr = sumError / statWindow;
        // Map average error to a percentage representation of signal loss
        const lossPercent = Math.min(100, (meanErr / 28.0) * 100);
        textLoss.textContent = `${lossPercent.toFixed(1)}%`;
      }
    }

    // Draw canvas plot
    drawFilterPlot(ctxFilter, filterCanvas);

    filterTimerId = requestAnimationFrame(runFilterLoop);
  }

  function drawFilterPlot(ctx, canvas) {
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    // Style background grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 40) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for (let y = 0; y < h; y += 30) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }

    // Border
    ctx.strokeStyle = 'rgba(255,255,255,0.1)';
    ctx.strokeRect(0, 0, w, h);

    const mapY = (val) => h - (val / 100) * h;
    const mapX = (idx) => (idx / filterMaxHistory) * w;

    if (filterHistoryRaw.length === 0) return;

    // 1. Draw Raw Noisy Signal (Thin red lines)
    ctx.strokeStyle = 'rgba(244, 63, 94, 0.35)'; // Rose/Red
    ctx.lineWidth = 1.25;
    ctx.beginPath();
    ctx.moveTo(mapX(0), mapY(filterHistoryRaw[0]));
    for (let i = 1; i < filterHistoryRaw.length; i++) {
      ctx.lineTo(mapX(i), mapY(filterHistoryRaw[i]));
    }
    ctx.stroke();

    // 2. Draw Clean Sine Signal (Thin green line representing ideal sensor reading)
    ctx.strokeStyle = 'rgba(16, 185, 129, 0.4)'; // Green
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(mapX(0), mapY(filterHistoryClean[0]));
    for (let i = 1; i < filterHistoryClean.length; i++) {
      ctx.lineTo(mapX(i), mapY(filterHistoryClean[i]));
    }
    ctx.stroke();

    // 3. Draw Filtered Signal (Solid thick cyan line representing smoothed values)
    ctx.strokeStyle = 'var(--color-secondary)'; // Cyan
    ctx.lineWidth = 3.25;
    ctx.shadowBlur = 6;
    ctx.shadowColor = 'rgba(6, 182, 212, 0.3)';
    ctx.beginPath();
    ctx.moveTo(mapX(0), mapY(filterHistoryFiltered[0]));
    for (let i = 1; i < filterHistoryFiltered.length; i++) {
      ctx.lineTo(mapX(i), mapY(filterHistoryFiltered[i]));
    }
    ctx.stroke();

    ctx.shadowBlur = 0;
  }
}

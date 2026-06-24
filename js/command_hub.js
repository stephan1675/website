import { runGame } from './api.js';
import { showToast } from './main.js';

// --- Projects Metadata ---
const PROJECTS = [
  {
    id: 'website',
    title: 'Dieses Portal (Command Center)',
    desc: 'Eine responsive Web-App mit Login-System, Session-Management und einer Python-Brücke zur lokalen Programmausführung.',
    runnable: false,
    tag: 'HTML5 / CSS3 / Vanilla JS',
    icon: 'fa-earth-americas'
  },
  {
    id: 'python_shooter',
    title: 'Python Shooter 3D',
    desc: 'Ein 3D-Shooter-Spiel, entwickelt mit Python und der Ursina-Engine. Nutzt lokale Ressourcen.',
    runnable: true,
    endpoint: '/api/run-python',
    tag: 'Python / Ursina Engine',
    icon: 'fa-brands fa-python'
  },
  {
    id: 'cpp_game',
    title: 'C++ Spiel',
    desc: 'Ein konsolenbasiertes C++ Spiel, das über das Web-Terminal ferngesteuert und angezeigt wird.',
    runnable: true,
    endpoint: 'terminal', // Handled via modal launcher in main.js
    tag: 'C++ / Console Game',
    icon: 'fa-solid fa-cubes'
  },
  {
    id: 'godot_shooter',
    title: 'Godot Shooter',
    desc: 'Ein in der Godot-Engine entwickelter 3D-Shooter. Planungsphase.',
    runnable: false,
    tag: 'Godot Engine / GDScript',
    icon: 'fa-solid fa-gamepad'
  }
];

let currentProjectId = null;

// Initialise the Command Hub features
export function initCommandHub() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  // 1. Tab Switching Listeners
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTabId = btn.getAttribute('data-tab');

      // Remove active states
      tabBtns.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.add('hidden'));

      // Add active state to clicked button
      btn.classList.add('active');
      
      const targetContent = document.getElementById(targetTabId);
      if (targetContent) {
        targetContent.classList.remove('hidden');
      }

      // Special trigger when entering simulators tab to boot loops
      if (targetTabId === 'tab-theory') {
        window.dispatchEvent(new CustomEvent('tab-theory-opened'));
      }
    });
  });

  // 2. Project Planner Setup
  const projectSelectorList = document.getElementById('project-selector-list');
  const activeProjectTitle = document.getElementById('active-project-title');
  const activeProjectDesc = document.getElementById('active-project-desc');
  const btnLaunchActiveProject = document.getElementById('btn-launch-active-project');
  
  const progressContainer = document.getElementById('active-project-progress-container');
  const progressBar = document.getElementById('active-project-progress-bar');
  const progressText = document.getElementById('active-project-progress-text');
  const progressResetBtn = document.getElementById('active-project-progress-reset');
  
  const boardContent = document.getElementById('active-project-board-content');
  const addTaskForm = document.getElementById('add-task-form');
  const newTaskInput = document.getElementById('new-task-input');
  const projectTasksList = document.getElementById('project-tasks-list');
  const projectNotesTextarea = document.getElementById('project-notes-textarea');

  // --- Manual Progress Override ---
  if (progressText) {
    progressText.addEventListener('click', () => {
      const currentData = getActiveProjectData();
      
      // If already editing (contains an input element), do nothing
      if (progressText.querySelector('input')) return;

      const currentPercent = getProgressBarPercentage(currentData);
      
      const input = document.createElement('input');
      input.type = 'number';
      input.min = '0';
      input.max = '100';
      input.className = 'progress-manual-input';
      input.value = currentPercent;
      
      // Store current display content
      const originalHTML = progressText.innerHTML;
      progressText.innerHTML = '';
      progressText.appendChild(input);
      input.focus();
      input.select();

      const finishEdit = () => {
        let val = parseInt(input.value);
        if (isNaN(val) || val < 0) val = 0;
        if (val > 100) val = 100;
        
        saveProjectData(undefined, undefined, val);
        const updatedData = getActiveProjectData();
        updateProgressBar(updatedData.tasks);
        showToast(`Fortschritt manuell auf ${val}% gesetzt.`, 'info');
      };

      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          input.blur();
        } else if (e.key === 'Escape') {
          // Cancel edit
          progressText.innerHTML = originalHTML;
        }
      });

      input.addEventListener('blur', () => {
        finishEdit();
      });
    });
  }

  if (progressResetBtn) {
    progressResetBtn.addEventListener('click', () => {
      saveProjectData(undefined, undefined, null);
      const updatedData = getActiveProjectData();
      updateProgressBar(updatedData.tasks);
      showToast('Fortschrittsbalken wird wieder automatisch berechnet.', 'success');
    });
  }

  // Render project selection list on load
  PROJECTS.forEach(project => {
    const item = document.createElement('div');
    item.className = 'project-selector-item';
    item.style.cssText = 'padding: 0.85rem 1.1rem; background: rgba(255, 255, 255, 0.02); border: 1px solid var(--glass-border); border-radius: var(--border-radius-sm); cursor: pointer; transition: var(--transition-fast); display: flex; align-items: center; gap: 0.75rem;';
    item.innerHTML = `
      <i class="${project.icon}" style="color: var(--color-primary); font-size: 1.15rem; width: 20px; text-align: center;"></i>
      <div style="text-align: left; flex-grow: 1;">
        <span style="font-weight: 600; font-size: 0.9rem; display: block; color: var(--color-text-primary);">${project.title.split(' ')[0]}</span>
        <span style="font-size: 0.7rem; color: var(--color-text-secondary);">${project.tag}</span>
      </div>
    `;

    item.addEventListener('click', () => {
      // Highlight selected project item
      projectSelectorList.querySelectorAll('.project-selector-item').forEach(el => {
        el.style.borderColor = 'var(--glass-border)';
        el.style.background = 'rgba(255, 255, 255, 0.02)';
      });
      item.style.borderColor = 'var(--color-primary)';
      item.style.background = 'rgba(99, 102, 241, 0.05)';

      selectProject(project.id);
    });

    projectSelectorList.appendChild(item);
  });

  // Select project action
  function selectProject(projectId) {
    currentProjectId = projectId;
    const project = PROJECTS.find(p => p.id === projectId);
    if (!project) return;

    // Update details
    activeProjectTitle.textContent = project.title;
    activeProjectDesc.textContent = project.desc;

    // Setup launch button
    if (project.runnable) {
      btnLaunchActiveProject.classList.remove('hidden');
    } else {
      btnLaunchActiveProject.classList.add('hidden');
    }

    // Show board containers
    progressContainer.classList.remove('hidden');
    boardContent.classList.remove('hidden');

    // Load data from LocalStorage
    loadProjectData();
  }

  // Load project notes and tasks
  function loadProjectData() {
    if (!currentProjectId) return;

    const dataKey = `project_data_${currentProjectId}`;
    const data = JSON.parse(localStorage.getItem(dataKey) || '{"tasks": [], "notes": "", "customProgress": null}');

    // Run data migration if needed
    let hasMigrated = false;
    if (data.tasks && Array.isArray(data.tasks)) {
      data.tasks.forEach(task => {
        if (task.status === undefined) {
          task.status = task.completed ? 'completed' : 'planned';
          delete task.completed;
          hasMigrated = true;
        }
        if (task.notes === undefined) {
          task.notes = '';
          hasMigrated = true;
        }
      });
    }

    if (data.customProgress === undefined) {
      data.customProgress = null;
      hasMigrated = true;
    }

    if (hasMigrated) {
      localStorage.setItem(dataKey, JSON.stringify(data));
    }

    // Load notes
    projectNotesTextarea.value = data.notes || '';

    // Render tasks
    renderTasksList(data.tasks);
    updateProgressBar(data.tasks);
  }

  // Save current project data back to LocalStorage
  function saveProjectData(tasks, notes, customProgress) {
    if (!currentProjectId) return;

    const dataKey = `project_data_${currentProjectId}`;
    const current = JSON.parse(localStorage.getItem(dataKey) || '{"tasks": [], "notes": "", "customProgress": null}');

    const data = {
      tasks: tasks !== undefined ? tasks : current.tasks,
      notes: notes !== undefined ? notes : current.notes,
      customProgress: customProgress !== undefined ? customProgress : current.customProgress
    };

    localStorage.setItem(dataKey, JSON.stringify(data));
  }

  // Render tasks checklist
  // Render tasks checklist
  function renderTasksList(tasks) {
    projectTasksList.innerHTML = '';

    if (tasks.length === 0) {
      projectTasksList.innerHTML = `<div style="text-align: center; color: var(--color-text-muted); font-size: 0.85rem; padding: 1.5rem 0;">Keine Aufgaben vorhanden. Erstelle eine neue Aufgabe oben!</div>`;
      return;
    }

    tasks.forEach(task => {
      const card = document.createElement('div');
      card.className = 'task-card';
      card.setAttribute('data-task-id', task.id);

      const isCompleted = task.status === 'completed';
      const textStyleClass = isCompleted ? 'task-text completed' : 'task-text';
      
      let statusClass = 'status-planned';
      if (task.status === 'in_progress') statusClass = 'status-in-progress';
      if (task.status === 'completed') statusClass = 'status-completed';

      card.innerHTML = `
        <div class="task-header">
          <!-- Status Select -->
          <select class="task-status-select ${statusClass}">
            <option value="planned" ${task.status === 'planned' ? 'selected' : ''} style="background-color: var(--bg-primary); color: var(--color-text-primary);">Geplant</option>
            <option value="in_progress" ${task.status === 'in_progress' ? 'selected' : ''} style="background-color: var(--bg-primary); color: var(--color-text-primary);">In Ausführung</option>
            <option value="completed" ${task.status === 'completed' ? 'selected' : ''} style="background-color: var(--bg-primary); color: var(--color-text-primary);">Erledigt</option>
          </select>
          
          <!-- Task Text -->
          <div class="${textStyleClass}">
            ${task.text}
          </div>

          <!-- Actions -->
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <i class="fa-solid fa-chevron-down chevron-icon"></i>
            <button class="btn-delete-task">
              <i class="fa-regular fa-trash-can"></i>
            </button>
          </div>
        </div>

        <!-- Collapsible Notes Pane -->
        <div class="task-notes-pane">
          <div class="task-notes-content">
            <div class="task-notes-divider"></div>
            <label class="task-notes-label">Notizen für diese Aufgabe</label>
            <textarea class="task-notes-textarea" placeholder="Notizen für diese Aufgabe eingeben... (automatisches Speichern)">${task.notes || ''}</textarea>
          </div>
        </div>
      `;

      const header = card.querySelector('.task-header');
      const select = card.querySelector('.task-status-select');
      const deleteBtn = card.querySelector('.btn-delete-task');
      const pane = card.querySelector('.task-notes-pane');
      const textarea = card.querySelector('.task-notes-textarea');
      const textDiv = card.querySelector('.task-text');

      // 1. Status Change Listener
      select.addEventListener('change', (e) => {
        e.stopPropagation();
        const newStatus = select.value;
        task.status = newStatus;

        // Update select color styling
        select.className = `task-status-select status-${newStatus.replace('_', '-')}`;
        
        // Update task text decoration
        if (newStatus === 'completed') {
          textDiv.className = 'task-text completed';
        } else {
          textDiv.className = 'task-text';
        }

        const currentData = getActiveProjectData();
        saveProjectData(currentData.tasks, projectNotesTextarea.value);
        updateProgressBar(currentData.tasks);
      });

      select.addEventListener('click', (e) => {
        e.stopPropagation();
      });

      // 2. Expand/Collapse Toggle on Header Click
      header.addEventListener('click', () => {
        const isExpanded = card.classList.toggle('expanded');
        if (isExpanded) {
          const contentHeight = pane.firstElementChild ? pane.firstElementChild.scrollHeight : 140;
          pane.style.maxHeight = contentHeight + 'px';
          
          const onTransitionEnd = (e) => {
            if (e.propertyName === 'max-height' && card.classList.contains('expanded')) {
              pane.style.maxHeight = 'none';
              pane.removeEventListener('transitionend', onTransitionEnd);
            }
          };
          pane.addEventListener('transitionend', onTransitionEnd);
        } else {
          if (pane.style.maxHeight === 'none') {
            const contentHeight = pane.firstElementChild ? pane.firstElementChild.scrollHeight : 140;
            pane.style.maxHeight = contentHeight + 'px';
            pane.offsetHeight; // force reflow
          }
          setTimeout(() => {
            pane.style.maxHeight = '0px';
          }, 0);
        }
      });

      // 3. Delete Task Click Listener
      deleteBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const currentData = getActiveProjectData();
        const filteredTasks = currentData.tasks.filter(t => t.id !== task.id);
        saveProjectData(filteredTasks, projectNotesTextarea.value);
        renderTasksList(filteredTasks);
        updateProgressBar(filteredTasks);
        showToast('Aufgabe entfernt.', 'info');
      });

      // 4. Notes Textarea auto-save
      textarea.addEventListener('input', () => {
        task.notes = textarea.value;
        const currentData = getActiveProjectData();
        saveProjectData(currentData.tasks, projectNotesTextarea.value);
      });

      projectTasksList.appendChild(card);
    });
  }

  // Helper to extract active data
  function getActiveProjectData() {
    const dataKey = `project_data_${currentProjectId}`;
    return JSON.parse(localStorage.getItem(dataKey) || '{"tasks": [], "notes": "", "customProgress": null}');
  }

  // Helper to calculate progress percentage
  function getProgressBarPercentage(data) {
    if (data.customProgress !== null && data.customProgress !== undefined) {
      return data.customProgress;
    }
    const tasks = data.tasks || [];
    if (tasks.length === 0) return 0;
    const completedCount = tasks.filter(t => t.status === 'completed').length;
    return Math.round((completedCount / tasks.length) * 100);
  }

  // Update progress bar
  function updateProgressBar(tasks) {
    const data = getActiveProjectData();
    const isManual = data.customProgress !== null && data.customProgress !== undefined;
    const percentage = getProgressBarPercentage(data);

    progressBar.style.width = `${percentage}%`;

    const completedCount = tasks.filter(t => t.status === 'completed').length;
    
    if (isManual) {
      progressText.textContent = `${percentage}% (manuell)`;
      if (progressResetBtn) {
        progressResetBtn.classList.remove('hidden');
      }
    } else {
      progressText.textContent = `${percentage}% (${completedCount}/${tasks.length})`;
      if (progressResetBtn) {
        progressResetBtn.classList.add('hidden');
      }
    }
  }

  // Add Task submit handler
  addTaskForm.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!currentProjectId) return;

    const taskText = newTaskInput.value.trim();
    if (!taskText) return;

    const currentData = getActiveProjectData();
    
    // Add new task with updated schema (status, notes)
    const newTask = {
      id: `task_${Date.now()}`,
      text: taskText,
      status: 'planned',
      notes: ''
    };

    currentData.tasks.push(newTask);
    saveProjectData(currentData.tasks, projectNotesTextarea.value);

    newTaskInput.value = '';
    renderTasksList(currentData.tasks);
    updateProgressBar(currentData.tasks);
    showToast('Aufgabe hinzugefügt!', 'success');
  });

  // Notes text area change / input autosave
  projectNotesTextarea.addEventListener('input', () => {
    const currentData = getActiveProjectData();
    saveProjectData(currentData.tasks, projectNotesTextarea.value);
  });

  // Launch project action listener
  btnLaunchActiveProject.addEventListener('click', () => {
    if (!currentProjectId) return;
    const project = PROJECTS.find(p => p.id === currentProjectId);
    if (!project || !project.runnable) return;

    if (project.endpoint === 'terminal') {
      // Trigger click event on C++ Spiel button on the public homepage to boot terminal
      const btnRunCpp = document.getElementById('btn-run-cpp');
      if (btnRunCpp) {
        btnRunCpp.click();
      }
    } else {
      // Run other local games via backend endpoint
      runGame(project.endpoint);
    }
  });
}

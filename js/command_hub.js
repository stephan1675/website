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
  
  const boardContent = document.getElementById('active-project-board-content');
  const addTaskForm = document.getElementById('add-task-form');
  const newTaskInput = document.getElementById('new-task-input');
  const projectTasksList = document.getElementById('project-tasks-list');
  const projectNotesTextarea = document.getElementById('project-notes-textarea');

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
    const data = JSON.parse(localStorage.getItem(dataKey) || '{"tasks": [], "notes": ""}');

    // Load notes
    projectNotesTextarea.value = data.notes || '';

    // Render tasks
    renderTasksList(data.tasks);
    updateProgressBar(data.tasks);
  }

  // Save current project data back to LocalStorage
  function saveProjectData(tasks, notes) {
    if (!currentProjectId) return;

    const dataKey = `project_data_${currentProjectId}`;
    const data = {
      tasks: tasks,
      notes: notes
    };

    localStorage.setItem(dataKey, JSON.stringify(data));
  }

  // Render tasks checklist
  function renderTasksList(tasks) {
    projectTasksList.innerHTML = '';

    if (tasks.length === 0) {
      projectTasksList.innerHTML = `<div style="text-align: center; color: var(--color-text-muted); font-size: 0.85rem; padding: 1.5rem 0;">Keine Aufgaben vorhanden. Erstelle eine neue Aufgabe oben!</div>`;
      return;
    }

    tasks.forEach(task => {
      const row = document.createElement('div');
      row.className = 'task-row';
      row.style.cssText = 'display: flex; justify-content: space-between; align-items: center; background: rgba(0, 0, 0, 0.15); border: 1px solid var(--glass-border); padding: 0.75rem 1rem; border-radius: var(--border-radius-sm); margin-bottom: 0.25rem; transition: var(--transition-fast);';

      const labelStyle = task.completed ? 'text-decoration: line-through; color: var(--color-text-muted);' : 'color: var(--color-text-primary);';

      row.innerHTML = `
        <label style="display: flex; align-items: center; gap: 0.75rem; cursor: pointer; flex-grow: 1; text-align: left; font-size: 0.9rem; ${labelStyle}">
          <input type="checkbox" class="task-checkbox" ${task.completed ? 'checked' : ''} style="cursor: pointer; width: 16px; height: 16px; accent-color: var(--color-primary);">
          <span>${task.text}</span>
        </label>
        <button class="btn-delete-task" style="background: none; border: none; color: var(--color-text-muted); cursor: pointer; transition: var(--transition-fast); font-size: 0.95rem;">
          <i class="fa-regular fa-trash-can"></i>
        </button>
      `;

      // Checkbox click listener
      row.querySelector('.task-checkbox').addEventListener('change', () => {
        task.completed = !task.completed;
        const currentData = getActiveProjectData();
        saveProjectData(currentData.tasks, projectNotesTextarea.value);
        renderTasksList(currentData.tasks);
        updateProgressBar(currentData.tasks);
      });

      // Delete click listener
      row.querySelector('.btn-delete-task').addEventListener('click', () => {
        const currentData = getActiveProjectData();
        const filteredTasks = currentData.tasks.filter(t => t.id !== task.id);
        saveProjectData(filteredTasks, projectNotesTextarea.value);
        renderTasksList(filteredTasks);
        updateProgressBar(filteredTasks);
        showToast('Aufgabe entfernt.', 'info');
      });

      // Hover styling
      row.addEventListener('mouseenter', () => {
        row.style.borderColor = 'rgba(255, 255, 255, 0.15)';
        row.querySelector('.btn-delete-task').style.color = 'var(--color-danger)';
      });
      row.addEventListener('mouseleave', () => {
        row.style.borderColor = 'var(--glass-border)';
        row.querySelector('.btn-delete-task').style.color = 'var(--color-text-muted)';
      });

      projectTasksList.appendChild(row);
    });
  }

  // Helper to extract active data
  function getActiveProjectData() {
    const dataKey = `project_data_${currentProjectId}`;
    return JSON.parse(localStorage.getItem(dataKey) || '{"tasks": [], "notes": ""}');
  }

  // Update progress bar
  function updateProgressBar(tasks) {
    if (tasks.length === 0) {
      progressBar.style.width = '0%';
      progressText.textContent = '0% (0/0)';
      return;
    }

    const completedCount = tasks.filter(t => t.completed).length;
    const percentage = Math.round((completedCount / tasks.length) * 100);

    progressBar.style.width = `${percentage}%`;
    progressText.textContent = `${percentage}% (${completedCount}/${tasks.length})`;
  }

  // Add Task submit handler
  addTaskForm.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!currentProjectId) return;

    const taskText = newTaskInput.value.trim();
    if (!taskText) return;

    const currentData = getActiveProjectData();
    
    // Add new task
    const newTask = {
      id: `task_${Date.now()}`,
      text: taskText,
      completed: false
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

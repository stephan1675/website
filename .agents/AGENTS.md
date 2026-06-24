# Git Workflow Rules

Please follow this Git workflow for all development tasks in this workspace:

1. **Branch Structure**:
   - **`main`**: Represents the stable, running code. Never commit experimental or untested code directly to `main`.
   - **`develop`**: Represents the latest development version that is currently being tested.
   - **Feature/Bugfix Branches**: When starting a new feature or fixing a bug, create a new branch from `develop` with a descriptive name (e.g., `feature/my-feature` or `bugfix/issue-name`).
   - **Merging**: 
     - Merge feature branches into `develop` once they are complete and verified.
     - Merge `develop` into `main` only when the code is fully verified and stable.

2. **Commits & Pushes (Atomic Commits)**:
   - Make small, atomic commits representing a single functional change or bug fix.
   - Write clear and descriptive commit messages (e.g., `feat: add token validation`, `fix: correct HTML tag nesting`).
   - Automatically commit and push code changes to the remote repository once the task is complete and verified.

# Karpathy Structured Agent Workflow

Please follow this structured workflow for all tasks in this workspace:

## 1. Layer 1: The Spec (Spezifikation)
- **Goal Interview**: Before editing any code or starting a complex build, interview the user to uncover the deep goal (what decisions or outcomes this task drives), not just the superficial task.
- **Project Context Lock**: Explicitly state and verify which project or directory (e.g., Website, C++ Game, Python Shooter, Godot Shooter) is targeted before making any changes.
- **Agile Spec-ing**: Bias towards smaller, compartmentalized implementation plans with tight scopes and clear checkpoints.

## 2. Layer 2: The Verifier (Verifikation)
- **Predefined Evaluation Criteria**: Define precise success criteria upfront.
- **Automated Verification**: Run `python tests/run_tests.py` in the workspace to verify portal/authentication logic before staging or committing changes.
- **Manual Verification Fallback**: If no automated tests exist for a specific component, write a step-by-step manual verification checklist.
- **Critic / Security Auditor**: For complex or security-sensitive changes, launch the `security_auditor` subagent to audit changes before presenting them to the user.

## 3. Layer 3: Guardrail Buckets
- **Always Do**:
  - Run syntax/compilation checks before requesting feedback.
  - Run `git status` and verify you are on the correct branch (`develop` or feature branch) before starting development.
  - Use `generate_image` for UI mockup designs and gain user visual approval before implementing frontend CSS/HTML.
- **Ask First**:
  - Start long-running background processes (e.g. servers).
  - Install new package dependencies.
- **Never Do**:
  - Commit or push directly to `main`.
  - Hardcode secrets, API keys, or credentials.
  - Use emojis or non-ASCII characters in console prints to prevent CP1252 encoding exceptions on Windows environments.

# Specialized Workspace Subagents

The following specialized subagents are predefined for this workspace and can be invoked using the `invoke_subagent` tool:

1. **`security_auditor`**:
   - **When to use**: Whenever implementing auth, session management, file uploads, handling user input, or modifying APIs.
   - **Task**: Run a comprehensive audit for BOLA, CSRF, insecure storage, input injection, and data leakage.
2. **`refactoring_expert`**:
   - **When to use**: When files grow too large, when duplicate logic is identified, or when codebase readability needs improvement.
   - **Task**: Review files for SOLID, DRY, and performance optimizations, presenting a clean refactoring plan.
3. **`cpp_compiler_check_agent`**:
   - **When to use**: When developing or debugging files in the C++ Tower Defense game (`c++ spiel/`) or embedded controls.
   - **Task**: Scan code for syntax errors, check compiler/linker compatibility, and verify modern C++ practices.

# Task Delegation & Overnight Runs

- Encourage the user to use the `/goal` command for complex, long-running tasks (e.g., building a complete PID simulator or an AI-based feature).
- When a `/goal` is set, the agent operates autonomously, building, testing, auditing, and compiling before delivering a fully validated result.


# Git Workflow Rules

Please follow this Git workflow for all development tasks in this workspace:

1. **Branch Structure**:
   - **`main`**: Represents the stable, running code. Never commit experimental or untested code directly to `main`.
   - **`develop`**: Represents the latest development version that is currently being tested.
   - **Feature/Bugfix Branches**: When starting a new feature or fixing a bug, create a new branch from `develop` with a descriptive name (e.g., `feature/my-feature` or `bugfix/issue-name`).
   - **Merging**: 
     - Merge feature branches into `develop` once they are complete and verified.
     - Merge `develop` into `main` only when the code is fully verified and stable.

2. **Commits & Pushes**:
   - Automatically commit and push code changes to the remote repository once the task is complete and verified, using clear and descriptive commit messages.

# Karpathy Structured Agent Workflow

Please follow this structured workflow for all tasks in this workspace:

## 1. Layer 1: The Spec (Spezifikation)
- **Goal Interview**: Before editing any code or starting a complex build, interview the user to uncover the deep goal (what decisions or outcomes this task drives), not just the superficial task.
- **Project Context Lock**: Explicitly state and verify which project or directory (e.g., Website, C++ Game, Python Shooter, Godot Shooter) is targeted before making any changes.
- **Agile Spec-ing**: Bias towards smaller, compartmentalized implementation plans with tight scopes and clear checkpoints.

## 2. Layer 2: The Verifier (Verifikation)
- **Predefined Evaluation Criteria**: Define precise success criteria upfront.
- **Manual Verification Fallback**: If no automated tests exist, write a step-by-step manual verification checklist.
- **Critic Subagent**: For complex changes, launch a background Critic subagent to audit and verify changes before presenting them to the user.

## 3. Layer 3: Guardrail Buckets
- **Always Do**:
  - Run syntax/compilation checks before requesting feedback.
  - Run `git status` and verify you are on the correct branch (`develop` or feature branch) before starting development.
- **Ask First**:
  - Start long-running background processes (e.g. servers).
  - Install new package dependencies.
- **Never Do**:
  - Commit or push directly to `main`.
  - Hardcode secrets, API keys, or credentials.


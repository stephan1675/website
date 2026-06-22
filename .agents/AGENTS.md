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

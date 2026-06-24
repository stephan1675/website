---
name: capture_portal_screenshot
description: Capture a high-resolution screenshot of the running local portal (Command Center) using a headless Playwright Chromium instance.
---

# Skill: Capture Portal Screenshot

This skill uses a headless Playwright Chromium instance to log in as the user `steste`, select the active project, and capture a screenshot of the local portal.

## Usage

Run the Python helper script from the workspace root:

```bash
python .agents/skills/capture_portal_screenshot/scripts/take_screenshot.py
```

The screenshot will be saved to `screenshot.png` in the workspace root.

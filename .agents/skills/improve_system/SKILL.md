---
name: improve_system
description: Refine, update, or extend the agent's internal operating system, including global/project-scoped rules (AGENTS.md), advisor profiles, user profile, or custom skills under the .agents directory.
---

# Skill: Improve System

This skill allows the agent to systematically update the rules, profiles, and custom skills that govern the agent's behavior in this workspace.

## Triggering Guidelines
Trigger this skill when:
- The user requests a change to how you operate (e.g. "always do X", "update your guidelines for python").
- You identify an inefficiency or missing instruction in the developer workflows, coding standards, or project structure.
- The user updates their career goals, active modules, or profiles.

## Execution Workflow

1. **Identify the Target File**:
   - For developer workflow or coding standards: `.agents/AGENTS.md`
   - For user goals, background, or study progress: `.agents/knowledge/me/user_profile.md`
   - For advisor profiles: `.agents/knowledge/advisors/`
   - For custom skills: `.agents/skills/<skill_name>/SKILL.md`

2. **Draft the Modification**:
   - Plan changes to be precise and clear.
   - Keep instructions concise, actionable, and formatted in clean markdown.

3. **Verify and Commit**:
   - Verify there are no YAML syntax errors in modified skills.
   - Present the changes clearly to the user for feedback.
   - Commit the updates to the active development branch.

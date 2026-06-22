---
name: skill_name_in_snake_case
description: A short, concise description of what the skill does and when the agent should use it.
---

# Skill: Skill Title

Provide a detailed description of the custom skill's purpose and its primary goals.

## Triggering Guidelines
- State the exact keywords, prompts, or circumstances under which this skill is triggered.
- Keep the triggering criteria simple and clear.

## Execution Workflow
Detail the step-by-step procedure the agent must follow when this skill is invoked:

1. **Step One**: Describe the initial step (e.g. loading context, verifying inputs).
2. **Step Two**: Describe the core processing or action.
3. **Step Three**: Describe the outputs, validation, or save actions.

## Customization & Resources
If this skill requires additional files, store them in the following subdirectories:
- `scripts/`: Python or batch scripts extending the skill.
- `examples/`: Reference implementations and input/output samples.
- `resources/`: Shared templates, assets, or data files.
- `references/`: Extra documentation or detailed API specs (keep `SKILL.md` under 500 lines).

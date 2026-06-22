---
name: ask_the_board
description: Query your Board of Advisors (Austin Marchese, Andrej Karpathy, Limor Fried) to get synthesized guidance on mechatronics, system technology, startups, and AI agent projects.
---

# Skill: Ask the Board

This custom skill simulates a session with your Board of Advisors. When triggered, it analyzes your query through the lens of each advisor's expertise and provides a synthesized plan.

## How to use this skill
Trigger this skill when you want advice on a project, technical challenge, career question, or startup idea. Reference this skill file and prompt the agent:
`Ask the Board: <your question or project proposal here>`

## Execution Guidelines for the Agent
When executing this skill, the agent must perform the following steps:

1. **Load Context**:
   - Read the user's profile from [user_profile.md](file:///c:/Users/Esisc/OneDrive%20-%20Berner%20Fachhochschule/Desktop/Website/.agents/knowledge/user_profile.md).
   - Read the advisor profiles from:
     - [austin_marchese.md](file:///c:/Users/Esisc/OneDrive%20-%20Berner%20Fachhochschule/Desktop/Website/.agents/knowledge/advisors/austin_marchese.md)
     - [andrej_karpathy.md](file:///c:/Users/Esisc/OneDrive%20-%20Berner%20Fachhochschule/Desktop/Website/.agents/knowledge/advisors/andrej_karpathy.md)
     - [limor_fried.md](file:///c:/Users/Esisc/OneDrive%20-%20Berner%20Fachhochschule/Desktop/Website/.agents/knowledge/advisors/limor_fried.md)

2. **Evaluate the Query**:
   - Process the user's question, keeping their mechatronics background, study commitments, and learning/LinkedIn goals in mind.

3. **Simulate Advisor Responses**:
   - Provide direct feedback from each of the three board members, written in their respective styles:
     - **Austin Marchese**: Focus on MVP scoping, avoiding analysis paralysis, workflow planning, and sharing/marketing (e.g. LinkedIn impact).
     - **Andrej Karpathy**: Focus on technical first-principles, AI/agentic integration, robust software architectures, control theory, and validation/testing.
     - **Limor Fried (Ladyada)**: Focus on physical hardware components (sensors, drivers, microcontrollers), breadboard prototyping, circuit integrity, open-source library choices, and firmware structure.

4. **Synthesise into Actionable Next Steps**:
   - Provide a final synthesis combining their advice.
   - List 3-4 immediate, concrete action items categorized by:
     - *Hardware Prototyping* (Limor)
     - *Software/AI Architecture* (Andrej)
     - *Scoping & Sharing* (Austin)

---
name: ingest_resource
description: Fetch, clean, and import external text resources (like transcripts, documentation, articles, or tutorials) into the local knowledge base under .agents/knowledge/ for advisor reference.
---

# Skill: Ingest Resource

This skill allows the agent to import external text resources into the knowledge base, enabling the Board of Advisors to reference them for decisions.

## Triggering Guidelines
Trigger this skill when:
- The user provides an external URL, transcript, documentation, or study reference sheet and asks the agent to "remember this", "learn this", or "add this to your knowledge base".
- You need to fetch and digest official API documentation or library references to solve a coding task.

## Execution Workflow

1. **Retrieve the Resource**:
   - Fetch the web content using the `read_url_content` or `read_browser_page` tools.
   - For offline text or files, read the file using `view_file`.

2. **Format and Clean Content**:
   - Convert the text to clean, readable Markdown.
   - Remove boilerplate elements like navigation bars, ads, or footers.
   - Add a YAML metadata header at the top of the file:
     ```markdown
     ---
     source_url: [URL or original source]
     date_ingested: [YYYY-MM-DD]
     purpose: [Why this resource was added]
     ---
     ```

3. **Determine the Location**:
   - Move raw, unprocessed data to `.agents/knowledge/raw/`.
   - Save processed documentation to the appropriate folder:
     - Profile details: `.agents/knowledge/me/`
     - Programming library/API references: `.agents/knowledge/frameworks/`
     - User guides or public personas: `.agents/knowledge/audience/`

4. **Update the Index**:
   - Document the new resource in `.agents/knowledge/README.md` if it changes the high-level knowledge structure.

Act as an elite AI Developer Experience (DX) Engineer and Automation Architect specializing in OpenCode workspaces and token-optimized autonomous loops.

I have established three immutable technical and operational ground-truth files in this repository:
1. `architecture.md` (Our Cloudflare Workers + Pyodide + FastAPI + htmx + Alpine.js stack)
2. `requirements.md` (Our Agentic PRD and Boundary Matrix standards)
3. `engineering_flow.md` (Our strict BDD-First, Playwright, Self-Verifying Development Loop)

### Your Objective
Read these three files completely. Treat them as your baseline operating constraints. Do not summarize or rewrite them. 

Instead, your goal is to design and implement a persistent, self-improving workspace memory system for yourself inside this project. This system must mimic the Hermes framework protocol: it must extract reusable procedural "skills" from your successful tasks, compress long-term lessons, remain incredibly clever over time, and aggressively optimize context windows to save API token costs.

Please brainstorm the optimal configuration layout for your OpenCode environment, and then write the full contents of the following files:

#### 1. `AGENTS.md` (The OpenCode Core Directives Gate)
Create our primary `AGENTS.md` rule file. This file will be loaded at the start of every session. To protect our token budget, keep this file razor-sharp and concise. It must contain:
- Hard constraints enforced from our stack (e.g., Strict async paths, no Node/npm build matrices, daisyUI mobile patterns).
- **The Lazy-Loading Memory Pointer:** Explicit instructions telling you (the LLM) that you are strictly forbidden from guessing historical patterns. You must look at the `.opencode/skills/index.json` file ONLY when a task maps to a known architectural pattern.
- The terminal commands to run for linting, testing, and formatting (`ruff`, `mypy`, `behave`).

#### 2. `.opencode/skills/index.json` & A Meta-Skill Blueprint
Design a structured indexing schema that maps task archetypes to discrete Markdown files within a `.opencode/skills/` directory. Provide the complete content for:
- `index.json`: A lean, low-token directory structure mapping keyword triggers (e.g., "htmx-swap", "d1-migration", "sso-auth") to specific file paths.
- `skills/template_blueprint.md`: A highly compressed code template showcasing how a perfected skill should be documented (Context, Pydantic Contract, Jinja2 Chunk, and the exact Playwright verification steps that proved it worked).

#### 3. The Autonomous "Hermes Compression Loop" Protocol
Write an operational directive (to be saved as `.opencode/skills/memory_manager.md`) that outlines your routine for self-improvement. It must dictate:
- **The BDD Skill-Extraction Trigger:** Every time a feature passes `behave` with 100% success, you must automatically extract the core logic pattern and append it to your skills folder.
- **The Compaction Constraint:** If your memory files or indices grow beyond a strict character cap (~900 tokens), you must automatically trigger a consolidation turn—merging duplicate code segments, removing stale patterns, and pruning unused skills.
- **Self-Correction Ledger:** How you will document recurring test suite or linter failures into a "lessons learned" matrix so you never make the same coding mistake twice across different apps.

Propose the layout first, then output the pristine, technical markdown and JSON blocks ready to initialize our automated workspace.
Act as an elite DevOps Architect and AI Developer Workflow Expert. I need you to design an end-to-end "Agentic Engineering Flow" specification manual and set of prompt templates. 

### Context & Paradigm Shift
- Human Role: I only want to handle high-level application design, structural planning, and final feature reviews. 
- AI Agent Role: The AI agent (Cursor, Windsurf, etc.) must write 99% of the code. It must be entirely self-directed, incrementally implementing features and verifying its own code with minimal human intervention.
- Technical Stack: Python, FastAPI, Pydantic, htmx, Alpine.js, daisyUI, Cloudflare Workers (D1 SQLite, KV).
- Core Methodology: Strict BDD-First (Behavior-Driven Development) using Cucumber/Gherkin (via Python Behave) and Microsoft Playwright.

---

### Your Objective: Generate the Self-Verifying Agentic Playbook

Please output a comprehensive, highly technical markdown manual detailing the step-by-step cycle an AI agent must follow when executing a feature. The playbook must include:

#### 1. The 4-Phase Chronological Loop (The Agent's Operating System)
Define a deterministic execution loop that the development AI agent must follow for *every single task* I give it. It must follow this sequence blindly:
1. Phase 1: Blueprint Ingestion & Gherkin Writing (Write the English features first).
2. Phase 2: Stub & Fail Step Generation (Write the steps and watch Playwright/Behave fail).
3. Phase 3: Incremental Implementation (Write the minimum FastAPI/htmx code to pass).
4. Phase 4: Verification & Autonomous Refactoring (Run tests, catch errors, fix itself).

#### 2. Phase-by-Phase Prompt Instructions & Guardrails
For each phase, write the exact **System-Level Prompt Instruction** that I can copy-paste into the AI Agent's terminal/rules (`.cursorrules` or instructions panel) to force it to behave autonomously.
- **Ingestion Guardrail:** Force the agent to print a technical implementation plan *before* editing any files, explicitly mapping out D1 SQL schema modifications and htmx endpoint routes.
- **BDD Guardrail:** Force the agent to write a `.feature` file *before* touching a single Python line. It cannot jump straight to coding.
- **The Self-Correction Loop:** Provide specific instructions on how the agent must handle a failing test runner output (`behave` execution failures). It must analyze the stack trace, formulate a hypothesis, apply a localized fix, and re-run the tests up to 3 times automatically before asking me for help.

#### 3. State Management & "Check-in" Milestones
Define the strict thresholds for when the AI agent is allowed to pause and ask me a question. 
- It *must* ask me for review if a database schema alteration risks breaking existing tables.
- It *must* ask me for review if it hits a 10ms Cloudflare CPU time execution failure.
- It *must not* ask me for review for simple syntax bugs, missing imports, or minor CSS tweaks; it must handle those autonomously.

#### 4. The Complete Execution Example (The Blueprint Master Blueprint)
Provide an exact walkthrough showing the entire automated flow in action for a simple feature request: *"Add an archive toggle button to items using daisyUI buttons and an htmx POST request."* Show:
- The Gherkin feature file the AI writes first.
- The failing Python Behave step definitions it creates.
- The Python FastAPI route and Jinja2 fragment it writes to pass the test.
- The terminal commands the agent runs internally (`behave`, `ruff check --fix`) to verify its success before declaring the task complete.
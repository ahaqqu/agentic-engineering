Act as an elite AI Product Strategist and Principal Engineer. I need you to create a comprehensive framework, set of guidelines, and templates for brainstorming, designing, and writing product requirements for a suite of applications I plan to build.

### Context & Goals
1. Tech Stack Constraint: Every app will be built using a Hypermedia-Driven Architecture (FastAPI, Python, Pydantic, htmx, Alpine.js, daisyUI) deployed as a serverless Cloudflare Worker (D1 SQL database, KV store). Apps will be wrapped via Capacitor.js for iOS/Android.
2. AI-Agentic Development: 99% of the code will be written by AI agents (Cursor, Windsurf, etc.). Therefore, the requirements generated using this framework must act as deterministic, context-rich blueprints that an AI code-gen tool can ingest and execute flawlessly on the first try.
3. Budget & Scale: Prototypes must cost $0 to run, strictly respecting Cloudflare’s 10ms CPU free-tier execution limit.
4. Scale: I plan to build multiple apps using this blueprint. The requirements framework must be repeatable, modular, and fast to execute.

---

### Your Objective: Generate the Product Engineering Playbook

Please output a comprehensive markdown guide containing the following structural systems:

#### 1. The "Vibe-to-Spec" Brainstorming Protocol
Design a step-by-step interactive framework I can use to brainstorm a raw app idea. It should guide me through translating a chaotic "vibe" or user story into technical constraints. Include a list of strategic questions to uncover:
- Core data models (D1 SQLite schema implications).
- What interactions require server-side rendering (htmx) vs. local UI snappy interactions (Alpine.js).
- Mobile-specific view adjustments (Capacitor/PWA layouts).

#### 2. The Agentic PRD (Product Requirement Document) Template
Create a highly structured PRD template designed specifically for AI consumption. Standard PRDs are too verbose for LLMs. This template must include explicit sections for:
- System Overview & Tech Stack alignment.
- Database Schema Mapping: Explicit definitions for D1 Tables, columns, types, and constraints.
- Ephemeral Cache Mapping: Defining exactly what data strings live in Cloudflare KV.
- Endpoint Specification Matrix: A clean table defining Route, HTTP Method, Triggering htmx attribute, Expected Inputs (Pydantic Schema format), and Expected Output (Jinja2 HTML fragment layout snippet).
- Component Interactivity Boundaries: Defining exactly which behaviors are driven by htmx over-the-wire vs. client-side Alpine.js toggle states.

#### 3. BDD-First Requirement Blueprinting
Provide guidelines on how to write product requirements directly alongside Cucumber/Gherkin (`Feature / Given / When / Then`) feature rules. Show how a feature can be designed from day one so that the AI writing the code can read the PRD, look at the `.feature` file, and instantly know if the code it wrote is correct.

#### 4. The "10ms Guardrail" Checklist
Include a standard requirement checklist template that evaluates every feature's performance before code generation begins. It must enforce constraints like: "Does this htmx fragment load a massive dataset that requires pagination?", "Are we utilizing KV caching for this layout element?", and "Is this endpoint execution path asynchronous to avoid locking worker threads?"

#### 5. A Concrete Example: A Token-Gated ToDo PWA Spec
To prove the framework works, provide a completely filled-out example of a simple requirement spec using this newly created framework for a "Collaborative, Mobile-First ToDo List with Google SSO."

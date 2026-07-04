Act as an elite software architect specializing in serverless cloud infrastructures, hypermedia-driven systems (HDA), and AI-driven automated application development ("vibe coding").

### Context
I am building a foundational, boilerplate architecture that will serve as the template for multiple independent applications I plan to build. 
* Production Target: 99% of the code will be written by AI engineering agents (e.g., Cursor, Windsurf, Bolt) guided by my natural language instructions.
* Budget: Total prototyping costs must stay strictly at $0.00 (utilizing completely free cloud tiers). Scale costs must remain remarkably cheap.
* Deployment Model: True write-once, deploy everywhere (Web App, native iOS App, native Android App) from a single repository.

### Target Tech Stack Blueprint
1. Infra & Computing: Cloudflare Workers Python environment (Pyodide V8 Isolate runtime).
2. Database: Cloudflare D1 (Serverless relational SQLite at the edge).
3. Cache & Session Tracking: Cloudflare KV (Key-Value) store.
4. Backend Framework: FastAPI (Async routes) + Pydantic v2 + Jinja2 Templates.
5. Hypermedia Frontend (No-Build Node Matrix): htmx 2.x + Alpine.js 3.x + Tailwind CSS (via CDN) + daisyUI 5.x.
6. Authentication: Google OAuth2 Single Sign-On (SSO) passing identity metrics into HttpOnly, Secure, SameSite=Lax browser cookies.
7. Mobile Wrapper: Capacitor.js pointing the native iOS and Android WebViews straight to the production Cloudflare web instance.
8. Code Quality Gate: Ruff (linting/formatting) + Mypy (strict type hints).
9. Quality Assurance BDD Stack: Python Behave (Cucumber Gherkin `.feature` syntax Parsing) driving headless Microsoft Playwright instances with built-in Google SSO mock bypass modules.
10. Automation CI/CD: GitHub Actions pipelines compiling tests, running style enforcement checkers, and automatically running 'npx wrangler deploy'.

---

### Your Objective: Review, Validate, and Systematically Document

Please thoroughly analyze this unified technical architecture specification. Provide an honest, highly technical validation report structured around the five analysis points below, and then **generate the foundational architectural markdown files for my repository.**

#### Part 1: Architecture Stress-Testing & Validation

1. **The 10ms CPU "Free-Tier" Hard Limit Evaluation:** Because Cloudflare Workers Free Tier enforces a strict 10ms CPU execution cap per invocation (excluding network wall-clock I/O wait times), assess the viability of Python/FastAPI rendering HTML chunks via Jinja2 under this constraint. Point out exact execution bottlenecks (e.g., Pyodide warm starts, heavy Pydantic validations, string parsing) and propose strict programmatic design patterns the AI engineering agents must implement to preserve a sub-5ms timeline.
2. **Agentic Friendly & Vibe-Coding Friction Score:** Rate this stack's compatibility with AI code generation tools on a scale of 1-10. Look closely for potential prompt-loops or common traps where code-writing AI agents tend to break down (e.g., asset pipelines without npm/Node, routing mismatches when handling partial htmx elements, or state desynchronization).
3. **Hypermedia Mobile PWA + Capacitor Feasibility:** Critically review using htmx and Alpine.js inside an iOS/Android Capacitor wrapper. Identify cross-platform UX hurdles (click/tap latency, offline service-worker interception, hardware APIs) and confirm if the mobile WebView wrapper will trigger unexpected CORS browser policies when htmx dispatches AJAX network swaps back to the edge origin.
4. **The Unified BDD Automation Pipeline Review:** Evaluate the Cucumber/Behave/Playwright/GitHub Actions pipeline. Is this configuration optimal for headless CI environments? Review the logic of bypassing Google SSO via Playwright browser cookie injection or secret mock routes to ensure test isolation doesn't compromise production database configurations.
5. **Blindspots & Edge Cases:** Detail any overlooked limitations, security vulnerabilities (like session hijacking, cache poisoning via Cloudflare KV, or D1 concurrency handling), or single points of failure.

---

#### Part 2: Required Architectural Deliverables

Once the validation is complete, act as a technical writer and output the following comprehensive documentation files in markdown syntax that I can directly save to my project:

1. **`ARCHITECTURE_DEEP_DIVE.md`**
   * A comprehensive system topology guide mapping out exact directory layouts optimized for AI agent readability.
   * Clear visual flow charts tracking data mutations (Client -> htmx -> Cloudflare Worker Engine -> Pydantic Validation -> D1 DB Execution -> Jinja2 Macro Output -> DOM Swap).
   * Strict coding guardrails, performance covenants, and anti-patterns that AI agents *must never use* to avoid breaking the 10ms compute threshold.

2. **`SECURITY_AND_AUTH_RUNBOOK.md`**
   * A rigorous breakdown of the Google SSO lifecycle engineered for this exact stack.
   * A clear definition of the cookie security properties (`HttpOnly`, `Secure`, `SameSite=Lax`) and how they prevent XSS/CSRF.
   * Instructions for managing and setting up production environment variables securely via Cloudflare Wrangler secrets (`.dev.vars`) without hardcoding values in code.

3. **`TESTING_AND_QUALITY_SPEC.md`**
   * A complete implementation reference manual for Cucumber BDD testing.
   * Production-ready boilerplate code templates for:
     - A Gherkin `.feature` file showing testing paths for both htmx API endpoints and live Playwright UI workflows.
     - The corresponding Python Behave step definitions (`api_steps.py` and `ui_steps.py`) showcasing exactly how to bypass Google SSO via token/cookie injection.
     - A pristine, optimized `.github/workflows/ci-cd.yml` configuration file that handles Ruff formatting, Mypy type validation, Playwright execution, and headless Wrangler deployment.

# Skill: mobile-capacitor            (seed · from docs/SECURITY_AND_AUTH_RUNBOOK.md §3)

## Context
iOS/Android shell work: deep links, native OAuth handoff, offline fallback.
NOT a remote-URL wrapper (App Store 4.2). NOT OAuth inside the WebView (Google blocks it).

## Pattern
```ts
// capacitor/ shell bundles: splash, offline.html, error-retry, local htmx/alpine/css.
// capacitor.config.ts: appId com.<org>.<app>; NO server.url in production builds.

// auth handoff (shell side):
import { Browser } from "@capacitor/browser";
import { App } from "@capacitor/app";
await Browser.open({ url: `${ORIGIN}/auth/login?platform=mobile` }); // system browser
App.addListener("appUrlOpen", async ({ url }) => {
  const code = new URL(url).searchParams.get("token");     // com.org.app://auth?token=…
  await fetch(`${ORIGIN}/auth/exchange`, { method: "POST", body: JSON.stringify({ code }) });
  webview.location.replace(`${ORIGIN}/`);                   // session cookie now set
});

// server: one-time code = 60s-TTL D1 row, single-use burn on /auth/exchange.
```

## Proof
```gherkin
@api Scenario: /auth/exchange burns the one-time code (second call → 401)
```
Manual device pass required for store-facing changes (Playwright can't cover Custom Tabs).

## Gotchas
- Register the custom scheme in AndroidManifest + Info.plist; test cold-start deep link.
- Offline: navigator.onLine listener → bundled offline.html with retry, never blank WebView.
- Mobile layouts: daisyUI btm-nav/drawer, 44px targets (PRD Pass 4).

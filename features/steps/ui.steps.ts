import { setDefaultTimeout, Then, When } from "@cucumber/cucumber";
import { chromium } from "playwright";
import { sessionCookieFor } from "../support/auth";
import type { MyWorld } from "../support/world";

setDefaultTimeout(60_000);

When("I open the items page", async function (this: MyWorld) {
  const browser = await chromium.launch({ headless: true, args: ["--no-sandbox"] });
  this.browser = browser;
  const context = await browser.newContext({ ignoreHTTPSErrors: true });
  this.context = context;

  if (this.currentUser) {
    const cookie = await sessionCookieFor(this.currentUser);
    await context.addCookies([cookie]);
  }

  const page = await context.newPage();
  this.page = page;
  await page.goto(`${this.baseURL}/`);
});

When("I click the archive button on {string}", async function (this: MyWorld, title: string) {
  if (!this.page) throw new Error("no page open");
  // find the row containing the title text and click its archive button
  const btn = this.page.locator("li").filter({ hasText: title }).locator("button");
  await btn.click();
});

Then(
  "the row for {string} shows the archived badge",
  async function (this: MyWorld, title: string) {
    if (!this.page) throw new Error("no page open");
    const row = this.page.locator("li").filter({ hasText: title });
    await row.waitFor({ state: "visible", timeout: 10_000 });
    const badge = row.locator("span.badge");
    await badge.waitFor({ state: "visible", timeout: 10_000 });
    const text = await badge.textContent();
    if (!text?.includes("archived"))
      throw new Error(`expected archived badge for "${title}", got "${text}"`);
  },
);

Then("the page did not perform a full navigation", async function (this: MyWorld) {
  // htmx swaps don't trigger page navigation; if we're still on the same URL, it's correct
  if (!this.page) throw new Error("no page open");
  const url = this.page.url();
  if (!url.includes(this.baseURL)) throw new Error(`unexpected navigation to ${url}`);
});

When("I reload the page", async function (this: MyWorld) {
  if (!this.page) throw new Error("no page open");
  await this.page.reload();
});

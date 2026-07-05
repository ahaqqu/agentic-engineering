import { Given, Then, When } from "@cucumber/cucumber";
import { signedInCookie } from "../support/auth";
import type { MyWorld } from "../support/world";

Given("I am signed in as {string}", async function (this: MyWorld, email: string) {
  this.currentUser = email;
});

Given("I have no session", async function (this: MyWorld) {
  this.currentUser = null;
});

Given("an item {string} exists", async function (this: MyWorld, title: string) {
  const cookie = await signedInCookie(this.currentUser ?? "test-default@example.com");
  const res = await fetch(`${this.baseURL}/items`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Cookie: `session=${cookie}`,
      Origin: this.baseURL,
    },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error(`create item failed: ${res.status} ${await res.text()}`);
  const html = await res.text();
  const match = html.match(/id="item-(\d+)"/);
  if (match) this.lastItemIds[title] = Number(match[1]);
  this.lastResponse = res;
});

When("I POST to the archive endpoint for {string}", async function (this: MyWorld, title: string) {
  const id = this.lastItemIds[title];
  if (!id) throw new Error(`no item id found for "${title}"`);
  const cookie = this.currentUser ? await signedInCookie(this.currentUser) : "";
  const headers: Record<string, string> = { Origin: this.baseURL };
  if (cookie) headers.Cookie = `session=${cookie}`;
  else headers["HX-Request"] = "true"; // simulate htmx → middleware returns 401 directly
  const res = await fetch(`${this.baseURL}/items/${id}/archive`, {
    method: "POST",
    headers,
  });
  this.lastResponse = res;
});

Then("the response status is {int}", async function (this: MyWorld, status: number) {
  if (!this.lastResponse) throw new Error("no response to check");
  if (this.lastResponse.status !== status) {
    throw new Error(
      `expected status ${status}, got ${this.lastResponse.status}: ${await this.lastResponse.text()}`,
    );
  }
});

Then(
  "the response HTML contains an element {string}",
  async function (this: MyWorld, selector: string) {
    if (!this.lastResponse) throw new Error("no response to check");
    const html = await this.lastResponse.text();
    if (selector.startsWith("[") && selector.endsWith("']")) {
      const attr = selector.slice(1, -2);
      const [name, raw] = attr.split("=") as [string, string];
      const val = raw.replace(/['"]/g, "");
      if (!html.includes(`${name}="${val}"`) && !html.includes(`${name}='${val}'`)) {
        throw new Error(`expected ${selector} not found in:\n${html}`);
      }
    } else if (!html.includes(selector)) {
      throw new Error(`expected "${selector}" not found in:\n${html}`);
    }
  },
);

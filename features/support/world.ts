import { type IWorld, type IWorldOptions, setWorldConstructor } from "@cucumber/cucumber";
import type { Browser, BrowserContext, Page } from "playwright";

export interface MyWorld extends IWorld {
  baseURL: string;
  currentUser: string | null;
  lastResponse: Response | null;
  lastItemIds: Record<string, number>;
  browser: Browser | null;
  context: BrowserContext | null;
  page: Page | null;
}

class CustomWorld implements MyWorld {
  baseURL = "";
  currentUser: string | null = null;
  lastResponse: Response | null = null;
  lastItemIds: Record<string, number> = {};
  browser: Browser | null = null;
  context: BrowserContext | null = null;
  page: Page | null = null;

  // biome-ignore lint/suspicious/noExplicitAny: cucumber-js internal types not exported
  readonly attach: any;
  // biome-ignore lint/suspicious/noExplicitAny: cucumber-js internal types not exported
  readonly log: any;
  // biome-ignore lint/suspicious/noExplicitAny: cucumber-js internal types not exported
  readonly link: any;
  // biome-ignore lint/suspicious/noExplicitAny: cucumber-js internal types not exported
  readonly parameters: any;
  // biome-ignore lint/suspicious/noExplicitAny: cucumber-js internal types not exported
  [key: string]: any;

  constructor(options: IWorldOptions) {
    this.attach = options.attach;
    this.log = options.log;
    this.link = options.link;
    this.parameters = options.parameters;
  }
}

setWorldConstructor(CustomWorld);

import { Hono } from "hono";
import { cors } from "hono/cors";
import { csrf } from "hono/csrf";
import { secureHeaders } from "hono/secure-headers";
import { requireSession, session } from "./lib/session";
import { healthRoute } from "./routes/health";
import { itemsRoute } from "./routes/items";

export type Item = {
  id: number;
  title: string;
  done: number;
  archived: number;
};

export type Env = {
  Bindings: {
    DB: D1Database;
    SESSION_SECRET: string;
  };
  Variables: {
    session: { sub: string; email: string; name: string; iat: number; exp: number };
  };
};

const app = new Hono<Env>();

app.use("*", secureHeaders());
app.use("*", cors({ origin: "*", credentials: true }));
app.use("/items/*", csrf({ origin: (_origin, c) => !!c.req.header("Origin") }));
app.use("*", session());

app.route("/health", healthRoute);
app.route("/items", itemsRoute);

app.get("/", requireSession, async (c) => {
  const { sub } = c.get("session");
  const { results } = await c.env.DB.prepare(
    "SELECT id, title, done, archived FROM items WHERE user_id = ? ORDER BY created_at DESC LIMIT 50",
  )
    .bind(sub)
    .all<{ id: number; title: string; done: number; archived: number }>();
  return c.html(<ItemsPage items={results} user={c.get("session")} />);
});

function ItemsPage({
  items,
}: {
  items: { id: number; title: string; done: number; archived: number }[];
  user: { sub: string; email: string; name: string };
}) {
  return (
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Items</title>
        <link href="/app.css" rel="stylesheet" />
        <script src="/htmx.min.js" />
      </head>
      <body class="p-4 max-w-lg mx-auto">
        <h1 class="text-xl font-bold mb-4">Items</h1>
        <ul id="item-list" class="space-y-2">
          {items.map((item) => (
            <ItemRow item={item} />
          ))}
        </ul>
      </body>
    </html>
  );
}

function ItemRow({
  item,
}: {
  item: { id: number; title: string; done: number; archived: number };
}) {
  return (
    <li
      id={`item-${item.id}`}
      class="flex items-center gap-2 py-2"
      data-archived={String(!!item.archived)}
    >
      <span class={`flex-1 ${item.archived ? "line-through opacity-50" : ""}`}>{item.title}</span>
      {item.archived ? <span class="badge">archived</span> : null}
      <button
        type="button"
        class="btn btn-sm"
        hx-post={`/items/${item.id}/archive`}
        hx-target={`#item-${item.id}`}
        hx-swap="outerHTML"
      >
        {item.archived ? "Unarchive" : "Archive"}
      </button>
    </li>
  );
}

export default app;

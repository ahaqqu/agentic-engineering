import { zValidator } from "@hono/zod-validator";
import { Hono } from "hono";
import { z } from "zod";
import type { Env, Item } from "..";
import { requireSession } from "../lib/session";

const ArchiveParams = z.object({ id: z.coerce.number() });
const CreateBody = z.object({ title: z.string().min(1).max(200) });

export const itemsRoute = new Hono<Env>()
  .use("*", requireSession)

  .post("/", zValidator("json", CreateBody), async (c) => {
    const { title } = c.req.valid("json");
    const { sub } = c.get("session");
    const item = await c.env.DB.prepare(
      "INSERT INTO items (user_id, title) VALUES (?1, ?2) RETURNING id, title, done, archived",
    )
      .bind(sub, title)
      .first<Pick<Item, "id" | "title" | "done" | "archived">>();
    if (!item) return c.text("create failed", 500);
    return c.html(<ItemRow item={item} />, 201);
  })

  .post("/:id/archive", zValidator("param", ArchiveParams), async (c) => {
    const { id } = c.req.valid("param");
    const { sub } = c.get("session");
    const item = await c.env.DB.prepare(
      "UPDATE items SET archived = 1 - archived WHERE id = ?1 AND user_id = ?2 RETURNING id, title, done, archived",
    )
      .bind(id, sub)
      .first<Item>();
    if (!item) return c.notFound();
    return c.html(<ItemRow item={item} />);
  });

function ItemRow({ item }: { item: Item }) {
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

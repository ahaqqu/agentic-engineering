from dataclasses import dataclass


@dataclass
class Item:
    id: int
    title: str
    done: bool = False
    archived: bool = False


class DB:
    def __init__(self, d1):
        self._d1 = d1

    async def list_all(self, user_sub: str) -> list[Item]:
        stmt = self._d1.prepare(
            "SELECT id, title, done, archived FROM items "
            "WHERE user_id = ? ORDER BY created_at DESC LIMIT 50"
        ).bind(user_sub)
        result = await stmt.all()
        items = []
        for row in result.results or []:
            items.append(
                Item(
                    id=row["id"],
                    title=row["title"],
                    done=bool(row["done"]),
                    archived=bool(row["archived"]),
                )
            )
        return items

    async def create(self, user_sub: str, title: str) -> Item | None:
        stmt = self._d1.prepare(
            "INSERT INTO items (user_id, title) VALUES (?, ?) RETURNING id, title, done, archived"
        ).bind(user_sub, title)
        row = await stmt.first()
        if not row:
            return None
        return Item(
            id=row["id"], title=row["title"], done=bool(row["done"]), archived=bool(row["archived"])
        )

    async def toggle_archive(self, item_id: int, user_sub: str) -> Item | None:
        stmt = self._d1.prepare(
            "UPDATE items SET archived = 1 - archived "
            "WHERE id = ? AND user_id = ? "
            "RETURNING id, title, done, archived"
        ).bind(item_id, user_sub)
        row = await stmt.first()
        if not row:
            return None
        return Item(
            id=row["id"], title=row["title"], done=bool(row["done"]), archived=bool(row["archived"])
        )

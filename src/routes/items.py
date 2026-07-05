from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from lib.session import require_session
from lib.csrf import csrf_check
from db.items import DB
from templates import render_template

router = APIRouter(dependencies=[Depends(require_session), Depends(csrf_check)])


async def _get_db(request: Request) -> DB:
    return DB(request.scope["env"].DB)


@router.post("", response_class=HTMLResponse, status_code=201)
async def create_item(
    request: Request,
    session: dict = Depends(require_session),
    db: DB = Depends(_get_db),
):
    body = await request.json()
    title = body.get("title", "")
    if not isinstance(title, str) or not (1 <= len(title) <= 200):
        return PlainTextResponse("title must be 1-200 chars", status_code=400)
    item = await db.create(session["sub"], title)
    if not item:
        return PlainTextResponse("create failed", status_code=500)
    html = render_template("item_row.html", request=request, item=item)
    return HTMLResponse(html, status_code=201)


@router.post("/{item_id}/archive", response_class=HTMLResponse)
async def archive_item(
    request: Request,
    item_id: int,
    session: dict = Depends(require_session),
    db: DB = Depends(_get_db),
):
    item = await db.toggle_archive(item_id, session["sub"])
    if not item:
        return PlainTextResponse("not found", status_code=404)
    html = render_template("item_row.html", request=request, item=item)
    return HTMLResponse(html)

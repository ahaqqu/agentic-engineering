from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from lib.session import session_middleware, require_session
from db.items import DB
from templates import render_template
from routes.items import router as items_router

app = FastAPI()

app.middleware("http")(session_middleware)

app.include_router(items_router, prefix="/items")


@app.get("/health", response_class=PlainTextResponse)
async def health():
    return "ok"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, session: dict = Depends(require_session)):
    db = DB(request.scope["env"].DB)
    items = await db.list_all(session["sub"])
    is_hx = request.headers.get("HX-Request") == "true"
    if is_hx:
        html = render_template("item_list.html", request=request, items=items)
    else:
        html = render_template("layout.html", request=request, items=items, user=session)
    return HTMLResponse(html)

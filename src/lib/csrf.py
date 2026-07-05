from fastapi import Request, HTTPException


async def csrf_check(request: Request):
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    origin = request.headers.get("Origin")
    if not origin:
        raise HTTPException(status_code=403, detail="CSRF: missing Origin")
    host = request.headers.get("Host", "")
    if origin not in [f"http://{host}", f"https://{host}"]:
        raise HTTPException(status_code=403, detail="CSRF: Origin mismatch")

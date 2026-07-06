import hmac
import hashlib
import base64
import json
import time
from fastapi import Request, HTTPException


COOKIE_NAME = "session"
SESSION_TTL = 7 * 86400


def to_b64(data: dict) -> str:
    payload = json.dumps(data, separators=(",", ":"))
    return base64.urlsafe_b64encode(payload.encode()).rstrip(b"=").decode()


def from_b64(raw: str) -> dict | None:
    padded = raw + "=" * (4 - len(raw) % 4)
    try:
        return json.loads(base64.urlsafe_b64decode(padded))
    except Exception:
        return None


def sign_token(payload: dict, secret: str) -> str:
    encoded = to_b64(payload)
    sig = hmac.new(secret.encode(), encoded.encode(), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
    return f"{encoded}.{sig_b64}"


def verify_token(token: str, secret: str) -> dict | None:
    parts = token.rsplit(".", 1)
    if len(parts) != 2:
        return None
    encoded, sig_b64 = parts
    try:
        sig = base64.urlsafe_b64decode(sig_b64 + "=" * (4 - len(sig_b64) % 4))
    except Exception:
        return None
    expected = hmac.new(secret.encode(), encoded.encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(sig, expected):
        return None
    payload = from_b64(encoded)
    if not payload or "sub" not in payload:
        return None
    if payload.get("exp", 0) < time.time():
        return None
    return payload


def make_payload(sub: str, email: str, name: str) -> dict:
    now = int(time.time())
    return {"sub": sub, "email": email, "name": name, "iat": now, "exp": now + SESSION_TTL}


def _get_secret(request: Request) -> str:
    try:
        return request.scope["env"].SESSION_SECRET or "insecure-dev-default"
    except AttributeError:
        return "insecure-dev-default"
    except KeyError:
        return "insecure-dev-default"


async def session_middleware(request: Request, call_next):
    raw = request.cookies.get(COOKIE_NAME)
    session = None
    if raw:
        secret = _get_secret(request)
        session = verify_token(raw, secret)
    request.state.session = session
    response = await call_next(request)
    return response


async def require_session(request: Request) -> dict:
    session = getattr(request.state, "session", None)
    if not session:
        if request.headers.get("HX-Request") == "true":
            raise HTTPException(
                status_code=401,
                detail="Unauthorized",
                headers={"HX-Redirect": "/auth/login"},
            )
        raise HTTPException(status_code=302, headers={"Location": "/auth/login"})
    return session

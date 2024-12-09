from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timezone
import math
import secrets
import time

app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

COMMENTS = []
PAGE_SIZE = 100

# CSRF Token: A single global token for demonstration purposes
CSRF_TOKEN = secrets.token_urlsafe(32)

# Rate limiting config
RATE_LIMIT = 5  # Max requests per TIME_WINDOW
TIME_WINDOW = 60.0  # In seconds
request_logs = {}  # { ip: [timestamps_of_requests] }


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Basic Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Content Security Policy to disallow inline scripts
        # Only allow scripts and styles from 'self' and fonts from google's CDN
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "  # Added 'unsafe-inline'
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self'; "
            "connect-src 'self';"
        )
        return response


app.add_middleware(SecurityHeadersMiddleware)


def is_rate_limited(ip: str) -> bool:
    """Check and update rate limit status for a given IP."""
    now = time.time()
    timestamps = request_logs.get(ip, [])
    # Filter out old requests outside the TIME_WINDOW
    timestamps = [t for t in timestamps if t > now - TIME_WINDOW]
    # Add current request time
    timestamps.append(now)
    request_logs[ip] = timestamps
    return len(timestamps) > RATE_LIMIT


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, page: int = 1):
    total_comments = len(COMMENTS)
    total_pages = math.ceil(total_comments / PAGE_SIZE) if total_comments > 0 else 1
    page = max(1, min(page, total_pages))
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    current_comments = COMMENTS[start_idx:end_idx]

    # Pass CSRF token to the template
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "comments": current_comments,
            "current_page": page,
            "total_pages": total_pages,
            "csrf_token": CSRF_TOKEN,  # Ensure form includes this token
        },
    )


@app.post("/post-comment", response_class=HTMLResponse)
async def post_comment(
    request: Request, message: str = Form(...), csrf_token: str = Form(...)
):
    client_ip = request.client.host
    if is_rate_limited(client_ip):
        # Too many requests recently
        raise HTTPException(status_code=429, detail="Too Many Requests")

    # CSRF check
    if csrf_token != CSRF_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

    # Validate message
    message = message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    new_comment = {"message": message, "timestamp": datetime.now(timezone.utc)}
    COMMENTS.insert(0, new_comment)

    page = 1
    total_comments = len(COMMENTS)
    total_pages = math.ceil(total_comments / PAGE_SIZE) if total_comments > 0 else 1
    start_idx = 0
    end_idx = PAGE_SIZE
    current_comments = COMMENTS[start_idx:end_idx]

    return templates.TemplateResponse(
        "_comments.html",
        {
            "request": request,
            "comments": current_comments,
            "current_page": page,
            "total_pages": total_pages,
        },
    )


@app.get("/comments", response_class=HTMLResponse)
async def get_comments(request: Request, page: int = 1):
    client_ip = request.client.host
    if is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too Many Requests")

    total_comments = len(COMMENTS)
    total_pages = math.ceil(total_comments / PAGE_SIZE) if total_comments > 0 else 1
    page = max(1, min(page, total_pages))
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    current_comments = COMMENTS[start_idx:end_idx]

    return templates.TemplateResponse(
        "_comments.html",
        {
            "request": request,
            "comments": current_comments,
            "current_page": page,
            "total_pages": total_pages,
        },
    )

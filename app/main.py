from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.templating import Jinja2Templates
import os

# Import routers from routes directory
from app.routes import chat, blog

app = FastAPI()

# Hard-coded absolute paths (adjust as needed)
BASE_DIR = "/home/sawyer/dunamismax.com"
APP_DIR = os.path.join(BASE_DIR, "app")

STATIC_DIR = os.path.join(APP_DIR, "static")
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")

# Mount static files at /static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self'; "
            "connect-src 'self';"
        )
        return response


app.add_middleware(SecurityHeadersMiddleware)

# Include routers for different sections
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(blog.router, prefix="/blog", tags=["blog"])


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """
    The main landing page at https://dunamismax.com/
    This page will have links to /chat and /blog,
    allowing easy navigation to different sections of the site.
    """
    return templates.TemplateResponse("index.html", {"request": request})

# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from app.routers import blog
from app.database import engine, Base

# Ensure database tables are created if they don't exist yet.
# For production, rely on Alembic migrations. This is just a safeguard.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="My Tech Blog")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Include Routers
app.include_router(blog.router, prefix="/blog", tags=["blog"])


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    # Render the index page, which will load recent blog posts dynamically using HTMX
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/contact", response_class=HTMLResponse)
def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
def contact_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

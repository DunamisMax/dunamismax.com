from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

app = FastAPI(title="dunamismax.com")

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Static list of blog posts (title, slug, excerpt, date, etc.)
# These are hard-coded for demonstration and can be edited as needed.
posts = [
    {
        "title": "Getting Started with FastAPI",
        "slug": "getting-started-with-fastapi",
        "excerpt": "Learn how to set up a simple FastAPI application and serve static content.",
        "date": "2024-12-09",
    },
    {
        "title": "Introduction to Bulma for Styling",
        "slug": "introduction-to-bulma",
        "excerpt": "A quick overview of the Bulma CSS framework and how to create responsive layouts.",
        "date": "2024-11-30",
    },
    {
        "title": "Enhancing UX with HTMX",
        "slug": "enhancing-ux-with-htmx",
        "excerpt": "Use HTMX for progressive enhancement and partial page updates without a full reload.",
        "date": "2024-11-20",
    },
]


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/contact", response_class=HTMLResponse)
def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/blog", response_class=HTMLResponse)
def list_posts(request: Request):
    # Renders a static blog page with predefined posts
    return templates.TemplateResponse(
        "blog_list.html", {"request": request, "title": "Blog", "posts": posts}
    )

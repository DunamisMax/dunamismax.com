# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

app = FastAPI(title="My Tech Blog")

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    # Just serve the index.html as a static page
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/contact", response_class=HTMLResponse)
def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


# Optionally, if you still want a "blog" section, make it static:
@app.get("/blog", response_class=HTMLResponse)
def list_posts(request: Request):
    # No database calls, just a static page or remove this route entirely if not needed
    # Create a blog_list.html if you wish to display static content or remove this route
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Blog"}
    )


# You can remove /blog/{slug} if you don't have dynamic posts
# or transform it into a static page as well, just remove it if unnecessary.

# main.py
from fastapi import FastAPI, Request, Depends, HTTPException, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from app.database import engine, Base, get_db
from app.models import User, Post
from app.schemas import UserCreate, UserLogin, UserRead
from app.utils import hash_password, verify_password
from app.dependencies import get_admin_user

# Create all tables (for development safeguard; in production use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="My Tech Blog")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# ---------- Public Pages ----------


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    # Homepage with recent posts loaded via HTMX
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/contact", response_class=HTMLResponse)
def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


# ---------- Authentication Pages ----------


@app.get("/auth/login", response_class=HTMLResponse)
def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/auth/register", response_class=HTMLResponse)
def show_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# ---------- Authentication Routes ----------


@app.post("/auth/register", response_class=HTMLResponse)
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user_data = UserCreate(username=username, password=password)

    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        return templates.TemplateResponse(
            "partials/error_message.html",
            {"request": request, "message": "Username already taken"},
            status_code=400,
        )

    hashed = hash_password(user_data.password)
    new_user = User(username=user_data.username, password_hash=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return templates.TemplateResponse(
        "partials/success_message.html",
        {"request": request, "message": "Account created successfully! Redirecting..."},
    )


@app.post("/auth/login", response_class=HTMLResponse)
def login(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        # Instead of HTTPException, return error partial with 200 OK
        return templates.TemplateResponse(
            "partials/error_message.html",
            {"request": request, "message": "Invalid credentials"},
            status_code=200,  # Keep it 200, so HTMX can process it gracefully
        )

    response.set_cookie(
        key="session_user_id", value=str(user.id), httponly=True, max_age=3600
    )
    return templates.TemplateResponse(
        "partials/success_message.html",
        {"request": request, "message": "Login successful! Redirecting..."},
        status_code=200,
    )


@app.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie("session_user_id")
    return {"message": "Logged out"}


# ---------- Blog Routes ----------


@app.get("/blog", response_class=HTMLResponse)
def list_posts(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).all()
    return templates.TemplateResponse(
        "blog_list.html", {"request": request, "posts": posts}
    )


@app.get("/blog/{slug}", response_class=HTMLResponse)
def read_post(slug: str, request: Request, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.slug == slug).first()
    if not post:
        return HTMLResponse("Post not found", status_code=404)
    return templates.TemplateResponse(
        "blog_detail.html", {"request": request, "post": post}
    )


@app.get("/blog/create", response_class=HTMLResponse)
def create_post_form(request: Request, admin=Depends(get_admin_user)):
    return templates.TemplateResponse("post_create.html", {"request": request})


@app.post("/blog/create", response_class=HTMLResponse)
def create_post(
    title: str = Form(...),
    slug: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    existing_post = db.query(Post).filter(Post.slug == slug).first()
    if existing_post:
        raise HTTPException(status_code=400, detail="Slug already exists")

    new_post = Post(title=title, slug=slug, content=content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return RedirectResponse(url=f"/blog/{new_post.slug}", status_code=303)

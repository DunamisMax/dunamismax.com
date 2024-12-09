# blog.py
from fastapi import APIRouter, Depends, Request, HTTPException, Form
from starlette.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from starlette.templating import Jinja2Templates
from app.dependencies import get_admin_user

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def list_posts(request: Request, db: Session = Depends(get_db)):
    posts = db.query(models.Post).order_by(models.Post.created_at.desc()).all()
    return templates.TemplateResponse(
        "blog_list.html", {"request": request, "posts": posts}
    )


@router.get("/{slug}", response_class=HTMLResponse)
def read_post(slug: str, request: Request, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.slug == slug).first()
    if not post:
        # Ideally return a 404 page template instead of plain text
        return HTMLResponse("Post not found", status_code=404)
    return templates.TemplateResponse(
        "blog_detail.html", {"request": request, "post": post}
    )


@router.get("/create", response_class=HTMLResponse)
def create_post_form(request: Request, admin=Depends(get_admin_user)):
    # Returns a simple form to create a new post
    return templates.TemplateResponse("post_create.html", {"request": request})


@router.post("/create", response_class=HTMLResponse)
def create_post(
    title: str = Form(...),
    slug: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    # Check if slug is unique
    existing_post = db.query(models.Post).filter(models.Post.slug == slug).first()
    if existing_post:
        raise HTTPException(status_code=400, detail="Slug already exists")

    new_post = models.Post(title=title, slug=slug, content=content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    # Redirect back to the newly created post
    return RedirectResponse(url=f"/blog/{new_post.slug}", status_code=303)

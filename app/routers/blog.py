# blog.py
from fastapi import APIRouter, Depends, Request
from starlette.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def list_posts(request: Request, db: Session = Depends(get_db)):
    posts = db.query(models.Post).order_by(models.Post.created_at.desc()).all()
    return templates.TemplateResponse("blog_list.html", {"request": request, "posts": posts})

@router.get("/{slug}", response_class=HTMLResponse)
def read_post(slug: str, request: Request, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.slug == slug).first()
    if not post:
        # Could return a 404 template here
        return HTMLResponse("Post not found", status_code=404)
    return templates.TemplateResponse("blog_detail.html", {"request": request, "post": post})

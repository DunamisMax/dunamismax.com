from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os, sqlite3
from datetime import datetime, timezone

BASE_DIR = "/home/sawyer/dunamismax.com"
APP_DIR = os.path.join(BASE_DIR, "app")
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
DB_PATH = os.path.join(APP_DIR, "app.db")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    # Create posts table if not exists
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


init_db()  # Call this once after app creation in main.py


def get_all_posts():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, timestamp FROM posts ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    posts = [
        {
            "id": row["id"],
            "title": row["title"],
            "content": row["content"],
            "timestamp": datetime.fromisoformat(row["timestamp"]),
        }
        for row in rows
    ]
    return posts


def get_post_by_id(post_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, content, timestamp FROM posts WHERE id = ?", (post_id,)
    )
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "id": row["id"],
            "title": row["title"],
            "content": row["content"],
            "timestamp": datetime.fromisoformat(row["timestamp"]),
        }
    return None


def insert_post(title: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    cur.execute(
        "INSERT INTO posts (title, content, timestamp) VALUES (?, ?, ?)",
        (title, content, now_iso),
    )
    conn.commit()
    conn.close()


@router.get("/", response_class=HTMLResponse)
async def blog_index(request: Request):
    posts = get_all_posts()
    return templates.TemplateResponse(
        "blog/blog_index.html", {"request": request, "posts": posts}
    )


@router.get("/post/{post_id}", response_class=HTMLResponse)
async def view_post(request: Request, post_id: int):
    post = get_post_by_id(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse(
        "blog/view_post.html", {"request": request, "post": post}
    )

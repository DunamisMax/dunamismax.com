from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone
import math
import secrets
import time
import sqlite3
import os
from typing import Optional

# Adjust paths as needed
BASE_DIR = "/home/sawyer/dunamismax.com"
APP_DIR = os.path.join(BASE_DIR, "app")
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
DB_PATH = os.path.join(APP_DIR, "app.db")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Global configuration for chat feature
CSRF_TOKEN = secrets.token_urlsafe(32)
RATE_LIMIT = 5
TIME_WINDOW = 60.0
request_logs = {}
PAGE_SIZE = 100

router = APIRouter()


# Create the comments database if it does not exist
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


def is_rate_limited(ip: str) -> bool:
    now = time.time()
    timestamps = request_logs.get(ip, [])
    timestamps = [t for t in timestamps if t > now - TIME_WINDOW]
    timestamps.append(now)
    request_logs[ip] = timestamps
    return len(timestamps) > RATE_LIMIT


def get_comment_count(room: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as count FROM comments WHERE room = ?", (room,))
    count = cur.fetchone()["count"]
    conn.close()
    return count


def get_comments(room: str, page: int):
    total_comments = get_comment_count(room)
    total_pages = math.ceil(total_comments / PAGE_SIZE) if total_comments > 0 else 1
    page = max(1, min(page, total_pages))
    start_idx = (page - 1) * PAGE_SIZE

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT message, timestamp FROM comments
        WHERE room = ?
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        """,
        (room, PAGE_SIZE, start_idx),
    )
    rows = cur.fetchall()
    conn.close()

    comments = [
        {
            "message": row["message"],
            "timestamp": datetime.fromisoformat(row["timestamp"]),
        }
        for row in rows
    ]

    return comments, total_pages, page


def insert_comment(room: str, message: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    cur.execute(
        "INSERT INTO comments (room, message, timestamp) VALUES (?, ?, ?)",
        (room, message, now_iso),
    )
    conn.commit()
    conn.close()


@router.get("/", response_class=HTMLResponse)
async def chat_root(request: Request):
    """
    /chat
    Redirects to /chat/main (or could render a page listing available rooms)
    """
    return HTMLResponse(status_code=307, headers={"Location": "main"})


@router.get("/{room}", response_class=HTMLResponse)
async def chat_index(request: Request, room: str, page: int = 1):
    comments, total_pages, current_page = get_comments(room, page)
    return templates.TemplateResponse(
        "chat/chat_index.html",
        {
            "request": request,
            "comments": comments,
            "current_page": current_page,
            "total_pages": total_pages,
            "csrf_token": CSRF_TOKEN,
            "room": room,
        },
    )


@router.post("/{room}/post-comment", response_class=HTMLResponse)
async def post_comment(
    request: Request, room: str, message: str = Form(...), csrf_token: str = Form(...)
):
    client_ip = request.client.host
    if is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too Many Requests")

    if csrf_token != CSRF_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

    message = message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    insert_comment(room, message)

    comments, total_pages, current_page = get_comments(room, 1)
    return templates.TemplateResponse(
        "chat/_comments.html",
        {
            "request": request,
            "comments": comments,
            "current_page": current_page,
            "total_pages": total_pages,
        },
    )


@router.get("/{room}/comments", response_class=HTMLResponse)
async def get_comments_endpoint(request: Request, room: str, page: int = 1):
    client_ip = request.client.host
    if is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too Many Requests")

    comments, total_pages, current_page = get_comments(room, page)
    return templates.TemplateResponse(
        "chat/_comments.html",
        {
            "request": request,
            "comments": comments,
            "current_page": current_page,
            "total_pages": total_pages,
        },
    )

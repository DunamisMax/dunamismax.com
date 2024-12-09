from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import math

app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

COMMENTS = []
PAGE_SIZE = 100


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, page: int = 1):
    total_comments = len(COMMENTS)
    total_pages = math.ceil(total_comments / PAGE_SIZE) if total_comments > 0 else 1
    page = max(1, min(page, total_pages))
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    current_comments = COMMENTS[start_idx:end_idx]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "comments": current_comments,
            "current_page": page,
            "total_pages": total_pages,
        },
    )


@app.post("/post-comment", response_class=HTMLResponse)
async def post_comment(request: Request, message: str = Form(...)):
    message = message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    new_comment = {"message": message, "timestamp": datetime.utcnow()}
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

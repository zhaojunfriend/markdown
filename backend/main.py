import os
import re
from pathlib import Path

import bleach
import markdown as md
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Markdown Editor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory where markdown files are stored
FILES_DIR = Path(__file__).parent / "files"
FILES_DIR.mkdir(exist_ok=True)

# Allowed HTML tags and attributes for sanitisation
ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "pre", "code", "blockquote",
    "ul", "ol", "li",
    "table", "thead", "tbody", "tr", "th", "td",
    "hr", "br", "img",
    "del", "s", "sup", "sub",
]
ALLOWED_ATTRIBUTES = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "img": ["src", "alt", "title", "width", "height"],
    "a": ["href", "title", "rel"],
    "td": ["align"],
    "th": ["align"],
    "code": ["class"],
    "pre": ["class"],
}

_SAFE_FILENAME = re.compile(r"^[\w\-.]+\.md$")


def _validate_filename(filename: str) -> None:
    if not _SAFE_FILENAME.match(filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename. Only alphanumerics, hyphens, underscores "
                   "and dots are allowed, and the file must end with .md",
        )


class RenderRequest(BaseModel):
    content: str


class RenderResponse(BaseModel):
    html: str


class FileContent(BaseModel):
    filename: str
    content: str


class FileInfo(BaseModel):
    filename: str


@app.post("/api/render", response_model=RenderResponse)
def render_markdown(body: RenderRequest) -> RenderResponse:
    """Convert Markdown text to sanitised HTML."""
    raw_html = md.markdown(
        body.content,
        extensions=["tables", "fenced_code", "codehilite", "nl2br", "sane_lists"],
    )
    safe_html = bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    return RenderResponse(html=safe_html)


@app.get("/api/files", response_model=list[FileInfo])
def list_files() -> list[FileInfo]:
    """Return a list of saved markdown files."""
    files = sorted(FILES_DIR.glob("*.md"), key=os.path.getmtime, reverse=True)
    return [FileInfo(filename=f.name) for f in files]


@app.post("/api/files", status_code=201)
def save_file(body: FileContent) -> FileInfo:
    """Save or overwrite a markdown file."""
    _validate_filename(body.filename)
    path = FILES_DIR / body.filename
    path.write_text(body.content, encoding="utf-8")
    return FileInfo(filename=body.filename)


@app.get("/api/files/{filename}")
def load_file(filename: str) -> FileContent:
    """Load the content of a saved markdown file."""
    _validate_filename(filename)
    path = FILES_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    content = path.read_text(encoding="utf-8")
    return FileContent(filename=filename, content=content)


@app.delete("/api/files/{filename}", status_code=204)
def delete_file(filename: str) -> None:
    """Delete a saved markdown file."""
    _validate_filename(filename)
    path = FILES_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    path.unlink()

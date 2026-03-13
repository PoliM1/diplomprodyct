# main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os

from database import engine
import models

models.Base.metadata.create_all(bind=engine)
os.makedirs("uploads", exist_ok=True)

# Автоматически добавляем новые колонки если их нет (миграция без alembic)
from sqlalchemy import text as _sa_text
with engine.connect() as _conn:
    _migrations = [
        "ALTER TABLE tasks ADD COLUMN is_deleted BOOLEAN DEFAULT 0",
        "ALTER TABLE tasks ADD COLUMN deleted_at DATETIME",
        "ALTER TABLE organizations ADD COLUMN industry VARCHAR(255)",
        "ALTER TABLE organizations ADD COLUMN location VARCHAR(255)",
        "ALTER TABLE organizations ADD COLUMN website VARCHAR(500)",
        "ALTER TABLE organizations ADD COLUMN logo_url VARCHAR(500)",
        "ALTER TABLE organizations ADD COLUMN gallery TEXT",
        "ALTER TABLE users ADD COLUMN last_seen DATETIME",
        "ALTER TABLE users ADD COLUMN reset_token VARCHAR(64)",
        "ALTER TABLE users ADD COLUMN reset_token_expires DATETIME",
        "ALTER TABLE users ADD COLUMN gender VARCHAR(10)",
        "ALTER TABLE users ADD COLUMN bio TEXT",
        "ALTER TABLE users ADD COLUMN skills TEXT",
        "ALTER TABLE users ADD COLUMN experience VARCHAR(100)",
    ]
    for _sql in _migrations:
        try:
            _conn.execute(_sa_text(_sql))
            _conn.commit()
        except Exception:
            pass  # Колонка уже существует — игнорируем

app = FastAPI(title="TaskFlow", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

from routers import auth_router, users_router, orgs_router, tasks_router
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(orgs_router.router)
app.include_router(tasks_router.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse, include_in_schema=False)
def profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/organization", response_class=HTMLResponse, include_in_schema=False)
def organization(request: Request):
    return templates.TemplateResponse("organization.html", {"request": request})

@app.get("/member", response_class=HTMLResponse, include_in_schema=False)
def member_profile(request: Request):
    return templates.TemplateResponse("member_profile.html", {"request": request})

@app.get("/reset-password", response_class=HTMLResponse, include_in_schema=False)
def reset_password_page(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})

@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
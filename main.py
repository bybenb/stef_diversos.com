import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.exceptions import HTTPException

from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from app.rotas import publicas, admin
from app.modelos import banco
from app.templates import templates

load_dotenv()

app = FastAPI(title="Stef Diversos", description="Loja virtual em Luanda - By Stef Neto")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, troque pelo domínio do Clerk
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("Valor na variável SECRET_KEY em falta!")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Cria as tabelas no Neon (apenas a primeira execução)
banco.criar_tabelas()

app.include_router(publicas.router)
app.include_router(admin.router)


@app.get("/dashboard")
async def dashboard_redirect():
    return RedirectResponse(url="/admin/dashboard", status_code=303)

app.mount("/static", StaticFiles(directory="app/static"), name="static")




@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)

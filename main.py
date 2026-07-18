import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from app.rotas import publicas, admin
from app.rotas import publicas
from app.modelos import banco

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

app.mount("/static", StaticFiles(directory="app/static"), name="static")

import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from app.rotas import publicas, admin
from app.modelos import banco
from fastapi.templating import Jinja2Templates  # Importação direta aqui

load_dotenv()

app = FastAPI(title="Stef Diversos")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sessão (para o carrinho)
SECRET_KEY = os.getenv("SECRET_KEY")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Cria as tabelas no banco
banco.criar_tabelas()

templates = Jinja2Templates(directory="app/templates")


app.include_router(publicas.router)
app.include_router(admin.router)


app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    # Vamos retornar um texto simples em vez de renderizar um HTML de erro,
    # pois o erro 500 originalmente aconteceu justamente ao renderizar o template!
    return HTMLResponse(
        content="<h1>Erro interno do servidor (500)</h1><p>Ocorreu um inesperado. Tente atualizar a pagina. Se persistir, contacte-nos, clicando <a href=\"https://wa.link/0m9tbc\">Aqui</a>.</p>",
        status_code=500
    )
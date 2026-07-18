import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.modelos import entidades

# Carrega as variáveis do arquivo .env
load_dotenv()

URL_BANCO = os.getenv("DATABASE_URL")

if not URL_BANCO:
    raise ValueError("ERRO: A variável DATABASE_URL não foi encontrada no .env!")

engine = create_engine(URL_BANCO, echo=True)  # echo=True mostra os comandos SQL no terminal
SessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def criar_tabelas():
    """Cria todas as tabelas no PostgreSQL se não existirem"""
    entidades.Base.metadata.create_all(bind=engine)

def obter_sessao():
    """Função geradora para obter uma sessão do banco"""
    sessao = SessaoLocal()
    try:
        yield sessao
    finally:
        sessao.close()
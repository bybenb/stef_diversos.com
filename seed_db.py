import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.modelos.entidades import Categoria, Produto, Base

load_dotenv()
URL_BANCO = os.getenv("DATABASE_URL")
engine = create_engine(URL_BANCO)
Base.metadata.create_all(bind=engine)
SessaoLocal = sessionmaker(bind=engine)

db = SessaoLocal()

# Cria uma categoria
categoria = Categoria(nome="Bolsas", descricao="Bolsas femininas de luxo")
db.add(categoria)
db.commit()

# Cria um produto teste
produto = Produto(
    nome="Bolsa Stef Elegance",
    descricao="Bolsa de couro sintético dourado, ideal para festas.",
    preco=199.90,
    estoque=50,
    url_imagem="https://via.placeholder.com/300x300/d4af37/ffffff?text=Bolsa+Stef",
    categoria_id=categoria.id,
    esta_ativo=True
)
db.add(produto)
db.commit()

print("Banco de dados populado com sucesso!")
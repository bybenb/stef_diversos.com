# seed_tags.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.modelos.entidades import Base, Tag, Produto, Categoria

load_dotenv()
URL_BANCO = os.getenv("DATABASE_URL")
engine = create_engine(URL_BANCO)
Base.metadata.create_all(bind=engine)
SessaoLocal = sessionmaker(bind=engine)

db = SessaoLocal()

# 1. Criar as Tags
tags = [
    Tag(nome="Novidades", slug="novidades"),
    Tag(nome="Promoções", slug="promocoes"),
    Tag(nome="Bolsas", slug="bolsas")
]
db.add_all(tags)
db.commit()

# 2. Pegar os produtos existentes (assumindo que você já tem alguns)
produtos = db.query(Produto).all()
tag_bolsas = db.query(Tag).filter(Tag.slug == "bolsas").first()
tag_novidades = db.query(Tag).filter(Tag.slug == "novidades").first()
tag_promocoes = db.query(Tag).filter(Tag.slug == "promocoes").first()

# 3. Adicionar tags aos produtos (exemplo simples)
if produtos and tag_novidades:
    produtos[0].tags.append(tag_novidades) # Adiciona "Novidades" ao primeiro produto
if produtos and len(produtos) > 1 and tag_promocoes:
    produtos[1].tags.append(tag_promocoes) # Adiciona "Promoções" ao segundo produto
if produtos and len(produtos) > 2 and tag_bolsas:
    produtos[2].tags.append(tag_bolsas)    # Adiciona "Bolsas" ao terceiro produto

db.commit()
print("Tags criadas e associadas aos produtos com sucesso!")
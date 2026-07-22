from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, Table
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()



produto_tag = Table('produto_tag', Base.metadata,
    Column('produto_id', Integer, ForeignKey('produtos.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)






class Categoria(Base):
    __tablename__ = 'categorias'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    produtos = relationship("Produto", back_populates="categoria")

class Produto(Base):
    __tablename__ = 'produtos'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, default=0)
    url_imagem = Column(String(500))  # URL da imagem do produto
    categoria_id = Column(Integer, ForeignKey('categorias.id'))
    categoria = relationship("Categoria", back_populates="produtos")
    esta_ativo = Column(Boolean, default=True)
    promocao = Column(Boolean, default=False)
    data_criacao = Column(DateTime, default=datetime.now)

    tags = relationship("Tag", secondary=produto_tag, back_populates="produtos")

class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String(200))
    email = Column(String(200), unique=True, index=True)
    senha_hash = Column(String(200)) 
    telefone = Column(String(20))
    endereco_rua = Column(String(200))
    endereco_numero = Column(String(10))
    endereco_bairro = Column(String(100))
    endereco_cidade = Column(String(100))
    endereco_estado = Column(String(2))
    endereco_cep = Column(String(10))
    pedidos = relationship("Pedido", back_populates="cliente")

class Pedido(Base):
    __tablename__ = 'pedidos'
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    cliente = relationship("Cliente", back_populates="pedidos")
    data_criacao = Column(DateTime, default=datetime.now)
    status = Column(String(50), default="Aguardando Pagamento") 
    total = Column(Float, default=0.0)
    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")

class ItemPedido(Base):
    __tablename__ = 'itens_pedido'
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey('pedidos.id'))
    pedido = relationship("Pedido", back_populates="itens")
    produto_id = Column(Integer, ForeignKey('produtos.id'))
    produto = relationship("Produto")
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False)  # Ex: "Adidas", "Promoção"
    slug = Column(String(50), unique=True, nullable=False)  # Ex: "adidas", "promocao" (para a URL)
    produtos = relationship("Produto", secondary=produto_tag, back_populates="tags")



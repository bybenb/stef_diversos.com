from fastapi import APIRouter, Request, Depends, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.modelos.banco import obter_sessao
from app.modelos.entidades import Produto, Categoria, Pedido, Cliente
from app.core.autenticacao import obter_usuario_admin
from app.core.upload import upload_imagem_cloudinary

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="app/templates")

# --- Página de Login (Agora apenas renderiza o HTML com o botão do Clerk) ---
@router.get("/login", response_class=HTMLResponse)
async def tela_login(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})

# --- Dashboard (Protegido pelo Clerk) ---
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request, 
    usuario: dict = Depends(obter_usuario_admin),  # <--- PROTEÇÃO AQUI
    db: Session = Depends(obter_sessao)
):
    # Se chegou aqui, o usuário está autenticado!
    total_produtos = db.query(Produto).count()
    total_pedidos = db.query(Pedido).count()
    total_clientes = db.query(Cliente).count()
    ultimos_pedidos = db.query(Pedido).order_by(Pedido.data_criacao.desc()).limit(5).all()
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "usuario": usuario,  # Passa os dados do usuário logado para o template
        "total_produtos": total_produtos,
        "total_pedidos": total_pedidos,
        "total_clientes": total_clientes,
        "ultimos_pedidos": ultimos_pedidos
    })

# --- CRUD de Produtos (Protegido) ---
@router.get("/produtos", response_class=HTMLResponse)
async def listar_produtos(
    request: Request, 
    usuario: dict = Depends(obter_usuario_admin),
    db: Session = Depends(obter_sessao)
):
    produtos = db.query(Produto).order_by(Produto.id.desc()).all()
    return templates.TemplateResponse("admin/produtos_lista.html", {
        "request": request,
        "usuario": usuario,
        "produtos": produtos
    })

@router.get("/produtos/novo", response_class=HTMLResponse)
async def novo_produto_form(
    request: Request, 
    usuario: dict = Depends(obter_usuario_admin),
    db: Session = Depends(obter_sessao)
):
    categorias = db.query(Categoria).all()
    return templates.TemplateResponse("admin/produto_form.html", {
        "request": request,
        "usuario": usuario,
        "produto": None,
        "categorias": categorias,
        "titulo": "Novo Produto"
    })

@router.post("/produtos/novo")
async def salvar_novo_produto(
    request: Request,
    usuario: dict = Depends(obter_usuario_admin),  # <--- Protegido
    nome: str = Form(...),
    imagem: UploadFile = File(...),
    descricao: str = Form(...),
    preco: float = Form(...),
    estoque: int = Form(...),
    url_imagem: str = Form(...),
    categoria_id: int = Form(...),
    db: Session = Depends(obter_sessao)
):
    url_imagem = upload_imagem_cloudinary(imagem)  if imagem else ""
    novo_produto = Produto(
        nome=nome, descricao=descricao, preco=preco, 
        estoque=estoque, url_imagem=url_imagem, categoria_id=categoria_id
    )
    db.add(novo_produto)
    db.commit()
    return RedirectResponse(url="/admin/produtos", status_code=303)

@router.get("/produtos/editar/{produto_id}", response_class=HTMLResponse)
async def editar_produto_form(
    request: Request, 
    produto_id: int, 
    usuario: dict = Depends(obter_usuario_admin),
    db: Session = Depends(obter_sessao)
):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        return RedirectResponse(url="/admin/produtos")
    categorias = db.query(Categoria).all()
    return templates.TemplateResponse("admin/produto_form.html", {
        "request": request,
        "usuario": usuario,
        "produto": produto,
        "categorias": categorias,
        "titulo": "Editar Produto"
    })

@router.post("/produtos/editar/{produto_id}")
async def salvar_edicao_produto(
    request: Request,
    produto_id: int,
    usuario: dict = Depends(obter_usuario_admin),
    nome: str = Form(...),
    descricao: str = Form(...),
    preco: float = Form(...),
    estoque: int = Form(...),
    url_imagem: str = Form(...),
    categoria_id: int = Form(...),
    db: Session = Depends(obter_sessao)
):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if produto:
        produto.nome = nome
        produto.descricao = descricao
        produto.preco = preco
        produto.estoque = estoque
        produto.url_imagem = url_imagem
        produto.categoria_id = categoria_id
        db.commit()
    return RedirectResponse(url="/admin/produtos", status_code=303)

@router.get("/produtos/excluir/{produto_id}")
async def excluir_produto(
    request: Request, 
    produto_id: int, 
    usuario: dict = Depends(obter_usuario_admin),
    db: Session = Depends(obter_sessao)
):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if produto:
        db.delete(produto)
        db.commit()
    return RedirectResponse(url="/admin/produtos", status_code=303)

# --- Pedidos (Protegido) ---
@router.get("/pedidos", response_class=HTMLResponse)
async def listar_pedidos(
    request: Request, 
    usuario: dict = Depends(obter_usuario_admin),
    db: Session = Depends(obter_sessao)
):
    pedidos = db.query(Pedido).order_by(Pedido.data_criacao.desc()).all()
    return templates.TemplateResponse("admin/pedidos_lista.html", {
        "request": request,
        "usuario": usuario,
        "pedidos": pedidos
    })

@router.post("/pedidos/status/{pedido_id}")
async def atualizar_status_pedido(
    request: Request,
    pedido_id: int,
    status: str = Form(...),
    usuario: dict = Depends(obter_usuario_admin),
    db: Session = Depends(obter_sessao)
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido:
        pedido.status = status
        db.commit()
    return RedirectResponse(url="/admin/pedidos", status_code=303)
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.modelos.banco import obter_sessao
from app.modelos.entidades import Produto, Categoria, Pedido, Cliente
from app.core.autenticacao import obter_usuario_admin

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="app/templates")

ADMIN_CREDENTIALS = {
    "itsbenyreis@gmail.com": "Stefiosos2026!",
    "benybkiamvu@gmail.com": "Stefiosos2026!",
    "estefanianeto20@gmail.com": "Stefiosos2026!"
}



@router.get("/login", response_class=HTMLResponse)
async def tela_login(request: Request):
    # Se já estiver logado, redireciona para o dashboard
    if request.session.get("admin_user"):
        return RedirectResponse(url="/admin/dashboard")
    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={"request": request})

@router.post("/login")
async def fazer_login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...)
):

    if email in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[email] == senha:
        request.session["admin_user"] = email
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    else:
        return templates.TemplateResponse(request=request, name="admin/login.html", context={ "request": request, "erro": "E-mail ou senha inválidos!" })

@router.get("/logout")
async def logout(request: Request):
    request.session.pop("admin_user", None)
    return RedirectResponse(url="/admin/login", status_code=303)

# --- Dashboard (Protegido) ---
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request, 
    usuario: dict = Depends(obter_usuario_admin),
    db: Session = Depends(obter_sessao)
):
    total_produtos = db.query(Produto).count()
    total_pedidos = db.query(Pedido).count()
    total_clientes = db.query(Cliente).count()
    ultimos_pedidos = db.query(Pedido).order_by(Pedido.data_criacao.desc()).limit(5).all()
    
    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "request": request,
            "usuario": usuario,
            "total_produtos": total_produtos,
            "total_pedidos": total_pedidos,
            "total_clientes": total_clientes,
            "ultimos_pedidos": ultimos_pedidos
        })

# --- CRUD Produtos (Protegido) ---
@router.get("/produtos", response_class=HTMLResponse)
async def listar_produtos(
    request: Request, 
    usuario: dict = Depends(obter_usuario_admin),
    db: Session = Depends(obter_sessao)
):
    produtos = db.query(Produto).order_by(Produto.id.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="admin/produtos_lista.html",
        context={
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
    return templates.TemplateResponse(
        request=request,
        name="admin/produto_form.html",
        context={
            "request": request,
            "usuario": usuario,
            "produto": None,
            "categorias": categorias,
            "titulo": "Novo Produto"
        })

@router.post("/produtos/novo")
async def salvar_novo_produto(
    request: Request,
    nome: str = Form(...),
    descricao: str = Form(...),
    preco: float = Form(...),
    estoque: int = Form(...),
    url_imagem: str = Form(...),
    categoria_id: int = Form(...),
    usuario: dict = Depends(obter_usuario_admin),
    db: Session = Depends(obter_sessao)
):
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
    return templates.TemplateResponse(
        request=request,
        name="admin/produto_form.html",
        context={
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
    nome: str = Form(...),
    descricao: str = Form(...),
    preco: float = Form(...),
    estoque: int = Form(...),
    url_imagem: str = Form(...),
    categoria_id: int = Form(...),
    usuario: dict = Depends(obter_usuario_admin),
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
    return templates.TemplateResponse(
        request=request,
        name="admin/pedidos_lista.html",
        context={
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
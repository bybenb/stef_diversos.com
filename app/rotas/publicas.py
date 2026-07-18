from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.modelos.entidades import Produto, Categoria
from app.modelos.banco import obter_sessao
from app.core.carrinho import GerenciadorCarrinho

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Página Inicial
@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(obter_sessao)):
    produtos = db.query(Produto).filter(Produto.esta_ativo == True).limit(8).all()
    return templates.TemplateResponse("home.html", {"request": request, "produtos": produtos})

# Detalhe do Produto
@router.get("/produto/{produto_id}", response_class=HTMLResponse)
async def detalhe_produto(request: Request, produto_id: int, db: Session = Depends(obter_sessao)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("produto.html", {"request": request, "produto": produto})

# Visualizar Carrinho (recupera da sessão)
@router.get("/carrinho", response_class=HTMLResponse)
async def ver_carrinho(request: Request):
    dados_carrinho = request.session.get("carrinho")
    carrinho = GerenciadorCarrinho.from_dict(dados_carrinho)
    return templates.TemplateResponse("carrinho.html", {"request": request, "carrinho": carrinho})

# Adicionar ao Carrinho (via JSON para HTMX)
@router.post("/api/adicionar-ao-carrinho")
async def adicionar_ao_carrinho(request: Request, produto_id: int, quantidade: int = 1,  db: Session = Depends(obter_sessao)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        return {"erro": "Produto não encontrado"}

    # Recupera carrinho da sessão
    dados_carrinho = request.session.get("carrinho")
    carrinho = GerenciadorCarrinho.from_dict(dados_carrinho)

    # Adiciona e salva de volta
    carrinho.adicionar_item(produto.id, produto.nome, produto.preco, quantidade)
    request.session["carrinho"] = carrinho.to_dict()

    return {
        "mensagem": f"{produto.nome} adicionado!",
        "total_itens": len(carrinho.itens),
        "total_preco": carrinho.calcular_total()
    }









@router.get("/checkout", response_class=HTMLResponse)
async def tela_checkout(request: Request):
    dados_carrinho = request.session.get("carrinho")
    carrinho = GerenciadorCarrinho.from_dict(dados_carrinho)
    
    if not carrinho.itens:
        return RedirectResponse(url="/carrinho")
        
    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "carrinho": carrinho,
        "total": carrinho.calcular_total()
    })

@router.post("/checkout/finalizar")
async def finalizar_pedido(
    request: Request,
    nome: str = Form(...),
    endereco: str = Form(...),
    pagamento: str = Form(...), # "multicaixa" ou "cod"
    db: Session = Depends(obter_sessao)
):
    dados_carrinho = request.session.get("carrinho")
    carrinho = GerenciadorCarrinho.from_dict(dados_carrinho)
    
    # 1. Cria Cliente (se não existir)
    cliente = db.query(Cliente).filter(Cliente.email == "email_do_usuario").first()
    if not cliente:
        cliente = Cliente(nome_completo=nome, endereco=endereco, email="email_do_usuario")
        db.add(cliente)
        db.commit()
        db.refresh(cliente)

    # 2. Cria Pedido
    pedido = Pedido(
        cliente_id=cliente.id,
        status="Aguardando Pagamento",
        total=carrinho.calcular_total()
    )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)

    # 3. Cria Itens do Pedido e Baixa Estoque
    for prod_id, item in carrinho.itens.items():
        produto = db.query(Produto).filter(Produto.id == int(prod_id)).first()
        if produto and produto.estoque >= item['quantidade']:
            produto.estoque -= item['quantidade']
            item_pedido = ItemPedido(
                pedido_id=pedido.id,
                produto_id=produto.id,
                quantidade=item['quantidade'],
                preco_unitario=item['preco']
            )
            db.add(item_pedido)
    
    db.commit()
    request.session["carrinho"] = None # Limpa carrinho

    # 4. Redireciona baseado na forma de pagamento
    if pagamento == "multicaixa":
        return RedirectResponse(url=f"/pagamento/multicaixa/{pedido.id}")
    elif pagamento == "cod":
        return RedirectResponse(url=f"/pedido-confirmado/{pedido.id}?metodo=COD")

# Contador do carrinho para o ícone (Adicione isso no final do arquivo)
@router.get("/api/carrinho/contador")
async def contador_carrinho(request: Request):
    dados_carrinho = request.session.get("carrinho")
    carrinho = GerenciadorCarrinho.from_dict(dados_carrinho)
    return {"total_itens": len(carrinho.itens)}
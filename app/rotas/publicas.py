import os
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse


from httpcore import request
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.gerador_pdf import gerar_fatura_pdf
from app.modelos.entidades import Produto, Categoria
from app.modelos.banco import obter_sessao
from app.core.carrinho import GerenciadorCarrinho
from app.modelos.entidades import  Cliente, Pedido, ItemPedido

from typing import Optional


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")





@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(obter_sessao)):
    produtos = db.query(Produto).filter(Produto.esta_ativo == True).limit(8).all()
    
    produtos_recentes = db.query(Produto).filter(Produto.esta_ativo == True).order_by(desc(Produto.data_criacao)).limit(8).all()
    
    produtos_promocao = db.query(Produto).filter(Produto.promocao == True, Produto.preco < 100000).limit(6).all()
    
    # 3. Categoria específica (ex: Bolsas - id 1, ajuste conforme seu seed)
    categoria_bolsas = db.query(Categoria).filter(Categoria.nome.ilike('%Bolsas%')).first()
    produtos_bolsas = []
    if categoria_bolsas:
        produtos_bolsas = db.query(Produto).filter(Produto.esta_ativo == True, Produto.categoria_id == categoria_bolsas.id).limit(6).all()

    """
    return templates.TemplateResponse("home.html", {
        "request": request,
        "produtos": produtos,
        "produtos_recentes": produtos_recentes,
        "produtos_promocao": produtos_promocao,
        "produtos_bolsas": produtos_bolsas
    })    
    
    """
    return templates.TemplateResponse(
    request=request,
    name="home.html",
    context={
        "request": request,
        "produtos": produtos,
        "produtos_recentes": produtos_recentes,
        "produtos_promocao": produtos_promocao,
        "produtos_bolsas": produtos_bolsas,
    },
    )
    





@router.get("/produtos", response_class=HTMLResponse)
async def listar_produtos_por_tag(
    request: Request, 
    tag: Optional[str] = None, 
    db: Session = Depends(obter_sessao)
):
    query = db.query(Produto).filter(Produto.esta_ativo == True)
    
    titulo_pagina = "Todos os Produtos"
    
    if tag:
        query = query.join(Produto.tags).filter(Tag.slug == tag)
        tag_obj = db.query(Tag).filter(Tag.slug == tag).first()
        if tag_obj:
            titulo_pagina = f"Produtos: {tag_obj.nome}"
    
    produtos = query.all()
    
    return templates.TemplateResponse("produtos_lista.html", {
        "request": request,
        "produtos": produtos,
        "titulo": titulo_pagina,
        "tag_atual": tag
    })







@router.get("/produto/{produto_id}", response_class=HTMLResponse)
async def detalhe_produto(request: Request, produto_id: int, db: Session = Depends(obter_sessao)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("produto.html", {"request": request, "produto": produto})



@router.get("/carrinho", response_class=HTMLResponse)
async def ver_carrinho(request: Request):
    dados_carrinho = request.session.get("carrinho")
    carrinho = GerenciadorCarrinho.from_dict(dados_carrinho)
    return templates.TemplateResponse("carrinho.html", {"request": request, "carrinho": carrinho})



@router.post("/api/adicionar-ao-carrinho")
async def adicionar_ao_carrinho(
    request: Request,
    produto_id: int = Form(...),
    quantidade: int = Form(1),
    db: Session = Depends(obter_sessao),
):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        return {"erro": "Produto não encontrado"}


    dados_carrinho = request.session.get("carrinho")
    carrinho = GerenciadorCarrinho.from_dict(dados_carrinho)


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
        "carrinho": carrinho
    })





@router.post("/checkout/finalizar")
async def finalizar_pedido(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    telefone: str = Form(...),
    endereco: str = Form(...),
    pagamento: str = Form(...),  # 'multicaixa express' ou 'cod'
    db: Session = Depends(obter_sessao)
):
    dados_carrinho = request.session.get("carrinho")
    carrinho = GerenciadorCarrinho.from_dict(dados_carrinho)
    
    if not carrinho.itens:
        return RedirectResponse(url="/carrinho")


    cliente = db.query(Cliente).filter(Cliente.email == email).first()
    if not cliente:
        cliente = Cliente(
            nome_completo=nome, 
            email=email, 
            telefone=telefone,
            endereco_rua=endereco
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)

    status_inicial = "Aguardando Pagamento" if pagamento == "multicaixa" else "Aguardando Entrega (COD)"


    pedido = Pedido(
        cliente_id=cliente.id,
        status=status_inicial,
        total=carrinho.calcular_total()
    )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)



    for prod_id, item in carrinho.itens.items():
        produto = db.query(Produto).filter(Produto.id == int(prod_id)).first()
        if produto:
            if produto.estoque >= item['quantidade']:
                produto.estoque -= item['quantidade']
            else:
            
                raise HTTPException(status_code=400, detail=f"Estoque insuficiente para {produto.nome}")
            
            item_pedido = ItemPedido(
                pedido_id=pedido.id,
                produto_id=produto.id,
                quantidade=item['quantidade'],
                preco_unitario=item['preco']
            )
            db.add(item_pedido)
    
    db.commit()

    request.session["carrinho"] = None

    return RedirectResponse(url=f"/pedido-confirmado/{pedido.id}?metodo={pagamento}", status_code=303)

@router.get("/pedido-confirmado/{pedido_id}", response_class=HTMLResponse)
async def pedido_confirmado(request: Request, pedido_id: int, db: Session = Depends(obter_sessao)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        return RedirectResponse(url="/")
    
    metodo = request.query_params.get("metodo", "multicaixa")    
    return templates.TemplateResponse("pedido_confirmado.html", {
        "request": request,
        "pedido": pedido,
        "metodo": metodo
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
    
    cliente = db.query(Cliente).filter(Cliente.email == "email_do_usuario").first()
    if not cliente:
        cliente = Cliente(nome_completo=nome, endereco=endereco, email="email_do_usuario")
        db.add(cliente)
        db.commit()
        db.refresh(cliente)

    pedido = Pedido(
        cliente_id=cliente.id,
        status="Aguardando Pagamento",
        total=carrinho.calcular_total()
    )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)

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

    if pagamento == "multicaixa":
        return RedirectResponse(url=f"/pagamento/multicaixa/{pedido.id}")
    elif pagamento == "cod":
        return RedirectResponse(url=f"/pedido-confirmado/{pedido.id}?metodo=COD")








@router.get("/api/download-fatura/{pedido_id}")
async def download_fatura(pedido_id: int, request: Request, db: Session = Depends(obter_sessao)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        return {"erro": "Pedido não encontrado"}
    
    cliente = db.query(Cliente).filter(Cliente.id == pedido.cliente_id).first()
    itens = db.query(ItemPedido).filter(ItemPedido.pedido_id == pedido_id).all()
    metodo = request.query_params.get("metodo", "Multicaixa Express")
    
    # Gera o PDF em memória
    pdf_buffer = gerar_fatura_pdf(pedido, cliente, itens, metodo)
    
    # Retorna como arquivo para download
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Fatura_Stef_{pedido_id}.pdf"}
    )

@router.get("/api/carrinho/contador")
async def contador_carrinho(request: Request):
    dados_carrinho = request.session.get("carrinho")
    carrinho = GerenciadorCarrinho.from_dict(dados_carrinho)
    return {"total_itens": len(carrinho.itens)}


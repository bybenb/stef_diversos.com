import io
import urllib.request
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

def gerar_fatura_pdf(pedido, cliente, itens, metodo):
    """
    Gera um PDF em memória (BytesIO) com os dados do pedido.
    Retorna um buffer para ser baixado pelo navegador.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    
    # caminho_logo = "app/static/imagens/logo.png" 
    # logo = ImageReader(caminho_logo)
    

    url_logo = "https://stef-diversos.onrender.com/static/img/logo.png" 
    try:
        req = urllib.request.Request(url_logo, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            logo_data = response.read()
        logo = ImageReader(io.BytesIO(logo_data))
        
        c.drawImage(logo, width - 8.5*cm, height - 6.5*cm, width=8*cm, height=5*cm, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        print(f"Não foi possível carregar a logo: {e}")


    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#b74265"))
    c.drawString(2*cm, height - 2*cm, "Stef Diversos")
    
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawString(2*cm, height - 3*cm, "Fatura do Pedido")
    
    # Informações do Pedido
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height - 5*cm, f"Pedido Nº: {pedido.id}")
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height - 5.8*cm, f"Data: {pedido.data_criacao.strftime('%d/%m/%Y %H:%M')}")
    c.drawString(10*cm, height - 5.8*cm, f"Pagamento: {metodo}")
    
    # Dados do Cliente
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, height - 7.5*cm, "Dados do Cliente:")
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height - 8.3*cm, f"Nome: {cliente.nome_completo}")
    c.drawString(2*cm, height - 9.1*cm, f"Email: {cliente.email}")
    c.drawString(2*cm, height - 9.9*cm, f"Telefone: {cliente.telefone}")
    c.drawString(2*cm, height - 10.7*cm, f"Endereço: {cliente.endereco_rua}")
    
    # Tabela de Itens
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, height - 12.5*cm, "Itens do Pedido:")
    
    data = [["Qtd", "Produto", "Preço Unit.", "Subtotal"]]
    for item in itens:
        data.append([
            str(item.quantidade),
            item.produto.nome,
            f"Kz {item.preco_unitario:.2f}",
            f"Kz {item.preco_unitario * item.quantidade:.2f}"
        ])
    
    table = Table(data, colWidths=[2*cm, 7*cm, 4*cm, 4*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d4af37")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
    ]))
    
    table.wrapOn(c, width, height)
    table.drawOn(c, 2*cm, height - 12.5*cm - (len(data)*0.7*cm))
    
    y_footer = height - 12.5*cm - (len(data)*0.7*cm) - 1.5*cm
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#b74265"))
    c.drawString(13*cm, y_footer, f"Total Geral: Kz {pedido.total:.2f}")
    
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.grey)
    c.drawString(width/2 - 5*cm, 2*cm, "Obrigado por comprar na Stef Diversos!")
    
    c.save()
    buffer.seek(0)  # Rebobina o buffer para o início
    return buffer
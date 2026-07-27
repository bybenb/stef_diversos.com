from typing import Dict, Any

class GerenciadorCarrinho:
    def __init__(self):
        self.itens: Dict[int, Dict[str, Any]] = {}  # {id: {'nome': x, 'preco': y, 'quantidade': z}}

    def adicionar_item(self, produto_id: int, nome: str, preco: float, quantidade: int = 1):
        if produto_id in self.itens:
            self.itens[produto_id]['quantidade'] += quantidade
        else:
            self.itens[produto_id] = {
                'nome': nome,
                'preco': preco,
                'url_imagem': url_imagem,
                'quantidade': quantidade
            }

    def remover_item(self, produto_id: int):
        if produto_id in self.itens:
            del self.itens[produto_id]

    def calcular_total(self) -> float:
        return sum(item['preco'] * item['quantidade'] for item in self.itens.values())

    def limpar_carrinho(self):
        self.itens = {}

    # Métodos especiais para salvar/recuperar da sessão (JSON)
    def to_dict(self) -> dict:
        return {"itens": self.itens}

    @classmethod
    def from_dict(cls, dados: dict):
        carrinho = cls()
        if dados and "itens" in dados:
            carrinho.itens = dados["itens"]
        return carrinho

CREATE TABLE categorias (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT
);

CREATE INDEX idx_categorias_id
ON categorias(id);




CREATE TABLE produtos (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    preco DOUBLE PRECISION NOT NULL,
    estoque INTEGER NOT NULL DEFAULT 0,
    url_imagem VARCHAR(500),
    categoria_id INTEGER,
    esta_ativo BOOLEAN NOT NULL DEFAULT TRUE,
    data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_produto_categoria
        FOREIGN KEY (categoria_id)
        REFERENCES categorias(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE INDEX idx_produtos_id
ON produtos(id);

CREATE INDEX idx_produtos_categoria
ON produtos(categoria_id);




CREATE TABLE clientes (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome_completo VARCHAR(200),
    email VARCHAR(200) UNIQUE,
    senha_hash VARCHAR(200),
    telefone VARCHAR(20),
    endereco_rua VARCHAR(200),
    endereco_numero VARCHAR(10),
    endereco_bairro VARCHAR(100),
    endereco_cidade VARCHAR(100),
    endereco_estado VARCHAR(2),
    endereco_cep VARCHAR(10)
);

CREATE INDEX idx_clientes_id
ON clientes(id);

CREATE INDEX idx_clientes_email
ON clientes(email);




CREATE TABLE pedidos (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id INTEGER,
    data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'Aguardando Pagamento',
    total DOUBLE PRECISION NOT NULL DEFAULT 0.0,

    CONSTRAINT fk_pedido_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES clientes(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE INDEX idx_pedidos_id
ON pedidos(id);

CREATE INDEX idx_pedidos_cliente
ON pedidos(cliente_id);




CREATE TABLE itens_pedido (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    preco_unitario DOUBLE PRECISION NOT NULL,

    CONSTRAINT fk_item_pedido
        FOREIGN KEY (pedido_id)
        REFERENCES pedidos(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_item_produto
        FOREIGN KEY (produto_id)
        REFERENCES produtos(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE INDEX idx_itens_pedido_id
ON itens_pedido(id);

CREATE INDEX idx_itens_pedido_pedido
ON itens_pedido(pedido_id);

CREATE INDEX idx_itens_pedido_produto
ON itens_pedido(produto_id);

-- 



ALTER TABLE produtos
ALTER COLUMN url_imagem TYPE TEXT;

ALTER TABLE produtos
ALTER COLUMN url_imagem SET NOT NULL;

-- 
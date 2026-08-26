############################################
# IMPORTAÇÕES
############################################
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Numeric,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database.database import Base


############################################
# CLASSE PRODUTO
############################################
# Representa um produto do estoque de uma empresa. É o coração do
# sistema: controla quantidade em estoque, estoque mínimo (usado
# para gerar alertas), preços e vínculos com categoria/fornecedor.
class Produto(Base):
    __tablename__ = "produtos"

    ########################################
    # RESTRIÇÕES DE UNICIDADE
    ########################################
    # O código do produto (SKU, ex: "PROD0008") deve ser único DENTRO
    # de cada empresa, mas duas empresas diferentes podem ter,
    # cada uma, um produto de código "PROD0008".
    __table_args__ = (
        UniqueConstraint("empresa_id", "codigo", name="uq_produto_codigo_empresa"),
    )

    ########################################
    # COLUNAS
    ########################################
    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)

    # categoria_id e fornecedor_id são opcionais (nullable=True),
    # pois um produto pode existir sem categoria ou fornecedor
    # definidos ainda.
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True)

    # Código/SKU do produto, usado nos alertas de estoque
    # (ex: "⚠ PROD0008 abaixo do estoque mínimo")
    codigo = Column(String(30), nullable=False, index=True)

    nome = Column(String(150), nullable=False)
    descricao = Column(String(500), nullable=True)

    # Numeric é usado (em vez de Float) para valores monetários,
    # pois evita erros de arredondamento comuns em ponto flutuante.
    # precision=10, scale=2 -> até 99.999.999,99
    preco_custo = Column(Numeric(10, 2), nullable=True)
    preco_venda = Column(Numeric(10, 2), nullable=True)

    # Quantidade atual em estoque
    quantidade_estoque = Column(Integer, nullable=False, default=0)

    # Quantidade mínima recomendada — quando quantidade_estoque cair
    # abaixo desse valor, o sistema deve gerar um alerta automático.
    estoque_minimo = Column(Integer, nullable=False, default=0)

    # Permite desativar um produto (descontinuado) sem apagar seu
    # histórico de movimentações.
    ativo = Column(Boolean, default=True, nullable=False)

    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    ########################################
    # RELACIONAMENTOS
    ########################################
    empresa = relationship("Empresa", back_populates="produtos")
    categoria = relationship("Categoria", back_populates="produtos")
    fornecedor = relationship("Fornecedor", back_populates="produtos")

    # Histórico de todas as movimentações (entradas/saídas) desse
    # produto. cascade="all, delete-orphan": se o produto for
    # excluído, seu histórico de movimentações é excluído junto.
    movimentacoes = relationship(
        "MovimentacaoEstoque", back_populates="produto", cascade="all, delete-orphan"
    )

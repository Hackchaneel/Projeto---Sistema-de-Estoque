############################################
# IMPORTAÇÕES
############################################
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database.database import Base


############################################
# CLASSE CATEGORIA
############################################
# Representa uma categoria de produtos (ex: "Bebidas", "Limpeza",
# "Eletrônicos"). Cada empresa tem suas próprias categorias — ou
# seja, a Empresa A pode ter uma categoria "Bebidas" totalmente
# independente da categoria "Bebidas" da Empresa B.
class Categoria(Base):
    __tablename__ = "categorias"

    ########################################
    # RESTRIÇÕES DE UNICIDADE
    ########################################
    # Evita que a mesma empresa cadastre duas categorias com o
    # mesmo nome (ex: duas categorias "Bebidas" na mesma empresa).
    __table_args__ = (
        UniqueConstraint("empresa_id", "nome", name="uq_categoria_nome_empresa"),
    )

    ########################################
    # COLUNAS
    ########################################
    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)

    nome = Column(String(100), nullable=False)
    descricao = Column(String(255), nullable=True)

    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    ########################################
    # RELACIONAMENTOS
    ########################################
    empresa = relationship("Empresa", back_populates="categorias")

    # Uma categoria pode ter vários produtos associados a ela.
    # Se a categoria for excluída, os produtos NÃO são excluídos
    # junto (por isso não usamos cascade delete aqui) — apenas
    # ficam sem categoria (ver categoria_id nullable em Produto).
    produtos = relationship("Produto", back_populates="categoria")

############################################
# IMPORTAÇÕES
############################################
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.database.database import Base


############################################
# CLASSE FORNECEDOR
############################################
# Representa um fornecedor de produtos. Conforme definido na
# arquitetura, o fornecedor é uma entidade SEPARADA (não é apenas um
# campo de texto dentro do produto), e cada produto pode (opcional-
# mente) estar vinculado a um fornecedor.
class Fornecedor(Base):
    __tablename__ = "fornecedores"

    ########################################
    # COLUNAS
    ########################################
    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)

    nome = Column(String(150), nullable=False)

    # Aceita tanto CNPJ (pessoa jurídica) quanto CPF (pessoa física),
    # já que um fornecedor pode ser um autônomo em alguns casos.
    cnpj_cpf = Column(String(18), nullable=True)

    telefone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)

    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    ########################################
    # RELACIONAMENTOS
    ########################################
    empresa = relationship("Empresa", back_populates="fornecedores")

    # Um fornecedor pode fornecer vários produtos. Assim como em
    # Categoria, não usamos cascade delete: se o fornecedor for
    # removido, o produto continua existindo, apenas sem fornecedor
    # vinculado.
    produtos = relationship("Produto", back_populates="fornecedor")

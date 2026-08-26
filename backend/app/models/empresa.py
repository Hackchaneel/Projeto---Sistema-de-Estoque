############################################
# IMPORTAÇÕES
############################################
# Column, Integer, String, DateTime: tipos de colunas do banco
# func: usado para gerar timestamps automáticos (data/hora atual)
# relationship: cria a ligação entre Empresa e suas tabelas filhas
#               (funcionários, produtos, fornecedores, categorias)
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.database.database import Base


############################################
# CLASSE EMPRESA
############################################
# Representa cada empresa cadastrada no sistema. Como o sistema é
# MULTIEMPRESA, toda tabela "filha" (funcionário, produto, fornecedor,
# categoria) possui uma chave estrangeira apontando para uma Empresa,
# garantindo que os dados de uma empresa nunca se misturem com os de
# outra.
class Empresa(Base):
    __tablename__ = "empresas"

    ########################################
    # COLUNAS
    ########################################
    id = Column(Integer, primary_key=True, index=True)

    # Código único da empresa, usado no login (junto com código do
    # funcionário, email e senha). Ex: "EMP001".
    codigo = Column(String(20), unique=True, nullable=False, index=True)

    # Razão social (nome oficial/jurídico da empresa)
    razao_social = Column(String(150), nullable=False)

    # Nome fantasia (nome popular/comercial da empresa)
    nome_fantasia = Column(String(150), nullable=True)

    # CNPJ da empresa (único no sistema)
    cnpj = Column(String(18), unique=True, nullable=False)

    # Dados de contato
    email = Column(String(150), nullable=True)
    telefone = Column(String(20), nullable=True)

    # Data de criação e última atualização do registro, preenchidas
    # automaticamente pelo próprio banco de dados.
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    ########################################
    # RELACIONAMENTOS
    ########################################
    # "back_populates" cria a ligação nos dois sentidos: a partir de
    # uma Empresa dá pra acessar empresa.funcionarios, e a partir de
    # um Funcionário dá pra acessar funcionario.empresa.
    #
    # cascade="all, delete-orphan": se uma empresa for excluída, todos
    # os registros filhos (funcionários, produtos, etc.) também são
    # excluídos automaticamente, evitando dados "órfãos" no banco.
    funcionarios = relationship(
        "Funcionario", back_populates="empresa", cascade="all, delete-orphan"
    )
    produtos = relationship(
        "Produto", back_populates="empresa", cascade="all, delete-orphan"
    )
    fornecedores = relationship(
        "Fornecedor", back_populates="empresa", cascade="all, delete-orphan"
    )
    categorias = relationship(
        "Categoria", back_populates="empresa", cascade="all, delete-orphan"
    )

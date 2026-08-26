############################################
# IMPORTAÇÕES
############################################
# enum: usado para criar o "PerfilUsuario", uma lista fixa de perfis
#       de permissão (Administrador, Gerente, Estoquista, Funcionário)
# Column, Integer, String, Boolean, DateTime, ForeignKey, Enum,
# UniqueConstraint: tipos de coluna e restrições do banco
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database.database import Base


############################################
# ENUM DE PERFIS DE USUÁRIO
############################################
# Define os 4 perfis de permissão previstos na arquitetura do
# sistema. Cada perfil terá regras de acesso diferentes, que serão
# validadas na camada de autenticação/autorização (app/auth).
class PerfilUsuario(str, enum.Enum):
    ADMINISTRADOR = "administrador"
    GERENTE = "gerente"
    ESTOQUISTA = "estoquista"
    FUNCIONARIO = "funcionario"


############################################
# CLASSE FUNCIONARIO
############################################
# Representa um funcionário vinculado a uma empresa. O login do
# sistema é composto por: código da empresa + código do funcionário
# + email + senha (nunca login apenas por email), conforme definido
# na arquitetura do projeto.
class Funcionario(Base):
    __tablename__ = "funcionarios"

    ########################################
    # RESTRIÇÕES DE UNICIDADE
    ########################################
    # Garante que o "código do funcionário" e o "email" sejam únicos
    # DENTRO de cada empresa (duas empresas diferentes podem ter,
    # cada uma, um funcionário de código "F001", por exemplo).
    __table_args__ = (
        UniqueConstraint("empresa_id", "codigo", name="uq_funcionario_codigo_empresa"),
        UniqueConstraint("empresa_id", "email", name="uq_funcionario_email_empresa"),
    )

    ########################################
    # COLUNAS
    ########################################
    id = Column(Integer, primary_key=True, index=True)

    # Chave estrangeira: a qual empresa esse funcionário pertence
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)

    # Código do funcionário dentro da empresa (usado no login). Ex: "F001"
    codigo = Column(String(20), nullable=False, index=True)

    nome = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)

    # Nunca armazenamos a senha em texto puro — apenas o hash gerado
    # com bcrypt (isso é feito na camada de autenticação, app/auth).
    senha_hash = Column(String(255), nullable=False)

    # Perfil de permissão do funcionário dentro do sistema
    perfil = Column(
        Enum(PerfilUsuario, name="perfil_usuario"),
        nullable=False,
        default=PerfilUsuario.FUNCIONARIO,
    )

    # Permite desativar um funcionário sem excluí-lo do banco
    # (mantendo o histórico de movimentações associado a ele)
    ativo = Column(Boolean, default=True, nullable=False)

    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    ########################################
    # RELACIONAMENTOS
    ########################################
    empresa = relationship("Empresa", back_populates="funcionarios")

############################################
# IMPORTAÇÕES
############################################
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
    func,
)
from sqlalchemy.orm import relationship

from app.database.database import Base


############################################
# ENUM: TIPO DE MOVIMENTAÇÃO
############################################
# Define os únicos dois tipos de movimentação de estoque previstos
# na arquitetura do projeto: entrada (compra, devolução, ajuste
# positivo) e saída (venda, perda, ajuste negativo).
class TipoMovimentacao(str, enum.Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"


############################################
# CLASSE MOVIMENTACAO ESTOQUE
############################################
# Representa cada alteração de quantidade em um produto. É a tabela
# de HISTÓRICO do sistema: nunca é editada ou apagada depois de
# criada, apenas consultada — isso garante rastreabilidade completa
# de tudo que já entrou ou saiu do estoque, e de quem fez cada
# movimentação.
class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"

    ########################################
    # COLUNAS
    ########################################
    id = Column(Integer, primary_key=True, index=True)

    # Guardamos o empresa_id diretamente (mesmo já sendo possível
    # chegar nele através do produto) para facilitar e acelerar
    # consultas de histórico filtradas por empresa.
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)

    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)

    # Quem realizou a movimentação (para fins de auditoria/histórico)
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)

    tipo = Column(Enum(TipoMovimentacao, name="tipo_movimentacao"), nullable=False)

    # Sempre um número positivo — o TIPO (entrada/saída) é quem
    # define se essa quantidade soma ou subtrai do estoque, e não o
    # sinal do número.
    quantidade = Column(Integer, nullable=False)

    # Motivo opcional da movimentação (ex: "Compra NF 1234",
    # "Venda balcão", "Produto danificado", "Ajuste de inventário")
    motivo = Column(String(255), nullable=True)

    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    ########################################
    # RELACIONAMENTOS
    ########################################
    produto = relationship("Produto", back_populates="movimentacoes")
    funcionario = relationship("Funcionario")

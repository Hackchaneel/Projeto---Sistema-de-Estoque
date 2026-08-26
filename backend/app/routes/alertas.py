############################################
# IMPORTAÇÕES
############################################
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.database import get_db
from app.models.produto import Produto
from app.models.funcionario import Funcionario
from app.auth.dependencies import obter_funcionario_atual


############################################
# CONFIGURAÇÃO DO ROUTER
############################################
router = APIRouter(prefix="/alertas", tags=["Alertas"])


############################################
# SCHEMA DE SAÍDA
############################################
class AlertaResponse(BaseModel):
    produto_id: int
    codigo: str
    nome: str
    quantidade_estoque: int
    estoque_minimo: int
    mensagem: str


############################################
# ROTA: LISTAR ALERTAS DE ESTOQUE BAIXO
############################################
# Reúne, em uma única lista, todos os produtos da empresa cujo
# estoque atual está abaixo do mínimo recomendado — a mesma regra
# já usada na rota de movimentação, só que aqui consultável a
# qualquer momento, sem precisar registrar uma movimentação nova
# para "descobrir" que um produto está em alerta.
@router.get("/", response_model=List[AlertaResponse])
def listar_alertas(
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
):
    produtos_da_empresa = (
        db.query(Produto)
        .filter(
            Produto.empresa_id == funcionario_atual.empresa_id,
            Produto.ativo == True,  # noqa: E712 (comparação explícita, mais clara aqui)
        )
        .all()
    )

    alertas = []
    for produto in produtos_da_empresa:
        if produto.quantidade_estoque < produto.estoque_minimo:
            alertas.append(
                AlertaResponse(
                    produto_id=produto.id,
                    codigo=produto.codigo,
                    nome=produto.nome,
                    quantidade_estoque=produto.quantidade_estoque,
                    estoque_minimo=produto.estoque_minimo,
                    mensagem=(
                        f"⚠ {produto.codigo} abaixo do estoque mínimo. "
                        f"Atual: {produto.quantidade_estoque}. "
                        f"Mínimo recomendado: {produto.estoque_minimo}."
                    ),
                )
            )

    # Ordena do mais crítico (menor quantidade) para o menos crítico
    alertas.sort(key=lambda a: a.quantidade_estoque)
    return alertas

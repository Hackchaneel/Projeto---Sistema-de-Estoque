############################################
# IMPORTAÇÕES
############################################
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.database import get_db
from app.models.produto import Produto
from app.models.movimentacao import MovimentacaoEstoque, TipoMovimentacao
from app.models.funcionario import Funcionario, PerfilUsuario
from app.auth.dependencies import obter_funcionario_atual, exigir_perfil


############################################
# CONFIGURAÇÃO DO ROUTER
############################################
router = APIRouter(prefix="/movimentacoes", tags=["Movimentações de Estoque"])

# Estoquista também pode registrar movimentações (é literalmente a
# função dele no dia a dia), além de Administrador e Gerente.
PERFIS_MOVIMENTACAO = [
    PerfilUsuario.ADMINISTRADOR,
    PerfilUsuario.GERENTE,
    PerfilUsuario.ESTOQUISTA,
]


############################################
# SCHEMAS (ENTRADA E SAÍDA)
############################################
class MovimentacaoCreate(BaseModel):
    produto_id: int
    tipo: TipoMovimentacao

    # gt=0 -> a quantidade tem que ser maior que zero. O FastAPI já
    # rejeita automaticamente valores negativos ou iguais a zero,
    # sem precisar validar isso manualmente na rota.
    quantidade: int = Field(gt=0)

    motivo: Optional[str] = None


class MovimentacaoResponse(BaseModel):
    id: int
    produto_id: int
    funcionario_id: int
    tipo: TipoMovimentacao
    quantidade: int
    motivo: Optional[str]
    criado_em: datetime

    # Campos "extras", calculados na hora da resposta (não existem
    # como coluna na tabela de movimentação, mas ajudam bastante
    # quem estiver consumindo a API a entender o resultado da ação
    # sem precisar fazer uma segunda consulta ao produto).
    estoque_atual: int
    alerta: Optional[str] = None

    class Config:
        from_attributes = True


############################################
# ROTA: REGISTRAR MOVIMENTAÇÃO (ENTRADA OU SAÍDA)
############################################
@router.post(
    "/", response_model=MovimentacaoResponse, status_code=status.HTTP_201_CREATED
)
def registrar_movimentacao(
    dados: MovimentacaoCreate,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    _: None = Depends(exigir_perfil(PERFIS_MOVIMENTACAO)),
):
    ########################################
    # 1) BUSCA O PRODUTO (garantindo que é da mesma empresa)
    ########################################
    produto = (
        db.query(Produto)
        .filter(
            Produto.id == dados.produto_id,
            Produto.empresa_id == funcionario_atual.empresa_id,
        )
        .first()
    )
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    ########################################
    # 2) APLICA A MOVIMENTAÇÃO NO ESTOQUE
    ########################################
    if dados.tipo == TipoMovimentacao.ENTRADA:
        produto.quantidade_estoque += dados.quantidade

    else:  # TipoMovimentacao.SAIDA
        # Nunca permite que o estoque fique negativo. Isso protege
        # a integridade dos dados mesmo que o frontend, por algum
        # bug, tente enviar uma saída maior do que o disponível.
        if dados.quantidade > produto.quantidade_estoque:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Estoque insuficiente. Disponível: "
                    f"{produto.quantidade_estoque}, solicitado: {dados.quantidade}."
                ),
            )
        produto.quantidade_estoque -= dados.quantidade

    ########################################
    # 3) REGISTRA A MOVIMENTAÇÃO NO HISTÓRICO
    ########################################
    nova_movimentacao = MovimentacaoEstoque(
        empresa_id=funcionario_atual.empresa_id,
        produto_id=produto.id,
        funcionario_id=funcionario_atual.id,
        tipo=dados.tipo,
        quantidade=dados.quantidade,
        motivo=dados.motivo,
    )
    db.add(nova_movimentacao)

    # Um único commit salva as DUAS mudanças juntas (a atualização
    # do produto E a criação da movimentação) de forma atômica: ou
    # as duas são salvas, ou nenhuma é (se der erro no meio).
    db.commit()
    db.refresh(nova_movimentacao)
    db.refresh(produto)

    ########################################
    # 4) VERIFICA SE PRECISA GERAR ALERTA
    ########################################
    # Prévia do sistema de alertas definido na arquitetura: sempre
    # que uma movimentação deixar o estoque abaixo do mínimo
    # recomendado, avisamos isso já na própria resposta.
    alerta = None
    if produto.quantidade_estoque < produto.estoque_minimo:
        alerta = (
            f"⚠ {produto.codigo} abaixo do estoque mínimo. "
            f"Atual: {produto.quantidade_estoque}. "
            f"Mínimo recomendado: {produto.estoque_minimo}."
        )

    # Monta a resposta manualmente (em vez de só devolver o objeto
    # do banco), pois precisamos incluir os campos calculados
    # "estoque_atual" e "alerta", que não existem na tabela.
    return MovimentacaoResponse(
        id=nova_movimentacao.id,
        produto_id=nova_movimentacao.produto_id,
        funcionario_id=nova_movimentacao.funcionario_id,
        tipo=nova_movimentacao.tipo,
        quantidade=nova_movimentacao.quantidade,
        motivo=nova_movimentacao.motivo,
        criado_em=nova_movimentacao.criado_em,
        estoque_atual=produto.quantidade_estoque,
        alerta=alerta,
    )


############################################
# ROTA: LISTAR HISTÓRICO DE MOVIMENTAÇÕES
############################################
# Qualquer funcionário logado pode CONSULTAR o histórico (é
# informação, não uma ação de risco) — só a criação de movimentação
# é restrita aos perfis definidos em PERFIS_MOVIMENTACAO.
#
# O parâmetro "produto_id" é opcional: se informado, filtra o
# histórico só daquele produto; se omitido, traz tudo da empresa.
@router.get("/", response_model=List[MovimentacaoResponse])
def listar_movimentacoes(
    produto_id: Optional[int] = None,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
):
    consulta = db.query(MovimentacaoEstoque).filter(
        MovimentacaoEstoque.empresa_id == funcionario_atual.empresa_id
    )

    if produto_id is not None:
        consulta = consulta.filter(MovimentacaoEstoque.produto_id == produto_id)

    movimentacoes = consulta.order_by(MovimentacaoEstoque.criado_em.desc()).all()

    # Monta a resposta de cada item incluindo o estoque atual do
    # produto correspondente (não o estoque "no momento daquela
    # movimentação", que exigiria guardar um snapshot histórico —
    # melhoria possível para uma versão futura do sistema).
    resposta = []
    for mov in movimentacoes:
        resposta.append(
            MovimentacaoResponse(
                id=mov.id,
                produto_id=mov.produto_id,
                funcionario_id=mov.funcionario_id,
                tipo=mov.tipo,
                quantidade=mov.quantidade,
                motivo=mov.motivo,
                criado_em=mov.criado_em,
                estoque_atual=mov.produto.quantidade_estoque,
                alerta=None,
            )
        )
    return resposta

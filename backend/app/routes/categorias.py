############################################
# IMPORTAÇÕES
############################################
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.database import get_db
from app.models.categoria import Categoria
from app.models.funcionario import Funcionario, PerfilUsuario
from app.auth.dependencies import obter_funcionario_atual, exigir_perfil


############################################
# CONFIGURAÇÃO DO ROUTER
############################################
router = APIRouter(prefix="/categorias", tags=["Categorias"])

# Perfis que podem criar, editar ou excluir categorias. Qualquer
# funcionário logado (independente do perfil) pode apenas VISUALIZAR.
PERFIS_GESTAO = [PerfilUsuario.ADMINISTRADOR, PerfilUsuario.GERENTE]


############################################
# SCHEMAS (ENTRADA E SAÍDA)
############################################
class CategoriaCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None


# Mesma estrutura da criação, mas todos os campos são opcionais —
# permite atualizar só o campo que a pessoa quiser, sem precisar
# reenviar tudo.
class CategoriaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None


class CategoriaResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    empresa_id: int

    class Config:
        from_attributes = True


############################################
# FUNÇÃO AUXILIAR: BUSCAR CATEGORIA DA PRÓPRIA EMPRESA
############################################
# Centraliza a lógica de "buscar a categoria pelo id, mas só se ela
# pertencer à empresa do funcionário logado". Isso é usado nas rotas
# de detalhe, edição e exclusão, evitando repetir esse código 3 vezes
# e garantindo que ninguém acesse/altere dado de outra empresa.
def _buscar_categoria_da_empresa(
    categoria_id: int, funcionario_atual: Funcionario, db: Session
) -> Categoria:
    categoria = (
        db.query(Categoria)
        .filter(
            Categoria.id == categoria_id,
            Categoria.empresa_id == funcionario_atual.empresa_id,
        )
        .first()
    )
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada.",
        )
    return categoria


############################################
# ROTA: CRIAR CATEGORIA
############################################
@router.post(
    "/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED
)
def criar_categoria(
    dados: CategoriaCreate,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    _: None = Depends(exigir_perfil(PERFIS_GESTAO)),
):
    # Impede duas categorias com o mesmo nome na mesma empresa
    ja_existe = (
        db.query(Categoria)
        .filter(
            Categoria.empresa_id == funcionario_atual.empresa_id,
            Categoria.nome == dados.nome,
        )
        .first()
    )
    if ja_existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma categoria com esse nome.",
        )

    nova_categoria = Categoria(
        empresa_id=funcionario_atual.empresa_id,
        nome=dados.nome,
        descricao=dados.descricao,
    )
    db.add(nova_categoria)
    db.commit()
    db.refresh(nova_categoria)
    return nova_categoria


############################################
# ROTA: LISTAR CATEGORIAS DA EMPRESA
############################################
@router.get("/", response_model=List[CategoriaResponse])
def listar_categorias(
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
):
    return (
        db.query(Categoria)
        .filter(Categoria.empresa_id == funcionario_atual.empresa_id)
        .all()
    )


############################################
# ROTA: BUSCAR UMA CATEGORIA ESPECÍFICA
############################################
@router.get("/{categoria_id}", response_model=CategoriaResponse)
def obter_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
):
    return _buscar_categoria_da_empresa(categoria_id, funcionario_atual, db)


############################################
# ROTA: ATUALIZAR CATEGORIA
############################################
@router.put("/{categoria_id}", response_model=CategoriaResponse)
def atualizar_categoria(
    categoria_id: int,
    dados: CategoriaUpdate,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    _: None = Depends(exigir_perfil(PERFIS_GESTAO)),
):
    categoria = _buscar_categoria_da_empresa(categoria_id, funcionario_atual, db)

    # exclude_unset=True: só considera os campos que a pessoa
    # realmente enviou no corpo da requisição, ignorando os que
    # ficaram de fora (evita sobrescrever com None sem querer).
    dados_para_atualizar = dados.model_dump(exclude_unset=True)
    for campo, valor in dados_para_atualizar.items():
        setattr(categoria, campo, valor)

    db.commit()
    db.refresh(categoria)
    return categoria


############################################
# ROTA: EXCLUIR CATEGORIA
############################################
@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    _: None = Depends(exigir_perfil(PERFIS_GESTAO)),
):
    categoria = _buscar_categoria_da_empresa(categoria_id, funcionario_atual, db)
    db.delete(categoria)
    db.commit()
    return None

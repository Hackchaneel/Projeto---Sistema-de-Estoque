############################################
# IMPORTAÇÕES
############################################
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.database import get_db
from app.models.produto import Produto
from app.models.categoria import Categoria
from app.models.fornecedor import Fornecedor
from app.models.funcionario import Funcionario, PerfilUsuario
from app.auth.dependencies import obter_funcionario_atual, exigir_perfil


############################################
# CONFIGURAÇÃO DO ROUTER
############################################
router = APIRouter(prefix="/produtos", tags=["Produtos"])

PERFIS_GESTAO = [PerfilUsuario.ADMINISTRADOR, PerfilUsuario.GERENTE]


############################################
# SCHEMAS (ENTRADA E SAÍDA)
############################################
class ProdutoCreate(BaseModel):
    codigo: str
    nome: str
    descricao: Optional[str] = None
    categoria_id: Optional[int] = None
    fornecedor_id: Optional[int] = None
    preco_custo: Optional[Decimal] = None
    preco_venda: Optional[Decimal] = None
    quantidade_estoque: int = 0
    estoque_minimo: int = 0


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    categoria_id: Optional[int] = None
    fornecedor_id: Optional[int] = None
    preco_custo: Optional[Decimal] = None
    preco_venda: Optional[Decimal] = None
    estoque_minimo: Optional[int] = None
    ativo: Optional[bool] = None
    # Nota: "quantidade_estoque" propositalmente NÃO aparece aqui.
    # A quantidade em estoque não deve ser editada livremente por
    # essa rota — ela será alterada apenas pelas rotas de
    # movimentação de entrada/saída (próxima etapa do projeto),
    # que também registram o histórico dessa mudança.


class ProdutoResponse(BaseModel):
    id: int
    codigo: str
    nome: str
    descricao: Optional[str]
    categoria_id: Optional[int]
    fornecedor_id: Optional[int]
    preco_custo: Optional[Decimal]
    preco_venda: Optional[Decimal]
    quantidade_estoque: int
    estoque_minimo: int
    ativo: bool
    empresa_id: int

    class Config:
        from_attributes = True


############################################
# FUNÇÃO AUXILIAR: BUSCAR PRODUTO DA PRÓPRIA EMPRESA
############################################
def _buscar_produto_da_empresa(
    produto_id: int, funcionario_atual: Funcionario, db: Session
) -> Produto:
    produto = (
        db.query(Produto)
        .filter(
            Produto.id == produto_id,
            Produto.empresa_id == funcionario_atual.empresa_id,
        )
        .first()
    )
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )
    return produto


############################################
# FUNÇÃO AUXILIAR: VALIDAR CATEGORIA E FORNECEDOR
############################################
# Garante que, se um categoria_id ou fornecedor_id for informado,
# eles realmente existam E pertençam à mesma empresa do funcionário
# — evita vincular um produto a uma categoria/fornecedor de outra
# empresa.
def _validar_categoria_e_fornecedor(
    categoria_id: Optional[int],
    fornecedor_id: Optional[int],
    empresa_id: int,
    db: Session,
) -> None:
    if categoria_id is not None:
        categoria = (
            db.query(Categoria)
            .filter(Categoria.id == categoria_id, Categoria.empresa_id == empresa_id)
            .first()
        )
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria informada não encontrada.",
            )

    if fornecedor_id is not None:
        fornecedor = (
            db.query(Fornecedor)
            .filter(
                Fornecedor.id == fornecedor_id, Fornecedor.empresa_id == empresa_id
            )
            .first()
        )
        if not fornecedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fornecedor informado não encontrado.",
            )


############################################
# ROTA: CRIAR PRODUTO
############################################
@router.post(
    "/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED
)
def criar_produto(
    dados: ProdutoCreate,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    _: None = Depends(exigir_perfil(PERFIS_GESTAO)),
):
    _validar_categoria_e_fornecedor(
        dados.categoria_id, dados.fornecedor_id, funcionario_atual.empresa_id, db
    )

    # Impede dois produtos com o mesmo código na mesma empresa
    ja_existe = (
        db.query(Produto)
        .filter(
            Produto.empresa_id == funcionario_atual.empresa_id,
            Produto.codigo == dados.codigo,
        )
        .first()
    )
    if ja_existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um produto com esse código.",
        )

    novo_produto = Produto(
        empresa_id=funcionario_atual.empresa_id,
        codigo=dados.codigo,
        nome=dados.nome,
        descricao=dados.descricao,
        categoria_id=dados.categoria_id,
        fornecedor_id=dados.fornecedor_id,
        preco_custo=dados.preco_custo,
        preco_venda=dados.preco_venda,
        quantidade_estoque=dados.quantidade_estoque,
        estoque_minimo=dados.estoque_minimo,
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto


############################################
# ROTA: LISTAR PRODUTOS DA EMPRESA
############################################
@router.get("/", response_model=List[ProdutoResponse])
def listar_produtos(
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
):
    return (
        db.query(Produto)
        .filter(Produto.empresa_id == funcionario_atual.empresa_id)
        .all()
    )


############################################
# ROTA: BUSCAR UM PRODUTO ESPECÍFICO
############################################
@router.get("/{produto_id}", response_model=ProdutoResponse)
def obter_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
):
    return _buscar_produto_da_empresa(produto_id, funcionario_atual, db)


############################################
# ROTA: ATUALIZAR PRODUTO
############################################
@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: int,
    dados: ProdutoUpdate,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    _: None = Depends(exigir_perfil(PERFIS_GESTAO)),
):
    produto = _buscar_produto_da_empresa(produto_id, funcionario_atual, db)

    dados_para_atualizar = dados.model_dump(exclude_unset=True)

    _validar_categoria_e_fornecedor(
        dados_para_atualizar.get("categoria_id"),
        dados_para_atualizar.get("fornecedor_id"),
        funcionario_atual.empresa_id,
        db,
    )

    for campo, valor in dados_para_atualizar.items():
        setattr(produto, campo, valor)

    db.commit()
    db.refresh(produto)
    return produto


############################################
# ROTA: EXCLUIR PRODUTO
############################################
@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    _: None = Depends(exigir_perfil(PERFIS_GESTAO)),
):
    produto = _buscar_produto_da_empresa(produto_id, funcionario_atual, db)
    db.delete(produto)
    db.commit()
    return None

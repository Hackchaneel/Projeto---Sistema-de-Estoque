############################################
# IMPORTAÇÕES
############################################
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database.database import get_db
from app.models.fornecedor import Fornecedor
from app.models.funcionario import Funcionario, PerfilUsuario
from app.auth.dependencies import obter_funcionario_atual, exigir_perfil


############################################
# CONFIGURAÇÃO DO ROUTER
############################################
router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])

PERFIS_GESTAO = [PerfilUsuario.ADMINISTRADOR, PerfilUsuario.GERENTE]


############################################
# SCHEMAS (ENTRADA E SAÍDA)
############################################
class FornecedorCreate(BaseModel):
    nome: str
    cnpj_cpf: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None


class FornecedorUpdate(BaseModel):
    nome: Optional[str] = None
    cnpj_cpf: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None


class FornecedorResponse(BaseModel):
    id: int
    nome: str
    cnpj_cpf: Optional[str]
    telefone: Optional[str]
    email: Optional[str]
    empresa_id: int

    class Config:
        from_attributes = True


############################################
# FUNÇÃO AUXILIAR: BUSCAR FORNECEDOR DA PRÓPRIA EMPRESA
############################################
def _buscar_fornecedor_da_empresa(
    fornecedor_id: int, funcionario_atual: Funcionario, db: Session
) -> Fornecedor:
    fornecedor = (
        db.query(Fornecedor)
        .filter(
            Fornecedor.id == fornecedor_id,
            Fornecedor.empresa_id == funcionario_atual.empresa_id,
        )
        .first()
    )
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado.",
        )
    return fornecedor


############################################
# ROTA: CRIAR FORNECEDOR
############################################
@router.post(
    "/", response_model=FornecedorResponse, status_code=status.HTTP_201_CREATED
)
def criar_fornecedor(
    dados: FornecedorCreate,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    _: None = Depends(exigir_perfil(PERFIS_GESTAO)),
):
    novo_fornecedor = Fornecedor(
        empresa_id=funcionario_atual.empresa_id,
        nome=dados.nome,
        cnpj_cpf=dados.cnpj_cpf,
        telefone=dados.telefone,
        email=dados.email,
    )
    db.add(novo_fornecedor)
    db.commit()
    db.refresh(novo_fornecedor)
    return novo_fornecedor


############################################
# ROTA: LISTAR FORNECEDORES DA EMPRESA
############################################
@router.get("/", response_model=List[FornecedorResponse])
def listar_fornecedores(
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
):
    return (
        db.query(Fornecedor)
        .filter(Fornecedor.empresa_id == funcionario_atual.empresa_id)
        .all()
    )


############################################
# ROTA: BUSCAR UM FORNECEDOR ESPECÍFICO
############################################
@router.get("/{fornecedor_id}", response_model=FornecedorResponse)
def obter_fornecedor(
    fornecedor_id: int,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
):
    return _buscar_fornecedor_da_empresa(fornecedor_id, funcionario_atual, db)


############################################
# ROTA: ATUALIZAR FORNECEDOR
############################################
@router.put("/{fornecedor_id}", response_model=FornecedorResponse)
def atualizar_fornecedor(
    fornecedor_id: int,
    dados: FornecedorUpdate,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    _: None = Depends(exigir_perfil(PERFIS_GESTAO)),
):
    fornecedor = _buscar_fornecedor_da_empresa(fornecedor_id, funcionario_atual, db)

    dados_para_atualizar = dados.model_dump(exclude_unset=True)
    for campo, valor in dados_para_atualizar.items():
        setattr(fornecedor, campo, valor)

    db.commit()
    db.refresh(fornecedor)
    return fornecedor


############################################
# ROTA: EXCLUIR FORNECEDOR
############################################
@router.delete("/{fornecedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_fornecedor(
    fornecedor_id: int,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    _: None = Depends(exigir_perfil(PERFIS_GESTAO)),
):
    fornecedor = _buscar_fornecedor_da_empresa(fornecedor_id, funcionario_atual, db)
    db.delete(fornecedor)
    db.commit()
    return None

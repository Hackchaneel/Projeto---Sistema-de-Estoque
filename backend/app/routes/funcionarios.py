############################################
# IMPORTAÇÕES
############################################
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database.database import get_db
from app.models.empresa import Empresa
from app.models.funcionario import Funcionario, PerfilUsuario
from app.auth.security import gerar_hash_senha
from app.auth.dependencies import obter_funcionario_atual, exigir_perfil


############################################
# CONFIGURAÇÃO DO ROUTER
############################################
router = APIRouter(prefix="/funcionarios", tags=["Funcionários"])


############################################
# SCHEMAS (ENTRADA E SAÍDA)
############################################
# Dados necessários para CRIAR um funcionário. Note que recebemos
# "codigo_empresa" (o código público da empresa, ex: "EMP001"),
# e não o "empresa_id" interno do banco — isso evita expor o ID
# numérico interno e mantém a mesma lógica usada no login.
class FuncionarioCreate(BaseModel):
    codigo_empresa: str
    codigo: str
    nome: str
    email: EmailStr
    senha: str
    perfil: PerfilUsuario = PerfilUsuario.FUNCIONARIO


# Dados para ATUALIZAR um funcionário. Todos os campos são
# opcionais — só os enviados são alterados. Note que "senha" também
# é opcional aqui: só é alterada se for explicitamente enviada.
class FuncionarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha: Optional[str] = None
    perfil: Optional[PerfilUsuario] = None
    ativo: Optional[bool] = None


# Dados devolvidos pela API. Note que "senha_hash" NUNCA aparece
# aqui — é um campo sensível que jamais deve ser exposto pela API.
class FuncionarioResponse(BaseModel):
    id: int
    codigo: str
    nome: str
    email: str
    perfil: PerfilUsuario
    ativo: bool
    empresa_id: int

    class Config:
        from_attributes = True


############################################
# ROTA: CRIAR FUNCIONÁRIO
############################################
# PROTEGIDA: exige estar logado (obter_funcionario_atual) E ter o
# perfil de ADMINISTRADOR (exigir_perfil). Ou seja, só um
# administrador já existente pode cadastrar novos funcionários.
#
# Exceção conhecida: o PRIMEIRO administrador de uma empresa nova
# ainda precisa ser criado manualmente direto no banco (ou por essa
# mesma rota usando o token de um administrador de outra empresa,
# se o sistema permitir múltiplas empresas serem geridas por um
# super-usuário — isso pode ser refinado mais adiante).
@router.post(
    "/", response_model=FuncionarioResponse, status_code=status.HTTP_201_CREATED
)
def criar_funcionario(
    dados: FuncionarioCreate,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    _: None = Depends(exigir_perfil([PerfilUsuario.ADMINISTRADOR])),
):

    ########################################
    # 1) BUSCA A EMPRESA PELO CÓDIGO
    ########################################
    empresa = (
        db.query(Empresa).filter(Empresa.codigo == dados.codigo_empresa).first()
    )
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada para o código informado.",
        )

    ########################################
    # 1.1) GARANTE QUE O ADMIN SÓ CADASTRA NA PRÓPRIA EMPRESA
    ########################################
    # Mesmo sendo administrador, ele não pode cadastrar funcionários
    # em uma empresa diferente da sua — isso é o que garante o
    # isolamento multiempresa também na escrita, não só na leitura.
    if empresa.id != funcionario_atual.empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode cadastrar funcionários na sua própria empresa.",
        )

    ########################################
    # 2) VERIFICA DUPLICIDADE DENTRO DA EMPRESA
    ########################################
    funcionario_existente = (
        db.query(Funcionario)
        .filter(
            Funcionario.empresa_id == empresa.id,
            (Funcionario.codigo == dados.codigo) | (Funcionario.email == dados.email),
        )
        .first()
    )
    if funcionario_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um funcionário com esse código ou email nessa empresa.",
        )

    ########################################
    # 3) CRIA O FUNCIONÁRIO COM SENHA JÁ EM HASH
    ########################################
    novo_funcionario = Funcionario(
        empresa_id=empresa.id,
        codigo=dados.codigo,
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash_senha(dados.senha),
        perfil=dados.perfil,
    )

    db.add(novo_funcionario)
    db.commit()
    db.refresh(novo_funcionario)

    return novo_funcionario


############################################
# ROTA: LISTAR FUNCIONÁRIOS DA PRÓPRIA EMPRESA
############################################
# PROTEGIDA: exige apenas estar logado (qualquer perfil). A empresa
# usada no filtro vem do TOKEN do funcionário logado, não de um
# parâmetro na URL — isso impede que alguém tente listar
# funcionários de outra empresa só trocando um valor na requisição.
@router.get("/", response_model=List[FuncionarioResponse])
def listar_funcionarios(
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
):
    return (
        db.query(Funcionario)
        .filter(Funcionario.empresa_id == funcionario_atual.empresa_id)
        .all()
    )


############################################
# FUNÇÃO AUXILIAR: BUSCAR FUNCIONÁRIO DA PRÓPRIA EMPRESA
############################################
def _buscar_funcionario_da_empresa(
    funcionario_id: int, funcionario_atual: Funcionario, db: Session
) -> Funcionario:
    funcionario = (
        db.query(Funcionario)
        .filter(
            Funcionario.id == funcionario_id,
            Funcionario.empresa_id == funcionario_atual.empresa_id,
        )
        .first()
    )
    if not funcionario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado.",
        )
    return funcionario


############################################
# ROTA: ATUALIZAR FUNCIONÁRIO
############################################
# PROTEGIDA: só Administrador pode editar dados de outros
# funcionários (nome, email, senha, perfil, status ativo/inativo).
@router.put("/{funcionario_id}", response_model=FuncionarioResponse)
def atualizar_funcionario(
    funcionario_id: int,
    dados: FuncionarioUpdate,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    _: None = Depends(exigir_perfil([PerfilUsuario.ADMINISTRADOR])),
):
    funcionario = _buscar_funcionario_da_empresa(funcionario_id, funcionario_atual, db)

    dados_para_atualizar = dados.model_dump(exclude_unset=True)

    # Se uma nova senha foi enviada, transforma em hash antes de
    # salvar — nunca gravamos senha em texto puro.
    if "senha" in dados_para_atualizar:
        senha_nova = dados_para_atualizar.pop("senha")
        if senha_nova:
            funcionario.senha_hash = gerar_hash_senha(senha_nova)

    for campo, valor in dados_para_atualizar.items():
        setattr(funcionario, campo, valor)

    db.commit()
    db.refresh(funcionario)
    return funcionario


############################################
# ROTA: DESATIVAR FUNCIONÁRIO
############################################
# Esta rota NÃO apaga o funcionário do banco — apenas marca
# "ativo=False". Isso é proposital: o histórico de movimentações de
# estoque referencia o funcionário que realizou cada ação, e excluir
# o registro de verdade quebraria essa rastreabilidade (ou exigiria
# apagar o histórico junto, o que é pior ainda). Um funcionário
# desativado simplesmente não consegue mais fazer login
# (verificado em obter_funcionario_atual), mas seu nome continua
# aparecendo corretamente no histórico.
@router.delete("/{funcionario_id}", status_code=status.HTTP_204_NO_CONTENT)
def desativar_funcionario(
    funcionario_id: int,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    _: None = Depends(exigir_perfil([PerfilUsuario.ADMINISTRADOR])),
):
    funcionario = _buscar_funcionario_da_empresa(funcionario_id, funcionario_atual, db)

    # Impede que um administrador desative a própria conta (evitaria
    # a empresa ficar sem nenhum administrador ativo por acidente).
    if funcionario.id == funcionario_atual.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode desativar a própria conta.",
        )

    funcionario.ativo = False
    db.commit()
    return None

############################################
# IMPORTAÇÕES
############################################
# APIRouter, Depends, HTTPException, status: montam a rota e tratam erros
# Session: tipo da sessão do banco de dados
# BaseModel: usado para criar os schemas de entrada/saída dessa rota
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database.database import get_db
from app.models.empresa import Empresa
from app.models.funcionario import Funcionario, PerfilUsuario
from app.auth.dependencies import obter_funcionario_atual, exigir_perfil


############################################
# CONFIGURAÇÃO DO ROUTER
############################################
router = APIRouter(prefix="/empresas", tags=["Empresas"])


############################################
# SCHEMAS (ENTRADA E SAÍDA)
############################################
# Nota: por simplicidade, os schemas de cada módulo (empresas,
# funcionários, produtos...) ficam no topo do próprio arquivo de
# rota, sem criar uma pasta "schemas" separada — isso mantém a
# arquitetura original definida pelo projeto (auth, database, models,
# routes, services). Se o projeto crescer muito, migrar os schemas
# para arquivos próprios é uma melhoria natural a considerar depois.

# Dados necessários para CRIAR uma empresa
class EmpresaCreate(BaseModel):
    codigo: str
    razao_social: str
    nome_fantasia: str | None = None
    cnpj: str
    email: EmailStr | None = None
    telefone: str | None = None


# Dados para ATUALIZAR uma empresa (as "configurações" da empresa).
# Propositalmente NÃO inclui "codigo" nem "cnpj" — mudar esses dois
# depois de criados poderia quebrar referências e identidade legal
# da empresa; se for realmente necessário, é um caso raro o
# suficiente para ser tratado manualmente, não por uma rota comum.
class EmpresaUpdate(BaseModel):
    razao_social: str | None = None
    nome_fantasia: str | None = None
    email: EmailStr | None = None
    telefone: str | None = None


# Dados devolvidos pela API ao consultar/criar uma empresa
# (nunca expomos campos sensíveis, mas aqui a Empresa não tem
# nenhum campo de senha, então tudo é seguro para exibir)
class EmpresaResponse(BaseModel):
    id: int
    codigo: str
    razao_social: str
    nome_fantasia: str | None
    cnpj: str
    email: str | None
    telefone: str | None

    class Config:
        from_attributes = True


############################################
# ROTA: CRIAR EMPRESA
############################################
# TODO DE SEGURANÇA: por enquanto essa rota está aberta (sem exigir
# login), pois é o único jeito de cadastrar a PRIMEIRA empresa do
# sistema (não existe ainda quem fazer login). Quando o sistema
# estiver mais maduro, o ideal é proteger esse cadastro (ex: com uma
# chave de administração do sistema, ou um fluxo de aprovação),
# para que qualquer pessoa não consiga criar empresas livremente.
@router.post("/", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
def criar_empresa(dados: EmpresaCreate, db: Session = Depends(get_db)):

    # Verifica se já existe uma empresa com esse código ou CNPJ,
    # para não permitir duplicidade.
    empresa_existente = (
        db.query(Empresa)
        .filter(
            (Empresa.codigo == dados.codigo) | (Empresa.cnpj == dados.cnpj)
        )
        .first()
    )
    if empresa_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma empresa cadastrada com esse código ou CNPJ.",
        )

    # Cria o objeto Empresa a partir dos dados recebidos e valida-
    # dos automaticamente pelo schema EmpresaCreate.
    nova_empresa = Empresa(
        codigo=dados.codigo,
        razao_social=dados.razao_social,
        nome_fantasia=dados.nome_fantasia,
        cnpj=dados.cnpj,
        email=dados.email,
        telefone=dados.telefone,
    )

    # Salva no banco: add() prepara o registro, commit() confirma a
    # gravação, e refresh() atualiza o objeto com os dados gerados
    # pelo banco (como o "id" e "criado_em").
    db.add(nova_empresa)
    db.commit()
    db.refresh(nova_empresa)

    return nova_empresa


############################################
# ROTA: LISTAR EMPRESAS
############################################
# TODO DE SEGURANÇA: futuramente restringir para que apenas um
# "super administrador" do sistema (não de uma empresa específica)
# consiga listar todas as empresas cadastradas.
@router.get("/", response_model=List[EmpresaResponse])
def listar_empresas(db: Session = Depends(get_db)):
    return db.query(Empresa).all()


############################################
# ROTA: ATUALIZAR DADOS DA PRÓPRIA EMPRESA (CONFIGURAÇÕES)
############################################
# PROTEGIDA: só Administrador pode editar os dados da empresa, e
# apenas da PRÓPRIA empresa (empresa_id vem do token, não de um
# parâmetro escolhido livremente — evita que um admin edite dados
# de uma empresa concorrente só adivinhando o id).
@router.put("/{empresa_id}", response_model=EmpresaResponse)
def atualizar_empresa(
    empresa_id: int,
    dados: EmpresaUpdate,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    _: None = Depends(exigir_perfil([PerfilUsuario.ADMINISTRADOR])),
):
    if empresa_id != funcionario_atual.empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode editar os dados da sua própria empresa.",
        )

    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada.",
        )

    dados_para_atualizar = dados.model_dump(exclude_unset=True)
    for campo, valor in dados_para_atualizar.items():
        setattr(empresa, campo, valor)

    db.commit()
    db.refresh(empresa)
    return empresa

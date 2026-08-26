############################################
# IMPORTAÇÕES
############################################
# BaseModel: classe base do Pydantic, usada para validar
#            automaticamente os dados recebidos/enviados pela API
from pydantic import BaseModel, EmailStr


############################################
# SCHEMA DE ENTRADA (LOGIN)
############################################
# Representa exatamente os dados que o frontend deve enviar para a
# rota de login. O FastAPI valida automaticamente: se faltar algum
# campo, ou se o email não tiver formato válido, a API já devolve um
# erro 422 sem a gente precisar validar isso manualmente.
class LoginRequest(BaseModel):
    codigo_empresa: str
    codigo_funcionario: str
    email: EmailStr
    senha: str


############################################
# SCHEMA DE SAÍDA (TOKEN)
############################################
# Representa o que a API devolve depois de um login bem-sucedido.
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


############################################
# SCHEMA DO FUNCIONÁRIO LOGADO
############################################
# Representa os dados básicos do funcionário autenticado, devolvidos
# junto com o token (útil para o frontend exibir nome, perfil, etc.
# sem precisar decodificar o JWT manualmente).
class FuncionarioLogado(BaseModel):
    id: int
    nome: str
    email: str
    perfil: str
    empresa_id: int

    # Permite que esse schema seja criado diretamente a partir de um
    # objeto do SQLAlchemy (model Funcionario), e não só de um dict.
    class Config:
        from_attributes = True

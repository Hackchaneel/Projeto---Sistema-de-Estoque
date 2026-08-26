############################################
# IMPORTAÇÕES
############################################
# os: usado para ler as variáveis de ambiente (SECRET_KEY, etc.)
# datetime/timedelta: usados para calcular a data de expiração do token
# jose: biblioteca usada para criar e validar tokens JWT
# CryptContext: usado pelo passlib para gerar e verificar hash de senha
import os
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv


############################################
# CONFIGURAÇÕES
############################################
load_dotenv()

# Chave secreta usada para assinar os tokens JWT. Vem do arquivo .env
# e NUNCA deve ser exposta publicamente (é ela que garante que
# ninguém consiga forjar um token válido sem conhecê-la).
SECRET_KEY = os.getenv("SECRET_KEY")

# Algoritmo de assinatura do token (definido no .env, padrão HS256)
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Tempo de expiração do token de acesso, em minutos
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

if not SECRET_KEY:
    raise ValueError(
        "A variável de ambiente SECRET_KEY não foi definida. "
        "Configure o arquivo .env antes de iniciar o sistema."
    )

# Contexto de criptografia de senha, usando o algoritmo bcrypt
# (padrão de mercado para hash de senhas, lento de propósito para
# dificultar ataques de força bruta).
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


############################################
# FUNÇÕES DE SENHA
############################################
def gerar_hash_senha(senha: str) -> str:
    """
    Recebe uma senha em texto puro e devolve o hash correspondente,
    que é o que deve ser armazenado no banco de dados (nunca a senha
    original).
    """
    return pwd_context.hash(senha)


def verificar_senha(senha_texto_puro: str, senha_hash: str) -> bool:
    """
    Compara uma senha digitada pelo usuário (texto puro) com o hash
    armazenado no banco, devolvendo True se baterem.
    """
    return pwd_context.verify(senha_texto_puro, senha_hash)


############################################
# FUNÇÕES DE TOKEN (JWT)
############################################
def criar_access_token(dados: dict) -> str:
    """
    Gera um token JWT assinado contendo os dados informados (ex: id
    do funcionário, id da empresa, perfil de permissão), além de uma
    data de expiração automática.
    """
    dados_para_codificar = dados.copy()

    # Calcula o momento exato em que o token vai expirar
    expira_em = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    dados_para_codificar.update({"exp": expira_em})

    # Codifica (assina) o token usando a chave secreta e o algoritmo
    # definidos nas configurações
    token = jwt.encode(dados_para_codificar, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decodificar_access_token(token: str) -> dict:
    """
    Valida e decodifica um token JWT. Se o token for inválido ou
    tiver expirado, lança uma exceção JWTError (tratada por quem
    chamar essa função).
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload

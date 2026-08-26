############################################
# IMPORTAÇÕES DOS MODELS
############################################
# Este arquivo importa todos os models do sistema em um único lugar.
# Isso é necessário para que o SQLAlchemy "enxergue" todas as tabelas
# na hora de rodar Base.metadata.create_all() (em app/main.py).
#
# Sem esses imports, o Python nunca chegaria a executar o código de
# cada arquivo de model, e as tabelas correspondentes não seriam
# criadas no banco de dados.
from app.models.empresa import Empresa
from app.models.funcionario import Funcionario, PerfilUsuario
from app.models.categoria import Categoria
from app.models.fornecedor import Fornecedor
from app.models.produto import Produto
from app.models.movimentacao import MovimentacaoEstoque, TipoMovimentacao

# Frontend — Sistema de Estoque

Interface web em React (Vite) que consome a API do backend.

## Como rodar localmente

1. Entre na pasta do frontend:
   ```
   cd frontend
   ```

2. Instale as dependências:
   ```
   npm install
   ```

3. Copie o arquivo de variáveis de ambiente:
   ```
   cp .env.example .env
   ```
   (o valor padrão já aponta para o backend local, não precisa mudar
   nada se o backend estiver rodando em http://localhost:8000)

4. Rode o servidor de desenvolvimento:
   ```
   npm run dev
   ```

5. Acesse no navegador:
   ```
   http://localhost:5173
   ```

**Importante:** o backend precisa estar rodando (`uvicorn app.main:app --reload`)
para o frontend conseguir fazer login e carregar os dados.

## Estrutura

```
src/
├── components/    -> componentes reutilizáveis (Layout, RotaPrivada)
├── contexts/       -> AuthContext (gerencia login/logout/sessão)
├── pages/          -> uma tela por arquivo (Login, Dashboard, Produtos...)
├── services/       -> configuração do Axios (api.js)
├── App.jsx         -> definição de rotas
├── main.jsx        -> ponto de entrada
└── index.css       -> design system (cores, tipografia, componentes)
```

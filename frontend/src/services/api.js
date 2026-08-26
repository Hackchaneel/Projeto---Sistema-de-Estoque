import axios from "axios";

// ============================================================
// CONFIGURAÇÃO BASE DO AXIOS
// ============================================================
// Cria uma instância do Axios já configurada com o endereço do
// backend (lido da variável de ambiente VITE_API_URL). Assim, em
// todo o projeto, usamos "api.get(...)", "api.post(...)" etc, sem
// precisar repetir a URL completa toda vez.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

// ============================================================
// INTERCEPTOR DE REQUISIÇÃO
// ============================================================
// Antes de CADA requisição sair para o backend, este interceptor
// verifica se existe um token salvo (do login) e, se existir,
// adiciona automaticamente o cabeçalho "Authorization: Bearer ...".
// Isso evita que cada chamada de API precise adicionar o token
// manualmente.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ============================================================
// INTERCEPTOR DE RESPOSTA
// ============================================================
// Se o backend responder 401 (token inválido ou expirado) em
// qualquer requisição, isso significa que a sessão do usuário não
// é mais válida. Nesse caso, limpamos os dados salvos e mandamos a
// pessoa de volta para a tela de login automaticamente.
api.interceptors.response.use(
  (resposta) => resposta,
  (erro) => {
    if (erro.response && erro.response.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("funcionario");
      window.location.href = "/login";
    }
    return Promise.reject(erro);
  }
);

export default api;

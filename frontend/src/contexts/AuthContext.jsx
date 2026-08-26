import React, { createContext, useContext, useState } from "react";
import api from "../services/api.js";

// ============================================================
// CRIAÇÃO DO CONTEXTO
// ============================================================
// O AuthContext guarda, em um único lugar, tudo relacionado à
// sessão do usuário (se está logado, quem é, e as funções de
// login/logout). Qualquer componente da aplicação pode acessar
// isso através do hook useAuth(), sem precisar receber essas
// informações via props manualmente.
const AuthContext = createContext(null);

// ============================================================
// PROVEDOR DO CONTEXTO
// ============================================================
export function AuthProvider({ children }) {
  // Ao carregar a aplicação, tenta recuperar uma sessão já salva
  // no localStorage (para a pessoa não precisar logar de novo toda
  // vez que atualizar a página).
  const [funcionario, setFuncionario] = useState(() => {
    const salvo = localStorage.getItem("funcionario");
    return salvo ? JSON.parse(salvo) : null;
  });

  // --------------------------------------------------------
  // FUNÇÃO: LOGIN
  // --------------------------------------------------------
  // Envia os dados de login para o backend. Se der certo, salva o
  // token e os dados básicos do funcionário no localStorage (para
  // persistir entre recarregamentos de página) e no estado do
  // React (para a interface reagir imediatamente).
  async function login({ codigoEmpresa, codigoFuncionario, email, senha }) {
    const resposta = await api.post("/auth/login", {
      codigo_empresa: codigoEmpresa,
      codigo_funcionario: codigoFuncionario,
      email,
      senha,
    });

    const { access_token: token } = resposta.data;

    // Decodifica o "payload" do JWT manualmente (sem biblioteca
    // extra) só para extrair o perfil e o id do funcionário, e
    // exibir isso na interface (ex: nome/perfil na barra lateral).
    const payload = JSON.parse(atob(token.split(".")[1]));

    const dadosFuncionario = {
      id: payload.funcionario_id,
      empresaId: payload.empresa_id,
      codigoEmpresa,
      perfil: payload.perfil,
      email,
    };

    localStorage.setItem("token", token);
    localStorage.setItem("funcionario", JSON.stringify(dadosFuncionario));
    setFuncionario(dadosFuncionario);

    return dadosFuncionario;
  }

  // --------------------------------------------------------
  // FUNÇÃO: LOGOUT
  // --------------------------------------------------------
  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("funcionario");
    setFuncionario(null);
  }

  const valor = {
    funcionario,
    estaLogado: Boolean(funcionario),
    login,
    logout,
  };

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>;
}

// ============================================================
// HOOK DE ACESSO AO CONTEXTO
// ============================================================
// Facilita o uso do contexto em qualquer componente:
// const { funcionario, login, logout } = useAuth();
export function useAuth() {
  const contexto = useContext(AuthContext);
  if (!contexto) {
    throw new Error("useAuth precisa ser usado dentro de um AuthProvider.");
  }
  return contexto;
}

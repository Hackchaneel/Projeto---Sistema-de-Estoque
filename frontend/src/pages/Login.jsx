import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext.jsx";

// ============================================================
// PÁGINA DE LOGIN
// ============================================================
// Reproduz exatamente o formato de login definido na arquitetura
// do sistema: código da empresa + código do funcionário + email +
// senha (nunca login apenas por email).
export default function Login() {
  const { login } = useAuth();
  const navegar = useNavigate();

  const [codigoEmpresa, setCodigoEmpresa] = useState("");
  const [codigoFuncionario, setCodigoFuncionario] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");

  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState(null);

  // --------------------------------------------------------
  // ENVIO DO FORMULÁRIO
  // --------------------------------------------------------
  async function aoEnviar(evento) {
    evento.preventDefault();
    setErro(null);
    setCarregando(true);

    try {
      await login({ codigoEmpresa, codigoFuncionario, email, senha });
      navegar("/");
    } catch (erroRequisicao) {
      // Traduz o erro técnico do backend em uma mensagem clara,
      // sem expor detalhes internos da API para quem está usando.
      if (erroRequisicao.response?.status === 401) {
        setErro("Empresa, código, email ou senha inválidos.");
      } else if (erroRequisicao.response?.status === 403) {
        setErro("Este funcionário está inativo. Contate o administrador.");
      } else {
        setErro("Não foi possível conectar ao sistema. Tente novamente.");
      }
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="tela-login">
      <div className="tela-login__painel">
        <div className="tela-login__marca">
          Estoque<span>ERP</span>
        </div>
        <h1 className="tela-login__titulo">Entrar no sistema</h1>
        <p className="tela-login__subtitulo">
          Use o código da sua empresa e suas credenciais de funcionário.
        </p>

        {erro && <div className="mensagem-erro">{erro}</div>}

        <form onSubmit={aoEnviar}>
          <div className="campo">
            <label htmlFor="codigo_empresa">Código da empresa</label>
            <input
              id="codigo_empresa"
              type="text"
              placeholder="EMP001"
              value={codigoEmpresa}
              onChange={(e) => setCodigoEmpresa(e.target.value)}
              required
            />
          </div>

          <div className="campo">
            <label htmlFor="codigo_funcionario">Código do funcionário</label>
            <input
              id="codigo_funcionario"
              type="text"
              placeholder="F001"
              value={codigoFuncionario}
              onChange={(e) => setCodigoFuncionario(e.target.value)}
              required
            />
          </div>

          <div className="campo">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              placeholder="voce@empresa.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="campo">
            <label htmlFor="senha">Senha</label>
            <input
              id="senha"
              type="password"
              placeholder="••••••••"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="botao botao--primario tela-login__botao"
            disabled={carregando}
          >
            {carregando ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}

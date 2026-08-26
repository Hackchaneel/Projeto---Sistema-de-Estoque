import React, { useEffect, useState } from "react";
import api from "../services/api.js";

const ROTULOS_PERFIL = {
  administrador: "Administrador",
  gerente: "Gerente",
  estoquista: "Estoquista",
  funcionario: "Funcionário",
};

const SENHA_FORMULARIO_VAZIO = { senha_atual: "", senha_nova: "", confirmar_senha_nova: "" };

export default function Perfil() {
  const [meuPerfil, setMeuPerfil] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  const [formularioSenha, setFormularioSenha] = useState(SENHA_FORMULARIO_VAZIO);
  const [enviando, setEnviando] = useState(false);
  const [erroSenha, setErroSenha] = useState(null);
  const [sucessoSenha, setSucessoSenha] = useState(false);

  useEffect(() => {
    async function carregar() {
      try {
        const resposta = await api.get("/perfil/");
        setMeuPerfil(resposta.data);
      } catch {
        setErro("Não foi possível carregar seus dados.");
      } finally {
        setCarregando(false);
      }
    }
    carregar();
  }, []);

  async function aoTrocarSenha(evento) {
    evento.preventDefault();
    setErroSenha(null);
    setSucessoSenha(false);

    if (formularioSenha.senha_nova !== formularioSenha.confirmar_senha_nova) {
      setErroSenha("A confirmação não coincide com a nova senha.");
      return;
    }

    setEnviando(true);
    try {
      await api.put("/perfil/senha", {
        senha_atual: formularioSenha.senha_atual,
        senha_nova: formularioSenha.senha_nova,
      });
      setFormularioSenha(SENHA_FORMULARIO_VAZIO);
      setSucessoSenha(true);
    } catch (erroRequisicao) {
      setErroSenha(
        erroRequisicao.response?.data?.detail || "Não foi possível trocar a senha."
      );
    } finally {
      setEnviando(false);
    }
  }

  if (carregando) return <p>Carregando perfil...</p>;
  if (erro) return <div className="mensagem-erro">{erro}</div>;

  return (
    <>
      <h1 className="pagina__titulo">Meu perfil</h1>
      <p className="pagina__subtitulo">Seus dados de acesso ao sistema.</p>

      <div className="cartao" style={{ marginBottom: 24, maxWidth: 480 }}>
        <h2 style={{ fontSize: "1.05rem", marginBottom: 16 }}>Dados da conta</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: 10, fontSize: "0.92rem" }}>
          <div>
            <strong>Nome:</strong> {meuPerfil.nome}
          </div>
          <div>
            <strong>Código:</strong> <span className="codigo-mono">{meuPerfil.codigo}</span>
          </div>
          <div>
            <strong>Email:</strong> {meuPerfil.email}
          </div>
          <div>
            <strong>Perfil:</strong>{" "}
            <span className="selo">{ROTULOS_PERFIL[meuPerfil.perfil] || meuPerfil.perfil}</span>
          </div>
        </div>
      </div>

      <div className="cartao" style={{ maxWidth: 480 }}>
        <h2 style={{ fontSize: "1.05rem", marginBottom: 16 }}>Trocar senha</h2>

        {erroSenha && <div className="mensagem-erro">{erroSenha}</div>}
        {sucessoSenha && (
          <div className="selo selo--sucesso" style={{ display: "block", padding: 12, marginBottom: 16, fontSize: "0.85rem" }}>
            Senha alterada com sucesso.
          </div>
        )}

        <form onSubmit={aoTrocarSenha}>
          <div className="campo">
            <label htmlFor="senha_atual">Senha atual</label>
            <input
              id="senha_atual"
              type="password"
              value={formularioSenha.senha_atual}
              onChange={(e) =>
                setFormularioSenha({ ...formularioSenha, senha_atual: e.target.value })
              }
              required
            />
          </div>
          <div className="campo">
            <label htmlFor="senha_nova">Nova senha</label>
            <input
              id="senha_nova"
              type="password"
              value={formularioSenha.senha_nova}
              onChange={(e) =>
                setFormularioSenha({ ...formularioSenha, senha_nova: e.target.value })
              }
              required
            />
          </div>
          <div className="campo">
            <label htmlFor="confirmar_senha_nova">Confirmar nova senha</label>
            <input
              id="confirmar_senha_nova"
              type="password"
              value={formularioSenha.confirmar_senha_nova}
              onChange={(e) =>
                setFormularioSenha({ ...formularioSenha, confirmar_senha_nova: e.target.value })
              }
              required
            />
          </div>
          <button type="submit" className="botao botao--primario" disabled={enviando}>
            {enviando ? "Salvando..." : "Trocar senha"}
          </button>
        </form>
      </div>
    </>
  );
}

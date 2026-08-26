import React, { useEffect, useState } from "react";
import api from "../services/api.js";
import { useAuth } from "../contexts/AuthContext.jsx";

const PERFIS_GESTAO = ["administrador", "gerente"];
const FORMULARIO_VAZIO = { nome: "", descricao: "" };

export default function Categorias() {
  const { funcionario } = useAuth();
  const podeGerenciar = PERFIS_GESTAO.includes(funcionario?.perfil);

  const [categorias, setCategorias] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [editandoId, setEditandoId] = useState(null);
  const [formulario, setFormulario] = useState(FORMULARIO_VAZIO);
  const [enviando, setEnviando] = useState(false);
  const [erroFormulario, setErroFormulario] = useState(null);

  async function carregar() {
    setCarregando(true);
    setErro(null);
    try {
      const resposta = await api.get("/categorias/");
      setCategorias(resposta.data);
    } catch {
      setErro("Não foi possível carregar as categorias.");
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => {
    carregar();
  }, []);

  function abrirCriacao() {
    setEditandoId(null);
    setFormulario(FORMULARIO_VAZIO);
    setErroFormulario(null);
    setMostrarFormulario(true);
  }

  function abrirEdicao(categoria) {
    setEditandoId(categoria.id);
    setFormulario({ nome: categoria.nome, descricao: categoria.descricao || "" });
    setErroFormulario(null);
    setMostrarFormulario(true);
  }

  function fechar() {
    setMostrarFormulario(false);
    setEditandoId(null);
  }

  async function aoEnviar(evento) {
    evento.preventDefault();
    setEnviando(true);
    setErroFormulario(null);

    const corpo = {
      nome: formulario.nome,
      descricao: formulario.descricao || null,
    };

    try {
      if (editandoId) {
        await api.put(`/categorias/${editandoId}`, corpo);
      } else {
        await api.post("/categorias/", corpo);
      }
      fechar();
      await carregar();
    } catch (erroRequisicao) {
      setErroFormulario(
        erroRequisicao.response?.data?.detail || "Não foi possível salvar a categoria."
      );
    } finally {
      setEnviando(false);
    }
  }

  async function excluir(categoria) {
    const confirmar = window.confirm(`Excluir a categoria "${categoria.nome}"?`);
    if (!confirmar) return;
    try {
      await api.delete(`/categorias/${categoria.id}`);
      await carregar();
    } catch {
      alert("Não foi possível excluir esta categoria.");
    }
  }

  if (carregando) return <p>Carregando categorias...</p>;

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 className="pagina__titulo">Categorias</h1>
          <p className="pagina__subtitulo">
            {categorias.length} categoria{categorias.length !== 1 ? "s" : ""} cadastrada
            {categorias.length !== 1 ? "s" : ""}.
          </p>
        </div>
        {podeGerenciar && !mostrarFormulario && (
          <button className="botao botao--primario" onClick={abrirCriacao}>
            + Nova categoria
          </button>
        )}
      </div>

      {erro && <div className="mensagem-erro">{erro}</div>}

      {mostrarFormulario && (
        <div className="cartao" style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: "1.05rem", marginBottom: 16 }}>
            {editandoId ? "Editar categoria" : "Nova categoria"}
          </h2>
          {erroFormulario && <div className="mensagem-erro">{erroFormulario}</div>}
          <form onSubmit={aoEnviar}>
            <div className="campo">
              <label htmlFor="nome">Nome</label>
              <input
                id="nome"
                type="text"
                value={formulario.nome}
                onChange={(e) => setFormulario({ ...formulario, nome: e.target.value })}
                required
              />
            </div>
            <div className="campo">
              <label htmlFor="descricao">Descrição</label>
              <textarea
                id="descricao"
                rows={2}
                value={formulario.descricao}
                onChange={(e) => setFormulario({ ...formulario, descricao: e.target.value })}
              />
            </div>
            <div style={{ display: "flex", gap: 10 }}>
              <button type="submit" className="botao botao--primario" disabled={enviando}>
                {enviando ? "Salvando..." : "Salvar"}
              </button>
              <button type="button" className="botao botao--secundario" onClick={fechar} disabled={enviando}>
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="cartao">
        {categorias.length === 0 ? (
          <p style={{ color: "var(--cor-texto-suave)", fontSize: "0.9rem" }}>
            Nenhuma categoria cadastrada ainda.
          </p>
        ) : (
          <table className="tabela">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Descrição</th>
                {podeGerenciar && <th></th>}
              </tr>
            </thead>
            <tbody>
              {categorias.map((categoria) => (
                <tr key={categoria.id}>
                  <td>{categoria.nome}</td>
                  <td>{categoria.descricao || "—"}</td>
                  {podeGerenciar && (
                    <td>
                      <div style={{ display: "flex", gap: 8 }}>
                        <button
                          className="botao botao--secundario"
                          style={{ padding: "6px 12px", fontSize: "0.82rem" }}
                          onClick={() => abrirEdicao(categoria)}
                        >
                          Editar
                        </button>
                        <button
                          className="botao botao--perigo"
                          style={{ padding: "6px 12px", fontSize: "0.82rem" }}
                          onClick={() => excluir(categoria)}
                        >
                          Excluir
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}

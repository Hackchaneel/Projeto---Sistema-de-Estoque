import React, { useEffect, useState } from "react";
import api from "../services/api.js";
import { useAuth } from "../contexts/AuthContext.jsx";

const PERFIS_GESTAO = ["administrador", "gerente"];
const FORMULARIO_VAZIO = { nome: "", cnpj_cpf: "", telefone: "", email: "" };

export default function Fornecedores() {
  const { funcionario } = useAuth();
  const podeGerenciar = PERFIS_GESTAO.includes(funcionario?.perfil);

  const [fornecedores, setFornecedores] = useState([]);
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
      const resposta = await api.get("/fornecedores/");
      setFornecedores(resposta.data);
    } catch {
      setErro("Não foi possível carregar os fornecedores.");
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

  function abrirEdicao(fornecedor) {
    setEditandoId(fornecedor.id);
    setFormulario({
      nome: fornecedor.nome,
      cnpj_cpf: fornecedor.cnpj_cpf || "",
      telefone: fornecedor.telefone || "",
      email: fornecedor.email || "",
    });
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
      cnpj_cpf: formulario.cnpj_cpf || null,
      telefone: formulario.telefone || null,
      email: formulario.email || null,
    };

    try {
      if (editandoId) {
        await api.put(`/fornecedores/${editandoId}`, corpo);
      } else {
        await api.post("/fornecedores/", corpo);
      }
      fechar();
      await carregar();
    } catch (erroRequisicao) {
      setErroFormulario(
        erroRequisicao.response?.data?.detail || "Não foi possível salvar o fornecedor."
      );
    } finally {
      setEnviando(false);
    }
  }

  async function excluir(fornecedor) {
    const confirmar = window.confirm(`Excluir o fornecedor "${fornecedor.nome}"?`);
    if (!confirmar) return;
    try {
      await api.delete(`/fornecedores/${fornecedor.id}`);
      await carregar();
    } catch {
      alert("Não foi possível excluir este fornecedor.");
    }
  }

  if (carregando) return <p>Carregando fornecedores...</p>;

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 className="pagina__titulo">Fornecedores</h1>
          <p className="pagina__subtitulo">
            {fornecedores.length} fornecedor{fornecedores.length !== 1 ? "es" : ""} cadastrado
            {fornecedores.length !== 1 ? "s" : ""}.
          </p>
        </div>
        {podeGerenciar && !mostrarFormulario && (
          <button className="botao botao--primario" onClick={abrirCriacao}>
            + Novo fornecedor
          </button>
        )}
      </div>

      {erro && <div className="mensagem-erro">{erro}</div>}

      {mostrarFormulario && (
        <div className="cartao" style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: "1.05rem", marginBottom: 16 }}>
            {editandoId ? "Editar fornecedor" : "Novo fornecedor"}
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
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <div className="campo">
                <label htmlFor="cnpj_cpf">CNPJ / CPF</label>
                <input
                  id="cnpj_cpf"
                  type="text"
                  value={formulario.cnpj_cpf}
                  onChange={(e) => setFormulario({ ...formulario, cnpj_cpf: e.target.value })}
                />
              </div>
              <div className="campo">
                <label htmlFor="telefone">Telefone</label>
                <input
                  id="telefone"
                  type="text"
                  value={formulario.telefone}
                  onChange={(e) => setFormulario({ ...formulario, telefone: e.target.value })}
                />
              </div>
            </div>
            <div className="campo">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={formulario.email}
                onChange={(e) => setFormulario({ ...formulario, email: e.target.value })}
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
        {fornecedores.length === 0 ? (
          <p style={{ color: "var(--cor-texto-suave)", fontSize: "0.9rem" }}>
            Nenhum fornecedor cadastrado ainda.
          </p>
        ) : (
          <table className="tabela">
            <thead>
              <tr>
                <th>Nome</th>
                <th>CNPJ / CPF</th>
                <th>Telefone</th>
                <th>Email</th>
                {podeGerenciar && <th></th>}
              </tr>
            </thead>
            <tbody>
              {fornecedores.map((fornecedor) => (
                <tr key={fornecedor.id}>
                  <td>{fornecedor.nome}</td>
                  <td>{fornecedor.cnpj_cpf || "—"}</td>
                  <td>{fornecedor.telefone || "—"}</td>
                  <td>{fornecedor.email || "—"}</td>
                  {podeGerenciar && (
                    <td>
                      <div style={{ display: "flex", gap: 8 }}>
                        <button
                          className="botao botao--secundario"
                          style={{ padding: "6px 12px", fontSize: "0.82rem" }}
                          onClick={() => abrirEdicao(fornecedor)}
                        >
                          Editar
                        </button>
                        <button
                          className="botao botao--perigo"
                          style={{ padding: "6px 12px", fontSize: "0.82rem" }}
                          onClick={() => excluir(fornecedor)}
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

import React, { useEffect, useState } from "react";
import api from "../services/api.js";
import { useAuth } from "../contexts/AuthContext.jsx";

// Só Administrador pode CADASTRAR, EDITAR ou DESATIVAR funcionários
// (regra que precisa bater com o backend).
const PODE_GERENCIAR = "administrador";

const ROTULOS_PERFIL = {
  administrador: "Administrador",
  gerente: "Gerente",
  estoquista: "Estoquista",
  funcionario: "Funcionário",
};

const FORMULARIO_CRIACAO_VAZIO = {
  codigo: "",
  nome: "",
  email: "",
  senha: "",
  perfil: "funcionario",
};

export default function Funcionarios() {
  const { funcionario } = useAuth();
  const podeGerenciar = funcionario?.perfil === PODE_GERENCIAR;

  const [funcionarios, setFuncionarios] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  // --- Formulário de CRIAÇÃO ---
  const [mostrarCriacao, setMostrarCriacao] = useState(false);
  const [formularioCriacao, setFormularioCriacao] = useState(FORMULARIO_CRIACAO_VAZIO);
  const [enviandoCriacao, setEnviandoCriacao] = useState(false);
  const [erroCriacao, setErroCriacao] = useState(null);

  // --- Formulário de EDIÇÃO ---
  const [editandoId, setEditandoId] = useState(null);
  const [formularioEdicao, setFormularioEdicao] = useState({ nome: "", email: "", perfil: "" });
  const [enviandoEdicao, setEnviandoEdicao] = useState(false);
  const [erroEdicao, setErroEdicao] = useState(null);

  async function carregar() {
    setCarregando(true);
    setErro(null);
    try {
      const resposta = await api.get("/funcionarios/");
      setFuncionarios(resposta.data);
    } catch {
      setErro("Não foi possível carregar os funcionários.");
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => {
    carregar();
  }, []);

  // --------------------------------------------------------
  // CRIAÇÃO
  // --------------------------------------------------------
  function abrirCriacao() {
    setFormularioCriacao(FORMULARIO_CRIACAO_VAZIO);
    setErroCriacao(null);
    setMostrarCriacao(true);
  }

  async function aoEnviarCriacao(evento) {
    evento.preventDefault();
    setEnviandoCriacao(true);
    setErroCriacao(null);

    try {
      await api.post("/funcionarios/", {
        codigo_empresa: funcionario.codigoEmpresa || "",
        codigo: formularioCriacao.codigo,
        nome: formularioCriacao.nome,
        email: formularioCriacao.email,
        senha: formularioCriacao.senha,
        perfil: formularioCriacao.perfil,
      });
      setMostrarCriacao(false);
      setFormularioCriacao(FORMULARIO_CRIACAO_VAZIO);
      await carregar();
    } catch (erroRequisicao) {
      setErroCriacao(
        erroRequisicao.response?.data?.detail || "Não foi possível cadastrar o funcionário."
      );
    } finally {
      setEnviandoCriacao(false);
    }
  }

  // --------------------------------------------------------
  // EDIÇÃO
  // --------------------------------------------------------
  function abrirEdicao(f) {
    setEditandoId(f.id);
    setFormularioEdicao({ nome: f.nome, email: f.email, perfil: f.perfil });
    setErroEdicao(null);
  }

  function fecharEdicao() {
    setEditandoId(null);
  }

  async function aoEnviarEdicao(evento, funcionarioId) {
    evento.preventDefault();
    setEnviandoEdicao(true);
    setErroEdicao(null);

    try {
      await api.put(`/funcionarios/${funcionarioId}`, {
        nome: formularioEdicao.nome,
        email: formularioEdicao.email,
        perfil: formularioEdicao.perfil,
      });
      setEditandoId(null);
      await carregar();
    } catch (erroRequisicao) {
      setErroEdicao(
        erroRequisicao.response?.data?.detail || "Não foi possível atualizar o funcionário."
      );
    } finally {
      setEnviandoEdicao(false);
    }
  }

  // --------------------------------------------------------
  // DESATIVAR
  // --------------------------------------------------------
  async function desativar(f) {
    const confirmar = window.confirm(
      `Desativar "${f.nome}"? Ele não conseguirá mais fazer login, mas o histórico dele será mantido.`
    );
    if (!confirmar) return;

    try {
      await api.delete(`/funcionarios/${f.id}`);
      await carregar();
    } catch (erroRequisicao) {
      alert(erroRequisicao.response?.data?.detail || "Não foi possível desativar este funcionário.");
    }
  }

  if (carregando) return <p>Carregando funcionários...</p>;

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 className="pagina__titulo">Funcionários</h1>
          <p className="pagina__subtitulo">
            {funcionarios.length} funcionário{funcionarios.length !== 1 ? "s" : ""} na sua empresa.
          </p>
        </div>
        {podeGerenciar && !mostrarCriacao && (
          <button className="botao botao--primario" onClick={abrirCriacao}>
            + Novo funcionário
          </button>
        )}
      </div>

      {erro && <div className="mensagem-erro">{erro}</div>}

      {!podeGerenciar && (
        <p style={{ color: "var(--cor-texto-suave)", fontSize: "0.85rem", marginBottom: 20 }}>
          Apenas administradores podem cadastrar, editar ou desativar funcionários.
        </p>
      )}

      {mostrarCriacao && (
        <div className="cartao" style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: "1.05rem", marginBottom: 16 }}>Novo funcionário</h2>
          {erroCriacao && <div className="mensagem-erro">{erroCriacao}</div>}
          <form onSubmit={aoEnviarCriacao}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: 16 }}>
              <div className="campo">
                <label htmlFor="codigo">Código</label>
                <input
                  id="codigo"
                  type="text"
                  placeholder="F002"
                  value={formularioCriacao.codigo}
                  onChange={(e) =>
                    setFormularioCriacao({ ...formularioCriacao, codigo: e.target.value })
                  }
                  required
                />
              </div>
              <div className="campo">
                <label htmlFor="nome">Nome</label>
                <input
                  id="nome"
                  type="text"
                  value={formularioCriacao.nome}
                  onChange={(e) =>
                    setFormularioCriacao({ ...formularioCriacao, nome: e.target.value })
                  }
                  required
                />
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <div className="campo">
                <label htmlFor="email">Email</label>
                <input
                  id="email"
                  type="email"
                  value={formularioCriacao.email}
                  onChange={(e) =>
                    setFormularioCriacao({ ...formularioCriacao, email: e.target.value })
                  }
                  required
                />
              </div>
              <div className="campo">
                <label htmlFor="senha">Senha</label>
                <input
                  id="senha"
                  type="password"
                  value={formularioCriacao.senha}
                  onChange={(e) =>
                    setFormularioCriacao({ ...formularioCriacao, senha: e.target.value })
                  }
                  required
                />
              </div>
            </div>

            <div className="campo">
              <label htmlFor="perfil">Perfil</label>
              <select
                id="perfil"
                value={formularioCriacao.perfil}
                onChange={(e) =>
                  setFormularioCriacao({ ...formularioCriacao, perfil: e.target.value })
                }
              >
                <option value="funcionario">Funcionário</option>
                <option value="estoquista">Estoquista</option>
                <option value="gerente">Gerente</option>
                <option value="administrador">Administrador</option>
              </select>
            </div>

            <div style={{ display: "flex", gap: 10 }}>
              <button type="submit" className="botao botao--primario" disabled={enviandoCriacao}>
                {enviandoCriacao ? "Cadastrando..." : "Cadastrar"}
              </button>
              <button
                type="button"
                className="botao botao--secundario"
                onClick={() => setMostrarCriacao(false)}
                disabled={enviandoCriacao}
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="cartao">
        <table className="tabela">
          <thead>
            <tr>
              <th>Código</th>
              <th>Nome</th>
              <th>Email</th>
              <th>Perfil</th>
              <th>Status</th>
              {podeGerenciar && <th></th>}
            </tr>
          </thead>
          <tbody>
            {funcionarios.map((f) => (
              <React.Fragment key={f.id}>
                <tr>
                  <td>
                    <span className="codigo-mono">{f.codigo}</span>
                  </td>
                  <td>{f.nome}</td>
                  <td>{f.email}</td>
                  <td>
                    <span className="selo">{ROTULOS_PERFIL[f.perfil] || f.perfil}</span>
                  </td>
                  <td>
                    <span className={f.ativo ? "selo selo--sucesso" : "selo selo--alerta"}>
                      {f.ativo ? "Ativo" : "Inativo"}
                    </span>
                  </td>
                  {podeGerenciar && (
                    <td>
                      <div style={{ display: "flex", gap: 8 }}>
                        <button
                          className="botao botao--secundario"
                          style={{ padding: "6px 12px", fontSize: "0.82rem" }}
                          onClick={() => (editandoId === f.id ? fecharEdicao() : abrirEdicao(f))}
                        >
                          {editandoId === f.id ? "Cancelar" : "Editar"}
                        </button>
                        {f.ativo && (
                          <button
                            className="botao botao--perigo"
                            style={{ padding: "6px 12px", fontSize: "0.82rem" }}
                            onClick={() => desativar(f)}
                          >
                            Desativar
                          </button>
                        )}
                      </div>
                    </td>
                  )}
                </tr>

                {editandoId === f.id && (
                  <tr>
                    <td colSpan={podeGerenciar ? 6 : 5} style={{ backgroundColor: "var(--cor-fundo)" }}>
                      {erroEdicao && <div className="mensagem-erro">{erroEdicao}</div>}
                      <form
                        onSubmit={(e) => aoEnviarEdicao(e, f.id)}
                        style={{ display: "grid", gridTemplateColumns: "2fr 2fr 1.5fr auto", gap: 12, alignItems: "end" }}
                      >
                        <div className="campo" style={{ marginBottom: 0 }}>
                          <label>Nome</label>
                          <input
                            type="text"
                            value={formularioEdicao.nome}
                            onChange={(e) =>
                              setFormularioEdicao({ ...formularioEdicao, nome: e.target.value })
                            }
                            required
                          />
                        </div>
                        <div className="campo" style={{ marginBottom: 0 }}>
                          <label>Email</label>
                          <input
                            type="email"
                            value={formularioEdicao.email}
                            onChange={(e) =>
                              setFormularioEdicao({ ...formularioEdicao, email: e.target.value })
                            }
                            required
                          />
                        </div>
                        <div className="campo" style={{ marginBottom: 0 }}>
                          <label>Perfil</label>
                          <select
                            value={formularioEdicao.perfil}
                            onChange={(e) =>
                              setFormularioEdicao({ ...formularioEdicao, perfil: e.target.value })
                            }
                          >
                            <option value="funcionario">Funcionário</option>
                            <option value="estoquista">Estoquista</option>
                            <option value="gerente">Gerente</option>
                            <option value="administrador">Administrador</option>
                          </select>
                        </div>
                        <button
                          type="submit"
                          className="botao botao--primario"
                          disabled={enviandoEdicao}
                        >
                          {enviandoEdicao ? "Salvando..." : "Salvar"}
                        </button>
                      </form>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

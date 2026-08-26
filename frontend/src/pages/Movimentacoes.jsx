import React, { useEffect, useState } from "react";
import api from "../services/api.js";
import { useAuth } from "../contexts/AuthContext.jsx";

// Perfis que podem REGISTRAR movimentação (precisa bater com
// PERFIS_MOVIMENTACAO no backend). Qualquer funcionário logado pode
// apenas VISUALIZAR o histórico.
const PERFIS_MOVIMENTACAO = ["administrador", "gerente", "estoquista"];

const FORMULARIO_VAZIO = {
  produto_id: "",
  tipo: "entrada",
  quantidade: "",
  motivo: "",
};

export default function Movimentacoes() {
  const { funcionario } = useAuth();
  const podeRegistrar = PERFIS_MOVIMENTACAO.includes(funcionario?.perfil);

  const [movimentacoes, setMovimentacoes] = useState([]);
  const [produtos, setProdutos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [formulario, setFormulario] = useState(FORMULARIO_VAZIO);
  const [enviando, setEnviando] = useState(false);
  const [erroFormulario, setErroFormulario] = useState(null);
  const [alertaGerado, setAlertaGerado] = useState(null);

  async function carregarTudo() {
    setCarregando(true);
    setErro(null);
    try {
      const [respMovimentacoes, respProdutos] = await Promise.all([
        api.get("/movimentacoes/"),
        api.get("/produtos/"),
      ]);
      setMovimentacoes(respMovimentacoes.data);
      setProdutos(respProdutos.data);
    } catch {
      setErro("Não foi possível carregar as movimentações.");
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => {
    carregarTudo();
  }, []);

  function nomeProduto(produtoId) {
    const produto = produtos.find((p) => p.id === produtoId);
    return produto ? `${produto.codigo} — ${produto.nome}` : "—";
  }

  function abrirFormulario() {
    setFormulario(FORMULARIO_VAZIO);
    setErroFormulario(null);
    setAlertaGerado(null);
    setMostrarFormulario(true);
  }

  function fecharFormulario() {
    setMostrarFormulario(false);
  }

  async function aoEnviar(evento) {
    evento.preventDefault();
    setEnviando(true);
    setErroFormulario(null);
    setAlertaGerado(null);

    try {
      const resposta = await api.post("/movimentacoes/", {
        produto_id: Number(formulario.produto_id),
        tipo: formulario.tipo,
        quantidade: Number(formulario.quantidade),
        motivo: formulario.motivo || null,
      });

      // Se a movimentação deixou o produto abaixo do mínimo, o
      // backend já avisa isso na própria resposta — exibimos aqui
      // antes de fechar o formulário, para a pessoa não perder o aviso.
      if (resposta.data.alerta) {
        setAlertaGerado(resposta.data.alerta);
      } else {
        setMostrarFormulario(false);
      }

      await carregarTudo();
      setFormulario(FORMULARIO_VAZIO);
    } catch (erroRequisicao) {
      setErroFormulario(
        erroRequisicao.response?.data?.detail || "Não foi possível registrar a movimentação."
      );
    } finally {
      setEnviando(false);
    }
  }

  if (carregando) return <p>Carregando movimentações...</p>;

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 className="pagina__titulo">Movimentações</h1>
          <p className="pagina__subtitulo">
            Histórico de entradas e saídas de estoque.
          </p>
        </div>
        {podeRegistrar && !mostrarFormulario && (
          <button className="botao botao--primario" onClick={abrirFormulario}>
            + Registrar movimentação
          </button>
        )}
      </div>

      {erro && <div className="mensagem-erro">{erro}</div>}

      {mostrarFormulario && (
        <div className="cartao" style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: "1.05rem", marginBottom: 16 }}>Registrar movimentação</h2>

          {erroFormulario && <div className="mensagem-erro">{erroFormulario}</div>}

          {alertaGerado && (
            <div
              className="mensagem-erro"
              style={{ marginBottom: 16 }}
            >
              {alertaGerado}
            </div>
          )}

          <form onSubmit={aoEnviar}>
            <div className="campo">
              <label htmlFor="produto_id">Produto</label>
              <select
                id="produto_id"
                value={formulario.produto_id}
                onChange={(e) => setFormulario({ ...formulario, produto_id: e.target.value })}
                required
              >
                <option value="">Selecione um produto</option>
                {produtos.map((produto) => (
                  <option key={produto.id} value={produto.id}>
                    {produto.codigo} — {produto.nome} (estoque atual: {produto.quantidade_estoque})
                  </option>
                ))}
              </select>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <div className="campo">
                <label htmlFor="tipo">Tipo</label>
                <select
                  id="tipo"
                  value={formulario.tipo}
                  onChange={(e) => setFormulario({ ...formulario, tipo: e.target.value })}
                >
                  <option value="entrada">Entrada</option>
                  <option value="saida">Saída</option>
                </select>
              </div>

              <div className="campo">
                <label htmlFor="quantidade">Quantidade</label>
                <input
                  id="quantidade"
                  type="number"
                  min="1"
                  value={formulario.quantidade}
                  onChange={(e) => setFormulario({ ...formulario, quantidade: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="campo">
              <label htmlFor="motivo">Motivo (opcional)</label>
              <input
                id="motivo"
                type="text"
                placeholder="Ex: Compra NF 1234, Venda balcão, Ajuste de inventário"
                value={formulario.motivo}
                onChange={(e) => setFormulario({ ...formulario, motivo: e.target.value })}
              />
            </div>

            <div style={{ display: "flex", gap: 10 }}>
              <button type="submit" className="botao botao--primario" disabled={enviando}>
                {enviando ? "Registrando..." : "Registrar"}
              </button>
              <button
                type="button"
                className="botao botao--secundario"
                onClick={fecharFormulario}
                disabled={enviando}
              >
                Fechar
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="cartao">
        {movimentacoes.length === 0 ? (
          <p style={{ color: "var(--cor-texto-suave)", fontSize: "0.9rem" }}>
            Nenhuma movimentação registrada ainda.
          </p>
        ) : (
          <table className="tabela">
            <thead>
              <tr>
                <th>Data</th>
                <th>Produto</th>
                <th>Tipo</th>
                <th>Quantidade</th>
                <th>Estoque após</th>
                <th>Motivo</th>
              </tr>
            </thead>
            <tbody>
              {movimentacoes.map((mov) => (
                <tr key={mov.id}>
                  <td>{new Date(mov.criado_em).toLocaleString("pt-BR")}</td>
                  <td>{nomeProduto(mov.produto_id)}</td>
                  <td>
                    <span
                      className={
                        mov.tipo === "entrada" ? "selo selo--sucesso" : "selo selo--alerta"
                      }
                    >
                      {mov.tipo === "entrada" ? "Entrada" : "Saída"}
                    </span>
                  </td>
                  <td>{mov.quantidade}</td>
                  <td>
                    <span className="codigo-mono">{mov.estoque_atual}</span>
                  </td>
                  <td>{mov.motivo || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}

import React, { useEffect, useState } from "react";
import api from "../services/api.js";

// ============================================================
// PÁGINA: PAINEL (DASHBOARD)
// ============================================================
// Primeira tela que a pessoa vê após o login. Busca, em paralelo,
// os dados necessários para montar um resumo rápido da situação
// do estoque: quantos produtos existem, quantos estão em alerta
// (via rota dedicada GET /alertas), e as movimentações recentes.
export default function Dashboard() {
  const [produtos, setProdutos] = useState([]);
  const [alertas, setAlertas] = useState([]);
  const [movimentacoes, setMovimentacoes] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  useEffect(() => {
    async function carregarDados() {
      try {
        // Promise.all dispara as três requisições ao mesmo tempo,
        // em vez de uma esperar a outra terminar — a tela carrega
        // mais rápido.
        const [respostaProdutos, respostaAlertas, respostaMovimentacoes] =
          await Promise.all([
            api.get("/produtos/"),
            api.get("/alertas/"),
            api.get("/movimentacoes/"),
          ]);
        setProdutos(respostaProdutos.data);
        setAlertas(respostaAlertas.data);
        setMovimentacoes(respostaMovimentacoes.data);
      } catch (erroRequisicao) {
        setErro("Não foi possível carregar os dados do painel.");
      } finally {
        setCarregando(false);
      }
    }

    carregarDados();
  }, []);

  if (carregando) {
    return <p>Carregando painel...</p>;
  }

  if (erro) {
    return <div className="mensagem-erro">{erro}</div>;
  }

  // Considera só as 5 movimentações mais recentes para a lista de
  // atividade do painel (o histórico completo fica na página
  // "Movimentações").
  const ultimasMovimentacoes = movimentacoes.slice(0, 5);

  return (
    <>
      <h1 className="pagina__titulo">Painel</h1>
      <p className="pagina__subtitulo">
        Visão geral do estoque da sua empresa.
      </p>

      <div className="resumo-grid">
        <div className="resumo-cartao">
          <div className="resumo-cartao__rotulo">Produtos cadastrados</div>
          <div className="resumo-cartao__valor">{produtos.length}</div>
        </div>

        <div className="resumo-cartao">
          <div className="resumo-cartao__rotulo">Abaixo do estoque mínimo</div>
          <div
            className={
              alertas.length > 0
                ? "resumo-cartao__valor destaque-alerta"
                : "resumo-cartao__valor"
            }
          >
            {alertas.length}
          </div>
        </div>

        <div className="resumo-cartao">
          <div className="resumo-cartao__rotulo">Movimentações registradas</div>
          <div className="resumo-cartao__valor">{movimentacoes.length}</div>
        </div>
      </div>

      {alertas.length > 0 && (
        <div className="cartao" style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: "1.05rem", marginBottom: 14 }}>
            Produtos que precisam de atenção
          </h2>
          <table className="tabela">
            <thead>
              <tr>
                <th>Código</th>
                <th>Produto</th>
                <th>Estoque atual</th>
                <th>Mínimo recomendado</th>
              </tr>
            </thead>
            <tbody>
              {alertas.map((alerta) => (
                <tr key={alerta.produto_id}>
                  <td>
                    <span className="codigo-mono">{alerta.codigo}</span>
                  </td>
                  <td>{alerta.nome}</td>
                  <td>
                    <span className="selo selo--alerta">
                      {alerta.quantidade_estoque}
                    </span>
                  </td>
                  <td>{alerta.estoque_minimo}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="cartao">
        <h2 style={{ fontSize: "1.05rem", marginBottom: 14 }}>
          Movimentações recentes
        </h2>
        {ultimasMovimentacoes.length === 0 ? (
          <p style={{ color: "var(--cor-texto-suave)", fontSize: "0.9rem" }}>
            Nenhuma movimentação registrada ainda.
          </p>
        ) : (
          <table className="tabela">
            <thead>
              <tr>
                <th>Data</th>
                <th>Tipo</th>
                <th>Quantidade</th>
                <th>Motivo</th>
              </tr>
            </thead>
            <tbody>
              {ultimasMovimentacoes.map((mov) => (
                <tr key={mov.id}>
                  <td>{new Date(mov.criado_em).toLocaleString("pt-BR")}</td>
                  <td>
                    <span
                      className={
                        mov.tipo === "entrada"
                          ? "selo selo--sucesso"
                          : "selo selo--alerta"
                      }
                    >
                      {mov.tipo === "entrada" ? "Entrada" : "Saída"}
                    </span>
                  </td>
                  <td>{mov.quantidade}</td>
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

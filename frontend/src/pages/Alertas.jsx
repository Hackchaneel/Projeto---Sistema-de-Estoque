import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api.js";

// ============================================================
// PÁGINA: ALERTAS
// ============================================================
// Consome a rota dedicada GET /alertas do backend, que já calcula
// e devolve os produtos abaixo do estoque mínimo prontos para
// exibição (código, nome, quantidade, mínimo e mensagem formatada).
export default function Alertas() {
  const [alertas, setAlertas] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  useEffect(() => {
    async function carregar() {
      try {
        const resposta = await api.get("/alertas/");
        setAlertas(resposta.data);
      } catch {
        setErro("Não foi possível carregar os alertas.");
      } finally {
        setCarregando(false);
      }
    }
    carregar();
  }, []);

  if (carregando) return <p>Carregando alertas...</p>;
  if (erro) return <div className="mensagem-erro">{erro}</div>;

  return (
    <>
      <h1 className="pagina__titulo">Alertas de estoque</h1>
      <p className="pagina__subtitulo">
        {alertas.length === 0
          ? "Nenhum produto abaixo do estoque mínimo no momento."
          : `${alertas.length} produto${alertas.length !== 1 ? "s" : ""} precisa${alertas.length !== 1 ? "m" : ""} de atenção.`}
      </p>

      {alertas.length === 0 ? (
        <div className="cartao">
          <p style={{ color: "var(--cor-texto-suave)", fontSize: "0.9rem" }}>
            Tudo certo por aqui — todos os produtos estão com estoque dentro
            do mínimo recomendado.
          </p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {alertas.map((alerta) => (
            <div
              key={alerta.produto_id}
              className="cartao"
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                borderLeft: "3px solid var(--cor-alerta)",
              }}
            >
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
                  <span className="codigo-mono">{alerta.codigo}</span>
                  <strong>{alerta.nome}</strong>
                </div>
                <p style={{ color: "var(--cor-alerta)", fontSize: "0.88rem" }}>
                  {alerta.mensagem}
                </p>
              </div>

              <Link to="/movimentacoes" className="botao botao--primario">
                Repor estoque
              </Link>
            </div>
          ))}
        </div>
      )}
    </>
  );
}

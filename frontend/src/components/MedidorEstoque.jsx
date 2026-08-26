import React from "react";

// ============================================================
// COMPONENTE: MEDIDOR DE ESTOQUE
// ============================================================
// Elemento de assinatura visual do sistema: mostra, de forma
// rápida de entender, o quanto a quantidade atual cobre o estoque
// mínimo recomendado. Fica verde quando está saudável e laranja
// quando fica abaixo do mínimo — a mesma lógica de alerta usada no
// backend, só que em forma de barra.
//
// Uso: <MedidorEstoque quantidade={produto.quantidade_estoque} minimo={produto.estoque_minimo} />
export default function MedidorEstoque({ quantidade, minimo }) {
  const abaixoDoMinimo = minimo > 0 && quantidade < minimo;

  // Se não houver estoque mínimo definido (0), a barra fica sempre
  // cheia — não faz sentido calcular "cobertura" de um mínimo que
  // não existe.
  const percentual =
    minimo > 0 ? Math.min(100, Math.round((quantidade / minimo) * 100)) : 100;

  return (
    <div className="medidor-estoque">
      <div className="medidor-estoque__trilho">
        <div
          className={
            abaixoDoMinimo
              ? "medidor-estoque__barra abaixo-minimo"
              : "medidor-estoque__barra"
          }
          style={{ width: `${percentual}%` }}
        />
      </div>
      <span className="medidor-estoque__valor">
        {quantidade} / mín. {minimo}
      </span>
    </div>
  );
}

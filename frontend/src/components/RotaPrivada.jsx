import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext.jsx";

// ============================================================
// ROTA PRIVADA
// ============================================================
// Envolve qualquer página que exija login. Se a pessoa não estiver
// autenticada, ela é redirecionada automaticamente para /login,
// antes mesmo de a página protegida chegar a ser exibida.
//
// Uso (em App.jsx):
//   <Route path="/" element={<RotaPrivada><Dashboard /></RotaPrivada>} />
export default function RotaPrivada({ children }) {
  const { estaLogado } = useAuth();

  if (!estaLogado) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

import React from "react";
import { Routes, Route } from "react-router-dom";

import RotaPrivada from "./components/RotaPrivada.jsx";
import Layout from "./components/Layout.jsx";

import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Produtos from "./pages/Produtos.jsx";
import Categorias from "./pages/Categorias.jsx";
import Fornecedores from "./pages/Fornecedores.jsx";
import Movimentacoes from "./pages/Movimentacoes.jsx";
import Alertas from "./pages/Alertas.jsx";
import Funcionarios from "./pages/Funcionarios.jsx";
import Perfil from "./pages/Perfil.jsx";

// ============================================================
// COMPONENTE RAIZ: DEFINIÇÃO DE ROTAS
// ============================================================
// Mapeia cada URL da aplicação para o componente de página
// correspondente. A rota "/login" é pública; todas as outras
// ficam dentro de <RotaPrivada>, que exige login, e de <Layout>,
// que desenha a sidebar ao redor do conteúdo de cada página.
export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route
        element={
          <RotaPrivada>
            <Layout />
          </RotaPrivada>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/produtos" element={<Produtos />} />
        <Route path="/categorias" element={<Categorias />} />
        <Route path="/fornecedores" element={<Fornecedores />} />
        <Route path="/movimentacoes" element={<Movimentacoes />} />
        <Route path="/alertas" element={<Alertas />} />
        <Route path="/funcionarios" element={<Funcionarios />} />
        <Route path="/perfil" element={<Perfil />} />
      </Route>
    </Routes>
  );
}

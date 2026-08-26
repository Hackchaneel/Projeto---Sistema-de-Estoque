import React from "react";
import { NavLink, Link, Outlet } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext.jsx";

// ============================================================
// RÓTULOS DE PERFIL (para exibição amigável na sidebar)
// ============================================================
const ROTULOS_PERFIL = {
  administrador: "Administrador",
  gerente: "Gerente",
  estoquista: "Estoquista",
  funcionario: "Funcionário",
};

// ============================================================
// ITENS DE NAVEGAÇÃO
// ============================================================
// Lista central dos links da sidebar. Adicionar uma nova página ao
// sistema no futuro (ex: Relatórios) significa só adicionar um
// item aqui — o resto do layout se ajusta sozinho.
const ITENS_NAVEGACAO = [
  { rota: "/", rotulo: "Painel", fim: true },
  { rota: "/produtos", rotulo: "Produtos" },
  { rota: "/categorias", rotulo: "Categorias" },
  { rota: "/fornecedores", rotulo: "Fornecedores" },
  { rota: "/movimentacoes", rotulo: "Movimentações" },
  { rota: "/alertas", rotulo: "Alertas" },
  { rota: "/funcionarios", rotulo: "Funcionários" },
];

// ============================================================
// LAYOUT PRINCIPAL
// ============================================================
// Estrutura toda página autenticada: uma sidebar fixa à esquerda
// (navegação + dados do usuário logado) e a área de conteúdo à
// direita, onde cada página específica é renderizada através do
// <Outlet /> (mecanismo do React Router para layouts aninhados).
export default function Layout() {
  const { funcionario, logout } = useAuth();

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar__marca">
          Estoque<span>ERP</span>
        </div>

        <nav className="sidebar__nav">
          {ITENS_NAVEGACAO.map((item) => (
            <NavLink
              key={item.rota}
              to={item.rota}
              end={item.fim}
              className={({ isActive }) =>
                isActive ? "sidebar__link ativo" : "sidebar__link"
              }
            >
              {item.rotulo}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar__rodape">
          <Link to="/perfil" className="sidebar__usuario" style={{ textDecoration: "none" }}>
            <span className="sidebar__usuario-nome">{funcionario?.email}</span>
            <span className="sidebar__usuario-perfil">
              {ROTULOS_PERFIL[funcionario?.perfil] || funcionario?.perfil}
            </span>
          </Link>
          <button className="sidebar__sair" onClick={logout}>
            Sair
          </button>
        </div>
      </aside>

      <main className="conteudo">
        <Outlet />
      </main>
    </div>
  );
}

import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App.jsx";
import { AuthProvider } from "./contexts/AuthContext.jsx";
import "./index.css";

// Ponto de partida da aplicação: monta o React dentro da div#root
// (definida em index.html), envolvendo tudo com:
// - BrowserRouter: habilita a navegação entre páginas (rotas)
// - AuthProvider: disponibiliza os dados de login (usuário, token)
//   para qualquer componente da aplicação, sem precisar passar
//   essas informações manualmente de componente em componente.
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);

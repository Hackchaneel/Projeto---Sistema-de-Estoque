import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Configuração do Vite (ferramenta que compila e serve a aplicação
// React durante o desenvolvimento). O plugin "react" habilita o
// suporte a JSX e o "Fast Refresh" (atualização instantânea da tela
// ao salvar um arquivo, sem perder o estado da aplicação).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});

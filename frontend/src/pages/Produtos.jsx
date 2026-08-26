import React, { useEffect, useState } from "react";
import api from "../services/api.js";
import { useAuth } from "../contexts/AuthContext.jsx";
import MedidorEstoque from "../components/MedidorEstoque.jsx";

// Perfis que podem criar, editar ou excluir produtos (precisa bater
// com a regra já aplicada no backend, em PERFIS_GESTAO).
const PERFIS_GESTAO = ["administrador", "gerente"];

// Valores iniciais do formulário de criação/edição
const FORMULARIO_VAZIO = {
  codigo: "",
  nome: "",
  descricao: "",
  categoria_id: "",
  fornecedor_id: "",
  preco_custo: "",
  preco_venda: "",
  quantidade_estoque: 0,
  estoque_minimo: 0,
};

export default function Produtos() {
  const { funcionario } = useAuth();
  const podeGerenciar = PERFIS_GESTAO.includes(funcionario?.perfil);

  const [produtos, setProdutos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [fornecedores, setFornecedores] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  // Controla se o formulário está visível, e se está em modo
  // "criar" (produtoEditando = null) ou "editar" (produtoEditando
  // guarda o id do produto sendo editado).
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [produtoEditando, setProdutoEditando] = useState(null);
  const [formulario, setFormulario] = useState(FORMULARIO_VAZIO);
  const [enviando, setEnviando] = useState(false);
  const [erroFormulario, setErroFormulario] = useState(null);

  // --------------------------------------------------------
  // CARREGAMENTO INICIAL
  // --------------------------------------------------------
  async function carregarTudo() {
    setCarregando(true);
    setErro(null);
    try {
      const [respProdutos, respCategorias, respFornecedores] = await Promise.all([
        api.get("/produtos/"),
        api.get("/categorias/"),
        api.get("/fornecedores/"),
      ]);
      setProdutos(respProdutos.data);
      setCategorias(respCategorias.data);
      setFornecedores(respFornecedores.data);
    } catch {
      setErro("Não foi possível carregar os produtos.");
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => {
    carregarTudo();
  }, []);

  // --------------------------------------------------------
  // FUNÇÕES AUXILIARES DE EXIBIÇÃO
  // --------------------------------------------------------
  function nomeCategoria(categoriaId) {
    const categoria = categorias.find((c) => c.id === categoriaId);
    return categoria ? categoria.nome : "—";
  }

  function nomeFornecedor(fornecedorId) {
    const fornecedor = fornecedores.find((f) => f.id === fornecedorId);
    return fornecedor ? fornecedor.nome : "—";
  }

  function formatarPreco(valor) {
    if (valor === null || valor === undefined || valor === "") return "—";
    return Number(valor).toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
  }

  // --------------------------------------------------------
  // ABRIR FORMULÁRIO (CRIAR OU EDITAR)
  // --------------------------------------------------------
  function abrirCriacao() {
    setProdutoEditando(null);
    setFormulario(FORMULARIO_VAZIO);
    setErroFormulario(null);
    setMostrarFormulario(true);
  }

  function abrirEdicao(produto) {
    setProdutoEditando(produto.id);
    setFormulario({
      codigo: produto.codigo,
      nome: produto.nome,
      descricao: produto.descricao || "",
      categoria_id: produto.categoria_id || "",
      fornecedor_id: produto.fornecedor_id || "",
      preco_custo: produto.preco_custo ?? "",
      preco_venda: produto.preco_venda ?? "",
      quantidade_estoque: produto.quantidade_estoque,
      estoque_minimo: produto.estoque_minimo,
    });
    setErroFormulario(null);
    setMostrarFormulario(true);
  }

  function fecharFormulario() {
    setMostrarFormulario(false);
    setProdutoEditando(null);
  }

  // --------------------------------------------------------
  // ENVIAR FORMULÁRIO (CRIAR OU EDITAR)
  // --------------------------------------------------------
  async function aoEnviarFormulario(evento) {
    evento.preventDefault();
    setEnviando(true);
    setErroFormulario(null);

    // Monta o corpo da requisição, convertendo campos vazios em
    // null (categoria/fornecedor opcionais) e números onde necessário.
    const corpo = {
      nome: formulario.nome,
      descricao: formulario.descricao || null,
      categoria_id: formulario.categoria_id ? Number(formulario.categoria_id) : null,
      fornecedor_id: formulario.fornecedor_id
        ? Number(formulario.fornecedor_id)
        : null,
      preco_custo: formulario.preco_custo === "" ? null : Number(formulario.preco_custo),
      preco_venda: formulario.preco_venda === "" ? null : Number(formulario.preco_venda),
    };

    try {
      if (produtoEditando) {
        // Edição: PUT não permite alterar quantidade_estoque nem
        // código (regra definida no backend), então enviamos só os
        // campos editáveis.
        corpo.estoque_minimo = Number(formulario.estoque_minimo);
        await api.put(`/produtos/${produtoEditando}`, corpo);
      } else {
        // Criação: inclui código e quantidades iniciais.
        corpo.codigo = formulario.codigo;
        corpo.quantidade_estoque = Number(formulario.quantidade_estoque);
        corpo.estoque_minimo = Number(formulario.estoque_minimo);
        await api.post("/produtos/", corpo);
      }

      fecharFormulario();
      await carregarTudo();
    } catch (erroRequisicao) {
      setErroFormulario(
        erroRequisicao.response?.data?.detail ||
          "Não foi possível salvar o produto."
      );
    } finally {
      setEnviando(false);
    }
  }

  // --------------------------------------------------------
  // EXCLUIR PRODUTO
  // --------------------------------------------------------
  async function excluirProduto(produto) {
    const confirmar = window.confirm(
      `Excluir o produto "${produto.nome}"? Essa ação não pode ser desfeita.`
    );
    if (!confirmar) return;

    try {
      await api.delete(`/produtos/${produto.id}`);
      await carregarTudo();
    } catch {
      alert("Não foi possível excluir este produto.");
    }
  }

  // --------------------------------------------------------
  // RENDERIZAÇÃO
  // --------------------------------------------------------
  if (carregando) {
    return <p>Carregando produtos...</p>;
  }

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 className="pagina__titulo">Produtos</h1>
          <p className="pagina__subtitulo">
            {produtos.length} produto{produtos.length !== 1 ? "s" : ""} cadastrado
            {produtos.length !== 1 ? "s" : ""}.
          </p>
        </div>
        {podeGerenciar && !mostrarFormulario && (
          <button className="botao botao--primario" onClick={abrirCriacao}>
            + Novo produto
          </button>
        )}
      </div>

      {erro && <div className="mensagem-erro">{erro}</div>}

      {mostrarFormulario && (
        <div className="cartao" style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: "1.05rem", marginBottom: 16 }}>
            {produtoEditando ? "Editar produto" : "Novo produto"}
          </h2>

          {erroFormulario && <div className="mensagem-erro">{erroFormulario}</div>}

          <form onSubmit={aoEnviarFormulario}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: 16 }}>
              <div className="campo">
                <label htmlFor="codigo">Código (SKU)</label>
                <input
                  id="codigo"
                  type="text"
                  placeholder="PROD001"
                  value={formulario.codigo}
                  onChange={(e) => setFormulario({ ...formulario, codigo: e.target.value })}
                  disabled={Boolean(produtoEditando)}
                  required
                />
              </div>

              <div className="campo">
                <label htmlFor="nome">Nome</label>
                <input
                  id="nome"
                  type="text"
                  value={formulario.nome}
                  onChange={(e) => setFormulario({ ...formulario, nome: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="campo">
              <label htmlFor="descricao">Descrição</label>
              <textarea
                id="descricao"
                rows={2}
                value={formulario.descricao}
                onChange={(e) => setFormulario({ ...formulario, descricao: e.target.value })}
              />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <div className="campo">
                <label htmlFor="categoria_id">Categoria</label>
                <select
                  id="categoria_id"
                  value={formulario.categoria_id}
                  onChange={(e) => setFormulario({ ...formulario, categoria_id: e.target.value })}
                >
                  <option value="">Sem categoria</option>
                  {categorias.map((categoria) => (
                    <option key={categoria.id} value={categoria.id}>
                      {categoria.nome}
                    </option>
                  ))}
                </select>
              </div>

              <div className="campo">
                <label htmlFor="fornecedor_id">Fornecedor</label>
                <select
                  id="fornecedor_id"
                  value={formulario.fornecedor_id}
                  onChange={(e) => setFormulario({ ...formulario, fornecedor_id: e.target.value })}
                >
                  <option value="">Sem fornecedor</option>
                  {fornecedores.map((fornecedor) => (
                    <option key={fornecedor.id} value={fornecedor.id}>
                      {fornecedor.nome}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <div className="campo">
                <label htmlFor="preco_custo">Preço de custo (R$)</label>
                <input
                  id="preco_custo"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formulario.preco_custo}
                  onChange={(e) => setFormulario({ ...formulario, preco_custo: e.target.value })}
                />
              </div>

              <div className="campo">
                <label htmlFor="preco_venda">Preço de venda (R$)</label>
                <input
                  id="preco_venda"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formulario.preco_venda}
                  onChange={(e) => setFormulario({ ...formulario, preco_venda: e.target.value })}
                />
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              {!produtoEditando && (
                <div className="campo">
                  <label htmlFor="quantidade_estoque">Quantidade inicial em estoque</label>
                  <input
                    id="quantidade_estoque"
                    type="number"
                    min="0"
                    value={formulario.quantidade_estoque}
                    onChange={(e) =>
                      setFormulario({ ...formulario, quantidade_estoque: e.target.value })
                    }
                  />
                </div>
              )}

              <div className="campo">
                <label htmlFor="estoque_minimo">Estoque mínimo recomendado</label>
                <input
                  id="estoque_minimo"
                  type="number"
                  min="0"
                  value={formulario.estoque_minimo}
                  onChange={(e) =>
                    setFormulario({ ...formulario, estoque_minimo: e.target.value })
                  }
                />
              </div>
            </div>

            {produtoEditando && (
              <p style={{ fontSize: "0.82rem", color: "var(--cor-texto-suave)", marginBottom: 16 }}>
                A quantidade em estoque só pode ser alterada pela tela de
                Movimentações (entrada/saída), para manter o histórico correto.
              </p>
            )}

            <div style={{ display: "flex", gap: 10 }}>
              <button type="submit" className="botao botao--primario" disabled={enviando}>
                {enviando ? "Salvando..." : "Salvar"}
              </button>
              <button
                type="button"
                className="botao botao--secundario"
                onClick={fecharFormulario}
                disabled={enviando}
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="cartao">
        {produtos.length === 0 ? (
          <p style={{ color: "var(--cor-texto-suave)", fontSize: "0.9rem" }}>
            Nenhum produto cadastrado ainda.
          </p>
        ) : (
          <table className="tabela">
            <thead>
              <tr>
                <th>Código</th>
                <th>Nome</th>
                <th>Categoria</th>
                <th>Fornecedor</th>
                <th>Preço venda</th>
                <th>Estoque</th>
                {podeGerenciar && <th></th>}
              </tr>
            </thead>
            <tbody>
              {produtos.map((produto) => (
                <tr key={produto.id}>
                  <td>
                    <span className="codigo-mono">{produto.codigo}</span>
                  </td>
                  <td>{produto.nome}</td>
                  <td>{nomeCategoria(produto.categoria_id)}</td>
                  <td>{nomeFornecedor(produto.fornecedor_id)}</td>
                  <td>{formatarPreco(produto.preco_venda)}</td>
                  <td>
                    <MedidorEstoque
                      quantidade={produto.quantidade_estoque}
                      minimo={produto.estoque_minimo}
                    />
                  </td>
                  {podeGerenciar && (
                    <td>
                      <div style={{ display: "flex", gap: 8 }}>
                        <button
                          className="botao botao--secundario"
                          style={{ padding: "6px 12px", fontSize: "0.82rem" }}
                          onClick={() => abrirEdicao(produto)}
                        >
                          Editar
                        </button>
                        <button
                          className="botao botao--perigo"
                          style={{ padding: "6px 12px", fontSize: "0.82rem" }}
                          onClick={() => excluirProduto(produto)}
                        >
                          Excluir
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}

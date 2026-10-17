"use strict";

const MOEDA = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const INTEIRO = new Intl.NumberFormat("pt-BR");
const SVG_NS = "http://www.w3.org/2000/svg";
const COLUNAS_ORDENAVEIS = ["data", "id_venda", "cidade", "categoria", "produto", "quantidade", "preco_unitario_centavos", "valor_venda_centavos", "forma_pagamento"];
const porId = (id) => document.getElementById(id);
const filtroCidade = porId("filtro-cidade");
const filtroCategoria = porId("filtro-categoria");

let vendas = [];
let vendasAtuais = [];
let chaveOrdenacao = "data";
let direcaoOrdenacao = -1;
let pagina = 1;
let tamanhoPagina = 25;

function moeda(centavos) {
  return MOEDA.format((Number.isFinite(centavos) ? centavos : 0) / 100);
}

function moedaEixo(centavos) {
  const reais = centavos / 100;
  if (Math.abs(reais) >= 1_000_000) return `R$ ${new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 }).format(reais / 1_000_000)} mi`;
  if (Math.abs(reais) >= 1_000) return `R$ ${new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 }).format(reais / 1_000)} mil`;
  return MOEDA.format(reais);
}

function criarSvg(tag, atributos = {}, texto = null) {
  const elemento = document.createElementNS(SVG_NS, tag);
  for (const [chave, valor] of Object.entries(atributos)) elemento.setAttribute(chave, String(valor));
  if (texto !== null) elemento.textContent = texto;
  return elemento;
}

function dimensoesSvg(svg) {
  const caixa = svg.getBoundingClientRect();
  return { largura: Math.max(1, caixa.width), altura: Math.max(1, caixa.height) };
}

function prepararSvg(svg, largura, altura) {
  svg.replaceChildren();
  svg.setAttribute("viewBox", `0 0 ${largura} ${altura}`);
  svg.setAttribute("preserveAspectRatio", "none");
}

function normalizarTexto(valor) {
  return String(valor).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR");
}

function preencherFiltro(seletor, valores) {
  [...new Set(valores)].sort((a, b) => a.localeCompare(b, "pt-BR")).forEach((valor) => {
    const opcao = document.createElement("option");
    opcao.value = valor;
    opcao.textContent = valor;
    seletor.append(opcao);
  });
}

function intervaloValido() {
  const inicio = porId("data-inicio").value;
  const fim = porId("data-fim").value;
  const invalido = Boolean(inicio && fim && inicio > fim);
  porId("erro-periodo").hidden = !invalido;
  porId("data-inicio").setAttribute("aria-invalid", String(invalido));
  porId("data-fim").setAttribute("aria-invalid", String(invalido));
  return !invalido;
}

function filtrarVendas() {
  if (!intervaloValido()) return [];
  const termo = normalizarTexto(porId("busca-venda").value.trim());
  const inicio = porId("data-inicio").value;
  const fim = porId("data-fim").value;
  return vendas.filter((venda) => {
    if (filtroCidade.value && venda.cidade !== filtroCidade.value) return false;
    if (filtroCategoria.value && venda.categoria !== filtroCategoria.value) return false;
    if (inicio && venda.data < inicio) return false;
    if (fim && venda.data > fim) return false;
    if (termo) {
      const pesquisaveis = [venda.id_venda, venda.produto, venda.cidade, venda.categoria, venda.forma_pagamento];
      if (!pesquisaveis.some((valor) => normalizarTexto(valor).includes(termo))) return false;
    }
    return true;
  });
}

function atualizarIndicadores(registros) {
  const total = registros.reduce((soma, venda) => soma + venda.valor_venda_centavos, 0);
  const numero = registros.length;
  porId("kpi-valor").textContent = moeda(total);
  porId("kpi-vendas").textContent = INTEIRO.format(numero);
  porId("kpi-ticket").textContent = moeda(numero ? total / numero : 0);
  porId("kpi-unidades").textContent = INTEIRO.format(registros.reduce((soma, venda) => soma + venda.quantidade, 0));
}

function desenharCategorias(registros) {
  const svg = porId("grafico-categorias");
  const { largura: w, altura: h } = dimensoesSvg(svg);
  prepararSvg(svg, w, h);
  const totais = new Map();
  for (const venda of registros) totais.set(venda.categoria, (totais.get(venda.categoria) || 0) + venda.valor_venda_centavos);
  const dados = [...totais.entries()].sort((a, b) => b[1] - a[1]);
  if (!dados.length) {
    svg.setAttribute("aria-label", "Gráfico por categoria: sem vendas para exibir");
    svg.append(criarSvg("text", { x: w / 2, y: h / 2, "text-anchor": "middle", class: "grafico-mensagem" }, "Sem vendas para exibir"));
    return;
  }
  const margemEsquerda = Math.min(132, Math.max(82, w * 0.29));
  const margemDireita = Math.min(120, Math.max(94, w * 0.2));
  const area = Math.max(1, w - margemEsquerda - margemDireita);
  const topo = 20;
  const passo = Math.min(60, (h - 58) / dados.length);
  const maximo = Math.max(...dados.map(([, valor]) => valor), 1);
  const marcas = w < 640 ? 2 : 4;
  for (let i = 0; i <= marcas; i += 1) {
    const x = margemEsquerda + (area * i) / marcas;
    svg.append(criarSvg("line", { x1: x, x2: x, y1: 14, y2: h - 33, class: "grafico-grade" }));
    svg.append(criarSvg("text", { x, y: h - 9, "text-anchor": "middle", class: "grafico-eixo" }, moedaEixo((maximo * i) / marcas)));
  }
  dados.forEach(([categoria, valor], i) => {
    const y = topo + i * passo;
    const larguraBarra = (valor / maximo) * area;
    svg.append(criarSvg("text", { x: margemEsquerda - 9, y: y + 19, "text-anchor": "end", class: "grafico-rotulo" }, categoria));
    svg.append(criarSvg("rect", { x: margemEsquerda, y, width: larguraBarra, height: 28, rx: 5, fill: i === 0 ? "#0e7a78" : "#76aaa3" }));
    const xValor = Math.min(margemEsquerda + larguraBarra + 7, w - 5);
    const âncora = margemEsquerda + larguraBarra + 7 > w - 5 ? "end" : "start";
    svg.append(criarSvg("text", { x: xValor, y: y + 19, "text-anchor": âncora, class: "grafico-valor" }, moeda(valor)));
  });
  svg.setAttribute("aria-label", `Valor vendido por categoria: ${dados.map(([nome, valor]) => `${nome}, ${moeda(valor)}`).join("; ")}`);
}

function desenharMeses(registros) {
  const svg = porId("grafico-mensal");
  const { largura: w, altura: h } = dimensoesSvg(svg);
  prepararSvg(svg, w, h);
  const totais = new Map();
  for (const venda of registros) {
    const mes = venda.data.slice(0, 7);
    totais.set(mes, (totais.get(mes) || 0) + venda.valor_venda_centavos);
  }
  const dados = [...totais.entries()].sort(([a], [b]) => a.localeCompare(b));
  if (!dados.length) {
    svg.setAttribute("aria-label", "Gráfico mensal: sem vendas para exibir");
    svg.append(criarSvg("text", { x: w / 2, y: h / 2, "text-anchor": "middle", class: "grafico-mensagem" }, "Sem vendas para exibir"));
    return;
  }
  const esquerda = Math.min(79, Math.max(69, w * 0.22));
  const direita = w - 50;
  const topo = 34;
  const base = h - 34;
  const maximo = Math.max(...dados.map(([, valor]) => valor), 1);
  for (let i = 0; i <= 4; i += 1) {
    const y = base - ((base - topo) * i) / 4;
    const valor = (maximo * i) / 4;
    svg.append(criarSvg("line", { x1: esquerda, x2: direita, y1: y, y2: y, class: "grafico-grade" }));
    svg.append(criarSvg("text", { x: esquerda - 8, y: y + 4, "text-anchor": "end", class: "grafico-eixo" }, moedaEixo(valor)));
  }
  const pontos = dados.map(([mes, valor], i) => ({
    mes,
    valor,
    x: dados.length === 1 ? (esquerda + direita) / 2 : esquerda + ((direita - esquerda) * i) / (dados.length - 1),
    y: base - ((base - topo) * valor) / maximo
  }));
  if (pontos.length > 1) svg.append(criarSvg("polyline", { points: pontos.map((p) => `${p.x},${p.y}`).join(" "), fill: "none", stroke: "#0e7a78", "stroke-width": 3, "stroke-linecap": "round", "stroke-linejoin": "round" }));
  for (const ponto of pontos) {
    svg.append(criarSvg("circle", { cx: ponto.x, cy: ponto.y, r: 5, fill: "#fff", stroke: "#0e7a78", "stroke-width": 3 }));
    const yValor = ponto.y - 13 < 17 ? ponto.y + 22 : ponto.y - 13;
    svg.append(criarSvg("text", { x: ponto.x, y: yValor, "text-anchor": "middle", class: "grafico-valor" }, moeda(ponto.valor)));
    const [ano, mes] = ponto.mes.split("-").map(Number);
    const nome = new Intl.DateTimeFormat("pt-BR", { month: "short", timeZone: "UTC" }).format(new Date(Date.UTC(ano, mes - 1, 1)));
    svg.append(criarSvg("text", { x: ponto.x, y: h - 7, "text-anchor": "middle", class: "grafico-eixo" }, `${nome.charAt(0).toLocaleUpperCase("pt-BR")}${nome.slice(1)} ${ano}`));
  }
  svg.setAttribute("aria-label", `Valor vendido por mês: ${dados.map(([mes, valor]) => `${mes}, ${moeda(valor)}`).join("; ")}`);
}

function compararVendas(a, b, chave) {
  const av = a[chave];
  const bv = b[chave];
  if (typeof av === "number" && typeof bv === "number") return av === bv ? 0 : av < bv ? -1 : 1;
  return String(av).localeCompare(String(bv), "pt-BR", { numeric: true, sensitivity: "base" });
}

function ordenarVendas(registros) {
  return [...registros].sort((a, b) => {
    const principal = compararVendas(a, b, chaveOrdenacao) * direcaoOrdenacao;
    return principal || a.id_venda.localeCompare(b.id_venda, "pt-BR");
  });
}

function montarLinha(venda) {
  const linha = document.createElement("tr");
  const [ano, mes, dia] = venda.data.split("-");
  const valores = [
    `${dia}/${mes}/${ano}`, venda.id_venda, venda.cidade, venda.categoria, venda.produto,
    INTEIRO.format(venda.quantidade), moeda(venda.preco_unitario_centavos), moeda(venda.valor_venda_centavos), venda.forma_pagamento
  ];
  for (const valor of valores) {
    const celula = document.createElement("td");
    celula.textContent = valor;
    linha.append(celula);
  }
  return linha;
}

function atualizarIndicadoresOrdenacao() {
  document.querySelectorAll("button[data-ordenar]").forEach((botao) => {
    const chave = botao.dataset.ordenar;
    const th = botao.closest("th");
    const indicador = botao.querySelector(".indicador-ordem");
    if (chave === chaveOrdenacao) {
      th.setAttribute("aria-sort", direcaoOrdenacao === 1 ? "ascending" : "descending");
      indicador.textContent = direcaoOrdenacao === 1 ? "↑" : "↓";
      botao.setAttribute("aria-label", `Ordenado por ${botao.querySelector("span").textContent.toLocaleLowerCase("pt-BR")}; ativar para inverter a ordem`);
    } else {
      th.removeAttribute("aria-sort");
      indicador.textContent = "↕";
      botao.setAttribute("aria-label", `Ordenar por ${botao.querySelector("span").textContent.toLocaleLowerCase("pt-BR")}`);
    }
  });
}

function preencherTabelaImpressao(registrosOrdenados) {
  const corpo = porId("corpo-tabela-impressao");
  corpo.replaceChildren();
  const fragmento = document.createDocumentFragment();
  for (const venda of registrosOrdenados) {
    const linha = document.createElement("tr");
    const [ano, mes, dia] = venda.data.split("-");
    const valores = [`${dia}/${mes}/${ano}`, venda.id_venda, venda.cidade, venda.categoria, venda.produto, INTEIRO.format(venda.quantidade), moeda(venda.preco_unitario_centavos), moeda(venda.valor_venda_centavos), venda.forma_pagamento];
    for (const valor of valores) { const celula = document.createElement("td"); celula.textContent = valor; linha.append(celula); }
    fragmento.append(linha);
  }
  corpo.append(fragmento);
}

function renderizarTabela() {
  const ordenadas = ordenarVendas(vendasAtuais);
  const total = ordenadas.length;
  const paginas = tamanhoPagina === 0 ? 1 : Math.max(1, Math.ceil(total / tamanhoPagina));
  pagina = Math.min(Math.max(pagina, 1), paginas);
  const inicio = tamanhoPagina === 0 ? 0 : (pagina - 1) * tamanhoPagina;
  const visiveis = tamanhoPagina === 0 ? ordenadas : ordenadas.slice(inicio, inicio + tamanhoPagina);
  const corpo = porId("corpo-tabela");
  corpo.replaceChildren();
  const fragmento = document.createDocumentFragment();
  for (const venda of visiveis) fragmento.append(montarLinha(venda));
  corpo.append(fragmento);
  preencherTabelaImpressao(ordenadas);
  porId("contagem-tabela").textContent = `${INTEIRO.format(total)} ${total === 1 ? "venda" : "vendas"}`;
  porId("mensagem-vazia").hidden = total > 0;
  porId("tabela-vendas").closest(".envoltorio-tabela").hidden = total === 0;
  porId("pagina-anterior").disabled = total === 0 || pagina <= 1;
  porId("pagina-proxima").disabled = total === 0 || pagina >= paginas;
  porId("pagina-atual").textContent = total === 0 ? "Página 1 de 1" : `Página ${INTEIRO.format(pagina)} de ${INTEIRO.format(paginas)} · ${INTEIRO.format(inicio + 1)}–${INTEIRO.format(Math.min(inicio + visiveis.length, total))} de ${INTEIRO.format(total)}`;
  porId("registros-por-pagina").value = String(tamanhoPagina);
  porId("exportar-csv").disabled = total === 0;
  atualizarIndicadoresOrdenacao();
}

function atualizarPainel() {
  vendasAtuais = filtrarVendas();
  pagina = 1;
  atualizarIndicadores(vendasAtuais);
  desenharCategorias(vendasAtuais);
  desenharMeses(vendasAtuais);
  renderizarTabela();
  const invalido = porId("erro-periodo").hidden === false;
  porId("resumo-filtros").textContent = invalido ? "Corrija o intervalo de datas para ver resultados." : `${INTEIRO.format(vendasAtuais.length)} de ${INTEIRO.format(vendas.length)} vendas correspondem à busca e aos filtros`;
}

function csvCampo(valor) {
  return `"${String(valor).replace(/"/g, '""')}"`;
}

function exportarCsv() {
  const linhas = ordenarVendas(vendasAtuais);
  if (!linhas.length) return;
  const cabecalhos = ["Data", "ID da venda", "Cidade", "Categoria", "Produto", "Unidades", "Preço unitário (R$)", "Valor vendido (R$)", "Forma de pagamento"];
  const csv = [cabecalhos, ...linhas.map((venda) => [
    venda.data, venda.id_venda, venda.cidade, venda.categoria, venda.produto, venda.quantidade,
    (venda.preco_unitario_centavos / 100).toFixed(2).replace(".", ","),
    (venda.valor_venda_centavos / 100).toFixed(2).replace(".", ","), venda.forma_pagamento
  ])].map((linha) => linha.map(csvCampo).join(";")).join("\r\n");
  const arquivo = new Blob(["\ufeff", csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(arquivo);
  const link = document.createElement("a");
  link.href = url;
  link.download = "vendas-papelaria-filtradas.csv";
  document.body.append(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 0);
  porId("mensagem-exportacao").textContent = `CSV exportado com ${INTEIRO.format(linhas.length)} vendas filtradas.`;
}

async function iniciar() {
  try {
    porId("sair-painel").addEventListener("click", () => {
      sessionStorage.removeItem("papelaria-demo-auth");
      window.location.replace("../");
    });
    const resposta = await fetch("../dados/vendas.json");
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
    vendas = await resposta.json();
    if (!Array.isArray(vendas)) throw new Error("Formato de dados inválido");
    preencherFiltro(filtroCidade, vendas.map((v) => v.cidade));
    preencherFiltro(filtroCategoria, vendas.map((v) => v.categoria));

    for (const id of ["busca-venda", "data-inicio", "data-fim"]) porId(id).addEventListener("input", () => { porId("mensagem-exportacao").textContent = ""; atualizarPainel(); });
    filtroCidade.addEventListener("change", atualizarPainel);
    filtroCategoria.addEventListener("change", atualizarPainel);
    porId("limpar-filtros").addEventListener("click", () => {
      porId("busca-venda").value = "";
      porId("data-inicio").value = "";
      porId("data-fim").value = "";
      filtroCidade.value = "";
      filtroCategoria.value = "";
      porId("mensagem-exportacao").textContent = "";
      pagina = 1;
      atualizarPainel();
      porId("busca-venda").focus();
    });
    porId("registros-por-pagina").addEventListener("change", (evento) => { tamanhoPagina = Number(evento.target.value); pagina = 1; renderizarTabela(); });
    porId("pagina-anterior").addEventListener("click", () => { if (pagina > 1) { pagina -= 1; renderizarTabela(); } });
    porId("pagina-proxima").addEventListener("click", () => { pagina += 1; renderizarTabela(); });
    document.querySelectorAll("button[data-ordenar]").forEach((botao) => botao.addEventListener("click", () => {
      if (!COLUNAS_ORDENAVEIS.includes(botao.dataset.ordenar)) return;
      if (botao.dataset.ordenar === chaveOrdenacao) direcaoOrdenacao *= -1;
      else { chaveOrdenacao = botao.dataset.ordenar; direcaoOrdenacao = 1; }
      pagina = 1;
      renderizarTabela();
    }));
    porId("exportar-csv").addEventListener("click", exportarCsv);
    porId("imprimir-painel").addEventListener("click", () => window.print());
    const observador = new ResizeObserver(() => { desenharCategorias(vendasAtuais); desenharMeses(vendasAtuais); });
    observador.observe(porId("grafico-categorias"));
    observador.observe(porId("grafico-mensal"));
    atualizarPainel();
  } catch (erro) {
    console.error("Falha ao carregar o dashboard:", erro);
    porId("erro-carregamento").hidden = false;
    porId("resumo-filtros").textContent = "Dados indisponíveis";
  }
}

try {
  if (sessionStorage.getItem("papelaria-demo-auth") !== "ok") window.location.replace("../");
  else iniciar();
} catch (_erro) {
  window.location.replace("../");
}

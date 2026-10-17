"""Testes reproduzíveis do preparo de dados e do dashboard estático.

Execute a partir de projeto-dashboard com:
    python -m unittest discover -s tests -v

Os testes de interface usam Firefox headless e o protocolo Marionette nativo;
não dependem de uma implementação simulada do DOM.
"""

from __future__ import annotations

import csv
import hashlib
import http.server
from html.parser import HTMLParser
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import unittest
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen
from urllib.parse import urljoin, urlsplit


PROJETO = Path(__file__).resolve().parents[1]
RAIZ = PROJETO.parent
SCRIPT_PREPARO = PROJETO / "preparar_dados.py"
JSON_SITE = PROJETO / "site" / "dados" / "vendas.json"
SITE = PROJETO / "site"
README = PROJETO / "README.md"
FIREFOX = Path(r"C:\Program Files\Mozilla Firefox\firefox.exe")
CHAVES_JSON = {
    "id_venda",
    "data",
    "cidade",
    "categoria",
    "produto",
    "quantidade",
    "preco_unitario_centavos",
    "forma_pagamento",
    "valor_venda_centavos",
}


def sha256(arquivo: Path) -> str:
    return hashlib.sha256(arquivo.read_bytes()).hexdigest().upper()


def centavos(valor: str) -> int:
    """Conversão independente baseada na representação decimal do CSV."""
    return int(Decimal(valor) * 100)


def ler_csv(caminho: Path) -> list[dict[str, str]]:
    with caminho.open(encoding="utf-8-sig", newline="") as fonte:
        return list(csv.DictReader(fonte))


class ServidorSilencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, _formato: str, *_args: object) -> None:
        pass


class ReferenciasHTML(HTMLParser):
    """Coleta recursos HTML que precisam resolver tanto na raiz quanto em /vendas/."""
    def __init__(self) -> None:
        super().__init__()
        self.recursos: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        atributos = dict(attrs)
        if tag == "link" and atributos.get("rel", "").casefold() in {"stylesheet", "icon"}:
            recurso = atributos.get("href")
        elif tag == "script":
            recurso = atributos.get("src")
        elif tag in {"img", "source"}:
            recurso = atributos.get("src")
        else:
            recurso = None
        if recurso and not recurso.startswith(("data:", "//")):
            self.recursos.append(recurso)


class Marionette:
    """Cliente pequeno do protocolo Marionette/WebDriver fornecido pelo Firefox."""

    def __init__(self, conexao: socket.socket):
        self.socket = conexao
        self.proximo_id = 1

    def _ler_exato(self, tamanho: int) -> bytes:
        resultado = bytearray()
        while len(resultado) < tamanho:
            parte = self.socket.recv(tamanho - len(resultado))
            if not parte:
                raise RuntimeError("Firefox encerrou a conexão Marionette.")
            resultado.extend(parte)
        return bytes(resultado)

    def _ler_pacote(self) -> object:
        tamanho_texto = bytearray()
        while True:
            byte = self._ler_exato(1)
            if byte == b":":
                break
            tamanho_texto.extend(byte)
        tamanho = int(tamanho_texto.decode("ascii"))
        return json.loads(self._ler_exato(tamanho).decode("utf-8"))

    def comando(self, nome: str, parametros: dict[str, object] | None = None) -> object:
        identificador = self.proximo_id
        self.proximo_id += 1
        conteudo = json.dumps([0, identificador, nome, parametros or {}]).encode("utf-8")
        self.socket.sendall(str(len(conteudo)).encode("ascii") + b":" + conteudo)
        while True:
            pacote = self._ler_pacote()
            if isinstance(pacote, list) and len(pacote) >= 4 and pacote[:2] == [1, identificador]:
                if pacote[2] is not None:
                    raise RuntimeError(f"Marionette {nome}: {pacote!r}")
                return pacote[3]


class TesteDados(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registros = json.loads(JSON_SITE.read_text(encoding="utf-8"))
        cls.csv_limpo = ler_csv(RAIZ / "papelaria_limpa.csv")
        cls.csv_original = ler_csv(RAIZ / "vendas_papelaria.csv")

    def test_esquema_tipos_nulos_ids_e_duplicatas(self) -> None:
        self.assertEqual(len(self.registros), 180)
        self.assertEqual(len(self.csv_limpo), 180)
        self.assertEqual(len(self.csv_original), 182)
        self.assertEqual(set(self.registros[0]), CHAVES_JSON)
        self.assertEqual(len({r["id_venda"] for r in self.registros}), 180)
        self.assertEqual(len({r["id_venda"] for r in self.csv_limpo}), 180)
        self.assertEqual(len({json.dumps(r, sort_keys=True) for r in self.registros}), 180)

        repeticoes = Counter(tuple(sorted(linha.items())) for linha in self.csv_original)
        self.assertEqual(sum(qtd - 1 for qtd in repeticoes.values() if qtd > 1), 2)
        self.assertEqual(
            {linha["id_venda"] for linha, qtd in ((dict(itens), n) for itens, n in repeticoes.items()) if qtd > 1},
            {"V0010", "V0020"},
        )

        ids_csv = {linha["id_venda"] for linha in self.csv_limpo}
        self.assertEqual(ids_csv, {r["id_venda"] for r in self.registros})
        pagamentos_vazios = sum(not linha["forma_pagamento"].strip() for linha in self.csv_limpo)
        self.assertEqual(pagamentos_vazios, 0)
        self.assertEqual(sum(r["forma_pagamento"] == "Não informado" for r in self.registros), 4)
        for r in self.registros:
            with self.subTest(id=r["id_venda"]):
                self.assertEqual(set(r), CHAVES_JSON)
                self.assertTrue(all(v is not None and v != "" for v in r.values()))
                self.assertIsInstance(r["id_venda"], str)
                self.assertRegex(r["data"], r"^2026-\d{2}-\d{2}$")
                self.assertIsInstance(r["quantidade"], int)
                self.assertGreater(r["quantidade"], 0)
                self.assertIsInstance(r["preco_unitario_centavos"], int)
                self.assertIsInstance(r["valor_venda_centavos"], int)
                self.assertEqual(
                    r["quantidade"] * r["preco_unitario_centavos"],
                    r["valor_venda_centavos"],
                )

    def test_totais_e_grupos_recalculados_do_csv_independentemente(self) -> None:
        # Recalcula por quantidade × preço do CSV, sem consumir valor_venda nem
        # usar funções/agregações do script construtor.
        total = 0
        unidades = 0
        por_categoria: defaultdict[str, int] = defaultdict(int)
        por_cidade: defaultdict[str, int] = defaultdict(int)
        por_mes: defaultdict[str, int] = defaultdict(int)
        for linha in self.csv_limpo:
            venda = int(linha["quantidade"]) * centavos(linha["preco_unitario"])
            total += venda
            unidades += int(linha["quantidade"])
            por_categoria[linha["categoria"]] += venda
            por_cidade[linha["cidade"].strip()] += venda
            por_mes[linha["data"][:7]] += venda

        self.assertEqual((len(self.csv_limpo), unidades, total), (180, 548, 2_005_900))
        self.assertEqual(
            dict(por_categoria),
            {"Acessórios": 1_051_700, "Livros": 743_800, "Papelaria": 210_400},
        )
        self.assertEqual(
            dict(por_cidade),
            {"Campinas": 857_800, "Santos": 693_750, "Sorocaba": 454_350},
        )
        self.assertEqual(sum(por_mes.values()), total)

        self.assertEqual(sum(r["quantidade"] for r in self.registros), unidades)
        self.assertEqual(sum(r["valor_venda_centavos"] for r in self.registros), total)
        for atributo, esperado in (("categoria", por_categoria), ("cidade", por_cidade)):
            observado: defaultdict[str, int] = defaultdict(int)
            for r in self.registros:
                observado[r[atributo]] += r["valor_venda_centavos"]
            self.assertEqual(dict(observado), dict(esperado))

    def test_fixture_pequeno_conhecido_do_preparador(self) -> None:
        linhas = [
            ["T01", "2026-01-02", "Teste", "Livros", "Caderno", "2", "1.25", "Cartão", "2.50"],
            ["T02", "2026-02-03", "Teste", "Acessórios", "Caneta", "3", "2.10", "Pix", "6.30"],
        ]
        colunas = [
            "id_venda", "data", "cidade", "categoria", "produto", "quantidade",
            "preco_unitario", "forma_pagamento", "valor_venda",
        ]
        with tempfile.TemporaryDirectory() as pasta:
            temporario = Path(pasta)
            entrada = temporario / "fixture.csv"
            saida = temporario / "vendas.json"
            with entrada.open("w", encoding="utf-8", newline="") as destino:
                escritor = csv.writer(destino)
                escritor.writerow(colunas)
                escritor.writerows(linhas)

            especificacao = importlib.util.spec_from_file_location("preparar_dados_fixture", SCRIPT_PREPARO)
            modulo = importlib.util.module_from_spec(especificacao)
            assert especificacao.loader is not None
            especificacao.loader.exec_module(modulo)
            modulo.ARQUIVO_FONTE = entrada
            modulo.ARQUIVO_SAIDA = saida
            resultado = modulo.preparar_dados()

            self.assertEqual(resultado, {"vendas": 2, "unidades": 5, "total_centavos": 880})
            exportado = json.loads(saida.read_text(encoding="utf-8"))
            self.assertEqual([r["valor_venda_centavos"] for r in exportado], [250, 630])
            self.assertEqual([r["preco_unitario_centavos"] for r in exportado], [125, 210])
            self.assertEqual(sum(r["valor_venda_centavos"] for r in exportado), 880)

    def test_comando_de_preparo_preserva_origens_e_resultados_anteriores(self) -> None:
        preservados = [
            RAIZ / "vendas_papelaria.csv",
            RAIZ / "papelaria_limpa.csv",
            RAIZ / "resumo.md",
            RAIZ / "verificacao.md",
            RAIZ / "graficos.py",
            RAIZ / "categorias.png",
            RAIZ / "cidades.png",
        ]
        hashes_antes = {arquivo: sha256(arquivo) for arquivo in preservados}
        json_antes = JSON_SITE.read_bytes()
        processo = subprocess.run(
            [os.fspath(Path(os.sys.executable)), os.fspath(SCRIPT_PREPARO)],
            cwd=PROJETO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(processo.returncode, 0, processo.stdout + processo.stderr)
        self.assertIn("180 vendas, 548 unidades", processo.stdout)
        self.assertIn("R$ 20.059,00", processo.stdout)
        self.assertEqual(JSON_SITE.read_bytes(), json_antes, "JSON gerado não é byte a byte reproduzível")
        self.assertEqual(hashes_antes, {arquivo: sha256(arquivo) for arquivo in preservados})

    def test_readme_documenta_comandos_reais(self) -> None:
        texto = README.read_text(encoding="utf-8")
        self.assertIn("preparar_dados.py", texto)
        self.assertIn("-m unittest discover -s tests -v", texto)
        self.assertIn("-m http.server 8000 --directory site", texto)
        self.assertIn("A pasta publicável é `site/`", texto)


class TesteHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.servidor = http.server.ThreadingHTTPServer(
            ("127.0.0.1", 0),
            lambda *args, **kwargs: ServidorSilencioso(*args, directory=os.fspath(SITE), **kwargs),
        )
        cls.thread = threading.Thread(target=cls.servidor.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.servidor.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.servidor.shutdown()
        cls.servidor.server_close()
        cls.thread.join(timeout=5)

    def test_http_carrega_site_scripts_css_e_json(self) -> None:
        for caminho in ("/", "/index.html", "/app.js", "/estilos.css", "/login.js", "/login.css", "/dados/vendas.json", "/vendas/"):
            with self.subTest(caminho=caminho), urlopen(self.url + caminho, timeout=5) as resposta:
                self.assertEqual(resposta.status, 200)
                conteudo = resposta.read()
                self.assertTrue(conteudo)
                if caminho.endswith("vendas.json"):
                    self.assertEqual(len(json.loads(conteudo)), 180)
                if caminho in {"/index.html", "/vendas/"}:
                    html = conteudo.decode("utf-8")
                    self.assertIn("type=\"password\"" if caminho == "/index.html" else "grafico-categorias", html)
                    parser = ReferenciasHTML()
                    parser.feed(html)
                    for referencia in parser.recursos:
                        alvo = urljoin(self.url + caminho, referencia)
                        partes = urlsplit(alvo)
                        self.assertEqual(partes.netloc, urlsplit(self.url).netloc, f"recurso externo inesperado: {alvo}")
                        with self.subTest(pagina=caminho, recurso=referencia), urlopen(alvo, timeout=5) as asset:
                            self.assertEqual(asset.status, 200)
                            self.assertTrue(asset.read())


class TesteFirefoxReal(TesteHTTP):
    """Interações no Firefox real headless via Marionette, sem DOM simulado."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.csv_limpo = ler_csv(RAIZ / "papelaria_limpa.csv")
        cls.registros = json.loads(JSON_SITE.read_text(encoding="utf-8"))
        if not FIREFOX.is_file():
            raise unittest.SkipTest("Firefox não instalado; interface real pendente.")
        try:
            cls.temp = tempfile.TemporaryDirectory(prefix="teste-dashboard-firefox-")
            cls.processo = subprocess.Popen(
                [os.fspath(FIREFOX), "--headless", "--marionette", "-no-remote", "-profile", cls.temp.name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            cls.socket = None
            limite = time.monotonic() + 20
            while time.monotonic() < limite:
                if cls.processo.poll() is not None:
                    raise RuntimeError("Firefox encerrou antes de iniciar Marionette.")
                try:
                    cls.socket = socket.create_connection(("127.0.0.1", 2828), timeout=0.5)
                    break
                except OSError:
                    time.sleep(0.2)
            if cls.socket is None:
                raise RuntimeError("Firefox não abriu a porta Marionette 2828.")
            cls.socket.settimeout(8)
            cliente = Marionette(cls.socket)
            saudacao = cliente._ler_pacote()
            if not isinstance(saudacao, dict) or saudacao.get("applicationType") != "gecko":
                raise RuntimeError(f"Saudação Marionette inesperada: {saudacao!r}")
            cliente.comando("WebDriver:NewSession")
            cls.marionette = cliente
            cls.marionette.comando("WebDriver:Navigate", {"url": cls.url + "/"})
            cls._autenticar_demo()
            cls.marionette.comando("WebDriver:ExecuteScript", {
                "script": "return document.readyState", "args": [],
            })
        except Exception as erro:
            cls._encerrar_firefox()
            super().tearDownClass()
            raise unittest.SkipTest(f"Automação Marionette indisponível: {erro}") from erro
        cls._aguardar_dados()

    @classmethod
    def _aguardar_dados(cls) -> None:
        fim = time.monotonic() + 10
        while time.monotonic() < fim:
            resposta = cls.marionette.comando("WebDriver:ExecuteScript", {
                "script": "return document.querySelector('#kpi-vendas').textContent",
                "args": [],
            })
            estado = resposta.get("value") if isinstance(resposta, dict) else resposta
            if estado == "180":
                return
            time.sleep(0.1)
        diagnostico = cls.marionette.comando("WebDriver:ExecuteScript", {
            "script": "return {url:location.href, pronto:document.readyState, erro:document.querySelector('#erro-carregamento').hidden, resumo:document.querySelector('#resumo-filtros').textContent, vendas:document.querySelector('#kpi-vendas').textContent}",
            "args": [],
        })
        raise AssertionError(f"Dashboard não carregou 180 vendas no Firefox: {diagnostico!r}")

    @classmethod
    def _autenticar_demo(cls) -> None:
        for seletor, valor in (("#usuario", "admin"), ("#senha", "papelaria2026")):
            elemento = cls.marionette.comando("WebDriver:FindElement", {"using": "css selector", "value": seletor}).get("value")
            cls.marionette.comando("WebDriver:ExecuteScript", {
                "script": f"document.querySelector({json.dumps(seletor)}).value='';", "args": [],
            })
            cls.marionette.comando("WebDriver:ElementSendKeys", {
                "id": elemento["element-6066-11e4-a52e-4f735466cecf"], "text": valor,
            })
        botao = cls.marionette.comando("WebDriver:FindElement", {"using": "css selector", "value": "#entrar-painel"}).get("value")
        cls.marionette.comando("WebDriver:ElementClick", {"id": botao["element-6066-11e4-a52e-4f735466cecf"]})

    @classmethod
    def _encerrar_firefox(cls) -> None:
        conexao = getattr(cls, "socket", None)
        cliente = getattr(cls, "marionette", None)
        if cliente:
            try:
                cliente.comando("WebDriver:DeleteSession")
            except Exception:
                pass
        if conexao:
            try:
                conexao.close()
            except OSError:
                pass
        processo = getattr(cls, "processo", None)
        if processo and processo.poll() is None:
            subprocess.run(["taskkill", "/PID", str(processo.pid), "/T", "/F"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            try:
                processo.wait(timeout=5)
            except subprocess.TimeoutExpired:
                processo.kill()
                processo.wait(timeout=5)
        temporario = getattr(cls, "temp", None)
        if temporario:
            shutil.rmtree(temporario.name, ignore_errors=True)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._encerrar_firefox()
        super().tearDownClass()

    def executar_js(self, script: str) -> object:
        resposta = self.marionette.comando("WebDriver:ExecuteScript", {"script": script, "args": []})
        return resposta.get("value") if isinstance(resposta, dict) else resposta

    def selecionar(self, seletor: str, valor: str) -> None:
        self.executar_js(
            f"const e=document.querySelector('{seletor}'); e.value={json.dumps(valor, ensure_ascii=False)}; "
            "e.dispatchEvent(new Event('change',{bubbles:true}));"
        )

    def estado(self) -> dict[str, object]:
        return self.executar_js(
            "return {valor:document.querySelector('#kpi-valor').textContent, "
            "vendas:document.querySelector('#kpi-vendas').textContent, "
            "ticket:document.querySelector('#kpi-ticket').textContent, "
            "linhas:document.querySelectorAll('#corpo-tabela tr').length, "
            "ids:[...document.querySelectorAll('#corpo-tabela tr td:nth-child(2)')].map(e=>e.textContent), "
            "categorias:document.querySelector('#grafico-categorias').textContent, "
            "mensal:document.querySelector('#grafico-mensal').textContent, "
            "valoresCategoria:[...document.querySelectorAll('#grafico-categorias .grafico-valor')].map(e=>e.textContent), "
            "valoresMensais:[...document.querySelectorAll('#grafico-mensal .grafico-valor')].map(e=>e.textContent), "
            "linhasTabela:[...document.querySelectorAll('#corpo-tabela tr')].map(tr=>[...tr.cells].map(td=>td.textContent)), "
            "vazio:document.querySelector('#mensagem-vazia').hidden, "
            "resumo:document.querySelector('#resumo-filtros').textContent};"
        )

    @staticmethod
    def centavos_formatados(texto: str) -> int:
        return int("".join(caractere for caractere in texto if caractere.isdigit()))

    def valores_grafico_em_centavos(self, valores: list[str]) -> set[int]:
        return {self.centavos_formatados(valor) for valor in valores}

    def test_kpis_graficos_tabela_e_filtros_reais(self) -> None:
        # A tabela passou a paginar; selecione “Todas” para manter a conferência
        # histórica das 180 linhas completas (não apenas da página inicial).
        self.executar_js(
            "const p=document.querySelector('#registros-por-pagina'); p.value='0'; "
            "p.dispatchEvent(new Event('change',{bubbles:true}));"
        )
        vendas = self.estado()
        self.assertEqual(self.centavos_formatados(vendas["valor"]), 2_005_900)
        self.assertEqual(vendas["vendas"], "180")
        self.assertEqual(vendas["linhas"], 180)
        self.assertTrue(vendas["vazio"])
        total_categoria: defaultdict[str, int] = defaultdict(int)
        total_mensal: defaultdict[str, int] = defaultdict(int)
        for linha in self.csv_limpo:
            total_categoria[linha["categoria"]] += centavos(linha["valor_venda"])
            total_mensal[linha["data"][:7]] += centavos(linha["valor_venda"])
        self.assertEqual(
            self.valores_grafico_em_centavos(vendas["valoresCategoria"]), set(total_categoria.values())
        )
        self.assertEqual(
            self.valores_grafico_em_centavos(vendas["valoresMensais"]), set(total_mensal.values())
        )
        self.assertEqual(set(vendas["ids"]), {linha["id_venda"] for linha in self.csv_limpo})

        por_cidade = {
            linha["cidade"]: (sum(centavos(l["valor_venda"]) for l in self.csv_limpo if l["cidade"].strip() == linha["cidade"]),
                              sum(l["cidade"].strip() == linha["cidade"] for l in self.csv_limpo))
            for linha in self.csv_limpo
        }
        esperado_campinas, qtd_campinas = por_cidade["Campinas"]
        self.selecionar("#filtro-cidade", "Campinas")
        filtrado = self.estado()
        self.assertEqual(self.centavos_formatados(filtrado["valor"]), esperado_campinas)
        self.assertEqual(filtrado["linhas"], qtd_campinas)
        self.assertEqual(filtrado["vendas"], str(qtd_campinas))
        self.assertTrue(all(r[2] == "Campinas" for r in filtrado["linhasTabela"]))
        self.assertEqual(
            set(filtrado["ids"]),
            {l["id_venda"] for l in self.csv_limpo if l["cidade"].strip() == "Campinas"},
        )
        # O gráfico continua agregando por categoria mesmo após o filtro de cidade;
        # a soma das barras (não uma barra artificial da cidade) deve ser o total filtrado.
        self.assertEqual(
            sum(self.centavos_formatados(valor) for valor in filtrado["valoresCategoria"]),
            esperado_campinas,
        )

        self.selecionar("#filtro-cidade", "")
        esperado_acessorios = sum(centavos(l["valor_venda"]) for l in self.csv_limpo if l["categoria"] == "Acessórios")
        qtd_acessorios = sum(l["categoria"] == "Acessórios" for l in self.csv_limpo)
        self.selecionar("#filtro-categoria", "Acessórios")
        filtrado = self.estado()
        self.assertEqual(self.centavos_formatados(filtrado["valor"]), esperado_acessorios)
        self.assertEqual(filtrado["linhas"], qtd_acessorios)
        self.assertIn(self.formatar_centavos(esperado_acessorios), filtrado["categorias"])
        self.assertTrue(all(r[3] == "Acessórios" for r in filtrado["linhasTabela"]))

        esperado_combinado = [
            l for l in self.csv_limpo if l["cidade"].strip() == "Campinas" and l["categoria"] == "Acessórios"
        ]
        self.selecionar("#filtro-cidade", "Campinas")
        combinado = self.estado()
        self.assertEqual(combinado["linhas"], len(esperado_combinado))
        self.assertEqual(
            self.centavos_formatados(combinado["valor"]),
            sum(centavos(l["valor_venda"]) for l in esperado_combinado),
        )
        self.assertEqual(
            set(combinado["ids"]), {l["id_venda"] for l in esperado_combinado}
        )
        self.assertTrue(all(r[2] == "Campinas" and r[3] == "Acessórios" for r in combinado["linhasTabela"]))

        # Categoria/cidade sem interseção presente na base: estado vazio e zeros finitos.
        self.executar_js(
            "const k=document.querySelector('#filtro-categoria'); const o=document.createElement('option'); "
            "o.value='Categoria inexistente'; o.textContent=o.value; k.append(o); k.value=o.value; "
            "k.dispatchEvent(new Event('change',{bubbles:true}));"
        )
        sem_resultado = self.estado()
        self.assertEqual(sem_resultado["linhas"], 0)
        self.assertEqual(sem_resultado["vendas"], "0")
        self.assertFalse(sem_resultado["vazio"])
        self.assertIn("Nenhuma venda", self.executar_js("return document.querySelector('#mensagem-vazia').textContent"))
        self.assertEqual(self.centavos_formatados(sem_resultado["valor"]), 0)
        self.assertEqual(self.centavos_formatados(sem_resultado["ticket"]), 0)
        sem_nan = self.executar_js(
            "return ![...document.querySelectorAll('#kpi-valor,#kpi-vendas,#kpi-ticket,"
            "#grafico-categorias,#grafico-mensal')].some(e=>/NaN|Infinity|undefined/.test(e.textContent))"
        )
        self.assertTrue(sem_nan)
        self.assertIn("Sem vendas", sem_resultado["categorias"])
        self.assertIn("Sem vendas", sem_resultado["mensal"])

        self.executar_js("document.querySelector('#limpar-filtros').click()")
        limpo = self.estado()
        self.assertEqual(limpo["linhas"], 180)
        self.assertEqual(self.centavos_formatados(limpo["valor"]), 2_005_900)
        self.assertEqual(self.executar_js("return document.activeElement.id"), "busca-venda")

    @staticmethod
    def formatar_centavos(valor: int) -> str:
        reais, cent = divmod(valor, 100)
        reais_local = f"{reais:,}".replace(",", ".")
        return f"R$\u00a0{reais_local},{cent:02d}"

    def test_teclado_e_viewports_grande_e_pequena(self) -> None:
        estrutura = self.executar_js(
            "return {labels:[...document.querySelectorAll('label')].map(e=>e.htmlFor), "
            "ids:[...document.querySelectorAll('select,button')].map(e=>e.id), "
            "atalho:!!document.querySelector('.pular-conteudo'), "
            "focoTabela:document.querySelector('.envoltorio-tabela').tabIndex}"
        )
        self.assertEqual(
            set(estrutura["labels"]),
            {"busca-venda", "filtro-cidade", "filtro-categoria", "data-inicio", "data-fim", "registros-por-pagina"},
        )
        self.assertTrue(estrutura["atalho"])
        self.assertGreaterEqual(estrutura["focoTabela"], 0)
        elemento = self.marionette.comando("WebDriver:FindElement", {
            "using": "css selector", "value": "#filtro-cidade",
        })
        elemento = elemento.get("value", elemento)
        self.marionette.comando("WebDriver:ElementClick", {"id": elemento["element-6066-11e4-a52e-4f735466cecf"]})
        self.marionette.comando("WebDriver:ElementSendKeys", {
            "id": elemento["element-6066-11e4-a52e-4f735466cecf"], "text": "Campinas",
        })
        self.assertEqual(self.executar_js("return document.querySelector('#filtro-cidade').value"), "Campinas")
        botao = self.marionette.comando("WebDriver:FindElement", {
            "using": "css selector", "value": "#limpar-filtros",
        }).get("value")
        self.marionette.comando("WebDriver:ElementClick", {
            "id": botao["element-6066-11e4-a52e-4f735466cecf"],
        })
        self.marionette.comando("WebDriver:ElementSendKeys", {
            "id": botao["element-6066-11e4-a52e-4f735466cecf"], "text": "\ue007",
        })
        self.assertEqual(self.executar_js("return document.activeElement.id"), "busca-venda")

        medidas = []
        for largura, altura in ((1280, 900), (390, 844)):
            self.marionette.comando("WebDriver:SetWindowRect", {
                "x": 0, "y": 0, "width": largura, "height": altura,
            })
            self.executar_js("window.dispatchEvent(new Event('resize'))")
            medidas.append(self.executar_js(
                "return {largura:innerWidth, viewport:document.documentElement.clientWidth, "
                "scroll:document.documentElement.scrollWidth, grid:getComputedStyle(document.querySelector('.graficos')).gridTemplateColumns, "
                "filtros:getComputedStyle(document.querySelector('.grade-filtros')).gridTemplateColumns, "
                "tabela:document.querySelector('.envoltorio-tabela').clientWidth, "
                "tabelaScroll:document.querySelector('.envoltorio-tabela').scrollWidth}"
            ))
        grande, pequeno = medidas
        self.assertGreaterEqual(grande["largura"], 760)
        self.assertGreaterEqual(pequeno["largura"], 320)
        self.assertLessEqual(pequeno["scroll"], pequeno["viewport"] + 1)
        self.assertLessEqual(pequeno["tabela"], pequeno["viewport"])
        self.assertGreater(pequeno["tabelaScroll"], pequeno["tabela"], "tabela deve rolar dentro do próprio contêiner")
        self.assertNotEqual(grande["grid"], pequeno["grid"], "gráficos devem empilhar em tela pequena")
        self.assertNotEqual(grande["filtros"], pequeno["filtros"], "filtros devem empilhar em tela pequena")


if __name__ == "__main__":
    unittest.main(verbosity=2)

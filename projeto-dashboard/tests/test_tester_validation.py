"""Independent acceptance checks for the static sales dashboard.

Run from projeto-dashboard with:
    python -m unittest discover -s tests -v

Browser checks use Firefox's real Marionette/WebDriver protocol; no DOM mock.
"""
from __future__ import annotations

import csv
import hashlib
import http.server
import importlib.util
import json
import os
import re
import socket
import subprocess
import tempfile
import threading
import time
import unicodedata
import unittest
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from urllib.request import urlopen


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
SITE = PROJECT / "site"
JSON_PATH = SITE / "dados" / "vendas.json"
FIREFOX = Path(r"C:\Program Files\Mozilla Firefox\firefox.exe")
FIELDS = {
    "id_venda", "data", "cidade", "categoria", "produto", "quantidade",
    "preco_unitario_centavos", "forma_pagamento", "valor_venda_centavos",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def money_cents(value: str) -> int:
    amount = Decimal(value)
    cents = amount * 100
    if cents != cents.to_integral_value():
        raise AssertionError(f"Not an exact cent value: {value}")
    return int(cents)


def parse_srgb(css_color: str) -> tuple[float, float, float]:
    """Parse Firefox's computed rgb()/rgba() color into normalized sRGB channels."""
    parts = re.findall(r"[-+]?(?:\d*\.\d+|\d+\.?\d*)%?", css_color)
    if len(parts) < 3:
        raise ValueError(f"Unsupported computed color: {css_color!r}")
    channels = []
    for part in parts[:3]:
        if part.endswith("%"):
            channel = float(part[:-1]) / 100
        else:
            channel = float(part) / 255
        channels.append(min(1.0, max(0.0, channel)))
    return channels[0], channels[1], channels[2]


def relative_luminance(css_color: str) -> float:
    def linear(channel: float) -> float:
        return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4

    red, green, blue = (linear(channel) for channel in parse_srgb(css_color))
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted((relative_luminance(foreground), relative_luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestWcagColorMath(unittest.TestCase):
    def test_known_wcag_srgb_pairs(self) -> None:
        self.assertAlmostEqual(contrast_ratio("rgb(0, 0, 0)", "rgb(255, 255, 255)"), 21.0, places=6)
        self.assertAlmostEqual(contrast_ratio("rgb(118, 118, 118)", "rgb(255, 255, 255)"), 4.5422, places=3)
        self.assertLess(contrast_ratio("rgb(119, 119, 119)", "rgb(255, 255, 255)"), 4.5)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args: object) -> None:
        pass


class Marionette:
    """Minimal client for Firefox's native Marionette framing protocol."""
    def __init__(self, conn: socket.socket):
        self.conn = conn
        self.command_id = 0

    def read_exact(self, length: int) -> bytes:
        data = bytearray()
        while len(data) < length:
            chunk = self.conn.recv(length - len(data))
            if not chunk:
                raise RuntimeError("Firefox closed Marionette connection")
            data.extend(chunk)
        return bytes(data)

    def packet(self) -> object:
        prefix = bytearray()
        while True:
            char = self.read_exact(1)
            if char == b":":
                break
            prefix.extend(char)
        return json.loads(self.read_exact(int(prefix)).decode("utf-8"))

    def command(self, name: str, params: dict[str, object] | None = None) -> object:
        self.command_id += 1
        payload = json.dumps([0, self.command_id, name, params or {}]).encode()
        self.conn.sendall(str(len(payload)).encode() + b":" + payload)
        while True:
            response = self.packet()
            if isinstance(response, list) and response[:2] == [1, self.command_id]:
                if response[2] is not None:
                    raise RuntimeError(f"Marionette {name} failed: {response!r}")
                return response[3]


class TestIndependentData(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = read_csv(ROOT / "papelaria_limpa.csv")
        cls.original = read_csv(ROOT / "vendas_papelaria.csv")
        cls.records = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    def test_schema_types_nulls_duplicates_and_source_lineage(self) -> None:
        self.assertEqual((len(self.original), len(self.source), len(self.records)), (182, 180, 180))
        self.assertEqual(set(self.records[0]), FIELDS)
        self.assertEqual(len({r["id_venda"] for r in self.records}), 180)
        self.assertEqual(len({r["id_venda"] for r in self.source}), 180)
        for source, record in zip(self.source, self.records):
            self.assertEqual(source["id_venda"], record["id_venda"])
            self.assertEqual(source["data"], record["data"])
            self.assertEqual(source["cidade"].strip(), record["cidade"])
            self.assertEqual(source["categoria"], record["categoria"])
            self.assertEqual(source["produto"], record["produto"])
            self.assertEqual(source["forma_pagamento"] or "Não informado", record["forma_pagamento"])
            self.assertTrue(all(value is not None and value != "" for value in record.values()))
            self.assertIs(type(record["quantidade"]), int)
            self.assertIs(type(record["preco_unitario_centavos"]), int)
            self.assertIs(type(record["valor_venda_centavos"]), int)
            self.assertEqual(record["preco_unitario_centavos"], money_cents(source["preco_unitario"]))
            self.assertEqual(record["quantidade"] * money_cents(source["preco_unitario"]), record["valor_venda_centavos"])
        # The raw source has exactly two repeated rows; neither source is edited by this test.
        rows = [tuple(sorted(row.items())) for row in self.original]
        self.assertEqual(len(rows) - len(set(rows)), 2)

    def test_independent_known_fixture_and_required_aggregates(self) -> None:
        fixture = [(2, Decimal("1.25")), (3, Decimal("2.10"))]
        self.assertEqual(sum(qty * int(price * 100) for qty, price in fixture), 880)
        self.assertEqual(sum(qty for qty, _price in fixture), 5)

        categories: defaultdict[str, int] = defaultdict(int)
        cities: defaultdict[str, int] = defaultdict(int)
        months: defaultdict[str, int] = defaultdict(int)
        total = units = 0
        for row in self.source:
            cents = int(row["quantidade"]) * money_cents(row["preco_unitario"])
            total += cents
            units += int(row["quantidade"])
            categories[row["categoria"]] += cents
            cities[row["cidade"].strip()] += cents
            months[row["data"][:7]] += cents
        self.assertEqual((len(self.source), units, total), (180, 548, 2_005_900))
        self.assertEqual(dict(categories), {"Acessórios": 1_051_700, "Livros": 743_800, "Papelaria": 210_400})
        self.assertEqual(dict(cities), {"Campinas": 857_800, "Santos": 693_750, "Sorocaba": 454_350})
        self.assertEqual(sum(months.values()), total)
        self.assertEqual(sum(r["valor_venda_centavos"] for r in self.records), total)

        # Exercise the actual exporter with a separate two-row CSV; its expected
        # cents are calculated above rather than by the exporter's conversion code.
        with tempfile.TemporaryDirectory(prefix="dashboard-fixture-") as temp:
            output_dir = Path(temp)
            fixture_path = output_dir / "fixture_known.csv"
            with fixture_path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(["id_venda", "data", "cidade", "categoria", "produto", "quantidade", "preco_unitario", "forma_pagamento", "valor_venda"])
                writer.writerow(["F01", "2026-01-02", "Teste", "Livros", "Caderno", "2", "1.25", "Cartão", "2.50"])
                writer.writerow(["F02", "2026-02-03", "Teste", "Acessórios", "Caneta", "3", "2.10", "Pix", "6.30"])
            spec = importlib.util.spec_from_file_location("preparador_teste_independente", PROJECT / "preparar_dados.py")
            self.assertIsNotNone(spec)
            module = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(module)
            module.ARQUIVO_FONTE = fixture_path
            module.ARQUIVO_SAIDA = output_dir / "vendas.json"
            result = module.preparar_dados()
            exported = json.loads(module.ARQUIVO_SAIDA.read_text(encoding="utf-8"))
            self.assertEqual(result, {"vendas": 2, "unidades": 5, "total_centavos": 880})
            self.assertEqual([r["valor_venda_centavos"] for r in exported], [250, 630])

    def test_preparation_preserves_original_and_prior_outputs(self) -> None:
        preserved = [ROOT / name for name in (
            "vendas_papelaria.csv", "papelaria_limpa.csv", "resumo.md", "verificacao.md",
            "graficos.py", "categorias.png", "cidades.png",
        )]
        before = {path: digest(path) for path in preserved}
        json_before = JSON_PATH.read_bytes()
        completed = subprocess.run(
            [os.fspath(Path(os.sys.executable)), os.fspath(PROJECT / "preparar_dados.py")],
            cwd=PROJECT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("180 vendas, 548 unidades", completed.stdout)
        self.assertEqual(JSON_PATH.read_bytes(), json_before)
        self.assertEqual(before, {path: digest(path) for path in preserved})


class TestIndependentHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = http.server.ThreadingHTTPServer(
            ("127.0.0.1", 0),
            lambda *args, **kwargs: QuietHandler(*args, directory=os.fspath(SITE), **kwargs),
        )
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def test_static_resources_http_and_script_syntax(self) -> None:
        for path in ("/", "/index.html", "/login.js", "/login.css", "/vendas/", "/vendas/index.html", "/app.js", "/estilos.css", "/dados/vendas.json"):
            with self.subTest(path=path), urlopen(self.base + path, timeout=5) as response:
                self.assertEqual(response.status, 200)
                self.assertTrue(response.read())
        result = subprocess.run(["node", "--check", os.fspath(SITE / "app.js")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class TestIndependentFirefox(TestIndependentHTTP):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        if not FIREFOX.is_file():
            raise unittest.SkipTest("Firefox não disponível; interação real pendente")
        cls.instrumented_site = tempfile.TemporaryDirectory(prefix="dashboard-browser-copy-")
        site_copy = Path(cls.instrumented_site.name) / "site"
        site_copy.mkdir()
        cls.download_dir = Path(cls.instrumented_site.name) / "downloads"
        cls.download_dir.mkdir()
        for source in SITE.rglob("*"):
            if source.is_file():
                destination = site_copy / source.relative_to(SITE)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source.read_bytes())
        listener = "<script>window.__testerJSErrors=[];window.__printCalls=0;window.__testerCsvText=null;window.__testerDownloadNames=[];window.print=()=>{window.__printCalls+=1};const __createObjectURL=URL.createObjectURL.bind(URL);URL.createObjectURL=(blob)=>{if(blob&&blob.type.includes('csv'))blob.text().then(text=>window.__testerCsvText=text);return __createObjectURL(blob)};const __anchorClick=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){if(this.download)window.__testerDownloadNames.push(this.download);return __anchorClick.call(this)};const __ce=console.error.bind(console);console.error=(...a)=>{window.__testerJSErrors.push(a.map(String).join(' '));__ce(...a)};window.addEventListener('error',e=>window.__testerJSErrors.push(e.message));window.addEventListener('unhandledrejection',e=>window.__testerJSErrors.push(String(e.reason)));</script>"
        for page, script_tag in (
            (site_copy / "index.html", '<script src="login.js" defer></script>'),
            (site_copy / "vendas" / "index.html", '<script src="../app.js" defer></script>'),
        ):
            html = page.read_text(encoding="utf-8")
            page.write_text(html.replace(script_tag, listener + script_tag), encoding="utf-8")
        cls.browser_server = http.server.ThreadingHTTPServer(
            ("127.0.0.1", 0),
            lambda *args, **kwargs: QuietHandler(*args, directory=os.fspath(site_copy), **kwargs),
        )
        cls.browser_thread = threading.Thread(target=cls.browser_server.serve_forever, daemon=True)
        cls.browser_thread.start()
        cls.browser_url = f"http://127.0.0.1:{cls.browser_server.server_port}"
        cls.profile = tempfile.TemporaryDirectory(prefix="tester-firefox-")
        profile_path = Path(cls.profile.name)
        (profile_path / "user.js").write_text(
            'user_pref("browser.download.folderList", 2);\n'
            'user_pref("browser.download.dir", ' + json.dumps(os.fspath(cls.download_dir)) + ');\n'
            'user_pref("browser.download.useDownloadDir", true);\n'
            'user_pref("browser.download.always_ask_before_handling_new_types", false);\n'
            'user_pref("browser.helperApps.neverAsk.saveToDisk", "text/csv,application/csv,application/octet-stream");\n',
            encoding="utf-8",
        )
        cls.process = subprocess.Popen(
            [os.fspath(FIREFOX), "--headless", "--marionette", "-no-remote", "-profile", cls.profile.name],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        cls.conn = None
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            if cls.process.poll() is not None:
                raise RuntimeError("Firefox saiu antes de iniciar")
            try:
                cls.conn = socket.create_connection(("127.0.0.1", 2828), timeout=0.5)
                break
            except OSError:
                time.sleep(0.2)
        if cls.conn is None:
            raise RuntimeError("Firefox Marionette não iniciou")
        cls.conn.settimeout(10)
        cls.driver = Marionette(cls.conn)
        greeting = cls.driver.packet()
        if not isinstance(greeting, dict) or greeting.get("applicationType") != "gecko":
            raise RuntimeError(f"Resposta Marionette inválida: {greeting!r}")
        cls.driver.command("WebDriver:NewSession")
        cls.driver.command("WebDriver:Navigate", {"url": cls.browser_url + "/"})
        cls.submit_login("admin", "papelaria2026")
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            state = cls.js("return {path:location.pathname,count:document.querySelector('#kpi-vendas')?.textContent}")
            if state == {"path": "/vendas/", "count": "180"}:
                return
            time.sleep(0.1)
        raise AssertionError("Dashboard não inicializou no Firefox")

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "driver"):
            try:
                cls.driver.command("WebDriver:DeleteSession")
            except Exception:
                pass
        if getattr(cls, "conn", None):
            cls.conn.close()
        process = getattr(cls, "process", None)
        if process and process.poll() is None:
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
            process.wait(timeout=5)
        if hasattr(cls, "profile"):
            cls.profile.cleanup()
        if hasattr(cls, "browser_server"):
            cls.browser_server.shutdown()
            cls.browser_server.server_close()
            cls.browser_thread.join(timeout=5)
        if hasattr(cls, "instrumented_site"):
            cls.instrumented_site.cleanup()
        super().tearDownClass()

    @classmethod
    def js(cls, script: str) -> object:
        result = cls.driver.command("WebDriver:ExecuteScript", {"script": script, "args": []})
        return result.get("value") if isinstance(result, dict) else result

    @classmethod
    def submit_login(cls, username: str, password: str) -> None:
        for selector, value in (("#usuario", username), ("#senha", password)):
            element = cls.driver.command("WebDriver:FindElement", {"using": "css selector", "value": selector}).get("value")
            cls.js(f"document.querySelector({json.dumps(selector)}).value=''")
            cls.driver.command("WebDriver:ElementSendKeys", {"id": element["element-6066-11e4-a52e-4f735466cecf"], "text": value})
        cls.click_css_static("#entrar-painel")

    @classmethod
    def click_css_static(cls, selector: str) -> None:
        element = cls.driver.command("WebDriver:FindElement", {"using": "css selector", "value": selector}).get("value")
        cls.driver.command("WebDriver:ElementClick", {"id": element["element-6066-11e4-a52e-4f735466cecf"]})

    def setUp(self) -> None:
        # Each browser case starts from the page's own reset path, not shared prior state.
        self.js("document.getElementById('limpar-filtros').click();const s=document.getElementById('registros-por-pagina');const d=[...s.options].find(o=>o.hasAttribute('selected'))||s.options[0];s.value=d.value;s.dispatchEvent(new Event('change',{bubbles:true}))")

    def choose(self, element_id: str, value: str) -> None:
        self.js(f"const e=document.getElementById('{element_id}');e.value={json.dumps(value, ensure_ascii=False)};e.dispatchEvent(new Event('change',{{bubbles:true}}))")

    def state(self) -> dict[str, object]:
        return self.js("return {total:document.querySelector('#kpi-valor').textContent,count:document.querySelector('#kpi-vendas').textContent,ticket:document.querySelector('#kpi-ticket').textContent,rows:[...document.querySelectorAll('#corpo-tabela tr')].map(tr=>[...tr.cells].map(td=>td.textContent)),cats:[...document.querySelectorAll('#grafico-categorias .grafico-valor')].map(e=>e.textContent),months:[...document.querySelectorAll('#grafico-mensal .grafico-valor')].map(e=>e.textContent),empty:!document.querySelector('#mensagem-vazia').hidden}")

    @staticmethod
    def cents(text: str) -> int:
        return int("".join(char for char in text if char.isdigit()))

    def set_control(self, element_id: str, value: str) -> None:
        self.js(
            f"const e=document.getElementById({json.dumps(element_id)});e.value={json.dumps(value, ensure_ascii=False)};"
            "e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));"
        )

    def click_css(self, selector: str) -> None:
        element = self.driver.command("WebDriver:FindElement", {"using": "css selector", "value": selector}).get("value")
        self.driver.command("WebDriver:ElementClick", {"id": element["element-6066-11e4-a52e-4f735466cecf"]})

    def page_ids(self) -> list[str]:
        return self.js("return [...document.querySelectorAll('#corpo-tabela tr td:nth-child(2)')].map(e=>e.textContent)")

    def all_page_ids(self) -> list[str]:
        ids: list[str] = []
        for _ in range(100):
            ids.extend(self.page_ids())
            if self.js("return document.getElementById('pagina-proxima').disabled"):
                return ids
            self.click_css("#pagina-proxima")
        self.fail("Paginação excedeu 100 páginas")

    def is_monotonic(self, values: list[object], ascending: bool) -> bool:
        encoded = json.dumps(values, ensure_ascii=False)
        operator = "<=" if ascending else ">="
        return bool(self.js(
            f"const v={encoded};const c=new Intl.Collator('pt-BR',{{numeric:true,sensitivity:'base'}});"
            f"return v.every((x,i)=>!i||(typeof x==='number'?v[i-1]{operator}x:c.compare(v[i-1],x){operator}0))"
        ))

    def expected_from_controls(self, records: list[dict[str, object]]) -> list[dict[str, object]]:
        values = self.js("return {q:document.getElementById('busca-venda').value.toLocaleLowerCase('pt-BR'),city:document.getElementById('filtro-cidade').value,cat:document.getElementById('filtro-categoria').value,start:document.getElementById('data-inicio').value,end:document.getElementById('data-fim').value}")
        def normalize(value: object) -> str:
            decomposed = unicodedata.normalize("NFD", str(value).casefold())
            return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
        query = normalize(values["q"])
        result = []
        searchable = ("id_venda", "produto", "cidade", "categoria", "forma_pagamento")
        for record in records:
            haystack = " ".join(normalize(record[key]) for key in searchable)
            if query and query not in haystack:
                continue
            if values["city"] and record["cidade"] != values["city"]:
                continue
            if values["cat"] and record["categoria"] != values["cat"]:
                continue
            if values["start"] and record["data"] < values["start"]:
                continue
            if values["end"] and record["data"] > values["end"]:
                continue
            result.append(record)
        return result

    def assert_filtered_components(self, records: list[dict[str, object]]) -> None:
        expected = self.expected_from_controls(records)
        total = sum(int(r["valor_venda_centavos"]) for r in expected)
        view = self.state()
        self.assertEqual(view["count"], str(len(expected)))
        self.assertEqual(self.cents(view["total"]), total)
        average = (2 * total + len(expected)) // (2 * len(expected)) if expected else 0
        self.assertEqual(self.cents(view["ticket"]), average)
        expected_by_category: defaultdict[str, int] = defaultdict(int)
        expected_by_month: defaultdict[str, int] = defaultdict(int)
        for record in expected:
            expected_by_category[str(record["categoria"])] += int(record["valor_venda_centavos"])
            expected_by_month[str(record["data"])[:7]] += int(record["valor_venda_centavos"])
        self.assertEqual({self.cents(x) for x in view["cats"]}, set(expected_by_category.values()))
        self.assertEqual({self.cents(x) for x in view["months"]}, set(expected_by_month.values()))
        all_ids = self.all_page_ids()
        self.assertEqual(set(all_ids), {str(record["id_venda"]) for record in expected})
        self.assertEqual(len(all_ids), len(expected), "tabela não deve omitir ou repetir linhas entre páginas")

    def test_kpis_charts_table_and_both_filters(self) -> None:
        self.set_control("registros-por-pagina", "0")
        records = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        view = self.state()
        self.assertEqual(self.cents(view["total"]), 2_005_900)
        self.assertEqual(view["count"], "180")
        self.assertEqual(self.cents(view["ticket"]), (2 * 2_005_900 + 180) // (2 * 180))
        self.assertEqual(len(view["rows"]), 180)
        self.assertEqual({row[1] for row in view["rows"]}, {r["id_venda"] for r in records})
        expected_cat: defaultdict[str, int] = defaultdict(int)
        expected_month: defaultdict[str, int] = defaultdict(int)
        for row in records:
            expected_cat[row["categoria"]] += row["valor_venda_centavos"]
            expected_month[row["data"][:7]] += row["valor_venda_centavos"]
        self.assertEqual({self.cents(v) for v in view["cats"]}, set(expected_cat.values()))
        self.assertEqual({self.cents(v) for v in view["months"]}, set(expected_month.values()))

        for city, category in (("Campinas", ""), ("", "Livros"), ("Campinas", "Livros")):
            self.choose("filtro-cidade", city)
            self.choose("filtro-categoria", category)
            actual = self.state()
            selected = [r for r in records if (not city or r["cidade"] == city) and (not category or r["categoria"] == category)]
            total = sum(r["valor_venda_centavos"] for r in selected)
            self.assertEqual(len(actual["rows"]), len(selected))
            self.assertEqual(actual["count"], str(len(selected)))
            self.assertEqual(self.cents(actual["total"]), total)
            rounded_ticket = (2 * total + len(selected)) // (2 * len(selected)) if selected else 0
            self.assertEqual(self.cents(actual["ticket"]), rounded_ticket)
            expected_ids = {r["id_venda"] for r in selected}
            self.assertEqual({r[1] for r in actual["rows"]}, expected_ids)
            self.assertTrue(all((not city or row[2] == city) and (not category or row[3] == category) for row in actual["rows"]))
            category_totals: defaultdict[str, int] = defaultdict(int)
            month_totals: defaultdict[str, int] = defaultdict(int)
            for row in selected:
                category_totals[row["categoria"]] += row["valor_venda_centavos"]
                month_totals[row["data"][:7]] += row["valor_venda_centavos"]
            self.assertEqual({self.cents(v) for v in actual["cats"]}, set(category_totals.values()))
            self.assertEqual({self.cents(v) for v in actual["months"]}, set(month_totals.values()))

        # Deliberately add a valid DOM option not represented in the source to test empty-state arithmetic.
        self.js("const s=document.querySelector('#filtro-categoria');const o=document.createElement('option');o.value='__sem_resultados__';s.append(o);s.value=o.value;s.dispatchEvent(new Event('change',{bubbles:true}))")
        empty = self.state()
        self.assertEqual((empty["count"], len(empty["rows"]), empty["total"], empty["ticket"]), ("0", 0, "R$\u00a00,00", "R$\u00a00,00"))
        self.assertTrue(empty["empty"])
        self.assertTrue(self.js("return ![...document.querySelectorAll('#kpi-valor,#kpi-vendas,#kpi-ticket,#grafico-categorias,#grafico-mensal')].some(e=>/NaN|Infinity|undefined/.test(e.textContent))"))
        self.js("document.querySelector('#limpar-filtros').click()")
        cleared = self.state()
        self.assertEqual(cleared["count"], "180")
        self.assertEqual(self.cents(cleared["total"]), 2_005_900)
        self.assertEqual(self.js("return document.activeElement.id"), "busca-venda")
        self.assertEqual(self.js("return window.__testerJSErrors"), [], "erros JavaScript registrados no navegador")

    def test_keyboard_labels_and_responsive_viewports(self) -> None:
        metadata = self.js("return {labels:[...document.querySelectorAll('label')].map(x=>x.htmlFor),skip:!!document.querySelector('.pular-conteudo'),tabIndex:document.querySelector('.envoltorio-tabela').tabIndex,labelFont:parseFloat(getComputedStyle(document.querySelector('label[for=filtro-cidade]')).fontSize),selectFont:parseFloat(getComputedStyle(document.querySelector('#filtro-cidade')).fontSize)}")
        self.assertEqual(
            set(metadata["labels"]),
            {"busca-venda", "filtro-cidade", "filtro-categoria", "data-inicio", "data-fim", "registros-por-pagina"},
        )
        self.assertTrue(metadata["skip"])
        self.assertGreaterEqual(metadata["tabIndex"], 0)
        self.assertGreaterEqual(metadata["labelFont"], 12, "rótulos de filtro devem permanecer legíveis")
        self.assertGreaterEqual(metadata["selectFont"], 14, "texto dos filtros deve permanecer legível")
        # Use WebDriver keyboard input on each native select, not synthetic change events.
        records = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        for element_id, value in (("filtro-cidade", "Campinas"), ("filtro-categoria", "Livros")):
            element = self.driver.command("WebDriver:FindElement", {"using": "css selector", "value": f"#{element_id}"}).get("value")
            self.driver.command("WebDriver:ElementClick", {"id": element["element-6066-11e4-a52e-4f735466cecf"]})
            self.driver.command("WebDriver:ElementSendKeys", {"id": element["element-6066-11e4-a52e-4f735466cecf"], "text": value})
            self.assertEqual(self.js(f"return document.querySelector('#{element_id}').value"), value)
        expected = [r for r in records if r["cidade"] == "Campinas" and r["categoria"] == "Livros"]
        self.assertGreater(len(expected), 0)
        self.assertEqual(int(self.js("return document.querySelector('#kpi-vendas').textContent")), len(expected))
        self.assertTrue(self.js("return [...document.querySelectorAll('#corpo-tabela tr')].every(r=>r.cells[2].textContent==='Campinas'&&r.cells[3].textContent==='Livros')"))
        button = self.driver.command("WebDriver:FindElement", {"using": "css selector", "value": "#limpar-filtros"}).get("value")
        self.js("document.querySelector('#limpar-filtros').focus()")
        self.driver.command("WebDriver:ElementSendKeys", {"id": button["element-6066-11e4-a52e-4f735466cecf"], "text": "\ue007"})
        self.assertEqual(self.js("return document.activeElement.id"), "busca-venda")
        self.assertEqual(self.js("return document.querySelector('#filtro-cidade').value + '|' + document.querySelector('#filtro-categoria').value"), "|")
        self.assertEqual(self.js("return document.querySelector('#kpi-vendas').textContent"), "180")
        measurements = []
        for width, height in ((1280, 900), (390, 844)):
            self.driver.command("WebDriver:SetWindowRect", {"x": 0, "y": 0, "width": width, "height": height})
            measurements.append(self.js("return {client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,graphs:getComputedStyle(document.querySelector('.graficos')).gridTemplateColumns,filters:getComputedStyle(document.querySelector('.grade-filtros')).gridTemplateColumns,table:document.querySelector('.envoltorio-tabela').clientWidth,tableScroll:document.querySelector('.envoltorio-tabela').scrollWidth}"))
        large, small = measurements
        self.assertLessEqual(small["scroll"], small["client"] + 1)
        self.assertLessEqual(small["table"], small["client"])
        self.assertGreater(small["tableScroll"], small["table"])
        self.assertNotEqual(large["graphs"], small["graphs"])
        self.assertNotEqual(large["filters"], small["filters"])

    def test_mobile_graph_text_has_minimum_rendered_height(self) -> None:
        self.driver.command("WebDriver:SetWindowRect", {"x": 0, "y": 0, "width": 390, "height": 844})
        measurements = self.js("return ['grafico-categorias','grafico-mensal'].map(id=>{const svg=document.getElementById(id);return {id,viewport:innerWidth,width:svg.getBoundingClientRect().width,textos:[...svg.querySelectorAll('text.grafico-eixo,text.grafico-rotulo,text.grafico-valor')].map(e=>{const r=e.getBoundingClientRect();return {classe:e.getAttribute('class'),texto:e.textContent.trim(),largura:r.width,altura:r.height,fontsize:getComputedStyle(e).fontSize}})}})")
        self.assertEqual([item["id"] for item in measurements], ["grafico-categorias", "grafico-mensal"])
        failures = []
        minima = {}
        for chart in measurements:
            self.assertLessEqual(chart["viewport"], 520, "Firefox deve estar no breakpoint móvel; requested window width=390px")
            self.assertGreater(chart["width"], 0, chart["id"])
            self.assertTrue(chart["textos"], chart["id"] + " sem textos medidos")
            minima[chart["id"]] = {
                classe: min(item["altura"] for item in chart["textos"] if item["classe"] == classe)
                for classe in {item["classe"] for item in chart["textos"]}
            }
            failures.extend(
                f"{chart['id']} {item['classe']} {item['texto']!r}: altura={item['altura']:.2f}px, fonte CSS={item['fontsize']}"
                for item in chart["textos"] if item["altura"] < 12
            )
        print(f"Firefox: window request=390px; innerWidth móvel real={measurements[0]['viewport']}px; altura mínima DOMRect por SVG/classe={minima}")
        self.assertFalse(failures, "Textos de eixo/rótulo/valor menores que 12px renderizados:\n" + "\n".join(failures))

    def test_partial_search_covers_all_five_fields_and_updates_components(self) -> None:
        records = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        examples = {
            "id": str(records[0]["id_venda"])[1:4],
            "produto": str(records[0]["produto"])[1:4],
            "cidade": "amp",
            "categoria": "cess",
            "pagamento": "ix",
        }
        self.assertTrue(all(examples.values()))
        for field, query in examples.items():
            with self.subTest(field=field, query=query):
                self.js("document.getElementById('limpar-filtros').click()")
                self.set_control("busca-venda", query)
                expected = self.expected_from_controls(records)
                self.assertGreater(len(expected), 0, f"fixture não cobre busca parcial de {field}")
                self.assert_filtered_components(records)

    def wait_for_path(self, path: str, timeout: float = 10) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.js("return location.pathname") == path:
                return
            time.sleep(0.1)
        self.fail(f"Rota atual não chegou a {path}; URL observada: {self.js('return location.href')}")

    def test_demo_login_error_success_route_guard_logout_and_relogin(self) -> None:
        # Login is a public demo convenience, not a security boundary.
        self.js("sessionStorage.clear()")
        self.driver.command("WebDriver:Navigate", {"url": self.browser_url + "/"})
        self.wait_for_path("/")
        self.assertTrue(self.js("return !!document.querySelector('#formulario-login input[type=password]')"))

        self.submit_login("admin", "senha-incorreta")
        self.assertEqual(self.js("return location.pathname"), "/")
        error = self.js("const e=document.getElementById('erro-login');return {visible:!!e&&!e.hidden,text:e?.textContent.trim()||'',session:sessionStorage.getItem('papelaria-demo-auth')}")
        self.assertTrue(error["visible"])
        self.assertTrue(error["text"])
        self.assertIsNone(error["session"])

        self.submit_login("admin", "papelaria2026")
        self.wait_for_path("/vendas/")
        self.assertEqual(self.js("return document.querySelector('#kpi-vendas')?.textContent"), "180")
        self.assertEqual(self.js("return sessionStorage.getItem('papelaria-demo-auth')"), "ok")

        # Direct dashboard access without the session must redirect to the login route.
        self.js("sessionStorage.clear()")
        self.driver.command("WebDriver:Navigate", {"url": self.browser_url + "/vendas/"})
        self.wait_for_path("/")
        self.assertTrue(self.js("return !!document.querySelector('#formulario-login')"))

        self.submit_login("admin", "papelaria2026")
        self.wait_for_path("/vendas/")
        self.click_css("#sair-painel")
        self.wait_for_path("/")
        self.assertIsNone(self.js("return sessionStorage.getItem('papelaria-demo-auth')"))
        self.assertTrue(self.js("return !!document.querySelector('#formulario-login')"))

        # Leave the shared Firefox session authenticated for later dashboard tests.
        self.submit_login("admin", "papelaria2026")
        self.wait_for_path("/vendas/")
        self.assertEqual(self.js("return document.querySelector('#kpi-vendas')?.textContent"), "180")

    def test_date_filters_start_end_and_combination_update_all_components(self) -> None:
        records = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        scenarios = (
            {"data-inicio": "2026-03-01"},
            {"data-fim": "2026-01-31"},
            {"data-inicio": "2026-02-01", "data-fim": "2026-02-28"},
        )
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                self.js("document.getElementById('limpar-filtros').click()")
                for field, value in scenario.items():
                    self.set_control(field, value)
                expected = self.expected_from_controls(records)
                self.assertGreater(len(expected), 0)
                self.assert_filtered_components(records)

    def test_pagination_page_sizes_and_complete_filter_reset(self) -> None:
        records = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        self.js("document.getElementById('limpar-filtros').click()")
        sizes = self.js("return [...document.querySelectorAll('#registros-por-pagina option')].map(o=>Number(o.value)).filter(Number.isFinite).filter(n=>n>0)")
        self.assertTrue(sizes, "seletor deve oferecer tamanhos de página numéricos")
        smallest, largest = min(sizes), max(sizes)
        self.set_control("registros-por-pagina", str(smallest))
        first = self.page_ids()
        self.assertEqual(len(first), smallest)
        self.assertTrue(self.js("return document.getElementById('pagina-anterior').disabled"))
        page1_label = self.js("return document.getElementById('pagina-atual').textContent")
        self.click_css("#pagina-proxima")
        second = self.page_ids()
        self.assertEqual(len(second), smallest)
        self.assertNotEqual(first, second)
        self.assertFalse(self.js("return document.getElementById('pagina-anterior').disabled"))
        page2_label = self.js("return document.getElementById('pagina-atual').textContent")
        self.assertNotEqual(page1_label, page2_label)
        self.click_css("#pagina-anterior")
        self.assertEqual(self.page_ids(), first)
        self.set_control("registros-por-pagina", str(largest))
        self.assertEqual(len(self.page_ids()), largest)

        # Move off page one, then activate every new filter and ensure clear restores them.
        self.set_control("registros-por-pagina", str(smallest))
        self.set_control("filtro-cidade", "Campinas")
        self.assertGreater(len(self.expected_from_controls(records)), smallest)
        self.click_css("#pagina-proxima")
        self.set_control("filtro-categoria", "Acessórios")
        self.set_control("busca-venda", "can")
        self.set_control("data-inicio", "2026-01-01")
        self.set_control("data-fim", "2026-03-31")
        self.js("document.getElementById('limpar-filtros').click()")
        cleared = self.js("return {q:document.getElementById('busca-venda').value,city:document.getElementById('filtro-cidade').value,cat:document.getElementById('filtro-categoria').value,start:document.getElementById('data-inicio').value,end:document.getElementById('data-fim').value,prev:document.getElementById('pagina-anterior').disabled,count:document.getElementById('kpi-vendas').textContent}")
        self.assertEqual(cleared, {"q": "", "city": "", "cat": "", "start": "", "end": "", "prev": True, "count": "180"})

    def test_each_sort_button_sorts_all_rows_in_both_directions(self) -> None:
        records = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        by_id = {str(record["id_venda"]): record for record in records}
        sizes = self.js("return [...document.querySelectorAll('#registros-por-pagina option')].map(o=>Number(o.value)).filter(n=>n>0)")
        self.assertTrue(sizes)
        self.set_control("registros-por-pagina", str(max(sizes)))
        for key in ("data", "id_venda", "cidade", "categoria", "produto", "quantidade", "preco_unitario_centavos", "valor_venda_centavos", "forma_pagamento"):
            with self.subTest(key=key):
                button = f'button[data-ordenar="{key}"]'
                self.assertEqual(self.js(f"return document.querySelectorAll({json.dumps(button)}).length"), 1)
                self.click_css(button)
                self.assertTrue(self.js("return document.getElementById('pagina-anterior').disabled"), f"ordenar por {key} deve voltar à página 1")
                first_ids = self.all_page_ids()
                self.assertEqual(set(first_ids), set(by_id))
                first_values = [by_id[identifier][key] for identifier in first_ids]
                ascending_first = self.is_monotonic(first_values, True)
                descending_first = self.is_monotonic(first_values, False)
                self.assertNotEqual(ascending_first, descending_first, f"ordem por {key} não é monotônica ou os dados não variam")
                self.click_css(button)
                second_ids = self.all_page_ids()
                self.assertEqual(set(second_ids), set(by_id))
                second_values = [by_id[identifier][key] for identifier in second_ids]
                ascending_second = self.is_monotonic(second_values, True)
                descending_second = self.is_monotonic(second_values, False)
                self.assertNotEqual(ascending_second, descending_second, f"segunda direção inválida para {key}")
                self.assertNotEqual(ascending_first, ascending_second, f"segunda ativação não inverteu {key}")

    def test_csv_export_contains_all_filtered_rows_and_filtered_total(self) -> None:
        records = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        self.js("document.getElementById('limpar-filtros').click()")
        counts: defaultdict[str, int] = defaultdict(int)
        for record in records:
            counts[str(record["cidade"])] += 1
        city = max(counts, key=counts.get)
        options = self.js("return [...document.querySelectorAll('#registros-por-pagina option')].map(o=>Number(o.value)).filter(n=>n>0)")
        self.assertTrue(options)
        page_size = min(options)
        self.set_control("registros-por-pagina", str(page_size))
        self.set_control("filtro-cidade", city)
        expected = self.expected_from_controls(records)
        self.assertGreater(len(expected), page_size, "fixture deve ter mais filtrados que uma página")
        self.click_css("#pagina-proxima")
        self.assertEqual(len(self.page_ids()), page_size)
        before = set(self.download_dir.iterdir())
        self.click_css("#exportar-csv")
        deadline = time.monotonic() + 15
        downloaded: Path | None = None
        csv_text: str | None = None
        while time.monotonic() < deadline:
            candidates = [p for p in self.download_dir.glob("*.csv") if p not in before]
            partials = list(self.download_dir.glob("*.part"))
            if candidates and not partials:
                downloaded = max(candidates, key=lambda p: p.stat().st_mtime)
                break
            csv_text = self.js("return window.__testerCsvText")
            if csv_text is not None:
                break
            time.sleep(0.2)
        if downloaded is not None:
            text = downloaded.read_text(encoding="utf-8-sig")
            print(f"CSV de exportação lido do download Firefox: {downloaded.name}")
        else:
            self.assertIsNotNone(csv_text, "o botão não produziu arquivo baixado nem Blob CSV no Firefox")
            self.assertTrue(self.js("return window.__testerDownloadNames.some(name=>name.toLowerCase().endsWith('.csv'))"), "deve acionar um link de download .csv")
            text = str(csv_text).lstrip("\ufeff")
            print("CSV de exportação lido do Blob real gerado no Firefox; Firefox não salvou arquivo nesta execução.")
        self.assertTrue(text.strip())
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;")
        rows = list(csv.DictReader(text.splitlines(), dialect=dialect))
        self.assertTrue(rows, "CSV deve ter cabeçalho e registros")
        header_by_lower = {str(name).strip().casefold(): name for name in rows[0]}
        id_column = next((name for lower, name in header_by_lower.items() if lower in {"id_venda", "id da venda", "id venda"}), None)
        self.assertIsNotNone(id_column, f"CSV precisa exportar o identificador de venda: {list(rows[0])}")
        ids = [str(row[id_column]).strip() for row in rows]
        expected_ids = {str(record["id_venda"]) for record in expected}
        self.assertEqual(set(ids), expected_ids, "CSV deve incluir todos os filtrados, não só a página atual")
        self.assertEqual(len(ids), len(expected))
        csv_total = sum(int(record["valor_venda_centavos"]) for record in expected if str(record["id_venda"]) in set(ids))
        self.assertEqual(csv_total, sum(int(record["valor_venda_centavos"]) for record in expected))
        amount_column = next((name for lower, name in header_by_lower.items() if "valor" in lower), None)
        self.assertIsNotNone(amount_column, f"CSV deve conter valor da venda: {list(rows[0])}")
        assert amount_column is not None
        exported_total = sum(int("".join(ch for ch in str(row[amount_column]) if ch.isdigit()) or "0") for row in rows)
        self.assertEqual(exported_total, csv_total, "soma dos valores exportados deve corresponder ao conjunto filtrado")

    def test_print_button_calls_print_and_print_styles_exist(self) -> None:
        css = urlopen(self.base + "/estilos.css", timeout=5).read().decode("utf-8")
        self.assertIn("@media print", css.casefold(), "CSS deve declarar regras de impressão")
        media_rules = self.js("return [...document.styleSheets].flatMap(s=>{try{return [...s.cssRules]}catch{return []}}).filter(r=>r instanceof CSSMediaRule&&r.conditionText.includes('print')).map(r=>r.cssText)")
        self.assertTrue(media_rules, "regras de impressão devem estar carregadas no site servido")
        print_css = " ".join(media_rules).casefold()
        self.assertIn(".tabela-impressao", print_css)
        self.assertIn("display: block", print_css)
        self.assertIn(".filtros", print_css)
        self.assertIn("display: none", print_css)
        self.click_css("#imprimir-painel")
        self.assertEqual(self.js("return window.__printCalls"), 1, "botão deve acionar window.print()")

    def measure_text_colors(self, specs: list[tuple[str, str, str | None]]) -> list[dict[str, object]]:
        encoded = json.dumps(specs, ensure_ascii=False)
        script = f"""
          const specs={encoded};
          function alphaOf(color) {{
            const match=String(color).match(/rgba?\\(([^)]+)\\)/i);
            if(!match)return 0;
            const numbers=match[1].match(/[-+]?(?:\\d*\\.)?\\d+/g)||[];
            return numbers.length>3?Number(numbers[3]):1;
          }}
          function opaqueBackground(element) {{
            for(let node=element;node;node=node.parentElement) {{
              const color=getComputedStyle(node).backgroundColor;
              if(alphaOf(color)>=0.999)return color;
            }}
            return 'rgb(255, 255, 255)';
          }}
          return specs.flatMap(([label,selector,pseudo])=>{{
            const elements=[...document.querySelectorAll(selector)];
            return elements.map((element,index)=>{{
              const style=pseudo?getComputedStyle(element,pseudo):getComputedStyle(element);
              const rect=element.getBoundingClientRect();
              const foreground=element.namespaceURI==='http://www.w3.org/2000/svg'?style.fill:style.color;
              return {{label:elements.length>1?`${{label}}[${{index+1}}]`:label,selector,pseudo,foreground,background:opaqueBackground(element),visible:style.display!=='none'&&style.visibility!=='hidden'&&rect.width>0&&rect.height>0}};
            }});
          }});
        """
        return self.js(script)

    def test_wcag_aa_normal_text_contrast_on_login_and_dashboard(self) -> None:
        self.js("sessionStorage.clear()")
        self.driver.command("WebDriver:Navigate", {"url": self.browser_url + "/"})
        self.wait_for_path("/")
        login_specs = [
            ("login.demo_notice", ".aviso-seguranca", None),
            ("login.demo_notice_strong", ".aviso-seguranca strong", None),
            ("login.footer", ".rodape-formulario", None),
            ("login.username_placeholder", "#usuario", "::placeholder"),
            ("login.password_placeholder", "#senha", "::placeholder"),
            ("login.instruction", ".instrucao", None),
            ("login.demo_credential_text", ".credenciais-demo p", None),
            ("login.demo_credential_code", ".credenciais-demo code", None),
            ("login.field_labels", ".campo label", None),
        ]
        measurements = self.measure_text_colors(login_specs)
        self.submit_login("admin", "papelaria2026")
        self.wait_for_path("/vendas/")
        panel_specs = [
            ("panel.chart_descriptions", ".descricao-grafico", None),
            ("panel.kpi_notes", ".indicador-nota", None),
            ("panel.kpi_labels", ".indicador-rotulo", None),
            ("panel.filter_summary", ".texto-auxiliar", None),
            ("panel.method_notes", ".nota-metodologica p", None),
            ("panel.footer", ".rodape", None),
            ("panel.search_placeholder", "#busca-venda", "::placeholder"),
            ("panel.filter_labels", ".campo label", None),
            ("panel.filter_select", "#filtro-cidade", None),
            ("panel.date_control", "#data-inicio", None),
            ("panel.clear_button", "#limpar-filtros", None),
            ("panel.export_button", "#exportar-csv", None),
            ("panel.print_button", "#imprimir-painel", None),
            ("panel.table_heading", "#tabela-vendas thead th", None),
            ("panel.table_cell", "#corpo-tabela tr:first-child td, #corpo-tabela tr:nth-child(2) td", None),
            ("panel.pagination_label", "#pagina-atual", None),
            ("panel.page_size", "#registros-por-pagina", None),
            ("panel.chart_axis", ".grafico-eixo", None),
            ("panel.chart_category_label", ".grafico-rotulo", None),
            ("panel.chart_value", ".grafico-valor", None),
        ]
        measurements.extend(self.measure_text_colors(panel_specs))
        self.set_control("busca-venda", "__sem_venda_correspondente__")
        self.assertFalse(self.js("return document.getElementById('mensagem-vazia').hidden"), "empty state precisa estar visível para medir seu texto")
        empty_specs = [
            ("panel.empty_state", ".mensagem-vazia", None),
            ("panel.empty_state_heading", ".mensagem-vazia strong", None),
            ("panel.empty_state_description", ".mensagem-vazia span:last-child", None),
        ]
        measurements.extend(self.measure_text_colors(empty_specs))

        all_specs = login_specs + panel_specs + empty_specs
        visible_labels = {str(item["label"]).split("[")[0] for item in measurements if item["visible"]}
        missing = sorted({label for label, _selector, _pseudo in all_specs} - visible_labels)
        visible_measurements = [item for item in measurements if item["visible"]]
        failures = []
        for item in visible_measurements:
            ratio = contrast_ratio(str(item["foreground"]), str(item["background"]))
            if ratio < 4.5:
                failures.append({
                    "alvo": item["label"], "foreground": item["foreground"],
                    "background": item["background"], "ratio": round(ratio, 3),
                })
        ratios = [contrast_ratio(str(item["foreground"]), str(item["background"])) for item in visible_measurements]
        print("WCAG AA Firefox computed samples: " + json.dumps({
            "count": len(ratios), "minimum": round(min(ratios), 3), "failures": failures,
        }, ensure_ascii=False))
        self.assertFalse(missing, "Alvos de contraste ausentes/ocultos: " + ", ".join(missing))
        self.assertFalse(failures, "Texto normal precisa de contraste WCAG AA >= 4.5:1; violações: " + json.dumps(failures, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main(verbosity=2)

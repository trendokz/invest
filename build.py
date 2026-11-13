"""Собирает index.html из template.html + data.json.
Запуск: python3 build.py
"""
import json, pathlib

here = pathlib.Path(__file__).parent
import os

def _load_env(path):
    # Минимальный парсер .env, чтобы не тянуть зависимости
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

_load_env(here / ".env")
DATA_DIR = pathlib.Path(os.environ.get("TRENDO_DATA_DIR", "./example"))
if not DATA_DIR.is_absolute():
    DATA_DIR = here / DATA_DIR
print("Данные из:", DATA_DIR)

def _src(name):
    p = DATA_DIR / name
    if not p.exists():
        raise SystemExit(f"Не найден {p}. Укажите TRENDO_DATA_DIR в .env (см. .env.example)")
    return p

data = json.loads(_src("data.json").read_text())

# Коды доступа лежат в private/codes.json
_codes = json.loads(_src("codes.json").read_text())
CODES, ADMIN = _codes["investors"], _codes["admin"]

html = (here / "cabinet" / "template.html").read_text()
html = (html.replace("/*DATA*/null", json.dumps(data, ensure_ascii=False))
            .replace("/*CODES*/null", json.dumps(CODES))
            .replace("/*ADMIN*/null", json.dumps(ADMIN)))
(here / "cabinet" / "index.html").write_text(html)
print("cabinet/index.html собран:", len(data["months"]), "мес.,", len(data["investors"]), "инвесторов")

# ---- Публичная страница для потенциальных инвесторов: только данные пула, без инвесторов и кодов
def between(s, a, b):
    i = s.index(a); j = s.index(b, i); return s[i:j]

tpl = (here / "cabinet" / "template.html").read_text()
style = between(tpl, "<style>", "</style>")[len("<style>"):]
helpers = "\n".join([
    between(tpl, "const LOGO", "const invById"),
    between(tpl, "const prevMonth", "function calcSteps"),
    between(tpl, "function niceStep", "\n") + "\n",
    between(tpl, "function poolBlock", "/* ---------- investor view"),
    between(tpl, "const RATE", "function calcView"),
    between(tpl, "function drawCalc", "window.addEventListener('hashchange'"),
])
pub_months = []
for m in data["months"]:
    pm = {k: m[k] for k in ("key", "label", "period", "orders", "returns", "periods", "pool", "expenses", "top")}
    pm["paidToInvestors"] = sum(r["dividend"] for r in m["investors"])
    pub_months.append(pm)
pub = (here / "calculator" / "template.html").read_text()
pub = (pub.replace("/*STYLE*/", style).replace("/*HELPERS*/", helpers)
          .replace("/*DATA*/null", json.dumps({"months": pub_months}, ensure_ascii=False)))
for bad in ["CODES", "ADMIN", "investors\":"] + [i["name"] for i in data["investors"]] + list(CODES.values()):
    assert bad not in pub, bad
(here / "calculator" / "index.html").write_text(pub)
print("calculator/index.html собран:", len(pub_months), "мес., без данных инвесторов")

# ---- dist/: только то, что выкладывается на хостинг (без private/, шаблонов и скриптов)
import shutil
dist = here / "dist"
shutil.rmtree(dist, ignore_errors=True)
(dist / "cabinet").mkdir(parents=True)
(dist / "calculator").mkdir(parents=True)
shutil.copy(here / "cabinet" / "index.html", dist / "cabinet" / "index.html")
shutil.copy(here / "calculator" / "index.html", dist / "calculator" / "index.html")
(dist / "index.html").write_text("""<!doctype html>
<meta charset="utf-8">
<title>Trendo Analytics</title>
<meta http-equiv="refresh" content="0; url=calculator/">
<link rel="canonical" href="calculator/">
<p>Переход на <a href="calculator/">страницу Trendo Analytics</a>…</p>
""")
(dist / "robots.txt").write_text("User-agent: *\nDisallow: /cabinet/\n")
print("dist/ готов: index.html, calculator/, cabinet/ — выкладывать на хостинг только эту папку")

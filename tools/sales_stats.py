"""Статистика продаж для публичной страницы: только агрегаты, без товаров.

Источник сейчас: лист «Сырые данные» в Excel-отчётах (TRENDO_DATA_DIR/reports/*.xlsx).
Позже его заменит сборщик заказов из Kaspi Merchant API с тем же форматом вывода.
Результат: TRENDO_DATA_DIR/sales.json

Запуск: python3 tools/sales_stats.py   (нужен openpyxl)
"""
import collections, datetime as dt, json, os, pathlib, sys

here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here))
from niches import niche  # noqa: E402

root = here.parent
for line in (root / ".env").read_text().splitlines() if (root / ".env").exists() else []:
    if "=" in line and not line.lstrip().startswith("#"):
        k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())
data_dir = pathlib.Path(os.environ.get("TRENDO_DATA_DIR", "./example"))
data_dir = data_dir if data_dir.is_absolute() else root / data_dir

import openpyxl  # noqa: E402

days = collections.defaultdict(lambda: {"orders": 0, "revenue": 0.0, "returns": 0.0})
niche_day = collections.defaultdict(float)   # (date, niche) -> revenue
for f in sorted((data_dir / "reports").glob("*.xlsx")):
    ws = openpyxl.load_workbook(f, read_only=True, data_only=True)["Сырые данные"]
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r[0] or not isinstance(r[4], dt.datetime):
            continue
        d, price = r[4].date(), float(r[3] or 0)
        if r[5] == "Покупка":
            days[d]["orders"] += 1
            days[d]["revenue"] += price
            niche_day[(d, niche(r[1]))] += price
        elif r[5] == "Возврат":
            days[d]["returns"] += -price

if not days:
    sys.exit("Нет данных о заказах")
last = max(days)
def total(a, b, key="revenue"):
    return sum(v[key] for d, v in days.items() if a <= d <= b)
def niches(a, b):
    c = collections.Counter()
    for (d, n), v in niche_day.items():
        if a <= d <= b:
            c[n] += v
    return c

D = datetime_delta = dt.timedelta
w0, w1 = last - D(days=6), last
p0, p1 = last - D(days=13), last - D(days=7)
m0 = last - D(days=29); pm0, pm1 = last - D(days=59), last - D(days=30)
cur, prev = niches(m0, last), niches(pm0, pm1)
S, SP = sum(cur.values()) or 1, sum(prev.values()) or 1
out = {
    "source": "Заказы Kaspi из ежемесячных отчётов",
    "asOf": last.isoformat(),
    "day": {"orders": days[last]["orders"], "revenue": round(days[last]["revenue"]),
            "prevOrders": days.get(last - D(days=1), {}).get("orders", 0),
            "prevRevenue": round(days.get(last - D(days=1), {}).get("revenue", 0))},
    "week": {"from": w0.isoformat(), "orders": total(w0, w1, "orders"), "revenue": round(total(w0, w1)),
             "prevOrders": total(p0, p1, "orders"), "prevRevenue": round(total(p0, p1))},
    "days30": {"from": m0.isoformat(), "orders": total(m0, last, "orders"), "revenue": round(total(m0, last)),
               "returns": round(total(m0, last, "returns")),
               "prevOrders": total(pm0, pm1, "orders"), "prevRevenue": round(total(pm0, pm1))},
    "daily": [{"d": d.isoformat(), "orders": days[d]["orders"], "revenue": round(days[d]["revenue"])}
              for d in sorted(days) if d > last - D(days=60)],
    "niches": [{"name": n, "revenue": round(v), "share": v / S, "prevShare": prev.get(n, 0) / SP}
               for n, v in cur.most_common()],
}
(data_dir / "sales.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(f"sales.json: по {last}, 30 дней {out['days30']['orders']} заказов, {out['days30']['revenue']:,} ₸, ниш {len(out['niches'])}")

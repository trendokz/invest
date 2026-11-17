"""Ниши товаров для публичной статистики. Порядок важен: первое совпадение побеждает."""
import re

NICHES = [
    ("Смарт-очки и гаджеты", r"смарт-очки|vision|glasses|translate|робот|tv box|magic|ir-mr|пульт"),
    ("Умные часы", r"смарт-час|smart ?watch|watch|gs-wear|y-13|colmi|smart k12|smart w16|smart fit|\bk12\b|\bw16\b|q15"),
    ("Аудио", r"наушник|ulanzi|speak|микрофон|audio-technica|колонк|m79|m47|yyk-|keiko k1\b|oudiobop|tdd|ttd-"),
    ("Климат", r"wind pro|fan pro|вентилятор|очиститель воздуха|увлажнител|pureair|air ?wash|multi air|air pro|air s1|air02|h2o|обогрев|k040|k60|\bk030\b|\bk15\b|879|pr-651"),
    ("Уход за одеждой и уборка", r"отпариват|пароочистител|пылесос|пылевого клеща|стиральн|швабр|sc-\d|hp-688|psp|steam|otp-|powerwash|shoewash|clean pro|sm-500|k4[0-9]\b|k43|k032|k046"),
    ("Фото и видео", r"lk-007|photo air|камер|фотокамер|cam\b"),
    ("Красота и здоровье", r"косметическ|расческ|hairbrush|массаж|лазерн|ролик"),
    ("Дом и кухня", r"гирлянд|соковыжималк|тестомес|aroma|вешалк|когтеточк|гамак|обои|зеркал|кресл|стул|столик|топпер|раскладушк|тарелк|кофеварк|миксер|xhb-01|льдогенератор|бутылк|сушилк|280280|don vassie|дозатор|лейка|haley|ylw|прожектор|лампоч"),
    ("3D-печать и электроника", r"bambu|дисплей|предохранител|liitokala|датчик|инструмент|набор|аккумулятор|зарядн"),
    ("Отдых и аксессуары", r"зонт|жилет|спасательн|портмоне|портфел|кварцев|curren|sunmood|спиннинг|dubery|ремень|сумк|predator|очки|raf r\.|механическ|чехол|рюкзак"),
]
_COMPILED = [(n, re.compile(p, re.I)) for n, p in NICHES]

def niche(name: str) -> str:
    s = str(name or "")
    for n, rx in _COMPILED:
        if rx.search(s):
            return n
    return "Другое"

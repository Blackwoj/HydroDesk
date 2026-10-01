"""Zmockowane dane makiety. Liczby spójne z przykładami z wymagań (sek. 4, 8, 9, 10)."""
from __future__ import annotations

import math
import random
from datetime import date, timedelta

TODAY = date(2026, 10, 1)

ROLES = {
    "client": "Użytkownik klienta",
    "hydrogeologist": "Hydrogeolog",
    "operator": "Operator",
    "admin": "Administrator",
}

USERS = {
    "client": {"name": "Anna Kowalska", "org": "Wodociągi Gminy Zielona Dolina"},
    "hydrogeologist": {"name": "dr Piotr Nowak", "org": "GEAQUA"},
    "operator": {"name": "Marta Wiśniewska", "org": "GEAQUA"},
    "admin": {"name": "Administrator", "org": "GEAQUA"},
}

STATUS = {
    "ok": {"label": "OK", "icon": "✓"},
    "watch": {"label": "Obserwacja", "icon": "◐"},
    "action": {"label": "Wymaga działania", "icon": "!"},
    "no_data": {"label": "Brak danych", "icon": "?"},
}

INTAKES = [
    {"id": 1, "name": "Ujęcie Zielona Dolina", "code": "UZD", "wells": ["S-1", "S-2", "S-3"], "status": "watch"},
    {"id": 2, "name": "Ujęcie Leśna Polana", "code": "ULP", "wells": ["L-1", "L-2"], "status": "ok"},
]

WELLS = {
    "S-1": {"code": "S-1", "intake": 1, "depth": 86.0, "status": "ok", "status_text": "OK",
            "last": {"date": date(2026, 9, 18), "static": 12.4, "dynamic": 17.1, "yield": 42.0}},
    "S-2": {"code": "S-2", "intake": 1, "depth": 92.5, "status": "watch", "status_text": "obserwowany spadek wydajności",
            "last": {"date": date(2026, 7, 2), "static": 13.1, "dynamic": 21.8, "yield": 33.5}},
    "S-3": {"code": "S-3", "intake": 1, "depth": 78.0, "status": "no_data", "status_text": "brak aktualnego pomiaru",
            "last": {"date": date(2026, 3, 11), "static": 11.9, "dynamic": 16.2, "yield": 38.0}},
}
for w in WELLS.values():
    last = w["last"]
    last["drawdown"] = round(last["dynamic"] - last["static"], 2)
    last["specific"] = round(last["yield"] / last["drawdown"], 2)

# Parametry: (kod, nazwa, jednostka, limit, ostatnia wartość, qualifier, grupa)
PARAMETERS = [
    ("Mn", "Mangan", "mg/l", 0.05, 0.043, "", "fizykochemiczne"),
    ("Fe", "Żelazo", "mg/l", 0.2, 0.08, "", "fizykochemiczne"),
    ("NO3", "Azotany", "mg/l", 50, 6.2, "", "fizykochemiczne"),
    ("NO2", "Azotyny", "mg/l", 0.5, 0.01, "<", "fizykochemiczne"),
    ("NH4", "Amonowy jon", "mg/l", 0.5, 0.05, "<", "fizykochemiczne"),
    ("pH", "Odczyn pH", "", 9.5, 7.4, "", "fizykochemiczne"),
    ("EC", "Przewodność", "µS/cm", 2500, 612, "", "fizykochemiczne"),
    ("Cl", "Chlorki", "mg/l", 250, 18.4, "", "fizykochemiczne"),
    ("SO4", "Siarczany", "mg/l", 250, 41.0, "", "fizykochemiczne"),
    ("F", "Fluorki", "mg/l", 1.5, 0.21, "", "fizykochemiczne"),
    ("As", "Arsen", "µg/l", 10, 1.0, "<", "fizykochemiczne"),
    ("Pb", "Ołów", "µg/l", 10, 1.0, "<", "fizykochemiczne"),
    ("Cd", "Kadm", "µg/l", 5, 0.5, "<", "fizykochemiczne"),
    ("Hg", "Rtęć", "µg/l", 1, 0.1, "<", "fizykochemiczne"),
    ("Cr", "Chrom", "µg/l", 25, 2.0, "<", "fizykochemiczne"),
    ("Ni", "Nikiel", "µg/l", 20, 2.0, "<", "fizykochemiczne"),
    ("Cu", "Miedź", "mg/l", 2.0, 0.02, "", "fizykochemiczne"),
    ("B", "Bor", "mg/l", 1.5, 0.05, "<", "fizykochemiczne"),
    ("Na", "Sód", "mg/l", 200, 14.2, "", "fizykochemiczne"),
    ("TWO", "Twardość ogólna", "mg CaCO₃/l", 500, 248, "", "fizykochemiczne"),
    ("UTL", "Utlenialność", "mg O₂/l", 5, 1.3, "", "fizykochemiczne"),
    ("MET", "Mętność", "NTU", 1, 0.3, "", "fizykochemiczne"),
    ("ECOLI", "Escherichia coli", "jtk/100 ml", 0, 0, "", "mikrobiologiczne"),
    ("ENT", "Enterokoki", "jtk/100 ml", 0, 0, "", "mikrobiologiczne"),
    ("BGK", "Bakterie grupy coli", "jtk/100 ml", 0, 0, "", "mikrobiologiczne"),
]


def assess(limit: float, value: float, qualifier: str) -> str:
    if qualifier == "<":
        return "ok"
    if limit == 0:
        return "action" if value > 0 else "ok"
    ratio = value / limit
    if ratio > 1:
        return "action"
    if ratio >= 0.8:
        return "watch"
    return "ok"


def parameters() -> list[dict]:
    rows = []
    for code, name, unit, limit, value, q, group in PARAMETERS:
        status = assess(limit, value, q)
        pct = None if q == "<" or limit == 0 else round(value / limit * 100)
        raw = f"{q}{value}".replace(".", ",")
        rows.append({
            "code": code, "name": name, "unit": unit, "limit": str(limit).replace(".", ","),
            "raw": raw, "pct": pct, "status": status, "group": group,
            "trend": "up" if code == "Mn" else "flat",
        })
    return rows


def quality_summary() -> dict:
    rows = parameters()
    return {
        "ok": sum(r["status"] == "ok" for r in rows),
        "watch": sum(r["status"] == "watch" for r in rows),
        "action": sum(r["status"] == "action" for r in rows),
        "total": len(rows),
        "last_sample": date(2026, 9, 9),
        "lab": "Laboratorium Wody AQUA-LAB Sp. z o.o.",
    }


def manganese_series() -> dict:
    """Seria Mn z trendem wzrostowym do 86% progu."""
    rnd = random.Random(7)
    labels, values = [], []
    d = date(2024, 3, 1)
    for i in range(10):
        labels.append(d.strftime("%m.%Y"))
        values.append(round(0.021 + i * 0.0024 + rnd.uniform(-0.002, 0.002), 4))
        d += timedelta(days=91)
    values[-1] = 0.043
    labels[-1] = "09.2026"
    return {"labels": labels, "values": values, "limit": 0.05, "unit": "mg/l", "name": "Mangan"}


def parameter_series(code: str) -> dict:
    if code == "Mn":
        return manganese_series()
    p = next(p for p in PARAMETERS if p[0] == code)
    rnd = random.Random(code)
    labels, values = [], []
    d = date(2024, 3, 1)
    for _ in range(10):
        labels.append(d.strftime("%m.%Y"))
        values.append(round(p[4] * rnd.uniform(0.85, 1.15), 4))
        d += timedelta(days=91)
    return {"labels": labels, "values": values, "limit": p[3], "unit": p[2], "name": p[1]}


def well_series(code: str) -> dict:
    """Seria pomiarów studni — dla S-2 spadek wydajności i wzrost depresji."""
    rnd = random.Random(code)
    labels, static, dynamic, yld = [], [], [], []
    d = date(2024, 1, 15)
    declining = code == "S-2"
    for i in range(12):
        labels.append(d.strftime("%m.%Y"))
        s = 12.6 + 0.4 * math.sin(i / 2) + rnd.uniform(-0.15, 0.15)
        y = (41 - i * 0.7 if declining else 42) + rnd.uniform(-0.8, 0.8)
        dd = (5.2 + i * 0.32 if declining else 4.8) + rnd.uniform(-0.2, 0.2)
        static.append(round(s, 2))
        dynamic.append(round(s + dd, 2))
        yld.append(round(y, 1))
        d += timedelta(days=55)
    drawdown = [round(b - a, 2) for a, b in zip(static, dynamic)]
    specific = [round(y / dd, 2) for y, dd in zip(yld, drawdown)]
    return {"labels": labels, "static": static, "dynamic": dynamic, "yield": yld,
            "drawdown": drawdown, "specific": specific}


def well_history(code: str) -> list[dict]:
    s = well_series(code)
    rows = []
    for i in range(len(s["labels"]) - 1, max(len(s["labels"]) - 7, -1), -1):
        rows.append({"date": s["labels"][i], "static": s["static"][i], "dynamic": s["dynamic"][i],
                     "yield": s["yield"][i], "drawdown": s["drawdown"][i], "specific": s["specific"][i],
                     "source": "ręcznie" if i % 3 else "import XLSX"})
    return rows


# Pobór — zgodnie z przykładem dashboardu: 68% wykorzystania, prognoza 91%
ANNUAL_LIMIT = 365_000


def abstraction() -> dict:
    monthly = [27_100, 25_300, 27_900, 27_200, 28_400, 29_100, 29_800, 28_300, 25_300]
    used = sum(monthly)
    elapsed = (TODAY - date(2026, 1, 1)).days
    forecast = round(used / elapsed * 365)
    months = ["sty", "lut", "mar", "kwi", "maj", "cze", "lip", "sie", "wrz", "paź", "lis", "gru"]
    cumulative, acc = [], 0
    for m in monthly:
        acc += m
        cumulative.append(acc)
    forecast_line = [None] * (len(monthly) - 1) + [cumulative[-1]]
    per_month = forecast / 12
    for i in range(len(monthly), 12):
        forecast_line.append(round(cumulative[-1] + per_month * (i - len(monthly) + 1)))
    return {
        "used": used, "limit": ANNUAL_LIMIT, "pct": round(used / ANNUAL_LIMIT * 100),
        "forecast": forecast, "forecast_pct": round(forecast / ANNUAL_LIMIT * 100),
        "months": months, "monthly": monthly, "cumulative": cumulative, "forecast_line": forecast_line,
        "limits": [
            {"name": "Limit roczny", "code": "Qrok", "value": "365 000 m³/rok", "used": f"{used:,} m³".replace(",", " "),
             "pct": round(used / ANNUAL_LIMIT * 100), "status": "ok"},
            {"name": "Maks. dobowy", "code": "Qmax,d", "value": "1 400 m³/d", "used": "1 182 m³ (14.08.2026)",
             "pct": 84, "status": "watch"},
            {"name": "Średni dobowy", "code": "Qśr,d", "value": "1 000 m³/d", "used": "909 m³/d", "pct": 91, "status": "watch"},
            {"name": "Maks. godzinowy", "code": "Qmax,h", "value": "70 m³/h", "used": "brak danych godzinowych",
             "pct": None, "status": "no_data"},
        ],
    }


PERMIT = {
    "number": "WR.RUZ.421.118.2017",
    "authority": "Dyrektor Zarządu Zlewni PGW Wody Polskie w Krakowie",
    "issued": date(2017, 3, 14),
    "valid_from": date(2017, 4, 1),
    "valid_to": date(2027, 3, 31),
    "months_left": 6,
    "scope": "Ujęcie Zielona Dolina — studnie S-1, S-2, S-3",
}

OBLIGATIONS = [
    {"name": "Pomiar zwierciadła — S-2", "freq": "raz na kwartał", "due": date(2026, 10, 13), "days": 12,
     "status": "watch", "action": "Dodaj pomiar", "url": "measurement_add", "well": "S-2"},
    {"name": "Badanie jakości wody surowej", "freq": "raz na pół roku", "due": date(2026, 11, 30), "days": 60,
     "status": "ok", "action": "Dodaj analizę", "url": "analysis_add", "well": ""},
    {"name": "Pomiar zwierciadła — S-3", "freq": "raz na kwartał", "due": date(2026, 9, 30), "days": -1,
     "status": "action", "action": "Dodaj pomiar", "url": "measurement_add", "well": "S-3"},
    {"name": "Odczyt wodomierza — ujęcie", "freq": "co miesiąc", "due": date(2026, 10, 31), "days": 30,
     "status": "ok", "action": "Dodaj pobór", "url": "abstraction_add", "well": ""},
    {"name": "Przekazanie wyników do organu", "freq": "raz w roku", "due": date(2027, 1, 31), "days": 122,
     "status": "ok", "action": "Dodaj dokument", "url": "document_add", "well": ""},
]

ALERTS = [
    {"id": 1, "severity": "action", "category": "Obowiązki", "title": "Po terminie: pomiar zwierciadła S-3",
     "message": "Termin pomiaru minął 30.09.2026. Ostatni pomiar S-3 wykonano 11.03.2026.",
     "next": "Wykonaj pomiar zwierciadła S-3 i dodaj go do systemu.", "action": "Dodaj pomiar",
     "url": "measurement_add", "well": "S-3", "since": date(2026, 10, 1), "consult": False},
    {"id": 2, "severity": "watch", "category": "Jakość", "title": "Mangan wykazuje trend wzrostowy",
     "message": "Aktualna wartość (0,043 mg/l) odpowiada 86% przyjętej wartości granicznej (0,05 mg/l). Wzrost obserwowany w 6 kolejnych badaniach.",
     "next": "Obserwuj kolejne wyniki. Jeśli wartość dalej rośnie, skonsultuj się z hydrogeologiem.",
     "action": "Zobacz wykres", "url": "parameter", "param": "Mn", "since": date(2026, 9, 12), "consult": True},
    {"id": 3, "severity": "watch", "category": "Studnia", "title": "S-2: obserwowany spadek wydajności",
     "message": "Wydajność jednostkowa S-2 spadła o 18% względem mediany z ostatnich 12 miesięcy (2 kolejne pomiary).",
     "next": "Zaplanuj kolejny pomiar. W razie wątpliwości skonsultuj się z hydrogeologiem.",
     "action": "Karta studni", "url": "well", "well": "S-2", "since": date(2026, 7, 3), "consult": True},
    {"id": 4, "severity": "watch", "category": "Pobór", "title": "Średni pobór dobowy: 91% limitu",
     "message": "Średni pobór dobowy od początku roku wynosi 909 m³/d przy limicie 1 000 m³/d.",
     "next": "Sprawdź harmonogram poboru w najbliższych miesiącach.", "action": "Zestawienie poboru",
     "url": "abstraction", "since": date(2026, 9, 1), "consult": True},
    {"id": 5, "severity": "info", "category": "Pozwolenia", "title": "Pozwolenie wodnoprawne wygasa za 6 miesięcy",
     "message": "Pozwolenie WR.RUZ.421.118.2017 jest ważne do 31.03.2027.",
     "next": "Rozpocznij przygotowanie wniosku o nowe pozwolenie.", "action": "Szczegóły pozwolenia",
     "url": "permit", "since": date(2026, 9, 30), "consult": True},
]

REPORTS = [
    {"name": "Raport miesięczny — wrzesień 2026", "kind": "automatyczny", "date": date(2026, 10, 1), "status": "ready"},
    {"name": "Raport miesięczny — sierpień 2026", "kind": "automatyczny", "date": date(2026, 9, 1), "status": "ready"},
    {"name": "Ocena stanu ujęcia — I półrocze 2026", "kind": "ekspercki", "date": date(2026, 7, 20), "status": "approved"},
    {"name": "Raport miesięczny — lipiec 2026", "kind": "automatyczny", "date": date(2026, 8, 1), "status": "ready"},
]

CONSULTATIONS = [
    {"id": 1, "client": "Wodociągi Gminy Zielona Dolina", "intake": "Ujęcie Zielona Dolina", "subject": "Mangan wykazuje trend wzrostowy",
     "message": "Czy powinniśmy coś zmienić w pracy stacji uzdatniania? Mangan rośnie od roku.", "date": date(2026, 9, 29), "status": "new"},
    {"id": 2, "client": "PWiK Brzozów", "intake": "Ujęcie Brzozów Północ", "subject": "S-4: wzrost depresji",
     "message": "Pompa pracuje dłużej niż zwykle, depresja wyższa o ok. 1 m.", "date": date(2026, 9, 24), "status": "in_progress"},
]

STAFF_QUEUE = {
    "alerts": [
        {"client": "PWiK Brzozów", "intake": "Brzozów Północ", "title": "Azotany: przekroczenie wartości granicznej (54 mg/l)", "severity": "action"},
        {"client": "Wodociągi Gminy Zielona Dolina", "intake": "Zielona Dolina", "title": "Po terminie: pomiar zwierciadła S-3", "severity": "action"},
        {"client": "ZGK Lipnica", "intake": "Lipnica", "title": "Prognozowane przekroczenie limitu rocznego (109%)", "severity": "action"},
    ],
    "to_review": [
        {"client": "Wodociągi Gminy Zielona Dolina", "what": "Analiza wody z 09.09.2026 (25 parametrów)", "who": "Anna Kowalska", "date": date(2026, 9, 12)},
        {"client": "ZGK Lipnica", "what": "Import XLSX — 3 próbki", "who": "Marta Wiśniewska", "date": date(2026, 9, 30)},
    ],
    "abstraction_risk": [
        {"client": "ZGK Lipnica", "intake": "Lipnica", "forecast": 109},
        {"client": "Wodociągi Gminy Zielona Dolina", "intake": "Zielona Dolina", "forecast": 91},
    ],
    "wells": [
        {"client": "Wodociągi Gminy Zielona Dolina", "well": "S-2", "issue": "spadek wydajności jednostkowej o 18%"},
        {"client": "PWiK Brzozów", "well": "S-4", "issue": "wzrost depresji o 22%"},
    ],
    "permits": [
        {"client": "Wodociągi Gminy Zielona Dolina", "intake": "Zielona Dolina", "valid_to": date(2027, 3, 31), "months": 6},
        {"client": "PWiK Brzozów", "intake": "Brzozów Południe", "valid_to": date(2026, 12, 31), "months": 3},
    ],
    "overdue": [
        {"client": "Wodociągi Gminy Zielona Dolina", "what": "Pomiar zwierciadła S-3", "days": 1},
        {"client": "ZGK Lipnica", "what": "Badanie jakości wody surowej", "days": 14},
    ],
    "missing": [
        {"client": "ZGK Lipnica", "what": "Brak poboru za sierpień i wrzesień"},
        {"client": "PWiK Brzozów", "what": "Brak pomiaru S-5 od 7 miesięcy"},
    ],
}

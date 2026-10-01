# 01 — Plan PoC

## 1. Cel PoC

Udowodnić, że na stosie **Django + PostgreSQL/PostGIS + Django Templates/HTMX** da się zrealizować pełną ścieżkę z sekcji 21 wymagań („Minimalne kryterium odbioru v1”) dla jednego pilotażowego klienta, z zachowaniem:

- izolacji danych klientów od pierwszej migracji,
- audytu zmian,
- reguł generujących alerty bez duplikatów,
- prostego, mobilnego UI dla klienta.

PoC **nie** jest wersją produkcyjną — ale fundamenty (model danych, tenancy, audyt, uprawnienia) budujemy docelowo, żeby nie przepisywać ich później.

## 2. Zakres

### W zakresie PoC

| Obszar | Zakres PoC |
|--------|-----------|
| Konta i role | logowanie, 4 role (admin, hydrogeolog, operator, użytkownik klienta), przypisanie hydrogeologa do klientów |
| Struktura | Klient → Ujęcie → Studnia (z lokalizacją PostGIS) |
| Jakość wody | wprowadzanie ręczne + import CSV/XLSX, zachowanie pliku źródłowego, wartość źródłowa vs znormalizowana, progi wersjonowane, wykres, prosty trend |
| Studnie | pomiary zwierciadła/wydajności, obliczenie depresji i wydajności jednostkowej, wykresy |
| Pobór | dane dobowe/miesięczne/roczne, porównanie z limitami pozwolenia, prognoza liniowa |
| Pozwolenia | rejestr pozwoleń, limity, przypomnienia o końcu ważności |
| Obowiązki | cykliczne obowiązki z pozwolenia, auto-zamknięcie po dodaniu pomiaru |
| Alerty | silnik reguł, deduplikacja, statusy OK / Obserwacja / Wymaga działania / Brak danych |
| Konsultacje | zgłoszenie z alertu, widok na dashboardzie hydrogeologa |
| Dashboardy | dashboard klienta i hydrogeologa |
| Raporty | automatyczny raport PDF (miesięczny / na żądanie) |
| Audyt | rejestr operacji + historia zmian wartości |
| Backup | skrypt backup/restore bazy i bucketu dokumentów |

### Poza zakresem PoC (ale architektura nie blokuje)

- OCR/AI dla PDF/skanów (w PoC: interfejs + stub; patrz [04-moduly.md](04-moduly.md#documents)),
- ODS (łatwe do dodania przez `pandas`/`odfpy`),
- raport ekspercki z workflow zatwierdzania (w PoC: model danych + prosty status),
- dedykowany UI konfiguracji słowników (w PoC: fixtures + Django Admin),
- wszystko z sekcji 20 wymagań.

## 3. Etapy

Każdy etap kończy się działającym przyrostem (demo). Szacunki dla 1–2 deweloperów.

### Etap 0 — Szkielet projektu (≈ 2–3 dni)

- repozytorium, `pyproject.toml` (uv), ruff, mypy, pytest, pre-commit,
- Docker Compose: `app`, `worker`, `beat`, `db` (postgis/postgis:16), `redis`, `minio`, `mailpit`,
- projekt Django (`config/`, settings dev/prod/test), `django-environ`, logowanie strukturalne,
- własny model `User` (logowanie e-mailem) **przed** pierwszą migracją,
- pierwsza migracja: rozszerzenia `postgis`, `pgcrypto`, `citext`, role DB,
- bazowy layout Django Templates + HTMX + CSS (Pico.css lub Tailwind CLI),
- CI (GitHub Actions): lint, typy, testy z Postgresem w kontenerze.

### Etap 1 — Fundamenty: konta, tenancy, audyt (≈ 4 dni)

- modele `organization`, `user`, `membership`, `staff_assignment`,
- logowanie z `django.contrib.auth` (sesje, CSRF, reset hasła wbudowane), Argon2, `django-axes`,
- role jako grupy Django + uprawnienia; mixiny/dekoratory widoków,
- **RLS w Postgresie** + `TenantMiddleware` (`transaction.atomic()` + `SET LOCAL app.org_ids`),
- audyt: `django-simple-history` (historia pól) + `AuditLog` (zdarzenia biznesowe),
- Django Admin dla admina systemu (klienci, użytkownicy, słowniki),
- testy izolacji: użytkownik klienta A nie widzi danych B (na poziomie API **i** SQL).

Kryteria odbioru: **1, 3** (częściowo), **19** (fundament).

### Etap 2 — Struktura obiektów i dokumenty (≈ 4 dni)

- CRUD: ujęcia, studnie (GeoDjango `PointField`, EPSG:2180),
- moduł dokumentów: upload do MinIO (`django-storages`), wersjonowanie, SHA-256, pobieranie przez autoryzowany endpoint,
- soft-delete + potwierdzenia usuwania w UI,
- widok QGIS: osobna rola DB tylko do odczytu, widoki `gis.*`.

Kryteria odbioru: **2, 3**.

### Etap 3 — Dane pomiarowe (≈ 2 tyg.)

- **Jakość wody:** słownik parametrów i jednostek, próbki, wyniki (operator `<`/`>`, wartość źródłowa i znormalizowana), import CSV/XLSX z mapowaniem kolumn i podglądem, wersjonowane zestawy wartości odniesienia,
- **Studnie:** pomiary, wyliczenie depresji i wydajności jednostkowej,
- **Pobór:** rekordy okresowe dla studni / ujęcia,
- wykresy (Chart.js w UI, matplotlib do PDF),
- statusy danych: `draft` → `submitted` → `approved`; zmiana zatwierdzonych = nowa rewizja.

Kryteria odbioru: **4, 5, 7, 8, 9**.

### Etap 4 — Pozwolenia i obowiązki (≈ 1 tydz.)

- rejestr pozwoleń: limity (Qmax,h, Qmax,d, Qśr,d, roczny, własne), zakres (ujęcie/studnie),
- obowiązki cykliczne: częstotliwość, kolejny termin, sposób potwierdzenia,
- automatyczne zaliczenie obowiązku po dodaniu pasującego pomiaru/analizy/dokumentu i wyliczenie następnego terminu,
- porównanie poboru z limitem + prognoza liniowa.

Kryteria odbioru: **10, 11, 12, 13**.

### Etap 5 — Silnik reguł i alerty (≈ 1,5 tyg.)

- rejestr reguł (kod Pythona + konfiguracja progów w DB),
- ewaluacja: na zdarzenie (po zapisie danych) + cyklicznie (Celery beat, codziennie),
- deduplikacja (`dedup_key` + częściowy indeks unikalny),
- cykl życia alertu: `open` → `acknowledged` → `resolved` / `auto_resolved`,
- komunikaty po polsku z „co zrobić dalej” i linkiem do akcji,
- powiadomienia e-mail (Mailpit lokalnie).

Kryteria odbioru: **6, 14, 15**.

### Etap 6 — Dashboardy i konsultacje (≈ 1 tydz.)

- dashboard klienta: 5 kafli (jakość, pobór, studnie, pozwolenie, obowiązki) + przyciski akcji,
- dashboard hydrogeologa: kolejka wyjątków (alerty wysokiego priorytetu, konsultacje, analizy do kontroli, braki danych),
- konsultacje: zgłoszenie z alertu, wątek wiadomości, statusy.

Kryteria odbioru: **15, 16, 17**.

### Etap 7 — Raporty (≈ 1 tydz.)

- szablon raportu automatycznego (HTML → PDF, WeasyPrint),
- generowanie w Celery, zapis jako dokument (wersjonowany, audytowany),
- harmonogram miesięczny + generowanie na żądanie,
- model raportu eksperckiego (status `draft` / `approved`, zatwierdza hydrogeolog).

Kryteria odbioru: **18**.

### Etap 8 — Utwardzenie i pilotaż (≈ 1 tydz.)

- backup: `pg_dump` + `mc mirror` bucketu, test odtworzenia (skrypt + instrukcja),
- HTTPS (Caddy jako reverse proxy z automatycznym certyfikatem),
- seed danych demonstracyjnych, scenariusz demo wszystkich 20 kryteriów,
- testy E2E (Playwright) dla ścieżki klienta na mobile viewport.

Kryteria odbioru: **19, 20** + przegląd całości.

**Łącznie:** ≈ 9 tygodni dla 1 osoby, ≈ 5–6 tygodni dla 2 osób.

## 4. Mapowanie kryteriów odbioru v1

| # | Kryterium | Etap | Moduł |
|---|-----------|------|-------|
| 1 | utworzyć klienta i użytkownika klienta | 1 | `accounts`, `organizations` |
| 2 | utworzyć ujęcie i ≥ 2 studnie | 2 | `assets` |
| 3 | klient widzi wyłącznie własne dane | 1–2 | `core.tenancy` + RLS |
| 4 | dodać analizę wody | 3 | `water_quality` |
| 5 | wyniki i wykres historyczny | 3 | `water_quality` |
| 6 | wykryć przekroczenie / zbliżenie do progu | 5 | `rules`, `alerts` |
| 7 | dodać pomiar zwierciadła i wydajności | 3 | `wells` |
| 8 | historia pomiarów | 3 | `wells` |
| 9 | wprowadzić pobór | 3 | `abstraction` |
| 10 | porównać pobór z pozwoleniem | 4 | `abstraction`, `permits` |
| 11 | prognoza wykorzystania limitu | 4 | `abstraction` |
| 12 | zapisać pozwolenie | 4 | `permits` |
| 13 | cykliczny obowiązek z pozwolenia | 4 | `obligations` |
| 14 | alert o zbliżającym się terminie | 5 | `rules`, `alerts` |
| 15 | alert widoczny dla klienta | 5–6 | `alerts`, `dashboard` |
| 16 | zgłoszenie konsultacji | 6 | `consultations` |
| 17 | konsultacja na dashboardzie hydrogeologa | 6 | `dashboard` |
| 18 | automatyczny raport PDF | 7 | `reports` |
| 19 | historia najważniejszych zmian | 1, 8 | `core.audit` |
| 20 | odtworzenie bazy i dokumentu z backupu | 8 | infra |

## 5. Ryzyka

| Ryzyko | Wpływ | Mitygacja |
|--------|-------|-----------|
| RLS nie jest wzorcem standardowym w Django | wycieki przy błędnym kontekście, niespodzianki w migracjach | `TenantMiddleware` + `TenantTask`, testy izolacji w CI od Etapu 1, ADR-0003 |
| RLS komplikuje testy i migracje | błędy uprawnień, wolniejszy development | wspólny helper sesji, testy izolacji w CI od Etapu 1 |
| Niejednorodne pliki z laboratoriów | import zawodzi | import z mapowaniem kolumn + ręczna korekta, OCR dopiero po PoC |
| Normalizacja jednostek i operatorów `<`/`>` | błędne alerty | słownik jednostek z przelicznikami, testy jednostkowe reguł na przypadkach granicznych |
| Zbyt dużo alertów („alert fatigue”) | klient ignoruje system | deduplikacja, priorytety, auto-resolve, przegląd reguł z hydrogeologiem |
| Zakres rośnie w trakcie PoC | opóźnienie | lista „poza zakresem” w tym dokumencie, kryteria odbioru jako kontrakt |

## 6. Otwarte pytania do ustalenia

1. Hosting docelowy (VPS / chmura PL / on-premise klienta)? Wpływa na S3 vs dysk lokalny i backup.
2. Czy hydrogeolog widzi wszystkich klientów, czy tylko przypisanych? (spec: „przypisanych” — przyjmujemy `staff_assignment`).
3. Źródło wartości odniesienia — Rozporządzenie MZ w sprawie jakości wody przeznaczonej do spożycia? Kto utrzymuje wersje?
4. Czy pobór może być wprowadzany jako stany wodomierza (odczyty narastające), czy tylko jako objętość za okres?
5. Logowanie: tylko e-mail + hasło, czy także magic link / 2FA dla personelu?
6. Czy OCR/AI ma być w PoC (np. Claude API — odczyt PDF z laboratorium), czy dopiero w v1?

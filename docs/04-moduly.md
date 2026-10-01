# 04 — Moduły domenowe

Każdy moduł to aplikacja Django: `models.py`, `admin.py`, `forms.py`, `services.py`, `selectors.py`, `views.py` (HTML/HTMX), `api.py` (Ninja, JSON), `templates/`. Pełna struktura: [07-struktura-repo.md](07-struktura-repo.md).
Prefiks `/api/...` = JSON, bez prefiksu = strony HTML. Uprawnienia w kolumnie „Uprawnienie” (mapowane na uprawnienia Django).

---

## core

Wspólna infrastruktura, bez logiki domenowej.

| Pakiet | Odpowiedzialność |
|--------|------------------|
| `config.settings` | ustawienia Django (`django-environ`, zmienne środowiskowe) |
| `core.tenancy` | `RequestContext` (user, role, org_ids) w `request.ctx`; `TenantMiddleware` — `transaction.atomic()` + `SET LOCAL` kontekstu RLS |
| `core.models` / `core.managers` | abstrakcyjne modele (`TenantModel`, `TimestampedModel`, `SoftDeleteModel`), `TenantQuerySet.for_ctx(ctx)` |
| `core.permissions` | mapowanie ról na grupy i uprawnienia Django, `PermissionRequiredMixin` / dekoratory |
| `core.audit` | `AuditLog` + `audit.record(ctx, action, entity, before, after)`; historia pól przez `django-simple-history` |
| `core.events` | zdarzenia domenowe, outbox, `transaction.on_commit` → Celery |
| `core.storage` | `django-storages` S3/MinIO; klucze `org/<org_id>/docs/<doc_id>/<ver>` |
| `core.templatetags` | komponenty (kafel statusu, badge, modal potwierdzenia), formatowanie dat i liczb po polsku |
| `core.tasks` | `TenantTask` — bazowe zadanie Celery z kontekstem RLS |

---

## accounts

Użytkownicy, logowanie, role.

- własny model `User` (e-mail jako login), `system_role`,
- logowanie, wylogowanie, reset hasła — widoki `django.contrib.auth` z własnymi szablonami,
- zaproszenie użytkownika klienta przez admina/hydrogeologa (e-mail z linkiem ustawienia hasła — mechanizm tokenów z resetu hasła),
- blokada po N nieudanych próbach (`django-axes`).

| Endpoint | Opis | Uprawnienie |
|----------|------|-------------|
| `GET/POST /login` | logowanie | publiczne |
| `POST /logout` | wylogowanie | zalogowany |
| `GET/POST /password/reset` | reset | publiczne |
| `/admin/accounts/user/` | zarządzanie użytkownikami (Django Admin) | `user:manage` |

---

## organizations

Klienci (organizacje), członkostwa, przypisania personelu.

| Endpoint | Opis | Uprawnienie |
|----------|------|-------------|
| `GET /clients` | lista klientów (personel) | `org:list` |
| `POST /clients` | utworzenie klienta | `org:manage` |
| `POST /clients/{id}/members` | dodanie użytkownika klienta | `org:manage` |
| `POST /clients/{id}/staff` | przypisanie hydrogeologa/operatora | `org:manage` |

---

## assets

Ujęcia i studnie (hierarchia Klient → Ujęcie → Studnia).

- CRUD ujęć i studni, lokalizacja (mapa Leaflet do wskazania punktu lub wpis współrzędnych),
- karta studni: dane, ostatnie pomiary, status, obowiązki, alerty, dokumenty.

| Endpoint | Opis | Uprawnienie |
|----------|------|-------------|
| `GET /intakes`, `GET /intakes/{id}` | lista / karta ujęcia | `intake:read` |
| `POST /intakes` | nowe ujęcie | `intake:write` |
| `GET /wells/{id}` | karta studni | `well:read` |
| `POST /intakes/{id}/wells` | nowa studnia | `well:write` |

---

## documents

Dokumenty źródłowe, wersjonowanie, pobieranie, ekstrakcja danych.

- upload (PDF, JPG/PNG, CSV, XLSX, ODS) — także z telefonu (`<input type=file accept="image/*" capture>`),
- każdy upload liczy SHA-256, zapisuje plik do S3, tworzy `document_version`,
- pobieranie wyłącznie przez `GET /documents/{id}/download` — sprawdzenie uprawnień, strumieniowanie z S3, `Content-Disposition: attachment`,
- powiązanie dokumentu z ujęciem/studnią/pozwoleniem/próbką.

**Ekstrakcja** (`documents.extractors`):

```python
class Extractor(Protocol):
    supported_mime: set[str]
    def extract(self, file: BinaryIO) -> ExtractionResult: ...
```

| Implementacja | PoC | Opis |
|---------------|-----|------|
| `TabularExtractor` | tak | CSV/XLSX/ODS → wiersze, mapowanie kolumn (zapamiętywane per laboratorium) |
| `OcrExtractor` | stub | PDF/obraz → propozycja wyników (np. Claude API vision / Tesseract) |

Wynik ekstrakcji to zawsze **propozycja** (`draft`) do przejrzenia i zatwierdzenia przez człowieka (FR-WQ-02: OCR pomocniczy).

---

## dictionaries

Słowniki i wartości referencyjne (zarządza admin w Django Admin, sek. 3.1).

- parametry jakości wody (kod, nazwa PL, grupa, jednostka domyślna, aliasy do importu np. „Mangan”, „Mn”, „mangan ogólny”),
- jednostki z przelicznikami (`mg/l` ↔ `µg/l`),
- zestawy wartości odniesienia (wersjonowane, z podstawą prawną),
- laboratoria, typy dokumentów, typy obowiązków.

Seed startowy: parametry i progi z rozporządzenia MZ dot. wody do spożycia (do potwierdzenia — patrz otwarte pytania w planie).

---

## water_quality

Analizy jakości wody (FR-WQ-01…07).

- **dodanie analizy**: formularz (data, punkt poboru, laboratorium, lista parametrów z wartościami) lub import pliku,
- **parser wartości**: `"<0,05"` → `qualifier="<"`, `value=Decimal("0.05")`; obsługa przecinka, spacji, `n.w.`, `ND`,
- **normalizacja jednostek** do jednostki bazowej parametru,
- **seria czasowa** parametru dla punktu poboru,
- **ocena wyniku** względem obowiązującego progu: `ok` / `near_limit` / `exceeded`,
- **trend**: regresja liniowa (lub Theil–Sen) na ostatnich N ≥ 4 wynikach; nachylenie istotne, gdy prognozowana zmiana w 12 mies. > X% progu; komunikat opisowy bez diagnozy,
- workflow: klient dodaje → `submitted`; hydrogeolog/operator kontroluje → `approved`.

| Endpoint | Opis | Uprawnienie |
|----------|------|-------------|
| `GET /intakes/{id}/water-quality` | tabela ostatnich wyników + statusy | `wq:read` |
| `GET/POST /water-quality/samples/new` | formularz analizy | `wq:write` |
| `POST /water-quality/imports` | upload pliku → podgląd mapowania | `wq:write` |
| `POST /water-quality/imports/{id}/confirm` | zatwierdzenie importu | `wq:write` |
| `GET /api/water-quality/series?point=&parameter=` | seria + progi (wykres) | `wq:read` |
| `POST /water-quality/samples/{id}/approve` | zatwierdzenie | `wq:approve` |

---

## wells

Monitoring studni (sek. 6).

- pomiar: data/godzina, zwierciadło statyczne, dynamiczne, wydajność, czas pracy, uwagi, źródło,
- depresja i wydajność jednostkowa liczone w bazie (kolumny generowane),
- wykresy: statyczne, dynamiczne, depresja, wydajność, wydajność jednostkowa,
- formularz uproszczony na telefon: wybór studni (domyślnie ostatnio używana), 3 pola liczbowe, zapisz.

| Endpoint | Opis | Uprawnienie |
|----------|------|-------------|
| `GET/POST /wells/{id}/measurements/new` | dodanie pomiaru | `well_measurement:write` |
| `GET /wells/{id}/measurements` | historia | `well_measurement:read` |
| `GET /api/wells/{id}/series?metric=` | seria do wykresu | `well_measurement:read` |

---

## abstraction

Pobór wody (sek. 7–8).

- rekordy dobowe/miesięczne/roczne dla studni lub ujęcia,
- agregacja do okresu limitu (godzina/doba/rok rozliczeniowy),
- porównanie z limitami aktualnego pozwolenia (`permit_limit`),
- **prognoza liniowa** do końca okresu rozliczeniowego:

```
forecast = used_to_date / elapsed_days * total_days
usage_pct = forecast / annual_limit
```

  wymagane minimum danych (np. ≥ 30 dni lub ≥ 2 miesiące), inaczej status „Brak danych”.

| Endpoint | Opis | Uprawnienie |
|----------|------|-------------|
| `GET/POST /intakes/{id}/abstraction/new` | wprowadzenie poboru | `abstraction:write` |
| `GET /intakes/{id}/abstraction` | zestawienie + wykorzystanie limitów + prognoza | `abstraction:read` |
| `GET /api/intakes/{id}/abstraction/series` | seria narastająca vs limit | `abstraction:read` |

---

## permits

Pozwolenia wodnoprawne (sek. 9).

- numer, organ, data wydania, okres obowiązywania, dokument źródłowy, zakres (ujęcie / wybrane studnie),
- limity: `q_max_h`, `q_max_d`, `q_avg_d`, `annual`, `custom` (nazwa + jednostka + okres),
- „aktualne pozwolenie” = obowiązujące dziś dla danego ujęcia/studni,
- konfigurowalne progi przypomnień (domyślnie 24/12/6/3/1 mies. + po terminie) — w `rule_config`.

| Endpoint | Opis | Uprawnienie |
|----------|------|-------------|
| `GET /intakes/{id}/permits` | lista | `permit:read` |
| `GET/POST /permits/new` | nowe pozwolenie | `permit:write` (personel) |
| `GET /permits/{id}` | szczegóły, limity, obowiązki | `permit:read` |

---

## obligations

Obowiązki wynikające z pozwolenia (sek. 10).

- definicja: nazwa, opis, typ (`quality_test`, `water_level`, `yield_test`, `meter_reading`, `report_submission`, `other`), ujęcie/studnia, pozwolenie, częstotliwość (RRULE, np. `FREQ=MONTHLY;INTERVAL=3`), pierwszy termin, sposób potwierdzenia,
- `obligation_occurrence` — konkretne terminy (bieżący + historia),
- **auto-zaliczenie**: po zdarzeniu (`WellMeasurementCreated`, `SampleSubmitted`, `DocumentUploaded`) serwis szuka otwartego terminu pasującego typem i przedmiotem w oknie realizacji → oznacza jako wykonany, wylicza następny termin (`dateutil.rrule`),
- potwierdzenie ręczne dla typu `other` (+ opcjonalny dokument).

| Endpoint | Opis | Uprawnienie |
|----------|------|-------------|
| `GET /obligations` | terminy (posortowane po dacie) | `obligation:read` |
| `POST /permits/{id}/obligations` | nowy obowiązek | `obligation:write` (personel) |
| `POST /obligations/occurrences/{id}/fulfil` | potwierdzenie ręczne | `obligation:fulfil` |

---

## rules + alerts

Opisane osobno: [05-silnik-regul-i-alerty.md](05-silnik-regul-i-alerty.md).

---

## consultations

Konsultacje z hydrogeologiem (sek. 13).

- przycisk „Skonsultuj z hydrogeologiem” na dashboardzie, alercie, karcie studni,
- formularz: wiadomość (kontekst — klient, ujęcie, studnia, alert — uzupełniany automatycznie),
- przypisanie do hydrogeologa z `staff_assignment` (pierwszy przypisany lub kolejka),
- wątek wiadomości, statusy `new` → `in_progress` → `answered` → `closed`,
- powiadomienie e-mail do hydrogeologa i klienta.

| Endpoint | Opis | Uprawnienie |
|----------|------|-------------|
| `GET/POST /consultations/new?alert_id=` | zgłoszenie | `consultation:create` |
| `GET /consultations/{id}` | wątek | `consultation:read` |
| `POST /consultations/{id}/messages` | odpowiedź | `consultation:reply` |

---

## reports

Raporty (sek. 15).

- **automatyczny**: zadanie Celery zbiera dane (status ujęcia, jakość, pobór + prognoza, trendy, studnie, pozwolenie, obowiązki, aktywne alerty), renderuje szablon Django z wykresami PNG (matplotlib), konwertuje WeasyPrint → PDF, zapisuje jako `document` + `report`,
- **ekspercki**: hydrogeolog uzupełnia sekcje interpretacji/zaleceń (edytor tekstu), status `draft` → `approved`; tylko zatwierdzony widoczny dla klienta,
- raport automatyczny nie zawiera diagnoz — tylko fakty i komunikaty reguł.

| Endpoint | Opis | Uprawnienie |
|----------|------|-------------|
| `GET /intakes/{id}/reports` | lista raportów | `report:read` |
| `POST /intakes/{id}/reports` | wygenerowanie na żądanie | `report:generate` |
| `GET /reports/{id}/download` | PDF | `report:read` |
| `POST /reports/{id}/approve` | zatwierdzenie eksperckiego | `report:approve` (hydrogeolog) |

---

## dashboard

Widoki agregujące (sek. 4 i 14). Nie ma własnych tabel — czyta z serwisów modułów.

### Dashboard klienta (`GET /`)

| Kafel | Źródło | Przykład |
|-------|--------|----------|
| Jakość wody | `water_quality.summary(intake)` | 24 OK · 1 obserwacja · 0 przekroczeń |
| Pobór | `abstraction.usage(intake)` | 68% limitu rocznego · prognoza 91% |
| Studnie | `wells.status_list(intake)` | S-1 OK · S-2 spadek wydajności · S-3 brak pomiaru |
| Pozwolenie | `permits.current(intake)` | ważne do 31.03.2027 · zostało 6 mies. |
| Obowiązki | `obligations.upcoming(intake)` | za 12 dni pomiar zwierciadła S-2 [Dodaj pomiar] |
| Działania | — | Dodaj analizę · Dodaj pomiar · Dodaj pobór · Dodaj dokument · Skonsultuj |

Status ogólny kafla = najgorszy status jego elementów (`action` > `watch` > `no_data` > `ok`).
Klient z wieloma ujęciami: przełącznik ujęć u góry (zapamiętany w sesji).

### Dashboard hydrogeologa (`GET /staff`)

Kolejka wyjątków dla przypisanych klientów: alerty `action`, konsultacje `new`, analizy `submitted` do kontroli, ryzyko przekroczenia poboru, pogarszające się studnie, pozwolenia < 12 mies., zaległe obowiązki, braki danych. Każdy wiersz linkuje do miejsca rozwiązania.

---

## Macierz uprawnień (skrót)

| Uprawnienie | Admin | Hydrogeolog | Operator | Klient |
|-------------|:-----:|:-----------:|:--------:|:------:|
| `user:manage`, `org:manage`, słowniki, progi globalne | ✔ | | | |
| odczyt danych klienta | ✔ (bypass, audyt) | przypisani | przypisani | własne |
| dodanie analizy / pomiaru / poboru / dokumentu | ✔ | ✔ | ✔ | ✔ |
| edycja danych roboczych | ✔ | ✔ | ✔ | własne `draft`/`submitted` |
| zatwierdzanie danych (`*:approve`) | ✔ | ✔ | | |
| edycja danych zatwierdzonych (z audytem) | ✔ | ✔ | | |
| pozwolenia, obowiązki | ✔ | ✔ | ✔ | odczyt |
| konfiguracja reguł per klient | ✔ | ✔ | | |
| interpretacje, zalecenia, raport ekspercki | | ✔ | | odczyt zatwierdzonych |
| zamknięcie alertu | ✔ | ✔ | | potwierdzenie (`acknowledge`) |
| konsultacja — zgłoszenie / odpowiedź | | odpowiedź | | zgłoszenie |
| logi, błędy | ✔ | | | |

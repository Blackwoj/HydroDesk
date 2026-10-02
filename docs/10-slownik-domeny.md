# 10 — Słownik domeny (PL → kod)

Jedno pojęcie = jedna nazwa w kodzie. Kod, modele, pola i identyfikatory po angielsku; UI po polsku.
Nowe pojęcie → dopisz tutaj w tym samym PR.

## Struktura

| PL (UI) | Kod | Uwagi |
|---------|-----|-------|
| Klient | `Organization` / `organization` | podmiot korzystający z systemu (np. wodociągi gminne) |
| Użytkownik | `User` | |
| Członkostwo | `Membership` | użytkownik ↔ organizacja klienta |
| Przypisanie personelu | `StaffAssignment` | hydrogeolog/operator ↔ organizacja |
| Ujęcie (wód podziemnych) | `Intake` / `intake` | zespół studni z wspólnym pozwoleniem |
| Studnia | `Well` / `well` | |
| Punkt poboru (próbki) | `sampling_point` | studnia, woda surowa zbiorczo, woda uzdatniona |
| Stacja uzdatniania wody (SUW) | `treatment_plant` | poza zakresem v1 — tylko jako punkt poboru |

## Role

| PL | Kod (`system_role`) |
|----|---------------------|
| Administrator systemu | `admin` |
| Hydrogeolog | `hydrogeologist` |
| Operator wewnętrzny | `operator` |
| Użytkownik klienta | `client` |

## Jakość wody

| PL | Kod | Uwagi |
|----|-----|-------|
| Analiza / badanie jakości wody | `WaterSample` | jedna próbka z datą poboru |
| Wynik (parametru) | `WaterResult` | |
| Parametr | `Parameter` | np. mangan `Mn` |
| Jednostka | `Unit` | |
| Wartość źródłowa | `raw_value` | dokładnie jak w sprawozdaniu, np. `<0,05` |
| Znak / kwalifikator | `qualifier` | `<`, `>`, `<=`, `>=` |
| Wartość znormalizowana | `value_normalized` | `Decimal` w jednostce bazowej parametru |
| Niepewność | `uncertainty` | |
| Metoda | `method` | |
| Laboratorium | `Laboratory` | |
| Sprawozdanie z badań | `Document` z `doc_type=lab_report` | |
| Wartość graniczna / próg | `ReferenceValue` (`limit_max`, `limit_min`) | |
| Zestaw wartości odniesienia | `ReferenceValueSet` | wersjonowany, z podstawą prawną |
| Podstawa prawna | `legal_basis` | |
| Zbliżenie do progu | `near_limit` | domyślnie ≥ 80% |
| Przekroczenie | `exceeded` | |
| Trend | `trend` | |

## Monitoring studni

| PL | Kod | Uwagi |
|----|-----|-------|
| Pomiar studni | `WellMeasurement` | |
| Zwierciadło statyczne | `static_level_m` | głębokość od terenu [m p.p.t.] |
| Zwierciadło dynamiczne | `dynamic_level_m` | [m p.p.t.] |
| Depresja | `drawdown_m` | dynamiczne − statyczne |
| Wydajność | `yield_m3h` | [m³/h] |
| Wydajność jednostkowa | `specific_yield` | wydajność / depresja [m³/h/m] |
| Czas pracy/pomiaru | `duration_h` | |
| Rzędna terenu | `ground_elevation_m` | [m n.p.m.] |
| Głębokość studni | `depth_m` | |
| m p.p.t. | — | metry poniżej poziomu terenu (tylko UI) |

## Pobór i pozwolenia

| PL | Kod | Uwagi |
|----|-----|-------|
| Pobór (wody) | `AbstractionRecord` / `abstraction` | „abstraction” = termin hydrologiczny |
| Okres (rozliczeniowy) | `period` | `DateRange` |
| Granulacja | `granularity` | `day`, `month`, `year` |
| Objętość | `volume` | [m³] |
| Odczyt wodomierza | `meter_reading` | jeżeli klient poda stany licznika |
| Prognoza poboru | `forecast` | liniowa w v1 |
| Wykorzystanie limitu | `usage_ratio` / `usage_pct` | |
| Pozwolenie wodnoprawne | `Permit` | |
| Organ (wydający) | `authority` | np. PGW Wody Polskie |
| Okres obowiązywania | `validity` | `DateRange` |
| Limit poboru | `PermitLimit` | |
| Qmax,h | `q_max_h` | maks. godzinowy |
| Qmax,d | `q_max_d` | maks. dobowy |
| Qśr,d | `q_avg_d` | średni dobowy |
| Limit roczny | `annual` | |
| Limit indywidualny | `custom` | |
| Zakres pozwolenia | `PermitScope` | studnie objęte pozwoleniem |

## Obowiązki

| PL | Kod | Uwagi |
|----|-----|-------|
| Obowiązek (z pozwolenia) | `Obligation` | |
| Termin (konkretny) | `ObligationOccurrence` | |
| Częstotliwość | `recurrence` | RRULE |
| Najbliższy termin | `next_due_on` | |
| Sposób potwierdzenia | `fulfilment_mode` | `auto`, `manual` |
| Wykonanie | `fulfilled_at` | |
| Dowód wykonania | `evidence_type`, `evidence_id` | pomiar, analiza, dokument |
| Typ obowiązku | `obligation_type` | `quality_test`, `water_level`, `yield_test`, `meter_reading`, `report_submission`, `other` |

## Alerty, konsultacje, raporty

| PL | Kod | Uwagi |
|----|-----|-------|
| Alert | `Alert` | |
| Reguła | `Rule` / `rule_key` | np. `quality.exceedance` |
| Konfiguracja reguły | `RuleConfig` | |
| Ważność alertu | `severity` | `info`, `watch`, `action` |
| Status alertu | `status` | `open`, `acknowledged`, `resolved`, `auto_resolved` |
| Klucz deduplikacji | `dedup_key` | |
| Co zrobić dalej | `next_step` | obowiązkowy w każdym alercie |
| Konsultacja | `Consultation` | |
| Wiadomość konsultacji | `ConsultationMessage` | |
| Raport automatyczny | `Report(kind="automatic")` | |
| Raport ekspercki | `Report(kind="expert")` | wymaga zatwierdzenia hydrogeologa |
| Zalecenie | `recommendation` | tylko w raporcie eksperckim / konsultacji |
| Interpretacja | `interpretation` | tylko hydrogeolog |

## Statusy w UI

| PL (UI) | Kod | Ikona |
|---------|-----|-------|
| OK | `ok` | ✓ |
| Obserwacja | `watch` | ◐ |
| Wymaga działania | `action` | ! |
| Brak danych | `no_data` | ? |

## Status danych

| PL | Kod |
|----|-----|
| Roboczy | `draft` |
| Przekazany do weryfikacji | `submitted` |
| Zatwierdzony | `approved` |
| Odrzucony | `rejected` |

## Źródło danych

| PL | Kod |
|----|-----|
| Wprowadzone ręcznie | `manual` |
| Import pliku | `import` |
| Odczyt OCR/AI | `ocr` |
| Telemetria | `telemetry` |

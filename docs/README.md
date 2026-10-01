# HydroDesk — dokumentacja PoC

Indeks dokumentów projektowych dla Proof of Concept systemu GEAQUA HydroDesk.

| Plik | Zawartość |
|------|-----------|
| [Requirements-Specification.md](Requirements-Specification.md) | Wymagania biznesowe (źródło prawdy) |
| [01-plan-poc.md](01-plan-poc.md) | Plan PoC: etapy, zakres, mapowanie na kryteria odbioru v1 |
| [02-architektura.md](02-architektura.md) | Architektura systemu: stack, moduły, warstwy, przepływy, deployment |
| [03-model-danych.md](03-model-danych.md) | Model danych PostgreSQL/PostGIS, ERD, wieloklientowość |
| [04-moduly.md](04-moduly.md) | Opis modułów domenowych, endpointy, reguły biznesowe |
| [05-silnik-regul-i-alerty.md](05-silnik-regul-i-alerty.md) | Reguły, alerty, statusy, deduplikacja, harmonogram zadań |
| [06-bezpieczenstwo.md](06-bezpieczenstwo.md) | Uwierzytelnianie, RBAC, izolacja klientów, audyt, backup |
| [07-struktura-repo.md](07-struktura-repo.md) | Struktura katalogów, konwencje, uruchomienie lokalne |
| [08-zadania.md](08-zadania.md) | Backlog: scope'y (testowalne przyrosty), atomowe tickety, zależności, fale |
| [adr/](adr/) | Decyzje architektoniczne (ADR) |

## Kluczowe decyzje (skrót)

- **Backend:** Python 3.12 + Django 5.2 LTS, modularny monolit; API JSON przez Django Ninja ([ADR-0001](adr/0001-django.md)).
- **Frontend:** renderowany po stronie serwera — Django Templates + HTMX, bez SPA ([ADR-0002](adr/0002-frontend-templates-htmx.md)).
- **Baza:** PostgreSQL 16 + PostGIS (GeoDjango), migracje Django.
- **Auth i admin:** `django.contrib.auth` (Argon2, `django-axes`), Django Admin dla personelu.
- **Izolacja klientów:** `organization_id` w każdej tabeli danych + Row Level Security ([ADR-0003](adr/0003-wieloklientowosc-rls.md)).
- **Zadania w tle:** Celery + Redis (reguły, przypomnienia, raporty, OCR).
- **Pliki:** MinIO / S3 (prywatny bucket), pobieranie wyłącznie przez autoryzowany endpoint ([ADR-0004](adr/0004-przechowywanie-dokumentow.md)).
- **Raporty PDF:** WeasyPrint (HTML → PDF) + wykresy renderowane serwerowo.
- **Uruchomienie:** Docker Compose.

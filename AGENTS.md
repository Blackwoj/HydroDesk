# AGENTS.md — zasady pracy w repozytorium HydroDesk

Ten plik czytają agenci AI (Claude Code, Codex, Cursor itd.) i ludzie. Obowiązuje przy każdym tickecie.

## Projekt w skrócie

GEAQUA HydroDesk — system do nadzoru nad ujęciami wód podziemnych. Modularny monolit w Django.
Hierarchia danych: **Klient (Organization) → Ujęcie (Intake) → Studnia (Well)**. System jest wieloklientowy — izolacja danych klientów jest najważniejszym wymaganiem niefunkcjonalnym.

Źródła prawdy (czytaj przed pracą):

| Co | Gdzie |
|----|-------|
| Wymagania | `docs/Requirements-Specification.md` |
| Architektura | `docs/02-architektura.md`, `docs/adr/` |
| Model danych | `docs/03-model-danych.md` |
| Moduły, endpointy, uprawnienia | `docs/04-moduly.md` |
| Reguły i alerty | `docs/05-silnik-regul-i-alerty.md` |
| Bezpieczeństwo | `docs/06-bezpieczenstwo.md` |
| Struktura repo i konwencje | `docs/07-struktura-repo.md` |
| Backlog (scope'y i tickety) | `docs/08-zadania.md` |
| **Słownik domeny PL → EN** | `docs/10-slownik-domeny.md` |

## Stack

Python 3.12 · Django 5.2 LTS (GeoDjango) · Django Ninja · PostgreSQL 16 + PostGIS · Django Templates + HTMX · Celery + Redis · MinIO (S3) · uv · pytest-django · Docker Compose.

## Komendy

> Uzupełniane w trakcie SC-01. Docelowo:

```bash
docker compose up -d db redis minio mailpit   # zależności
uv sync                                       # pakiety
uv run python manage.py migrate
uv run python manage.py seed_demo
uv run python manage.py runserver
uv run pytest                                 # wszystkie testy
uv run pytest -m sc07                         # testy jednego scope'u
uv run ruff check . && uv run ruff format --check . && uv run mypy .
uv run lint-imports                           # granice modułów
```

## Jak pracujesz z ticketem

1. Weź ticket z `docs/08-zadania.md` (lub GitHub Issue), którego wszystkie zależności są `done`.
2. Branch `feat/HD-XXX-krotki-opis` od aktualnego `poc`. Jeden ticket = jeden PR do `poc`.
3. Rób **tylko** zakres ticketu. Rzeczy spoza zakresu → zapisz w opisie PR jako propozycję nowego ticketu.
4. Przed PR: testy, ruff, mypy, `makemigrations --check` zielone.
5. Tytuł PR: `HD-XXX: <tytuł>`, opis wg szablonu (`.github/pull_request_template.md`).

## Zasady architektury (twarde)

- **Tenancy**: każdy model z danymi klienta dziedziczy po `TenantModel` (ma `organization`). Każda nowa taka tabela ma w migracji `EnableTenantRLS`. Zapytania przez `.for_ctx(ctx)`.
- **Kontekst**: funkcje `services` i `selectors` przyjmują `ctx: RequestContext` jako pierwszy argument.
- **Zapisy tylko w `services.py`** — tam transakcja, audyt (`audit.record`), zdarzenia (`events.publish`). Nie w widokach, nie w `Model.save()`, nie w sygnałach.
- **Odczyty w `selectors.py`**. Widoki są cienkie: formularz → service/selector → szablon.
- **Granice modułów**: z innej aplikacji importuj tylko `services`, `selectors`, `events`. Klucze obce między aplikacjami są OK.
- **Brak twardego usuwania** danych pomiarowych i dokumentów — tylko soft delete.
- **Dokumenty** nigdy nie są nadpisywane — nowa wersja = nowy obiekt.
- **Liczby pomiarowe**: `Decimal` / `NumericField`, nigdy `float`.
- **Wartość z laboratorium** zapisujemy w dwóch postaciach: źródłowej (`raw_value`, `qualifier`) i znormalizowanej.
- **Reguły alertów** opisują zjawisko, nigdy przyczynę. Zakazane w komunikatach: „z powodu”, „przyczyną”, „spowodowane”.

## Bezpieczeństwo (twarde)

- Zasób spoza tenanta użytkownika → **404**, nie 403.
- Każdy nowy widok/endpoint z danymi klienta → test izolacji (`tests/isolation/`).
- Uprawnienia sprawdzane w backendzie; ukrycie przycisku w UI to nie zabezpieczenie.
- Pliki pobierane wyłącznie przez autoryzowany widok; żadnych publicznych URL do S3.
- Żadnych sekretów, danych klientów ani prawdziwych sprawozdań w repo. Dane testowe są syntetyczne lub zanonimizowane.

## UI

- Teksty po polsku, przez gettext (`{% translate %}`, `gettext`). Kod, identyfikatory, commity po angielsku.
- Nazwy pojęć zgodnie ze słownikiem (`docs/10-slownik-domeny.md`) — w kodzie i w UI.
- Status zawsze jako ikona + tekst + kolor (komponent badge).
- Formularze: minimum pól, słowniki jako listy wyboru, wartości domyślne, używalne na 375 px.
- Każdy komunikat mówi użytkownikowi, **co zrobić dalej**.
- Wzorzec wyglądu: makieta na branchu `demo/ui-mockup` (`demo/ui/static/ui/app.css`).

## Testy

- pytest-django + factory-boy. Marker scope'u w każdym pliku testów: `pytestmark = pytest.mark.sc07`.
- Logika czysta (parsery, reguły, prognozy) → testy jednostkowe z przypadkami granicznymi.
- Reguły alertów → test „wyzwala / nie wyzwala / auto-zamyka”.
- Nie mockuj bazy w testach izolacji i RLS — muszą działać na prawdziwym Postgresie.

## Commity

Conventional Commits po angielsku: `feat(water_quality): ...`, `fix(rules): ...`, `test(...)`, `docs(...)`, `chore(...)`.

## Czego nie robić

- Nie zmieniaj ADR-ów ani modelu danych „przy okazji” — to osobny ticket z aktualizacją `docs/`.
- Nie dodawaj zależności bez uzasadnienia w PR.
- Nie wyłączaj testów, strażnika RLS ani reguł lintera, żeby przeszło CI.
- Nie używaj sygnałów Django do logiki domenowej.
- Nie twórz automatycznych diagnoz ani interpretacji — to rola hydrogeologa.

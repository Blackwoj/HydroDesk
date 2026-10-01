# 07 — Struktura repozytorium

## 1. Drzewo katalogów

```
HydroDesk/
├── README.md
├── pyproject.toml              # uv, ruff, mypy, pytest
├── uv.lock
├── manage.py
├── Dockerfile                  # Python 3.12 + GDAL/GEOS/PROJ + WeasyPrint deps
├── docker-compose.yml          # dev: web, worker, beat, db, redis, minio, mailpit
├── docker-compose.prod.yml     # prod: + caddy, backup, bez mailpit
├── .env.example
├── docs/                       # ta dokumentacja
│   └── adr/
├── ops/
│   ├── Caddyfile
│   ├── backup.sh
│   ├── restore.sh
│   ├── RESTORE.md
│   └── db/init/                # role DB, rozszerzenia (uruchamiane przy starcie kontenera)
├── config/                     # projekt Django
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   ├── prod.py
│   │   └── test.py
│   ├── urls.py
│   ├── api.py                  # NinjaAPI, rejestracja routerów modułów
│   ├── celery.py
│   ├── wsgi.py
│   └── asgi.py
├── hydrodesk/
│   ├── core/                   # aplikacja Django (bez własnych tabel domenowych)
│   │   ├── tenancy.py          # RequestContext, TenantMiddleware (atomic + SET LOCAL)
│   │   ├── models.py           # abstrakcyjne: TenantModel, TimestampedModel, SoftDeleteModel
│   │   ├── managers.py         # TenantQuerySet.for_ctx(ctx), SoftDeleteManager
│   │   ├── permissions.py      # role → uprawnienia, dekoratory / mixiny widoków
│   │   ├── audit.py            # AuditLog + audit.record(...)
│   │   ├── events.py           # zdarzenia domenowe, outbox, on_commit → Celery
│   │   ├── storage.py          # dostęp do dokumentów (django-storages S3)
│   │   ├── tasks.py            # TenantTask — bazowe zadanie Celery z kontekstem RLS
│   │   ├── migrations_ops.py   # EnableTenantRLS, CompositeForeignKey (operacje migracji)
│   │   └── templatetags/       # kafel statusu, badge, formatowanie liczb/dat po polsku
│   ├── accounts/
│   ├── organizations/
│   ├── assets/
│   ├── documents/
│   │   └── extractors/
│   ├── dictionaries/
│   ├── water_quality/
│   ├── wells/
│   ├── abstraction/
│   ├── permits/
│   ├── obligations/
│   ├── rules/
│   │   ├── engine.py
│   │   ├── registry.py
│   │   └── definitions/        # quality.py, well.py, abstraction.py, permit.py, obligation.py
│   ├── alerts/
│   ├── consultations/
│   ├── reports/
│   └── dashboard/
├── templates/                  # base.html, layout, wspólne partiale, szablony auth/admin override
├── static/                     # htmx.min.js, alpine, chart.js, leaflet, css, ikony
├── locale/pl/LC_MESSAGES/
├── fixtures/                   # parametry, jednostki, progi, dane demo
└── tests/
    ├── conftest.py             # fixture dwóch klientów, kontekst RLS
    ├── factories.py            # factory-boy
    ├── unit/                   # parser wartości, reguły, prognoza, trend
    ├── integration/            # services + DB + RLS
    ├── views/                  # widoki i API, izolacja klientów
    └── e2e/                    # Playwright: ścieżka klienta (mobile)
```

Struktura pojedynczej aplikacji:

```
hydrodesk/water_quality/
├── __init__.py
├── apps.py
├── models.py
├── admin.py           # rejestracja w Django Admin
├── forms.py
├── schemas.py         # Ninja / Pydantic (JSON)
├── services.py        # zapis: transakcje, audyt, zdarzenia
├── selectors.py       # odczyt: listy, serie, agregaty
├── views.py           # strony HTML + partiale HTMX
├── api.py             # router Ninja (/api/water-quality/...)
├── urls.py
├── tasks.py           # zadania Celery modułu
├── events.py          # zdarzenia publikowane przez moduł
├── parsing.py         # np. parser wartości "<0,05"
├── migrations/
└── templates/water_quality/
```

## 2. Konwencje

- **Granice modułów**: widoki i serwisy importują z innych aplikacji tylko `services`, `selectors` lub `events`. Klucze obce między aplikacjami dozwolone. Pilnowane przez `import-linter` w CI.
- **Logika**: wzorzec services/selectors — bez logiki biznesowej w widokach, sygnałach i `Model.save()`.
- **Sygnały Django**: nie używamy do logiki domenowej (trudne do śledzenia) — zamiast tego jawne zdarzenia w `services`.
- **Transakcje**: `TenantMiddleware` otwiera transakcję per żądanie; zadania Celery — `TenantTask`.
- **Model użytkownika**: własny `accounts.User` od pierwszej migracji (`AUTH_USER_MODEL`), logowanie e-mailem.
- **Typy**: mypy + django-stubs; `--strict` dla `core` i `rules`.
- **Nazewnictwo**: kod i identyfikatory po angielsku, teksty UI i komunikaty po polsku (gettext).
- **Migracje**: każda zmiana schematu = migracja Django; polityki RLS i role w migracjach, nie ręcznie. `makemigrations --check` w CI.
- **Commity**: Conventional Commits (`feat:`, `fix:`, `docs:` …).
- **Gałęzie**: `main` chroniony; praca na `poc` i gałęziach funkcjonalnych (`feat/...`) z PR do `poc`.

## 3. Uruchomienie lokalne (docelowo)

```bash
cp .env.example .env
docker compose up -d db redis minio mailpit
uv sync
uv run python manage.py migrate
uv run python manage.py loaddata dictionaries demo
uv run python manage.py createsuperuser
uv run python manage.py runserver
uv run celery -A config worker -B -l info
```

Albo całość: `docker compose up --build`.

| Usługa | URL |
|--------|-----|
| Aplikacja | http://localhost:8000 |
| Django Admin | http://localhost:8000/admin |
| API (OpenAPI) | http://localhost:8000/api/docs |
| MinIO console | http://localhost:9001 |
| Mailpit | http://localhost:8025 |
| PostGIS (QGIS) | `localhost:5432`, rola `hydrodesk_gis_ro` |

## 4. Główne zależności (`pyproject.toml`)

```toml
[project]
name = "hydrodesk"
requires-python = ">=3.12"
dependencies = [
  "django>=5.2,<5.3",
  "psycopg[binary]>=3",
  "django-environ",
  "django-ninja",
  "django-htmx",
  "django-template-partials",
  "django-widget-tweaks",
  "django-axes",
  "django-simple-history",
  "django-storages[s3]",
  "django-celery-beat",
  "celery[redis]",
  "argon2-cffi",
  "whitenoise",
  "gunicorn",
  "pandas",
  "openpyxl",
  "odfpy",
  "python-magic",
  "python-dateutil",
  "weasyprint",
  "matplotlib",
  "structlog",
  "django-structlog",
]

[dependency-groups]
dev = [
  "pytest", "pytest-django", "factory-boy", "playwright", "pytest-playwright",
  "ruff", "mypy", "django-stubs[compatible-mypy]", "import-linter",
  "pip-audit", "pre-commit", "django-debug-toolbar",
]
```

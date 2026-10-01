# 06 — Bezpieczeństwo, audyt, backup

Odpowiada sekcjom 16 i 19 wymagań.

## 1. Uwierzytelnianie

| Element | Rozwiązanie |
|---------|-------------|
| Metoda | `django.contrib.auth`, własny model `User` (e-mail jako login), sesja serwerowa |
| Hasła | `Argon2PasswordHasher` jako pierwszy w `PASSWORD_HASHERS`; walidatory: `MinimumLengthValidator(12)`, `CommonPasswordValidator`, `UserAttributeSimilarityValidator` |
| Sesja | `django.contrib.sessions` (backend DB); `SESSION_COOKIE_SECURE`, `HttpOnly`, `SameSite=Lax`; wygasanie po bezczynności (8 h, `SESSION_SAVE_EVERY_REQUEST`) i absolutne; unieważnienie sesji przy zmianie hasła (wbudowane) |
| CSRF | `CsrfViewMiddleware`; dla HTMX token w `hx-headers` na `<body>` |
| Rate limiting | `django-axes`: blokada po N nieudanych logowaniach per IP + konto |
| Reset hasła | wbudowane `PasswordResetView` (jednorazowy token, `PASSWORD_RESET_TIMEOUT` = 1 h) |
| 2FA | poza PoC; architektura gotowa (TOTP dla personelu) |

## 2. Autoryzacja (RBAC)

- Rola systemowa użytkownika: `admin`, `hydrogeologist`, `operator`, `client` — każda to **grupa Django** z zestawem uprawnień.
- Uprawnienia Django: standardowe (`view_`/`add_`/`change_`) + własne w `Meta.permissions` (np. `water_quality.approve_sample`). Grupy i uprawnienia tworzone migracją danych (powtarzalnie, nie ręcznie).
- Uprawnienia Django mówią **co** wolno; **do czyich danych** — tenancy (`ctx.org_ids` + RLS).
- Sprawdzanie **zawsze w backendzie**: dekorator/mixin na widoku + ponowne sprawdzenie w serwisie dla operacji wrażliwych.
- UI ukrywa niedostępne akcje (`{% if perms.water_quality.approve_sample %}`), ale nie jest mechanizmem bezpieczeństwa.

```python
@require_POST
@permission_required("water_quality.approve_sample", raise_exception=True)
def approve_sample(request, sample_id):
    sample = selectors.get_sample(request.ctx, sample_id)  # Http404 poza zakresem
    services.approve_sample(request.ctx, sample)
    return render(request, "water_quality/sample_detail.html#status", {"sample": sample})
```

## 3. Izolacja danych klientów

Dwie niezależne warstwy (defense in depth):

1. **Aplikacja** — `TenantQuerySet.for_ctx(ctx)` filtruje po `ctx.org_ids`; `RequestContext` jest wymagany w każdej funkcji `services`/`selectors`; Django Admin ma `get_queryset` z zakresem tenanta.
2. **Baza** — RLS (`FORCE ROW LEVEL SECURITY`) na każdej tabeli z `organization_id`; kontekst ustawiany `SET LOCAL` na początku transakcji. Błąd w kodzie aplikacji nie ujawni danych innego klienta.

Dodatkowo:

- złożone klucze obce `(organization_id, parent_id)` uniemożliwiają „przepięcie” rekordu do innego klienta,
- identyfikatory UUID (nieprzewidywalne),
- odpowiedź 404 (nie 403) dla zasobów spoza zakresu użytkownika,
- **testy izolacji w CI**: fixture z dwoma klientami; dla każdego endpointu odczytu/zapisu test, że klient A dostaje 404 dla zasobu B; test SQL, że bez kontekstu zapytanie zwraca 0 wierszy,
- migracja Django nowej tabeli bez polityki RLS → test w CI kończy się błędem (sprawdzenie `pg_class.relrowsecurity` dla tabel z kolumną `organization_id`).

## 4. Dokumenty

- bucket MinIO prywatny, brak polityki publicznej, brak listowania,
- pobieranie wyłącznie przez `GET /documents/{id}/download` (sprawdzenie uprawnień + RLS), strumieniowanie przez backend,
- brak presigned URL w PoC (ewentualnie później: ważność ≤ 60 s, generowane dopiero po autoryzacji),
- walidacja uploadu: limit rozmiaru (np. 25 MB), whitelist MIME + sprawdzenie sygnatury pliku (`python-magic`), nazwy plików sanityzowane, klucz w S3 niezależny od nazwy pliku,
- wersjonowanie bucketu włączone (ochrona przed nadpisaniem), pliki niemodyfikowalne,
- opcjonalnie skan antywirusowy (ClamAV) jako zadanie Celery — poza PoC.

## 5. Transport i nagłówki

- HTTPS wyłącznie (Caddy, automatyczne certyfikaty), HSTS,
- `SecurityMiddleware` + `manage.py check --deploy` w CI; `Content-Security-Policy` (skrypty tylko własne + HTMX/Chart.js serwowane lokalnie, bez CDN), `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`, `X-Frame-Options: DENY`,
- baza, Redis i MinIO niedostępne z internetu (sieć wewnętrzna Compose); QGIS łączy się przez VPN/SSH tunnel lub whitelistę IP z TLS.

## 6. Audyt (sek. 16)

Tabela `audit.audit_log` (append-only — rola aplikacji ma tylko `INSERT`, `SELECT`).

| Zdarzenie | `action` |
|-----------|----------|
| dodanie / zmiana / usunięcie danych | `<entity>.created/updated/deleted` (z `before`/`after`) |
| zatwierdzenie | `<entity>.approved` |
| zamknięcie alertu | `alert.resolved` |
| wygenerowanie raportu | `report.generated` |
| konsultacja | `consultation.created/replied/closed` |
| logowanie / nieudane logowanie | `auth.login`, `auth.login_failed` |
| dostęp admina z pominięciem RLS | `admin.bypass` |
| pobranie dokumentu | `document.downloaded` |

Mechanizm:

- jawne `audit.record(...)` w serwisach dla zdarzeń biznesowych,
- `django-simple-history` (`HistoricalRecords()`) na modelach danych — pełna historia wartości pól, kto i kiedy (również zmiany z Django Admin),
- `request_id` i IP z middleware,
- widok „Historia zmian” na kartach obiektów (filtr po `entity_id`).

## 7. Ochrona przed przypadkowym usunięciem (sek. 17 pkt 11)

- brak twardego `DELETE` w aplikacji dla danych pomiarowych i dokumentów,
- modal potwierdzenia z nazwą obiektu, usunięcie = `deleted_at`,
- przywracanie przez hydrogeologa/admina,
- usunięcie ujęcia/studni z danymi niedozwolone — tylko archiwizacja (`status = archived`).

## 8. Backup i odtwarzanie (sek. 19, kryterium 20)

| Co | Jak | Częstotliwość | Retencja |
|----|-----|---------------|----------|
| Baza | `pg_dump -Fc` do zaszyfrowanego katalogu / zewnętrznego S3 | codziennie | 7 dziennych, 4 tygodniowe, 12 miesięcznych |
| Baza (opcjonalnie) | WAL archiving (pgBackRest) dla PITR | ciągle | 7 dni |
| Dokumenty | `mc mirror` bucketu na zewnętrzny storage | codziennie | jak baza |
| Konfiguracja | `.env` / sekrety w menedżerze haseł / Vault | przy zmianie | — |

- Backupy szyfrowane (`age` / szyfrowanie po stronie S3), przechowywane poza serwerem aplikacji.
- **Procedura odtworzenia** opisana w `ops/RESTORE.md` i testowana: skrypt `ops/restore.sh` odtwarza bazę i bucket na czystym środowisku; test odtworzenia raz w miesiącu (kryterium 20 sprawdzane w demo).

## 9. Sekrety i konfiguracja

- zmienne środowiskowe przez `django-environ` (`.env` tylko lokalnie, nie w repo — `.env.example` w repo),
- osobne hasła dla ról DB (`hydrodesk_app`, `hydrodesk_gis_ro`, ...),
- `SECRET_KEY` rotowalny,
- zależności skanowane (`pip-audit` w CI, Dependabot).

## 10. Logi i błędy

- logi JSON (structlog) bez danych wrażliwych (bez haseł, tokenów, treści dokumentów),
- błędy aplikacji: Sentry (self-hosted lub SaaS — do decyzji) — dostęp dla admina,
- `/healthz` (proces), `/readyz` (DB, Redis, S3).

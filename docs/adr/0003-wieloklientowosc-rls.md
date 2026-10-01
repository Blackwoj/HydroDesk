# ADR-0003: Wieloklientowość — wspólny schemat + Row Level Security

**Status:** zaakceptowana (PoC)
**Data:** 2026-10-01

## Kontekst

Spec (sek. 2, 19): dane klientów logicznie odseparowane, bezpieczeństwo wieloklientowe od pierwszej migracji. Personel (hydrogeolog, operator) pracuje na danych wielu klientów; QGIS czyta PostGIS bezpośrednio.

## Rozważone opcje

| Opcja | Plusy | Minusy |
|-------|-------|--------|
| Osobna baza per klient | najsilniejsza izolacja | migracje × N, trudne widoki przekrojowe dla hydrogeologa, koszt operacyjny |
| Schemat per klient (np. django-tenants) | dobra izolacja | jak wyżej, migracje per schemat, QGIS wiele warstw, personel przełącza schematy |
| **Wspólny schemat + `organization_id` + RLS** | jedna migracja, proste zapytania przekrojowe, izolacja wymuszona przez DB | wymaga dyscypliny w ustawianiu kontekstu, testy RLS |

## Decyzja

Wspólny schemat, kolumna `organization_id` w każdej tabeli danych klienta, **RLS z `FORCE`** i kontekstem ustawianym `SET LOCAL app.org_ids` w każdej transakcji (żądanie HTTP i zadanie Celery). Filtrowanie również w aplikacji — managery modeli i selektory z zakresem `ctx.org_ids` (defense in depth).

## Konsekwencje

- polityki RLS w migracjach Django (`RunSQL` / własna operacja `EnableTenantRLS`); test CI wykrywa tabelę z `organization_id` bez RLS,
- aplikacja łączy się rolą bez `BYPASSRLS`; migracje inną rolą (właściciel),
- `SET LOCAL` działa tylko w transakcji — `TenantMiddleware` otwiera `transaction.atomic()` dla całego żądania (zamiast `ATOMIC_REQUESTS`) i jako pierwsze wykonuje `SET LOCAL`; zadania Celery robią to samo w klasie bazowej zadania; przy poolerze (PgBouncer) wymagany tryb transakcyjny,
- admin z pominięciem RLS tylko jawnie i z wpisem audytowym,
- QGIS korzysta z widoków `gis.*` z osobną rolą read-only (personel wewnętrzny).

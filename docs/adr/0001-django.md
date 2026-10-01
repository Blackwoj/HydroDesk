# ADR-0001: Django jako framework aplikacji

**Status:** zaakceptowana (PoC)
**Data:** 2026-10-01

## Kontekst

Specyfikacja (sek. 18) wskazuje Django + Django Templates + HTMX. Rozważaliśmy też FastAPI.

HydroDesk to system głównie formularzowy: CRUD na hierarchii Klient → Ujęcie → Studnia, cztery role z różnymi uprawnieniami, panel administracyjny (słowniki, progi, klienci, użytkownicy), server-side rendering, raporty, zadania w tle. Ruch niewielki, ciężkie operacje w Celery.

## Rozważone opcje

| Kryterium | Django | FastAPI |
|-----------|--------|---------|
| Użytkownicy, sesje, reset hasła, CSRF | wbudowane | do napisania / złożenia z bibliotek |
| Uprawnienia, grupy | wbudowane | do napisania |
| Panel admina | Django Admin (dojrzały) | SQLAdmin (dużo uboższy) |
| Formularze HTML + walidacja | Django Forms | Pydantic + ręczne renderowanie |
| PostGIS | GeoDjango (natywnie, także w adminie) | GeoAlchemy2 |
| i18n | wbudowane | Babel, ręczna integracja |
| Migracje | wbudowane | Alembic |
| Historia zmian | `django-simple-history` | do napisania |
| Harmonogram zadań edytowalny w UI | `django-celery-beat` | brak gotowego |
| Typowane API + OpenAPI | Django Ninja | natywnie |
| Async | częściowe (wystarczające) | natywne |
| Zgodność ze specyfikacją | tak | odejście, wymaga akceptacji |

## Decyzja

**Django 5.2 LTS** jako modularny monolit; endpointy JSON przez **Django Ninja**.

## Konsekwencje

Plusy:

- ok. 1,5–2 tygodnie mniej pracy w PoC (auth, admin, formularze, i18n z pudełka),
- Django Admin pokrywa potrzeby administratora i część potrzeb operatora bez pisania UI,
- zgodność z preferowaną architekturą ze specyfikacji,
- duży ekosystem i łatwa rekrutacja.

Minusy / ryzyka:

- RLS wymaga własnego middleware z `transaction.atomic()` + `SET LOCAL` (patrz [ADR-0003](0003-wieloklientowosc-rls.md)) — Django domyślnie nie zakłada RLS,
- ORM Django słabiej obsługuje niektóre konstrukcje Postgresa (złożone klucze obce, polityki RLS) — rozwiązujemy `RunSQL` w migracjach,
- zależności GIS (GDAL/GEOS) w obrazie Dockera,
- Django Admin nie jest dla klienta — UI klienta to własne widoki (Templates + HTMX).

Jeżeli w przyszłości powstanie osobny frontend lub aplikacja mobilna, Django Ninja daje typowane API w stylu FastAPI bez zmiany frameworka.

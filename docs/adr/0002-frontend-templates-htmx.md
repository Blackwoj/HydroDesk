# ADR-0002: Frontend renderowany serwerowo (Django Templates + HTMX)

**Status:** zaakceptowana (PoC)
**Data:** 2026-10-01

## Kontekst

Spec (sek. 18): „Nie ma potrzeby stosowania osobnego SPA w pierwszej wersji”. Użytkownik klienta nie jest specjalistą IT, korzysta także z telefonu. Zespół jest mały.

## Decyzja

- Strony renderowane przez **Django Templates**, formularze przez **Django Forms**.
- Interaktywność przez **HTMX** (`django-htmx`), partiale w tym samym pliku szablonu (`django-template-partials`), drobne zachowania przez **Alpine.js**.
- Wykresy **Chart.js** zasilane z endpointów JSON (Django Ninja).
- Mapa (wskazanie lokalizacji studni) — **Leaflet**.
- Wszystkie biblioteki JS serwowane lokalnie (WhiteNoise, CSP bez CDN).
- CSS: Pico.css na start PoC; ewentualnie Tailwind (standalone CLI, bez Node w runtime).
- Panel `/admin` (Django Admin) tylko dla personelu wewnętrznego — klient nigdy go nie widzi.

## Konsekwencje

- jeden deployment, brak osobnego builda frontu,
- endpointy JSON (`/api/...`) i tak powstają — przyszłe SPA/mobile może z nich korzystać,
- bogatsze interakcje (np. tabela edycji wielu wyników z importu) wymagają przemyślanego HTMX; dopuszczalna lokalna „wyspa” JS w razie potrzeby.

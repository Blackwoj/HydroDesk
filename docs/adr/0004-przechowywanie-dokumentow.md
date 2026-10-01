# ADR-0004: Przechowywanie dokumentów w S3 (MinIO)

**Status:** zaakceptowana (PoC)
**Data:** 2026-10-01

## Kontekst

Spec (sek. 16, 19): każdy dokument źródłowy musi być zachowany, bez nadpisywania bez historii; brak publicznych URL; backup dokumentów.

## Decyzja

- Pliki w **S3-kompatybilnym storage** — lokalnie i on-premise **MinIO**, w chmurze dowolny S3.
- Metadane i wersje w PostgreSQL (`document`, `document_version` z SHA-256, rozmiarem, MIME).
- Klucz obiektu: `org/<organization_id>/documents/<document_id>/<version_no>` — niezależny od nazwy pliku.
- Bucket prywatny, wersjonowanie włączone, pliki niemodyfikowalne (nowa wersja = nowy obiekt).
- Pobieranie wyłącznie przez autoryzowany endpoint backendu (strumieniowanie).
- Backup: `mc mirror` na zewnętrzny storage.

## Konsekwencje

- dodatkowy kontener (MinIO), ale łatwa migracja do chmury bez zmian w kodzie,
- strumieniowanie przez backend obciąża `web` — akceptowalne dla wolumenu PoC; później możliwe krótkotrwałe presigned URL po autoryzacji,
- spójność DB ↔ S3: zapis pliku przed commitem metadanych; osierocone obiekty sprzątane zadaniem okresowym.

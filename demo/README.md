# HydroDesk — makieta UI

Klikalna makieta interfejsu na **zmockowanych danych**: Django + szablony + HTMX + Chart.js, bez bazy danych.
Służy do oceny wyglądu i przepływów przed implementacją właściwego systemu (patrz `docs/`). Formularze niczego nie zapisują.

Kod makiety jest celowo uproszczony i **nie jest** szkieletem docelowej aplikacji (struktura docelowa: `docs/07-struktura-repo.md`).

## Uruchomienie

```bash
cd demo
uv sync
uv run python manage.py runserver
```

Otwórz http://127.0.0.1:8000 i wybierz rolę na ekranie logowania (hasło dowolne).

## Co obejrzeć

| Ekran | URL | Rola |
|-------|-----|------|
| Pulpit klienta (5 kafli, działania, alerty) | `/` | klient |
| „Do zrobienia” — kolejka wyjątków hydrogeologa | `/zespol/` | hydrogeolog |
| Ujęcie i lista studni | `/ujecia/1/` | dowolna |
| Karta studni z wykresami (S-2: spadek wydajności) | `/studnie/S-2/` | dowolna |
| Jakość wody — tabela parametrów, filtry HTMX | `/jakosc/` | dowolna |
| Parametr z wykresem i wartością graniczną (mangan) | `/jakosc/parametr/Mn/` | dowolna |
| Pobór — limity, prognoza, wykres narastający | `/pobor/` | dowolna |
| Pozwolenie i obowiązki | `/pozwolenie/` | dowolna |
| Alerty i szczegóły alertu | `/alerty/`, `/alerty/2/` | dowolna |
| Konsultacje (klient: zgłoszenie, hydrogeolog: odpowiedź) | `/konsultacje/` | obie |
| Raporty („Generuj raport teraz” — HTMX) | `/raporty/` | dowolna |
| Formularze: pomiar (mobile), analiza, pobór, dokument | `/pomiary/dodaj/`, `/jakosc/dodaj/`, `/pobor/dodaj/`, `/dokumenty/dodaj/` | klient |

Najlepiej oglądać także w trybie telefonu (DevTools → 375 px).

## Struktura

```
demo/
├── manage.py
├── mockup/          # ustawienia (bez bazy, sesja w cookie)
└── ui/
    ├── mock_data.py # wszystkie dane makiety
    ├── views.py
    ├── templates/ui/
    └── static/ui/app.css
```

Biblioteki JS (HTMX, Chart.js) ładowane z CDN — w docelowym systemie serwowane lokalnie (CSP).

## Wystawienie publiczne (Cloudflare Tunnel)

Makieta jest wystawiona pod https://hydro.wnikiel.pl przez tunel `local-django` z tego komputera.

```bash
# 1. serwer makiety (gunicorn, DEBUG=0, port 8100)
PUBLIC_HOST=hydro.wnikiel.pl ./serve.sh

# 2. tunel (w drugim terminalu)
cloudflared tunnel --config ~/.cloudflared/hydro.yml run local-django
```

`~/.cloudflared/hydro.yml`:

```yaml
protocol: http2
tunnel: 070a6ab4-f997-4ed8-8d66-6c3ade1c4ef0
credentials-file: /Users/wojciechnikiel/.cloudflared/070a6ab4-f997-4ed8-8d66-6c3ade1c4ef0.json
ingress:
  - hostname: hydro.wnikiel.pl
    service: http://127.0.0.1:8100
  - service: http_status:404
```

Rekord DNS `hydro.wnikiel.pl` → tunel utworzony raz: `cloudflared tunnel route dns local-django hydro.wnikiel.pl`.
Strona działa tylko, gdy komputer jest włączony i oba procesy działają.

### Stałe działanie (launchd)

Serwer, tunel i blokada usypiania działają jako agenci launchd (`~/Library/LaunchAgents/pl.wnikiel.hydro.{server,tunnel,awake}.plist`):
startują przy logowaniu, wstają po awarii, logi w `~/Library/Logs/hydro-demo/`.

```bash
launchctl list | grep pl.wnikiel.hydro                                   # status
launchctl kickstart -k gui/$(id -u)/pl.wnikiel.hydro.server              # restart serwera (np. po zmianach w kodzie)
for s in server tunnel awake; do launchctl bootout gui/$(id -u)/pl.wnikiel.hydro.$s; done   # wyłączenie
```

`caffeinate -i -s` blokuje usypianie tylko przy zasilaniu sieciowym; zamknięcie klapy na baterii nadal usypia Maca.

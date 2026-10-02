# 11 — Kwestionariusz przed implementacją

Do wypełnienia z zleceniodawcą (GEAQUA), hydrogeologiem i 1–2 klientami pilotażowymi.
Każda odpowiedź zamyka założenie z dokumentacji; kolumna „Domyślnie” to wartość przyjęta w planie, jeśli nie ustalimy inaczej.

Po wypełnieniu: odpowiedzi przenosimy do `docs/` (model danych, reguły), a zmiany w zakresie — do backlogu.

---

## A. Decyzje zleceniodawcy

| # | Pytanie | Domyślnie (w planie) | Odpowiedź |
|---|---------|----------------------|-----------|
| A1 | Akceptacja Django zamiast stosu ze specyfikacji? (ADR-0001 — spec też wskazuje Django) | tak | |
| A2 | Akceptacja zakresu PoC i kryteriów odbioru (sek. 21 + `01-plan-poc.md`) jako kontraktu? | tak | |
| A3 | Hosting docelowy: VPS w UE / chmura PL / serwer klienta? | VPS w UE (Hetzner/OVH) | |
| A4 | Domena systemu i adres nadawcy e-maili? | `app.geaqua.pl`, `powiadomienia@geaqua.pl` | |
| A5 | Czy hydrogeolog widzi wszystkich klientów, czy tylko przypisanych? | tylko przypisanych | |
| A6 | Logowanie: e-mail + hasło wystarczy? 2FA dla personelu? | hasło; 2FA po PoC | |
| A7 | OCR/AI odczytu sprawozdań PDF w PoC? | nie — tylko CSV/XLSX/ODS + ręcznie | |
| A8 | Kto zakłada klientów i użytkowników — admin GEAQUA czy także hydrogeolog? | admin i hydrogeolog | |
| A9 | Raport ekspercki w PoC — pełny workflow czy tylko model danych? | prosty workflow draft → zatwierdzony | |
| A10 | Ilu klientów / ujęć / studni w pilotażu i w ciągu roku? | 1–3 / 5 / 15 w pilotażu; 50 / 150 / 500 w rok | |
| A11 | RODO: kto jest administratorem danych, czy potrzebna umowa powierzenia z klientami? | GEAQUA = podmiot przetwarzający, umowa powierzenia | |
| A12 | Wymagana dostępność (np. 99%) i dopuszczalna utrata danych (RPO)? | RPO 24 h, RTO 4 h | |

## B. Dane do zebrania (zanonimizowane)

Nie wrzucamy do repozytorium. Folder współdzielony poza GitHubem.

- [ ] **B1** 5–10 sprawozdań z badań wody (PDF), z co najmniej 2 różnych laboratoriów
- [ ] **B2** te same lub inne wyniki w CSV/XLSX, jeśli laboratorium je udostępnia
- [ ] **B3** 1–2 pełne pozwolenia wodnoprawne (decyzje) z limitami i obowiązkami
- [ ] **B4** przykładowe arkusze pomiarów studni (zwierciadło, wydajność) — w formie, w jakiej klient je dziś prowadzi
- [ ] **B5** przykładowe dane poboru: odczyty wodomierzy lub zestawienia miesięczne/roczne
- [ ] **B6** seria historyczna jednego ujęcia z 2–3 lat (jakość + pomiary + pobór) — do testów reguł i danych demo
- [ ] **B7** przykład obecnego raportu dla klienta (jeśli istnieje) — jako wzór raportu automatycznego
- [ ] **B8** obowiązująca lista parametrów i wartości granicznych używana przez GEAQUA

## C. Procesy — jak to działa dziś

| # | Pytanie | Odpowiedź |
|---|---------|-----------|
| C1 | Kto u klienta wprowadza dane (technik, kierownik SUW, biuro)? Na komputerze czy telefonie? | |
| C2 | Jak często klient robi pomiary zwierciadła i wydajności? Ręcznie (świstawka/sonda) czy z automatyki? | |
| C3 | Pobór: klient zna stany wodomierzy (narastająco) czy tylko objętości za okres? Per studnia czy zbiorczo? | |
| C4 | Czy są dane godzinowe (do Qmax,h)? Skąd? | |
| C5 | Rok rozliczeniowy poboru = rok kalendarzowy? | |
| C6 | Skąd pochodzi analiza: zawsze laboratorium zewnętrzne? Jakie punkty poboru (studnia, woda surowa zbiorczo, uzdatniona)? | |
| C7 | Czy pozwolenie może obejmować kilka ujęć lub tylko część studni? Czy zdarzają się zmiany pozwolenia w trakcie obowiązywania? | |
| C8 | Jakie obowiązki z pozwoleń występują najczęściej i jak dziś są potwierdzane? | |
| C9 | Jak dziś wygląda kontakt klient ↔ hydrogeolog (telefon, e-mail)? Jaki czas odpowiedzi jest akceptowalny? | |
| C10 | Kto powinien dostawać powiadomienia e-mail u klienta i jak często (od razu / dzienne podsumowanie)? | |

## D. Kalibracja reguł (hydrogeolog)

Wartości z `05-silnik-regul-i-alerty.md`. Proszę o potwierdzenie lub korektę i — jeśli możliwe — przykład z praktyki (seria danych + czy powinien być alert).

| Reguła | Warunek domyślny | Ważność | Zatwierdzona wartość / uwagi |
|--------|------------------|---------|------------------------------|
| `quality.near_limit` | wynik ≥ **80%** wartości granicznej | Obserwacja | |
| `quality.exceedance` | wynik > wartość graniczna (z uwzględnieniem `<`/`>`) | Wymaga działania | |
| `quality.adverse_trend` | ≥ **4** wyniki, trend rosnący, prognoza 12 mies. ≥ próg lub wzrost > **20%** | Obserwacja | |
| `quality.microbiology` | wynik mikrobiologiczny > **0** | Wymaga działania | |
| `well.yield_decline` | spadek wydajności jednostkowej > **15%** vs mediana 12 mies., w **2** kolejnych pomiarach | Obserwacja | |
| `well.drawdown_increase` | wzrost depresji > **20%** przy porównywalnej wydajności (± **10%**) | Obserwacja | |
| `well.level_change` | zmiana zwierciadła statycznego > **1,0 m** vs poprzedni pomiar | Obserwacja | |
| `well.missing_measurement` | brak pomiaru > częstotliwość z obowiązku, domyślnie **90 dni** | Brak danych | |
| `abstraction.limit_usage` | **80% / 90% / 100%** limitu | Obserwacja / Obserwacja / Wymaga działania | |
| `abstraction.forecast_exceedance` | prognoza na koniec okresu > **100%**; minimum **60 dni** danych | Obserwacja | |
| `abstraction.systematic_increase` | **3** kolejne miesiące wzrostu r/r > **10%** | Informacja | |
| `permit.expiring` | **24 / 12 / 6 / 3 / 1** mies. przed końcem; od **6 mies.** — „Wymaga działania” | Informacja → Wymaga działania | |
| `obligation.due_soon` | termin za ≤ **14** dni | Informacja | |
| `obligation.overdue` | termin minął | Wymaga działania | |

Dodatkowe pytania:

- **D1** Które parametry są „krytyczne” (przekroczenie = natychmiastowy e-mail do hydrogeologa)?
- **D2** Czy progi mają być różne dla wody surowej i uzdatnionej?
- **D3** Czy klient może sam potwierdzić alert, czy tylko hydrogeolog może go zamknąć? (domyślnie: klient potwierdza, hydrogeolog zamyka)
- **D4** Jakich reguł brakuje na liście?

## E. Komunikaty do akceptacji

Proszę o ocenę, czy brzmią zrozumiale dla klienta i nie sugerują diagnozy.

| Sytuacja | Tytuł | Co zrobić | OK / poprawka |
|----------|-------|-----------|---------------|
| zbliżenie do progu | Mangan: 86% wartości granicznej | Obserwuj kolejne wyniki. Jeśli wartość dalej rośnie, skonsultuj się z hydrogeologiem. | |
| trend | Mangan wykazuje trend wzrostowy | Zaplanuj kolejne badanie zgodnie z harmonogramem. | |
| spadek wydajności | S-2: obserwowany spadek wydajności | Zaplanuj kolejny pomiar. W razie wątpliwości skonsultuj się z hydrogeologiem. | |
| brak pomiaru | Brakuje pomiaru zwierciadła S-3 | Dodaj pomiar. | |
| prognoza poboru | Prognozowane przekroczenie limitu rocznego (109%) | Przy obecnym tempie limit zostanie przekroczony ok. 15.11. Rozważ ograniczenie poboru. | |
| pozwolenie | Pozwolenie wodnoprawne wygasa za 6 miesięcy | Rozpocznij przygotowanie wniosku o nowe pozwolenie. | |
| obowiązek po terminie | Po terminie: pomiar zwierciadła S-2 | Wykonaj pomiar i dodaj go do systemu. | |

## F. Makieta (https://hydro.wnikiel.pl)

Zadania do wykonania przez klienta i hydrogeologa — obserwujemy, gdzie się zatrzymują.

| # | Zadanie | Rola | Udało się? Uwagi |
|---|---------|------|------------------|
| F1 | Powiedz, czy na ujęciu wszystko jest w porządku i co wymaga działania | klient | |
| F2 | Dodaj pomiar zwierciadła studni S-3 z telefonu | klient | |
| F3 | Sprawdź, jak zmieniał się mangan w ostatnich 2 latach | klient | |
| F4 | Sprawdź, ile zostało do limitu rocznego poboru | klient | |
| F5 | Poproś hydrogeologa o konsultację w sprawie manganu | klient | |
| F6 | Znajdź klienta, który najpilniej potrzebuje Twojej uwagi | hydrogeolog | |
| F7 | Czego brakuje na pulpicie? Co jest zbędne? | obie | |

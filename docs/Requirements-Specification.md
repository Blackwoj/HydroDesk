# GEAQUA HydroDesk  
## Requirements Specification — pierwsza wersja produkcyjna

**Status:** projekt do implementacji  
**Zakres:** pierwsza wersja użytkowa / MVP produkcyjne  
**Cel dokumentu:** określenie funkcji koniecznych do rozpoczęcia obsługi rzeczywistych klientów bez nadmiernego rozbudowywania systemu.

---

## 1. Cel systemu

GEAQUA HydroDesk jest internetowym systemem do bieżącego nadzoru nad ujęciami wód podziemnych.

System ma:

- umożliwiać klientom samodzielne przekazywanie danych;
- automatycznie kontrolować jakość wody, eksploatację studni, pobór oraz obowiązki wynikające z pozwoleń wodnoprawnych;
- prezentować klientowi prostą informację o aktualnym stanie ujęcia;
- wykrywać sytuacje wymagające uwagi;
- ograniczać rutynową pracę hydrogeologa;
- umożliwiać konsultację problemów z hydrogeologiem;
- generować automatyczne raporty operacyjne.

HydroDesk nie zastępuje interpretacji hydrogeologicznej. Automatyzuje czynności, które można oprzeć na jednoznacznych danych, terminach i regułach.

---

# 2. Podstawowy model

Hierarchia:

**Klient → Ujęcie → Studnia**

Klient może posiadać wiele ujęć.

Ujęcie może posiadać wiele studni.

Do ujęcia lub studni przypisuje się:

- dokumenty;
- pozwolenia wodnoprawne;
- analizy jakości wody;
- pomiary zwierciadła;
- pomiary wydajności;
- pobór wody;
- obowiązki i harmonogramy;
- alerty;
- raporty;
- zdarzenia eksploatacyjne.

System musi być wieloklientowy. Dane poszczególnych klientów muszą być od siebie logicznie odseparowane.

---

# 3. Użytkownicy i role

## 3.1. Administrator systemu

Może:

- zarządzać użytkownikami;
- zarządzać klientami;
- konfigurować system;
- zarządzać słownikami;
- zarządzać wartościami referencyjnymi;
- przeglądać logi i błędy.

## 3.2. Hydrogeolog

Może:

- przeglądać wszystkich przypisanych klientów;
- zatwierdzać i korygować dane;
- analizować alerty;
- dodawać interpretacje;
- tworzyć zalecenia;
- prowadzić konsultacje;
- zatwierdzać raporty eksperckie;
- konfigurować indywidualne reguły nadzoru.

## 3.3. Operator wewnętrzny

Może:

- wprowadzać dane;
- importować dokumenty;
- poprawiać dane robocze;
- przygotowywać dane do weryfikacji.

Nie może zatwierdzać interpretacji eksperckich.

## 3.4. Użytkownik klienta

Ma dostęp wyłącznie do danych własnej organizacji.

Może:

- przeglądać swoje ujęcia i studnie;
- dodawać analizy wody;
- wprowadzać pobór;
- wprowadzać pomiary studni;
- dodawać dokumenty;
- przeglądać wykresy;
- przeglądać alerty;
- przeglądać terminy;
- pobierać raporty;
- zgłaszać potrzebę konsultacji.

Nie może:

- zmieniać progów systemowych;
- modyfikować zatwierdzonych danych historycznych bez pozostawienia śladu;
- zmieniać interpretacji hydrogeologa;
- przeglądać danych innych klientów.

---

# 4. Dashboard klienta

Dashboard jest głównym ekranem systemu.

Ma odpowiadać przede wszystkim na pytania:

**Czy wszystko jest w porządku?**

**Co się zmienia?**

**Co wymaga uwagi?**

**Co muszę zrobić?**

Dashboard powinien pokazywać maksymalnie kilka najważniejszych sekcji:

### Jakość wody
Przykład:

> 24 parametry prawidłowe  
> 1 parametr wymaga obserwacji  
> brak przekroczeń

### Pobór
Przykład:

> wykorzystano 68% limitu rocznego  
> prognoza na koniec roku: 91%

### Studnie
Przykład:

> S-1 — OK  
> S-2 — obserwowany spadek wydajności  
> S-3 — brak aktualnego pomiaru

### Pozwolenie
Przykład:

> ważne do 31.03.2027  
> pozostało 6 miesięcy

### Obowiązki
Przykład:

> za 12 dni należy wykonać pomiar zwierciadła S-2

### Działania

Widoczne powinny być proste przyciski:

**Dodaj analizę**

**Dodaj pomiar**

**Dodaj pobór**

**Dodaj dokument**

**Skonsultuj z hydrogeologiem**

---

# 5. Analizy jakości wody

## FR-WQ-01 — Import

System umożliwia dodanie:

- PDF;
- skanu;
- JPG/PNG;
- CSV;
- XLSX;
- ODS;
- danych ręcznych.

Oryginalny dokument musi zostać zachowany.

## FR-WQ-02 — Odczyt danych

System może wykorzystywać OCR/AI do rozpoznawania:

- daty poboru;
- punktu poboru;
- laboratorium;
- parametrów;
- wartości;
- jednostek;
- znaków `<`, `>`, `<=`, `>=`;
- metody;
- niepewności.

OCR jest mechanizmem pomocniczym.

## FR-WQ-03 — Normalizacja

System musi zachować zarówno:

- wartość źródłową;
- wartość znormalizowaną.

Przykład:

`<0,05 mg/l`

nie może zostać zapisane wyłącznie jako:

`0,05 mg/l`.

## FR-WQ-04 — Historia

Dla każdego parametru dostępna jest seria czasowa wyników.

## FR-WQ-05 — Wykres

System generuje wykres parametru w czasie wraz z właściwą wartością odniesienia.

## FR-WQ-06 — Progi

System automatycznie identyfikuje:

- wartość prawidłową;
- wartość zbliżającą się do progu;
- przekroczenie;
- niekorzystny trend.

Wartości graniczne muszą być wersjonowane oraz posiadać źródło/podstawę obowiązywania.

## FR-WQ-07 — Trend

System może obliczać podstawowy trend na podstawie serii czasowej.

Trend automatyczny informuje o zmianie danych, ale nie diagnozuje jej przyczyny.

Przykład:

> Mangan wykazuje trend wzrostowy. Aktualna wartość odpowiada 86% przyjętej wartości granicznej.

System nie powinien automatycznie stwierdzać:

> Przyczyną wzrostu jest zmiana warunków hydrogeochemicznych.

Taka ocena należy do hydrogeologa.

---

# 6. Monitoring studni

Dla każdej studni system umożliwia zapis:

- daty pomiaru;
- zwierciadła statycznego;
- zwierciadła dynamicznego;
- wydajności;
- czasu pracy/pomiaru, jeżeli dotyczy;
- uwag;
- źródła danych.

System automatycznie oblicza, jeżeli dane pozwalają:

**depresję**

oraz

**wydajność jednostkową**.

Dostępne są wykresy zmian:

- poziomu statycznego;
- poziomu dynamicznego;
- depresji;
- wydajności;
- wydajności jednostkowej.

System powinien sygnalizować m.in.:

- systematyczny spadek wydajności;
- wzrost depresji;
- istotną zmianę zwierciadła;
- brak wymaganego pomiaru.

Automatyczny komunikat ma wskazywać obserwowane zjawisko, a nie diagnozować jego przyczynę.

---

# 7. Pobór wody

System obsługuje dane:

- dobowe;
- miesięczne;
- roczne;
- dla pojedynczej studni;
- dla całego ujęcia.

Każdy rekord musi posiadać:

- okres;
- wartość;
- jednostkę;
- źródło danych.

System porównuje pobór z warunkami aktualnego pozwolenia.

Obsługiwane powinny być co najmniej:

- Qmax,h;
- Qmax,d;
- Qśr,d;
- limit roczny;
- inne limity zapisane indywidualnie.

System generuje ostrzeżenia np. przy:

- 80% limitu;
- 90% limitu;
- 100% limitu;
- przekroczeniu limitu.

Progi muszą być konfigurowalne.

---

# 8. Prognozowanie poboru

System powinien wyliczać prostą prognozę poboru do końca okresu rozliczeniowego na podstawie aktualnego tempa poboru.

Przykład:

> Pobór od początku roku: 247 000 m³  
> Limit: 365 000 m³  
> Prognoza na koniec roku: 397 000 m³  
> Prognozowane wykorzystanie limitu: 109%

System powinien ostrzec o ryzyku przekroczenia limitu **przed faktycznym przekroczeniem**.

Nie jest wymagana zaawansowana prognoza statystyczna w pierwszej wersji.

---

# 9. Pozwolenia wodnoprawne

Dla pozwolenia przechowuje się co najmniej:

- numer;
- organ;
- datę wydania;
- datę rozpoczęcia obowiązywania;
- datę końca obowiązywania;
- dokument źródłowy;
- limity poboru;
- zakres obowiązywania;
- warunki i obowiązki.

System automatycznie przypomina o zbliżającym się terminie końca pozwolenia.

Domyślnie:

- 24 miesiące;
- 12 miesięcy;
- 6 miesięcy;
- 3 miesiące;
- 1 miesiąc;
- po terminie.

Progi mają być konfigurowalne.

---

# 10. Obowiązki wynikające z pozwolenia

Jest to osobna funkcja systemu.

Pozwolenie może nakładać obowiązki, np.:

- badanie jakości wody surowej;
- pomiar zwierciadła;
- pomiar wydajności;
- odczyt wodomierza;
- okresowe przekazanie wyników;
- wykonanie określonych pomiarów;
- wykonanie innych czynności wskazanych w decyzji.

Każdy obowiązek powinien posiadać:

- nazwę;
- opis;
- ujęcie lub studnię, której dotyczy;
- podstawę — pozwolenie;
- częstotliwość;
- pierwszy/najbliższy termin;
- sposób potwierdzenia wykonania;
- status.

Przykład:

> **Pomiar zwierciadła — S-2**  
> Wymagany raz na kwartał  
> Termin: 31.12.2026  
> Pozostało: 18 dni  
> [Dodaj pomiar]

Po wykonaniu odpowiedniej czynności system powinien, jeśli to możliwe, automatycznie oznaczyć obowiązek jako wykonany i wyliczyć następny termin.

---

# 11. Alerty

Alert musi być wynikiem konkretnej reguły.

Podstawowe kategorie v1:

### Jakość
- przekroczenie;
- zbliżenie do wartości granicznej;
- niekorzystny trend;
- wynik mikrobiologiczny wymagający reakcji.

### Studnia
- spadek wydajności;
- wzrost depresji;
- istotna zmiana zwierciadła;
- brak pomiaru.

### Pobór
- 80/90/100% limitu;
- przekroczenie;
- prognozowane przekroczenie;
- systematyczny wzrost poboru.

### Pozwolenia
- zbliżający się koniec ważności;
- pozwolenie wygasłe.

### Obowiązki
- zbliżający się termin;
- termin przypadający dzisiaj;
- obowiązek po terminie;
- brak wymaganego wyniku/dokumentu.

System nie może tworzyć wielu identycznych aktywnych alertów dotyczących tego samego zdarzenia.

---

# 12. Poziomy statusów

Interfejs klienta powinien używać prostych statusów:

**OK**

**Obserwacja**

**Wymaga działania**

**Brak danych**

Kolory mogą wspierać status, ale kolor nie może być jedyną metodą przekazywania informacji.

---

# 13. Konsultacja hydrogeologiczna

Przy alertach wymagających interpretacji klient powinien mieć możliwość wybrania:

**Skonsultuj z hydrogeologiem**

System zapisuje:

- klienta;
- ujęcie;
- studnię, jeśli dotyczy;
- alert;
- wiadomość klienta;
- datę zgłoszenia;
- status konsultacji.

Hydrogeolog widzi konsultacje na swoim dashboardzie.

---

# 14. Dashboard hydrogeologa

Dashboard wewnętrzny powinien pokazywać przede wszystkim wyjątki wymagające pracy człowieka.

Przykładowe sekcje:

- alerty wysokiego priorytetu;
- konsultacje od klientów;
- nowe analizy wymagające kontroli;
- ryzyko przekroczenia poboru;
- pogarszające się parametry studni;
- pozwolenia wymagające działań;
- zaległe obowiązki;
- braki danych.

Celem jest uniknięcie konieczności ręcznego przeglądania wszystkich ujęć.

---

# 15. Raporty

## 15.1. Raport automatyczny

Generowany bez konieczności ręcznego przygotowywania przez hydrogeologa.

Może być miesięczny, kwartalny lub generowany na żądanie.

Powinien zawierać:

- okres;
- status ujęcia;
- jakość wody;
- pobór;
- najważniejsze trendy;
- stan studni;
- pozwolenie;
- obowiązki;
- aktywne alerty;
- maksymalnie kilka istotnych wykresów.

Raport nie powinien zawierać automatycznej diagnozy przyczyn zjawisk.

## 15.2. Raport ekspercki

Może zawierać:

- interpretację;
- ocenę hydrogeologiczną;
- zalecenia;
- komentarz specjalisty.

Wymaga zatwierdzenia hydrogeologa.

---

# 16. Dokumenty i audyt

Każdy dokument źródłowy musi być zachowany.

Nie wolno nadpisywać dokumentu bez zachowania historii.

Należy zapisywać istotne operacje:

- kto dodał dane;
- kiedy;
- kto je zmienił;
- poprzednią wartość;
- zatwierdzenie;
- zamknięcie alertu;
- wygenerowanie raportu;
- konsultację.

---

# 17. Wymagania UX

System musi być projektowany przede wszystkim dla użytkownika, który nie jest specjalistą IT.

Wymagania obowiązkowe:

1. Dashboard po zalogowaniu zamiast rozbudowanego menu administracyjnego.
2. Najważniejsze informacje widoczne bez przechodzenia przez wiele ekranów.
3. Komunikaty w języku użytkownika, np.:
   - „Brakuje pomiaru zwierciadła”,
   - nie: „measurement schedule overdue”.
4. Alert powinien prowadzić bezpośrednio do czynności rozwiązującej problem.
5. Minimalna liczba pól formularzy.
6. Listy wyboru zamiast ręcznego wpisywania, gdy istnieje słownik.
7. Automatyczne uzupełnianie znanych danych.
8. Responsywny interfejs.
9. Dodanie pomiaru lub dokumentu musi być możliwe również z telefonu.
10. Funkcje zaawansowane powinny być ukryte przed zwykłym użytkownikiem klienta.
11. System powinien zapobiegać przypadkowemu usunięciu danych.
12. Każdy istotny komunikat powinien informować użytkownika również, **co powinien zrobić dalej**.

---

# 18. Wymagania techniczne

Preferowana architektura:

- Python;
- Django;
- PostgreSQL;
- PostGIS;
- Django Templates + HTMX;
- Celery;
- Redis;
- Docker Compose;
- QGIS jako narzędzie eksperckie.

Aplikacja ma być modularnym monolitem.

Nie ma potrzeby stosowania mikroserwisów ani osobnego SPA w pierwszej wersji.

PostgreSQL/PostGIS jest głównym źródłem danych.

QGIS korzysta bezpośrednio z danych PostGIS.

---

# 19. Bezpieczeństwo

Wymagane:

- uwierzytelnienie użytkowników;
- izolacja danych klientów;
- kontrola uprawnień po stronie backendu;
- HTTPS;
- rejestr operacji;
- backup bazy;
- backup dokumentów;
- brak publicznych URL umożliwiających pobranie dokumentu bez autoryzacji.

Bezpieczeństwo wieloklientowe należy uwzględnić od pierwszej migracji bazy danych.

---

# 20. Poza zakresem pierwszej wersji

Nie są wymagane:

- SCADA;
- automatyczna telemetria;
- integracja API z laboratoriami;
- aplikacja natywna Android/iOS;
- SMS;
- płatności;
- fakturowanie;
- publiczne API;
- pełna ocena ryzyka;
- PBW;
- zaawansowane modele hydrogeologiczne;
- automatyczna diagnoza przyczyn problemów;
- automatyczne podejmowanie decyzji eksperckich.

Architektura nie powinna jednak uniemożliwiać dodania tych funkcji później.

---

# 21. Minimalne kryterium odbioru v1

Pierwsza wersja jest gotowa do pilotażu, gdy można:

1. utworzyć klienta i użytkownika klienta;
2. utworzyć ujęcie i minimum dwie studnie;
3. zalogować się jako klient i widzieć wyłącznie własne dane;
4. dodać analizę wody;
5. zobaczyć wyniki i wykres historyczny;
6. wykryć przekroczenie lub zbliżenie do progu;
7. dodać pomiar zwierciadła i wydajności;
8. zobaczyć ich historię;
9. wprowadzić pobór;
10. porównać pobór z pozwoleniem;
11. wygenerować prognozę wykorzystania limitu;
12. zapisać pozwolenie wodnoprawne;
13. utworzyć minimum jeden cykliczny obowiązek wynikający z pozwolenia;
14. wygenerować alert o zbliżającym się terminie;
15. pokazać alert klientowi;
16. umożliwić zgłoszenie konsultacji;
17. pokazać konsultację na dashboardzie hydrogeologa;
18. wygenerować automatyczny raport PDF;
19. odtworzyć historię najważniejszych zmian;
20. odtworzyć bazę i dokument z backupu.

---

# 22. Podstawowa zasada projektowa

HydroDesk nie powinien wymagać od użytkownika znajomości hydrogeologii ani struktury systemu.

Aplikacja ma tłumaczyć dane na prostą informację:

**co jest w porządku → co się zmienia → co wymaga uwagi → co należy zrobić → kiedy warto skonsultować się z hydrogeologiem.**

Automatyzacja zajmuje się rutynowym monitoringiem.

Hydrogeolog zajmuje się interpretacją, nietypowymi sytuacjami i zaleceniami eksperckimi.
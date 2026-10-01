# 03 — Model danych

PostgreSQL 16 + PostGIS. Schemat `public` dla danych aplikacji, `gis` dla widoków dla QGIS, `audit` dla rejestru operacji.

## 1. Konwencje

| Element | Konwencja |
|---------|-----------|
| Klucz główny | `UUIDField(primary_key=True)`, UUIDv7 generowane w aplikacji (sortowalne) |
| Tenant | `organization_id UUID NOT NULL` w **każdej** tabeli danych klienta |
| Znaczniki | `created_at`, `created_by`, `updated_at`, `updated_by` |
| Usuwanie | miękkie: `deleted_at`, `deleted_by`; brak `DELETE` dla ról aplikacyjnych na tabelach danych |
| Status danych | `data_status`: `draft` / `submitted` / `approved` / `rejected` |
| Źródło | `source`: `manual` / `import` / `ocr` / `telemetry` + `source_document_id` |
| Nazwy | snake_case, liczba pojedyncza (`well`, `permit`) |
| Geometria | GeoDjango `PointField(srid=2180)` (PUWG 1992), widoki w `gis` udostępniają też 4326 |
| Wartości liczbowe | `NUMERIC` (nie `float`) dla wyników analiz i limitów |
| Czas | `timestamptz` dla zdarzeń, `date` dla dat pomiaru/okresów, `daterange`/`tstzrange` dla okresów ważności |

## 2. ERD — rdzeń

```mermaid
erDiagram
    ORGANIZATION ||--o{ MEMBERSHIP : ma
    USER ||--o{ MEMBERSHIP : należy
    USER ||--o{ STAFF_ASSIGNMENT : "obsługuje (hydrogeolog)"
    ORGANIZATION ||--o{ STAFF_ASSIGNMENT : przypisany
    ORGANIZATION ||--o{ INTAKE : posiada
    INTAKE ||--o{ WELL : posiada
    INTAKE ||--o{ PERMIT : "objęte"
    PERMIT ||--o{ PERMIT_LIMIT : definiuje
    PERMIT ||--o{ OBLIGATION : nakłada
    PERMIT }o--o{ WELL : "zakres (permit_scope)"
    OBLIGATION ||--o{ OBLIGATION_OCCURRENCE : "terminy"
    DOCUMENT ||--o{ DOCUMENT_VERSION : wersje

    ORGANIZATION {
        uuid id PK
        text name
        text nip
        text status
    }
    USER {
        uuid id PK
        citext email UK
        text password_hash
        text full_name
        text system_role "admin|hydrogeologist|operator|client"
        bool is_active
    }
    MEMBERSHIP {
        uuid user_id FK
        uuid organization_id FK
        text org_role "owner|member"
    }
    STAFF_ASSIGNMENT {
        uuid user_id FK
        uuid organization_id FK
    }
    INTAKE {
        uuid id PK
        uuid organization_id FK
        text name
        text code
        geometry location
    }
    WELL {
        uuid id PK
        uuid organization_id FK
        uuid intake_id FK
        text code "S-1"
        numeric depth_m
        numeric ground_elevation_m
        geometry location
        text status
    }
    PERMIT {
        uuid id PK
        uuid organization_id FK
        uuid intake_id FK
        text number
        text authority
        date issued_on
        daterange validity
        uuid source_document_id FK
    }
    PERMIT_LIMIT {
        uuid id PK
        uuid permit_id FK
        text limit_type "q_max_h|q_max_d|q_avg_d|annual|custom"
        numeric value
        text unit
        uuid well_id FK "NULL = całe ujęcie"
    }
    OBLIGATION {
        uuid id PK
        uuid permit_id FK
        uuid well_id FK
        text name
        text obligation_type
        text recurrence "RRULE"
        date next_due_on
        text fulfilment_mode "auto|manual"
        text status
    }
    OBLIGATION_OCCURRENCE {
        uuid id PK
        uuid obligation_id FK
        date due_on
        timestamptz fulfilled_at
        text evidence_type
        uuid evidence_id
    }
    DOCUMENT {
        uuid id PK
        uuid organization_id FK
        text title
        text doc_type
        uuid intake_id FK
        uuid well_id FK
        uuid current_version_id FK
    }
    DOCUMENT_VERSION {
        uuid id PK
        uuid document_id FK
        int version_no
        text storage_key
        text sha256
        text mime_type
        bigint size_bytes
    }
```

## 3. ERD — dane pomiarowe

```mermaid
erDiagram
    PARAMETER ||--o{ REFERENCE_VALUE : "progi"
    REFERENCE_VALUE_SET ||--o{ REFERENCE_VALUE : zawiera
    UNIT ||--o{ PARAMETER : "jednostka domyślna"
    WATER_SAMPLE ||--o{ WATER_RESULT : wyniki
    PARAMETER ||--o{ WATER_RESULT : dotyczy
    WELL ||--o{ WATER_SAMPLE : "punkt poboru"
    WELL ||--o{ WELL_MEASUREMENT : pomiary
    WELL ||--o{ ABSTRACTION_RECORD : pobór

    PARAMETER {
        uuid id PK
        text code "Mn, Fe, NO3"
        text name_pl
        text group "fizykochemiczne|mikrobiologiczne"
        uuid default_unit_id FK
    }
    UNIT {
        uuid id PK
        text symbol "mg/l, µg/l"
        text dimension
        numeric factor_to_base
    }
    REFERENCE_VALUE_SET {
        uuid id PK
        text name "Rozp. MZ 2017"
        text legal_basis
        daterange validity
        uuid organization_id "NULL = globalny"
        int version
    }
    REFERENCE_VALUE {
        uuid id PK
        uuid set_id FK
        uuid parameter_id FK
        numeric limit_max
        numeric limit_min
        numeric warning_ratio "np. 0.8"
        uuid unit_id FK
    }
    WATER_SAMPLE {
        uuid id PK
        uuid organization_id FK
        uuid intake_id FK
        uuid well_id FK
        date sampled_on
        text sampling_point
        text laboratory
        uuid source_document_id FK
        text data_status
    }
    WATER_RESULT {
        uuid id PK
        uuid sample_id FK
        uuid parameter_id FK
        text raw_value "'<0,05'"
        text raw_unit "'mg/l'"
        text qualifier "'<','>','<=','>=',NULL"
        numeric value_normalized "0.05"
        uuid unit_id FK
        text method
        numeric uncertainty
    }
    WELL_MEASUREMENT {
        uuid id PK
        uuid organization_id FK
        uuid well_id FK
        timestamptz measured_at
        numeric static_level_m
        numeric dynamic_level_m
        numeric yield_m3h
        numeric duration_h
        numeric drawdown_m "GENERATED"
        numeric specific_yield "GENERATED"
        text source
        text notes
        text data_status
    }
    ABSTRACTION_RECORD {
        uuid id PK
        uuid organization_id FK
        uuid intake_id FK
        uuid well_id FK "NULL = całe ujęcie"
        text granularity "day|month|year"
        daterange period
        numeric volume
        text unit "m3"
        text source
        text data_status
    }
```

### 3.1. Wartość źródłowa vs znormalizowana (FR-WQ-03)

`<0,05 mg/l` zapisujemy jako:

| kolumna | wartość |
|---------|---------|
| `raw_value` | `<0,05` |
| `raw_unit` | `mg/l` |
| `qualifier` | `<` |
| `value_normalized` | `0.05` |
| `unit_id` | `mg/l` (jednostka bazowa parametru) |

Reguły progów biorą pod uwagę `qualifier`: wynik `<0,05` przy progu `0,05` **nie** jest przekroczeniem; `>0,5` przy progu `0,5` **jest** przekroczeniem. Wykres rysuje takie punkty innym markerem.

### 3.2. Wielkości wyliczane (studnie)

Kolumny generowane (`GENERATED ALWAYS AS ... STORED`, w Django `models.GeneratedField(db_persist=True)`):

- `drawdown_m = dynamic_level_m - static_level_m` (gdy oba niepuste; zwierciadło mierzone jako głębokość od terenu),
- `specific_yield = yield_m3h / drawdown_m` (gdy `drawdown_m > 0`), jednostka m³/h/m.

### 3.3. Wersjonowanie progów (FR-WQ-06)

- `reference_value_set` ma `validity` (zakres dat), `legal_basis` (źródło) i `version`.
- Wynik oceniany jest wg zestawu obowiązującego w dniu `sampled_on`.
- Klient może mieć zestaw indywidualny (`organization_id` niepusty) — ma pierwszeństwo przed globalnym.
- Zestawów zatwierdzonych nie edytujemy — tworzymy nową wersję.

## 4. ERD — alerty, konsultacje, raporty, audyt

```mermaid
erDiagram
    RULE_DEFINITION ||--o{ RULE_CONFIG : "konfiguracja"
    RULE_DEFINITION ||--o{ ALERT : generuje
    ALERT ||--o{ ALERT_EVENT : historia
    ALERT ||--o| CONSULTATION : "może mieć"
    CONSULTATION ||--o{ CONSULTATION_MESSAGE : wiadomości
    REPORT }o--|| DOCUMENT : "plik PDF"

    RULE_DEFINITION {
        text key PK "quality.exceedance"
        text category
        text description_pl
        jsonb default_params
    }
    RULE_CONFIG {
        uuid id PK
        text rule_key FK
        uuid organization_id "NULL = globalna"
        uuid intake_id
        uuid well_id
        jsonb params "np. thresholds: [0.8,0.9,1.0]"
        bool enabled
    }
    ALERT {
        uuid id PK
        uuid organization_id FK
        text rule_key FK
        text dedup_key
        text severity "info|watch|action"
        text status "open|acknowledged|resolved|auto_resolved"
        text subject_type "well|intake|permit|obligation|parameter"
        uuid subject_id
        text title_pl
        text message_pl
        text next_step_pl
        text action_url
        jsonb facts
        timestamptz first_seen_at
        timestamptz last_seen_at
        timestamptz resolved_at
    }
    ALERT_EVENT {
        uuid id PK
        uuid alert_id FK
        text event "created|updated|acknowledged|resolved|reopened"
        uuid actor_id
        jsonb payload
    }
    CONSULTATION {
        uuid id PK
        uuid organization_id FK
        uuid intake_id FK
        uuid well_id FK
        uuid alert_id FK
        uuid requested_by FK
        uuid assigned_to FK
        text status "new|in_progress|answered|closed"
    }
    CONSULTATION_MESSAGE {
        uuid id PK
        uuid consultation_id FK
        uuid author_id FK
        text body
    }
    REPORT {
        uuid id PK
        uuid organization_id FK
        uuid intake_id FK
        text kind "automatic|expert"
        daterange period
        text status "generating|ready|draft|approved|failed"
        uuid document_id FK
        uuid approved_by
    }
    AUDIT_LOG {
        bigint id PK
        timestamptz at
        uuid actor_id
        uuid organization_id
        text action "sample.created, alert.resolved"
        text entity_type
        uuid entity_id
        jsonb before
        jsonb after
        inet ip
        text request_id
    }
    OUTBOX {
        bigint id PK
        text event_type
        jsonb payload
        timestamptz created_at
        timestamptz dispatched_at
    }
```

### 4.1. Deduplikacja alertów (sek. 11)

```sql
CREATE UNIQUE INDEX alert_active_dedup
    ON alert (organization_id, dedup_key)
    WHERE status IN ('open', 'acknowledged');
```

`dedup_key` = `rule_key` + identyfikator przedmiotu + wariant, np.
`abstraction.limit_usage:intake=<id>:limit=annual:level=90`.
Ewaluacja robi `INSERT ... ON CONFLICT DO UPDATE SET last_seen_at, facts, severity`.

## 5. Wieloklientowość (izolacja danych)

Szczegóły i uzasadnienie: [ADR-0003](adr/0003-wieloklientowosc-rls.md).

1. Każda tabela danych klienta ma `organization_id NOT NULL` + indeks.
2. Tabele potomne (np. `water_result`) też mają `organization_id` (denormalizacja) — prostsze i szybsze polityki RLS.
3. Spójność: klucze obce złożone `(organization_id, intake_id) REFERENCES intake (organization_id, id)` — nie da się podpiąć studni pod ujęcie innego klienta. Django nie obsługuje złożonych FK w ORM, więc: zwykły `ForeignKey` + `UniqueConstraint(organization_id, id)` na rodzicu + dodatkowy constraint złożony przez własną operację migracji (`core.migrations_ops.CompositeForeignKey`).
4. RLS włączone i wymuszone (`FORCE ROW LEVEL SECURITY`) na każdej tabeli danych:

```sql
ALTER TABLE well ENABLE ROW LEVEL SECURITY;
ALTER TABLE well FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON well
    USING (
        current_setting('app.bypass_rls', true) = 'on'
        OR organization_id = ANY (string_to_array(current_setting('app.org_ids', true), ',')::uuid[])
    )
    WITH CHECK (
        current_setting('app.bypass_rls', true) = 'on'
        OR organization_id = ANY (string_to_array(current_setting('app.org_ids', true), ',')::uuid[])
    );
```

5. `app.org_ids` ustawiane per transakcja (`SET LOCAL`, w `TenantMiddleware` / `TenantTask`) z kontekstu użytkownika:
   - użytkownik klienta → jego organizacje z `membership`,
   - hydrogeolog / operator → organizacje z `staff_assignment`,
   - admin → `app.bypass_rls = on` (tylko dla operacji administracyjnych, logowane w audycie),
   - zadania Celery → jawnie podany zakres organizacji zadania.
6. Brak ustawionego kontekstu ⇒ brak wierszy (bezpieczny domyślny stan).

## 6. Role bazodanowe

| Rola | Uprawnienia |
|------|-------------|
| `hydrodesk_owner` | właściciel schematu, `manage.py migrate` — nie używana przez aplikację w runtime |
| `hydrodesk_app` | `SELECT/INSERT/UPDATE` na tabelach danych, **bez** `DELETE` na danych pomiarowych, podlega RLS (tabele systemowe Django — sesje, auth, celery-beat — bez RLS) |
| `hydrodesk_gis_ro` | `SELECT` tylko na widokach `gis.*` (QGIS), widoki z `security_barrier` |
| `hydrodesk_backup` | `pg_dump` |

## 7. Widoki dla QGIS

```sql
CREATE VIEW gis.wells WITH (security_barrier) AS
SELECT w.id, o.name AS client, i.name AS intake, w.code, w.status,
       w.location AS geom_2180,
       ST_Transform(w.location, 4326) AS geom_4326,
       lm.measured_at AS last_measurement_at, lm.static_level_m, lm.yield_m3h
FROM well w
JOIN intake i ON i.id = w.intake_id
JOIN organization o ON o.id = w.organization_id
LEFT JOIN LATERAL (
    SELECT * FROM well_measurement m
    WHERE m.well_id = w.id AND m.deleted_at IS NULL
    ORDER BY measured_at DESC LIMIT 1
) lm ON true
WHERE w.deleted_at IS NULL;
```

## 8. Historia zmian danych

- **Dokumenty**: każdy upload = nowy `document_version`; `document.current_version_id` wskazuje aktualną; pliki niezmienne w S3.
- **Dane zatwierdzone** (`data_status = approved`): edycja tworzy rekord historii (`django-simple-history`) i wpis w `audit_log`; użytkownik klienta nie może edytować zatwierdzonych — może zgłosić korektę.
- **Usuwanie**: tylko miękkie, z potwierdzeniem w UI i wpisem audytowym; przywracanie przez hydrogeologa/admina.

# Hvordan fikse Railway Database - Manglende kolonner

## Problem
Railway produksjon får feilmeldingen:
```
(psycopg2.errors.UndefinedColumn) column users.reset_token does not exist
```

Dette skjer fordi Railway databasen mangler flere kolonner som User modellen forventer.

## Løsning

### Alternativ 1: Bruk Railway CLI (Anbefalt)
1. Installer Railway CLI hvis du ikke har det:
   ```bash
   npm install -g @railway/cli
   ```

2. Logg inn på Railway:
   ```bash
   railway login
   ```

3. Koble til ditt prosjekt:
   ```bash
   railway link
   ```

4. Kjør database migration script:
   ```bash
   railway run python fix_railway_columns.py
   ```

### Alternativ 2: Fra Railway Dashboard
1. Gå til Railway dashboard: https://railway.app
2. Velg ditt aksjeradar prosjekt
3. Gå til "Deployments" > "Create New Deployment"
4. Under "Build Command" skriv: `python fix_railway_columns.py`
5. Deploy

### Alternativ 3: Manuel SQL (Ekspert)
Hvis du har tilgang til Railway PostgreSQL database direkte:

```sql
-- Legg til manglende kolonner
ALTER TABLE users ADD COLUMN reset_token VARCHAR(100);
ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP;
ALTER TABLE users ADD COLUMN language VARCHAR(10) DEFAULT 'no';
ALTER TABLE users ADD COLUMN notification_settings TEXT;
ALTER TABLE users ADD COLUMN two_factor_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN two_factor_secret VARCHAR(32);
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN is_locked BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN reports_used_this_month INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN last_reset_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;
```

## Hva skriptet gjør
`fix_railway_columns.py` scriptet:

1. ✅ Sjekker eksisterende kolonner i users tabellen
2. ✅ Legger til manglende kolonner automatisk
3. ✅ Håndterer både PostgreSQL og SQLite syntaks
4. ✅ Oppretter test bruker (helene721@gmail.com) hvis den ikke finnes
5. ✅ Tester at login fungerer
6. ✅ Gir detaljert rapport om hva som ble fikset

## Verifisering
Etter at scriptet har kjørt:

1. Sjekk Railway deployment logs
2. Gå til https://aksjeradar.trade/login
3. Logg inn med: helene721@gmail.com / password123
4. Ingen "column does not exist" feil skal oppstå

## Fallback System
Koden har også en fallback-system:
- Hvis kolonner fortsatt mangler, vil User modellen gi standardverdier
- Login vil fortsatt fungere, men med begrenset funksjonalitet
- Feilmeldinger vil være mer brukervennlige

## Fremtidige Deployments
Når du deployer endringer fremover:
- Alle nye kolonner vil automatisk håndteres av SQLAlchemy
- Fallback-systemet sørger for bakoverkompatibilitet
- Ingen manuelle database-endringer trengs

---

**Kontakt support** hvis problemet vedvarer etter å ha fulgt disse stegene.

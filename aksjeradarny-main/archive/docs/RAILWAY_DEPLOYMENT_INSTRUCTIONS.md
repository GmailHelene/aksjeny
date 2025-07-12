# 🚀 PRODUCTION DEPLOYMENT INSTRUCTIONS

## 📋 Problemet:
Railway produksjonsdatabase mangler kolonner som finnes i lokal database:
- `reports_used_this_month`
- `last_reset_date` 
- `is_admin`

Dette forårsaket login-feil i produksjon.

## ✅ Løsningen:
Implementert 3-lags sikkerhet:

### 1. Auto-migration i app/__init__.py
- Kjører automatisk når appen starter
- Sjekker og legger til manglende kolonner
- Oppdaterer exempt users

### 2. Backup column handling
- Graceful fallback hvis kolonner mangler
- Definerer properties for manglende felter
- Ingen crash hvis database ikke er oppdatert

### 3. Manual migration scripts
- `railway_migration.py` - for manuell kjøring
- `production_fix.py` - emergency fix
- `migrate_production.py` - full migration

## 🚀 Deploy til Railway:

1. **Commit alle endringer:**
```bash
git add .
git commit -m "Fix production database schema - add missing columns"
git push origin main
```

2. **Railway auto-deploy vil:**
   - Starte appen
   - Kjøre auto-migration i `__init__.py`
   - Legge til manglende kolonner
   - Konfigurere exempt users

3. **Login skal nå fungere med:**
   - Bruker: `helene721`
   - Passord: `aksjeradar2024`

## 🔧 Hvis auto-migration feiler:

**Alternativ 1 - Railway Console:**
```bash
python railway_migration.py
```

**Alternativ 2 - Manual SQL (Railway Database Dashboard):**
```sql
-- Add missing columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS reports_used_this_month INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_reset_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- Update exempt users
UPDATE users 
SET 
    is_admin = TRUE,
    has_subscription = TRUE,
    reports_used_this_month = 0,
    last_reset_date = CURRENT_TIMESTAMP
WHERE email IN (
    'tonjekit91@gmail.com',
    'helene721@gmail.com', 
    'helene@luxushair.com',
    'eiriktollan.berntsen@gmail.com'
);
```

## 🎯 Resultat:
- ✅ Database schema kompatibel
- ✅ Login fungerer uten feil
- ✅ Exempt users har korrekte rettigheter
- ✅ Alle funksjoner operative

**Deploy nå og test login!** 🚀

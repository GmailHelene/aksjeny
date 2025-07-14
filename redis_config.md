# Redis Configuration for Aksjeradar

## Current Status: OPTIONAL
Redis cache er nå valgfritt og vil ikke lage advarsler hvis ikke tilgjengelig.

## Aktivering av Redis (valgfritt)

### Lokalt (Development)
```bash
# Installer Redis
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server

# Test Redis
redis-cli ping
```

### Produksjon (Railway)
Legg til miljøvariabler i Railway:
```
REDIS_URL=redis://your-redis-url:6379
CACHE_LOGGING=true  # For å se cache status
```

### Development med logging
```bash
export FLASK_ENV=development
export CACHE_LOGGING=true
```

## Fallback
Hvis Redis ikke er tilgjengelig, brukes in-memory cache automatisk.
Dette er perfekt for development og små produksjonsmiljøer.

## Benefits med Redis
- Persistent cache mellom app restarts
- Delt cache mellom flere app instances  
- Bedre ytelse for store datamengder
- Innebygd expiration/TTL støtte

## Uten Redis
- In-memory cache fungerer perfekt
- Ingen eksterne avhengigheter
- Enklere deployment
- Cache nullstilles ved app restart

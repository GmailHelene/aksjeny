# Aksjeradar Ny - Opprydding og Reorganisering

Dette dokumentet beskriver den nye prosjektstrukturen og oppryddingsrutiner.

## Struktur
```
aksjeradarny-main/
│
├── app.py
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── CLEANUP.md
├── OPPRYDDING.MD
├── models/
│   └── __init__.py
├── routes/
│   └── basic_routes.py
├── services/
│   └── __init__.py
├── app/
│   └── __init__.py  # main application package
├── templates/  # HTML/Jinja2 templates
│   └── base.html
├── static/     # CSS, JS, images
│   └── css/
│   └── js/
├── tests/
│   ├── __init__.py
│   ├── test_all_endpoints_access.py
│   └── test_frontend_urls_access.py
├── migrations/
└── archive/
```

## Ryddingsrutiner
- Følg [](#dependencies) for avhengigheter
- Følg [](#modularisering) for kodeorganisering

## Avhengigheter
- production: `requirements.txt`
- utvikling/test: `requirements-dev.txt`

## Kodeorganisering
- `routes/`: Flask Blueprints
- `services/`: forretningslogikk
- `models/`: SQLAlchemy-modeller
- `tests/`: enhetstester og integrasjonstester

## Migrasjoner
- Oppdater migrasjoner med `flask db migrate`
- Hold `migrations/`-mappen ren

## Arkiv
- Flytt gamle notebooks til `archive/`

## CI/CD, Docker, Linting, osv.
Se OPPRYDDING.MD for fullstendig sjekkliste.

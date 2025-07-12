# Hvordan teste Aksjeradar-appen lokalt på Windows

Denne guiden forklarer hvordan du kan teste Aksjeradar-appen og dens endepunkter lokalt på Windows-maskinen din.

## Forutsetninger

1. Python 3.8 eller nyere installert
2. pip installert
3. Git installert (valgfritt, for versionskontroll)

## Steg for å teste appen lokalt

### Alternativ 1: Bruk test_lokalt.bat (Anbefalt)

Dette er den enkleste måten å teste appen på. Den automatiserer oppsettet og gir deg flere testmuligheter.

1. Åpne en Command Prompt (cmd) som administrator
2. Naviger til prosjektmappen:
   ```
   cd "c:\Users\helen\Desktop\AKSJERADAR-NY-APP"
   ```
3. Kjør test_lokalt.bat:
   ```
   test_lokalt.bat
   ```
4. Velg testmetode fra menyen:
   - **1) Start appen lokalt** - Starter Flask-serveren og åpner nettleseren
   - **2) Start appen lokalt med dummy-data** - Bruker genererte testdata uavhengig av API-tilgjengelighet
   - **3) Test alle endepunkter** - Tester alle API-endepunkter
   - **4) Test PWA-funksjonalitet** - Sjekker at PWA-implementasjonen er korrekt
   - **5) Test tjenester (API-tilkobling)** - Tester at API-tjenester fungerer
   - **6) Start appen og test endepunkter samtidig** - Starter appen og tester endepunkter

### Alternativ 2: Manuell testing

Hvis du foretrekker å kjøre kommandoene manuelt:

#### Installer avhengigheter

```
pip install -r requirements.txt
```

#### Start Flask-serveren

```
python run.py
```

Dette vil starte serveren på http://localhost:5000

#### Test endepunkter

Åpne en ny Command Prompt og kjør:

```
python test_endpoints.py http://localhost:5000
```

## Viktige endepunkter å teste

Her er en liste over de viktigste endepunktene i appen:

| Endepunkt | Beskrivelse | URL |
|-----------|-------------|-----|
| Hovedside | Forsiden med oversikt | http://localhost:5000/ |
| Aksjer | Oversikt over aksjer | http://localhost:5000/stocks/ |
| Teknisk analyse | Tekniske indikatorer | http://localhost:5000/analysis/technical |
| AI-analyse | AI-drevet analyse | http://localhost:5000/analysis/ai |
| Portefølje | Porteføljeoversikt | http://localhost:5000/portfolio/ |

## Teste en spesifikk aksje

For å teste data for en spesifikk aksje:

1. Start appen lokalt
2. Gå til http://localhost:5000/stocks/
3. Søk etter en aksje (f.eks. EQNR.OL, AAPL, TSLA)
4. Sjekk at detaljer og diagrammer lastes korrekt

## Feilsøking

### Problem: Appen starter ikke

Kontroller følgende:
- Er alle avhengigheter installert? Kjør `pip install -r requirements.txt`
- Er port 5000 ledig? Prøv en annen port ved å endre i run.py
- Sjekk feilmeldinger i terminalen

### Problem: Endepunktene svarer ikke

Kontroller følgende:
- Kjører Flask-serveren?
- Er URL-ene korrekte?
- Sjekk feillogger i terminalen der serveren kjører

### Problem: Data vises ikke korrekt

- Sjekk nettverkstilkoblingen (API-kall til Yahoo Finance)
- Se etter Javascript-feil i nettleserens utviklerverktøy (F12)
- Verifiser at JSON-dataene fra API-kall er korrekte

### Problem: "Error fetching stock data" eller lignende feilmeldinger

Hvis du ser feilmeldinger relatert til Yahoo Finance API:
- Dette er vanligvis forårsaket av API-begrensninger eller nettverksproblemer
- Appen skal automatisk falle tilbake til dummy-data
- Du kan eksplisitt aktivere dummy-data ved å bruke alternativ 2 i test_lokalt.bat
- Sjekk at nettverkstilkoblingen din fungerer og at du ikke blokkeres av brannmurer

## Tips for mer avansert testing

1. **Bruk utviklerverktøyene i nettleseren**:
   - Trykk F12 i Chrome/Edge
   - Gå til "Network"-fanen for å se API-kall
   - Sjekk "Console" for feilmeldinger

2. **Test PWA-funksjonalitet**:
   - Bruk Chrome for å teste PWA-funksjonalitet
   - Gå til Hovedmenyen > Flere verktøy > Utviklerverktøy > Application > Manifest
   - Sjekk at manifest.json er korrekt

3. **Test offline-funksjonalitet**:
   - Start appen og last en side
   - Gå offline (slå av nettverkstilkoblingen)
   - Prøv å laste siden på nytt, den burde fortsatt vise innhold

4. **Teste API-tjenester direkte**:
   ```
   python test_services.py
   ```

## Dummy-data og håndtering av API-problemer

Aksjeradar-appen er designet for å håndtere situasjoner hvor Yahoo Finance API eller andre datakilder er utilgjengelige. Her er hvordan dette fungerer:

### Automatisk feilhåndtering

1. **Automatisk deteksjon**: Når appen starter, sjekker den om Yahoo Finance API er tilgjengelig
2. **Fallback til dummy-data**: Hvis API-et er utilgjengelig, aktiveres dummy-data automatisk
3. **Logging**: Se terminalen for informasjon om API-tilgjengelighet

### Manuell bruk av dummy-data

Du kan tvinge appen til å bruke dummy-data på følgende måter:

1. **Via test_lokalt.bat**: Velg alternativ 2 fra menyen
2. **Via miljøvariabel**: Sett `USE_DUMMY_DATA=True` før du starter appen:
   ```
   set USE_DUMMY_DATA=True
   python run.py
   ```

### Hvordan dummy-data fungerer

- Generer realistiske, tilfeldige data for aksjer, kryptovalutaer og valutakurser
- All funksjonalitet i appen fungerer normalt
- Dummy-dataen inkluderer historiske data, slik at diagrammer og grafer fungerer
- Du vil se en melding i terminalen som indikerer at dummy-data brukes

Dette gjør det mulig å teste og demonstrere alle appens funksjoner selv når eksterne API-er er nede eller blokkert.

## Nyttige kommandoer

- **Start appen**: `python run.py`
- **Test endepunkter**: `python test_endpoints.py`
- **Test PWA**: `python test_pwa.py`
- **Test tjenester**: `python test_services.py`
- **Full testsuite**: `run_tests.bat`

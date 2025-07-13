@echo off
echo ===================================================
echo     AKSJERADAR - LOKAL TESTMILJO
echo ===================================================
echo.

REM Sjekk om Python er installert
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo FEIL: Python er ikke installert eller ikke i PATH.
    echo Vennligst installer Python fra https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Sett opp testmiljøet
echo Setter opp testmiljø...
set DEBUG=True
set PORT=5000

REM Installer avhengigheter hvis de mangler
echo Sjekker og installerer nødvendige pakker...
pip install -r requirements.txt

echo.
echo ===================================================
echo     VELG TESTEMETODE
echo ===================================================
echo.
echo 1) Start appen lokalt
echo 2) Start appen lokalt med dummy-data
echo 3) Test alle endepunkter
echo 4) Test PWA-funksjonalitet
echo 5) Test tjenester (API-tilkobling)
echo 6) Start appen og test endepunkter samtidig
echo 7) Start i produksjonsmodus
echo 8) Test produksjonsklar (alle sjekker)
echo 9) Kjør full test suite
echo 10) Avslutt
echo.

set /p valg="Velg et alternativ (1-10): "

if "%valg%"=="1" (
    echo.
    echo Starter Aksjeradar lokalt...
    echo Åpner nettleser automatisk...
    echo Trykk CTRL+C for å avslutte serveren.
    echo.
    python run.py
    goto end
)

if "%valg%"=="2" (
    echo.
    echo Starter Aksjeradar lokalt med dummy-data...
    echo Åpner nettleser automatisk...
    echo Trykk CTRL+C for å avslutte serveren.
    echo.
    set USE_DUMMY_DATA=True
    python run.py
    goto end
)

if "%valg%"=="3" (
    echo.
    echo Tester alle endepunkter...
    echo.
    python test_endpoints.py http://localhost:5000
    goto end
)

if "%valg%"=="4" (
    echo.
    echo Tester PWA-funksjonalitet...
    echo.
    python test_pwa.py
    goto end
)

if "%valg%"=="5" (
    echo.
    echo Tester tjenester (API-tilkobling)...
    echo.
    python test_services.py
    goto end
)

if "%valg%"=="6" (
    echo.
    echo Starter appen og tester endepunkter samtidig...
    echo.
    start cmd /k "python run.py"
    timeout /t 5 /nobreak >nul
    python test_endpoints.py http://localhost:5000
    goto end
)

if "%valg%"=="7" (
    echo.
    echo Starter Aksjeradar i produksjonsmodus...
    echo.
    set FLASK_DEBUG=false
    set DEBUG=False
    set USE_DUMMY_DATA=False
    python -m app.run
    goto end
)

if "%valg%"=="8" (
    echo.
    echo Kjører produksjonssjekker...
    echo.
    python test_production.py
    goto end
)

if "%valg%"=="9" (
    echo.
    echo Kjører full test suite...
    echo.
    python -m pytest
    goto end
)

if "%valg%"=="10" (
    echo Avslutter...
    goto end
)

echo Ugyldig valg!

:end
echo.
echo Trykk en tast for å avslutte...
pause >nul

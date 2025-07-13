## Todo List

### Phas- [x] Feilsøke og etablere et stabilt testmiljø for Flask-applikasjonen- [x] Midlertidig deaktivere `@access_required` dekoratøren på relevante ruter i `main.py` for å isolere problemet.
- [x] Forenkle `create_app` funksjonen i `app/__init__.py` for å sikre en stabil oppstart i testmiljøet.
- [ ] Sørge for at databasen initialiseres korrekt for testmiljøet.
- [ ] Kjøre tester for å bekrefte at sidene laster uten 500-feil og at innholdet er til stede.
- [ ] **Isolate the `create_app` function:** Create a minimal Flask app outside the main project structure to ensure `create_app` itself works in isolation.
- [ ] **Verify Flask-SQLAlchemy and database setup:** Ensure the in-memory SQLite database is correctly initialized and accessible during tests.
- [ ] **Check template rendering:** Debug why `render_template` might be failing or returning unexpected content.
- [ ] **Review `config.py`:** Double-check all configuration settings, especially those related to database, sessions, and Flask-Login, for any inconsistencies or missing values that might cause issues in a testing environment.

### Phase 4: Feilsøke og fikse tilgangskontroll og prøveperiodelogikk
- [ ] Gjenaktivere `@access_required` og systematisk feilsøke tilgangskontroll-logikken, spesielt cookie- og sesjonshåndtering i testmiljøet.
- [ ] Implementere mock-objekter for `current_user` and `request` i testene for å simulere ulike brukertilstander (autentisert, uautentisert, prøveperiode aktiv/utløpt, abonnement aktiv).
- [ ] Skrive spesifikke tester for `_check_trial_access` og `access_required` for å dekke alle scenarier.

### Phase 5: Teste og fikse URL-er/endepunkter og språkproblemer
- [ ] Utføre omfattende testing av alle URL-er og endepunkter for å sikre at de fungerer som forventet.
- [ ] Verifisere at alt innhold vises riktig og på riktig språk (norsk).
- [ ] Identifisere og rette opp eventuelle N/A-verdier eller manglende informasjon.

### Phase 6: Teste og fikse demo/redirect-funksjonalitet for alle brukertyper
- [ ] Teste demo-funksjonaliteten for brukere med utløpt prøveperiode og aktive abonnementer.
- [ ] Verifisere at omdirigeringsfunksjonene er konsistente og fungerer korrekt for alle brukertyper.

### Phase 7: Kjøre omfattende testing og validering
- [ ] Utføre en fullstendig regresjonstest for å sikre at ingen nye feil er introdusert.
- [ ] Gjennomføre ytelsestester for å identifisere flaskehalser.
- [ ] Sjekke for sikkerhetssårbarheter (f.eks. XSS, CSRF).

### Phase 8: Levere resultater og oppsummering til bruker
- [ ] Kompilere en detaljert rapport over funn og løsninger.
- [ ] Presentere en oversikt over appens status og anbefalinger for fremtidige forbedringer.



# Arbeidslogg / Work In Progress Summary

**Dato:** 2025-07-12

## Hva vi har jobbet med (siste økt)

- Feilretting og forbedring av tilgangskontroll og endepunkter i Flask-appen.
- Fikset Jinja2 template-feil (`{% endblock %}` manglet i `index.html`).
- Løst problemer med blueprint-registrering og import-feil (f.eks. `StockTip`-modellen).
- Refaktorert hovedruten (`/`) til å bruke `@access_required` direkte for å sikre at tilgangskontroll alltid håndheves.
- Lagt til logging i `access_required`-dekoratøren for å feilsøke hvorfor tilgangskontroll ikke alltid blokkerer som forventet.
- Kjørt og feilet tester for tilgangskontroll (restricted/fresh users får fortsatt tilgang til hovedsiden, videre feilsøking pågår).
- Alle endringer er pushet til GitHub (branch: `main`).

## Neste steg

- Analysere logger fra `access_required` for å finne ut hvorfor tilgangskontroll ikke blokkerer uautoriserte brukere.
- Videre feilsøking og testing av tilgangskontroll for hovedsiden og andre kritiske endepunkter.
- Fullføre og verifisere at alle tilgangsregler fungerer som forventet for alle brukertyper.

## Teknisk status

- Kodebase er oppdatert og pushet til GitHub.
- Flask-app starter og de fleste endepunkter fungerer, men tilgangskontroll for hovedsiden må fortsatt forbedres.
- Logger og testresultater brukes aktivt for å feilsøke.

---

**Pausepunkt:**

Alt arbeid er lagret og pushet. Vi fortsetter feilsøking og forbedring av tilgangskontroll neste økt.

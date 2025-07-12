# Slett Tampermonkey script som ikke hører hjemme i prosjektet
rm /workspaces/aksjeradarny/static/js/enhanced-realtime.js

# Sjekk at den riktige filen eksisterer
ls -la /workspaces/aksjeradarny/app/static/js/enhanced-realtime.js

# Fjern eventuelle andre Tampermonkey-relaterte filer
find /workspaces/aksjeradarny -name "*.user.js" -type f -delete
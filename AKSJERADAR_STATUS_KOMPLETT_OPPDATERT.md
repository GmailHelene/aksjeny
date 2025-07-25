# 🚀 AKSJERADAR - KOMPLETT STATUS RAPPORT
**Oppdatert: 23. juli 2025**
NØDVENDIGE FIKS PR 25.07, I AKSJENY GITHUB REPOET:

/Demo,  ingen av knapene og funksjonene her fungerer, det  må fikses 
Spesialtilbud blokken, den må endres til info om vanlig abb og evt årsabb, og riktige priser som er 399,- og 2999,-    

Lenkene tiul kjøp hos stripe fungerr ikke,de må gå til stripe der det såtr Velg månedlig, og velg årlig

Fortsatt som uinnlogget eller bruker uten aktivt abb. har jeg tilgang til ALT for mye..jeg bør redirectes fra start til demo løsningen,og på alle ruter som skal kreve betalt abb. som egentlig er nesten alle utenom demo, login,register,prices,subscription, contact, prices oog slike, ..

Mobilnavigasjonen, altså der det står Aksjer, Analyser og Portefølje må styles riktig, nå er det aaaaalt for mye mellomrom mellom (under) hver av disse xD 

Det oppstod en feil med screeneren. Prøv igjen senere.
Får denne på /sentiment-view    og  /sentiment  (vet ikke om begge disse er nødvendige)

analysis/currency-overview
FÅr her error:
500
Teknisk feil
Det oppstod en teknisk feil. Vi jobber med å løse problemet.

Får her: 

/market-overview
tabellen helt nederst her er overflødig (den det står "Valuta Markedsoversikt" i, helt nederst, og ingen valutadata tilgjengelig. Fordi en lik tabell finnes allerede (som nesten fungerer, denne tabellen må fikses mtp Kurs og N/A..)    litt høyere opp på siden.

Popup med Navigasjonstips:  "  den blå, ønsker jeg fjernet

/stocks/list/currency (i)knappene her fungerer ikke

/stocks/details/AAPL(OG ALLE ANDRE SIKKERT)
graf/visualisering her under "Kursuvitkling" vises ikke

stocks/compare?csrf_token=IjNkOTYwMGY4OTEwZjBmYjk4ZjNmZWRmZDQ3ZjAxN2E4N2ViNjBhYTci.aILbeA.8C5cOMllspIhEuRMLKwam4wRsLY&tickers=EQNR.OL&tickers=DNB.OL&tickers=&tickers=&period=6mo&interval=1d&normalize=1
Problem her, du ser det i urlen....og funksjonen "sammenlign" fungerer heller ikke

/profile ERROR 500 her

/my-subscription  her er det feil info, som helene721 skal jeg egentlig ha premium stående på den siden

Og pruisene påd enne siden er feil.... Det skal være Måned og År, hvor Måned er 399,- og År er 2999,-
Du kan kalle begge Premium
Knappene der for "velg", fungerer heller ikke, de må lenke til riktig abb på riktig Stripe url
Knappene på samme side som viser "rediger prodil" fungerer ikke, men den ved siden av fungerer "innstillinger", så du kan fjerne knappen helt som er "rediger profil" 

/portfolio/create
teknisk feil

/portfolio/tips
Knappen "legg til tips" fungerer ikke 

/portfolio/overview
får her feilen:  Feil: Kunne ikke laste porteføljedata.

/portfolio/
Får her feilen: Det oppstod en teknisk feil ved lasting av porteføljer. Vennligst prøv igjen senere.

/analysis/screener-view
Fungerer ikke helt, under "ferdigdefinerte screener" så stå  det bare velg preset i dropdownen, men går ikke an å gjøre noe, og får error når jeg trykker på knappen under der "søk aksjer"

/analysis/
her står det ignenting under "Markedssammendrag" 


analysis/benjamin-graham
  fungerer ikke

/analysis/warren-buffett
fungerer ikke

  på /analysis/ai  så står det ingenting under "popuilære aksjer for analyse"

/analysis/technical/?symbol=eqnr
Her sår bare Avansert tardingview-style chart og laster og laster, vises ikke...

/backtest/
Her på egentlig alle funksjonene/knappene under "populære strategier" så får jeg error og de fungerer ikke...
Feil: Cannot read properties of null (reading 'getAttribute')
(eneste av de som fungerer er den siste "Auto optimaliser")

Knapper: på market-overview, og egentlig alle andre sider som har tabeller med aksjer, crypto, valuta osv, så ønsker jeg noen knapper på hver ticker, knapper som kan ta brukeren videre til andre relaterte sider for den tickereen, slik som: Detaljer, Analyse, Anbefaling, Utvikling, Kjøp, osv! Kjøp knappen kan lenke til en ekstern side hvor brukerne faktisk kan kjøpe tickeren, f.eks nordnet osv. 

på alle analysis/ ruter, , altså analysis/technical, analysis/short-analysis, osv, så må subnavigasjonen
vises, altså den som viser en "Knappe-meny" øverst på siden med knapper for "Teknisk analyse", "Prisprediksjon", "KI-analyse" osv...Nå vises denne knappe navigasjonen bare på /analysis/prediction og /analysis/ai. Kan du sørge for at den vises på alle analysis/ routes. 

Implementer fulletendig løsning for at brukere kan sette opp varsling dersom de ønsker det

Plutselig ser jeg denne beskjeden;
"Du har brukt opp dine 3 daglige analyser. Oppgrader for ubegrenset tilgang."
Dette må fjernes, som beskjed , og som funksjon.
Løsningen vår skal være slik (!):  
ALT er tilgjengelig for de som har enten mnd, eller års- abonnement betalt
For de som IKKE har det, altsåa ktivt ebtalt abbonement, eller for brukere som ikke er innlogget, så har vi en demoløsning/side med en rekke funksjoner for å vise frem appen vår, som kan testes, og forhåpentligvis føre til at brukeren vil kjøpe abbonement .
Men det er ikke noe restrictions på tid, eller antall analyser osv.
Så dette må rettes opp i. 


/analysis/recommendation
Knappene øverst her, for teknisk analyse, prisprediksjon, ki-analyse osvosv, noen av de står alt for langt unna hverandre? Samle disse knappene mer på midten på en ryddig måte

Knappene som viser en stjerne og "Favoritt" som lar brukeren legge til som favoritt / legge til i watchlist, virker ikke som at fungerer. 


"Kursutvikling" pås stocks/details/og de diverse tickersene, viser ingenting, her må det implementeres visualisering/graf

Feil ved søk etter innsidehandel data." Denne erroren får jeg når jeg tester Innsidehandel Søk på /insider-trading, 
Får også feil/fungerer heller ikke å trykke på Populære aksjer med insider aktivitet:
EQNR.OL 12 DNB.OL 11 TEL.OL 10 MOWI.OL NOR.OL AKER.OL YAR.OL STL.OL AAPL MSFT GOOGL TSLA, noen av disse på denne siden, og fungerer heller ikke å trykke på "Last inn transaksjoner"
Denne funksjonen/siden for innsidehandel, må også være mer synlig/lettere tilgjengelig, ønsker også at denne siden er i hovednavigasjonen vår

/stocks/
Denme siden,  som innlogget betalende bruker er nå veldig simpel, den er grei øverst, men under "populære aksjer" tabellen, legg gjerne til flere andre tabeller, og annen praktisk data, info osv som du tenker betalte brukere ønsker ha her


/stocks/list/currency
(i) knappen her fungerer ikke. Sjekk også andre steder etter (i) knapper og sjekk at alle fuingerer som de skal.

kontakt@aksjeradar.no og support@aksjeradar.no er feil epost, disse må endres til: kontakt@aksjeradar.trade

SPRÅKVELGER: Kan vi legge til et flagg e.l øverst eller nederst i appen som lar brukerenn endre fra norsk til engelsk språk? Sjekk isåfall til slutt at dette også fungerer, at all norsk tekst faktisk blir ovrersatt ttil engelsk tekst 

GDPR og cookies: Sjekk/implementer at dette er implementert i forhold til krav!

SEO optimalisering: Sjekk/fiks at appen er 100% SEO optimalisert for google norge! =) 

Som innlogget helene721, så ser jeg at på min "forside" som innlogget bruker, under "Personlig oversikt" så er det nok noe demo/test data, fordi det stemmer jo ikke at jeg har "lagt til" noe i watchlist osv, så dette må settes til 0, gå gjennom alle disse under "siste aktivitet", "din aktivitet", og "personlig oversikt", og gjør så det bruktes FAKTISK data fra brukeren som er innlogget med aktivt abonnement her, og ikke noe demo mockup data på dette.
Og på samme side: "Sett opp varsler
Aktiver prisvarsler for dine favorittaksjer" Dette må være en knapp som fungerer og lenker til en side hvor man får satt opp varslinger på ordentlig  (lag en side med ritkig fungerende funksjonalitet for dette, dersom det ikke finnes, og fiks lenken deretter )
Og lenken "Se full aktivitetslogg" fungerer ikke, den må fungere (lag en side med ritkig fungerende funksjonalitet for dette, dersom det ikke finnes, og fiks lenken deretter )
(Forsiden som "ikke innnlogget" bruke,r eller bruker som ikke har aktivt abbonement,  skal være demo siden)


📊 Real-time kurser
🤖 AI-analyser
📈 Porteføljesporing
🔔 Smart varsling
📱 Mobil app
Dette her i "Imponert av det du ser-banneret på demo forsiden, er i hvit tekstfarge og må være i sort text font color,, for nå synes dette nesten ikke. Og knappen i samme banner "start ditt abonnement nå" virker ikke, den må gå til siden vår for priser og abonnementer.


Teksten på 
Ofte stilte spørsmål, endre til dette:
Hvordan fungerer plattformen med abonnement?
Du får full tilgang til alle funksjoner med ditt abonnement, og det er ingen forskjell
i tilgang til full funksjonalitet om du har Premium måneds-abonnement, eller Premium års-abonnement. 

Hvordan betaler jeg?
Du kan betale med kort (Visa, Mastercard). Alle priser vises i norske kroner (kr) og er inkl. mva.

Er det bindingstid og kan jeg si opp når som helst?
Ditt abonnement fortsetter til slutten av betalingsperioden. Hvis du avslutter abonnementet ditt, løper det ut perioden du har betalt for (månedlig eller årlig), og fornyes automatisk neste periode hvis det ikke sies opp i forkant av utløpsdato for abonnert periode.


Og her er noen store konkurrenter, kan vi lære av de, og se hva de har av funksjoner og annet, og implementere 
det vi enda ikke har?:
https://www.stockmarketguides.com/
https://www.cmcmarkets.com/
https://stockanalysis.com/
https://subscriptions.seekingalpha.com/
https://www.tradingview.com/
https://www.fool.com/
https://www.morningstar.com/
https://www.ii.co.uk/ii-accounts/trading-account
https://www.etoro.com/stocks/trading-and-investing-in-stocks


- 
Rydd gjerne opp i filer vi ikke bruker lenger! 
-
Evt. implementere nødvendige sikkerhetstiltakn mtp at appen nå skal gå live , og andre ting vi evt. bør tenke på og implementere i forhold til live lansering



NYTT:
focused-dedication


production
Architecture
Observability
Logs
Settings

Share








Activity

web

Deployment successful

1 hour ago

web

Deployment successful

1 hour ago

web

Deployment restarted

1 hour ago

web

Deployment restarted

1 hour ago

web

Deployment restarted

1 hour ago

web

Deployment restarted

1 hour ago

web

Deployment restarted

1 hour ago

web

Deployment restarted

1 hour ago

web

Deployment restarted

1 hour ago

web

Deployment restarted

1 hour ago

web

Deployment restarted

1 hour ago

web

Deployment restarted

1 hour ago

web

Deployment failed

1 hour ago

web

Deployment failed
Out of Memory (OOM)


1 hour ago

web

Deployment failed
Out of Memory (OOM)


1 hour ago

web

Deployment failed

1 hour ago


Fetch More

web
Deployments
Variables
Metrics
Settings
aksjeradar.trade
europe-west4-drams3a
1 Replica




History



















web
/
8037b8d
Jul 25, 2025, 10:08 PM
Active

aksjeradar.trade

Details
Build Logs
Deploy Logs
HTTP Logs

Filter
@responseDetails:



You reached the start of the range → Jul 25, 2025, 10:08 PM




























requestId:
"fsO4rogZQgedFBy5m3z_FQ"
timestamp:
"2025-07-25T21:08:09.418976613Z"
method:
"GET"
path:
"/api/insider-trading/latest"
host:
"aksjeradar.trade"
httpStatus:
404
upstreamProto:
"HTTP/1.1"
downstreamProto:
"HTTP/2.0"
responseDetails:
""
totalDuration:
49
upstreamAddress:
"http://[fd12:c21c:387d:0:1000:40:a06b:95ee]:8080"
clientUa:
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
upstreamRqDuration:
49
txBytes:
36809
rxBytes:
1035
srcIp:
"82.146.81.188"
edgeRegion:
"europe-west4-drams3a"








requestId:
"SqW3UCm7TvCuBODqm3z_FQ"
timestamp:
"2025-07-25T21:13:59.639949401Z"
method:
"GET"
path:
"/api/insider-trading/latest"
host:
"aksjeradar.trade"
httpStatus:
404
upstreamProto:
"HTTP/1.1"
downstreamProto:
"HTTP/2.0"
responseDetails:
""
totalDuration:
265
upstreamAddress:
"http://[fd12:c21c:387d:0:1000:40:a06b:95ee]:8080"
clientUa:
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
upstreamRqDuration:
265
txBytes:
36809
rxBytes:
1035
srcIp:
"82.146.81.188"
edgeRegion:
"europe-west4-drams3a"





web | Railway

insider-trading/search og  api/insider-trading/latest har http errors 


mobilnavigasjon,dropdownen der det står ANalyser og Aksjer, har aaaalt for mye mellomrom mellom hverandre , altså mellom elementene

Forsiden som innlogget betalende bruker fungerer ikke

Ser ikke språkflagg (og funksjon som lar brukeren oversette hele appen fra norsk til engelsk)

Demosiden har en del funksjoner og knapper, men de virker ikke - det må fikses 
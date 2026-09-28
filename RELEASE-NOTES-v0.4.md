# GBO-Core v0.4

Deze release doet twee dingen. Ze herstructureert de fiscale kern van het deelmodel Belastingen rond het onderscheid tussen wat is *aangegeven* en wat is *vastgesteld*, en ze voegt een eerste pilotmodel toe: het Toestemmingenmodel voor gemeentelijke vergunningen en ontheffingen, gemaakt met Centric. Aan de aanbodzijde vervalt het bron-profiel `bd` en gaat zijn inhoud op in een verbreed `bri-plus`; aan de bevragingskant verhuizen de aangifterubrieken van de persoon naar de aanslag, zodat een afnemer een heel belastingjaar via één ingang ophaalt in plaats van via zes losse queries.

## In het kort

- Het deelmodel Belastingen kent nu `Aangifte` (wat is opgegeven of voorgevuld) naast `Aanslag` (wat de inspecteur heeft vastgesteld), met `FiscaleOpgave` als gedeeld supertype dat de rubriekrelatie draagt. De tussenlaag `BelastingjaarAangifte` vervalt.
- De VIA en BRI-plus leveren voortaan dezelfde rubrieken in een ander stadium: de VIA als `Aangifte` met status `Voorinvulling`, BRI-plus vastgesteld onder een `Aanslag`.
- Nieuw Toestemmingenmodel: 11 objecttypen en 5 enumeraties in een eigen namespace, met eigen OWL en SHACL, ontsloten via het nieuwe bron-profiel `vth`.
- Het bron-profiel `bd` vervalt; alles wat het dekte en geen voorinvulling is, staat nu in `bri-plus` (van 7 naar 30 objecttypen, van 2 naar 7 benoemde queries).
- Het bronprofiel-meta-schema krijgt `inverse: false`, waarmee een bron een objecttype uitsluitend via één pad kan aanbieden.
- Nieuwe task `publish:check` bewaakt de publicatie op een schone working tree, een `VERSION` die met de versiemappen klopt, en een HEAD die nog niet als die mike-versie is gepubliceerd.
- De site krijgt een aparte nav-kop "Informatiemodellen Pilots", met het Toestemmingenmodel eronder als "Vergunningen en Ontheffingen", los van de kern- en voorzieningenmodellen.

## Model en semantiek

De fiscale kern van v0.3 hing scheef. `BelastingAangifte` en `BelastingjaarAangifte` waren twee abstracte lagen boven elkaar terwijl alles wat GBO ontsluit jaargebonden is, dus de tussenlaag drukte niets uit dat het supertype niet ook kon dragen. Belangrijker: vermogensbestanddelen, aftrekposten, de eigen woning en het fiscaal partnerschap hingen rechtstreeks aan de persoon met een los `belastingjaar`-attribuut, terwijl het rubrieken van een opgave zijn. En de VIA werd als aangifte behandeld zonder dat het model kon uitdrukken dat een voorinvulling geen vastgesteld gegeven is.

v0.4 zet dat recht met drie klassen. `FiscaleOpgave` is een abstract supertype dat één ding doet: het draagt `belastingjaar` en de rubriekrelatie `onderdeelVan`, zodat een fiscaal feit met een enkele relatie aan zowel een aangifte als een aanslag kan hangen. Het is bewust een geconstrueerd modelbegrip; er bestaat geen wettelijke koepelterm die zowel de aangifte (AWR art. 8) als de belastingaanslag (AWR art. 2 lid 3 sub e) omvat. `Aangifte` is de opgave die de grondslag voor een aanslag vormt, in elk stadium — vooringevuld, ingediend of herzien — met de nieuwe enum `AangifteStatus`. `Aanslag` is wat de inspecteur heeft vastgesteld, met `aanslagnummer`, `dagtekening` (bepalend voor de bezwaartermijn), de bedragen en de nieuwe enum `SoortAanslag` (voorlopig, definitief, navordering, herziening).

De belastingsoort blijft de subtype-as: `AangifteInkomstenbelasting`, `AangifteSchenkbelasting` en `AangifteErfbelasting`. Het attribuut `belastingsoort` vervalt daarmee, want het dubbelde het subtype. `Aanslag` krijgt géén subtypen: alleen de aanslag inkomstenbelasting draagt de volledige rubriekenset, terwijl schenk- en erfbelasting een andere sleutel volgen — per schenking respectievelijk per nalatenschap, niet per belastingjaar — zodat er per jaar meerdere kunnen zijn.

De rubriekrelatie is optioneel en aggregerend, geen compositie: een fiscaal feit kan bij de bron bekend zijn voordat er een aangifte of aanslag over dat jaar bestaat, en de houder respectievelijk opvoerder blijft daarnaast rechtstreeks aan de persoon gerelateerd. `EigenWoning`, `FiscaalFeit` en `FiscalePartner` krijgen elk `onderdeelVan`.

Buiten de opgave blijven twee dingen bewust los. Toeslagen vallen onder de Awir met een eigen toekenningsproces en krijgen daarvoor het nieuwe attribuut `berekeningsjaar`, de sleutel waarop ze worden bevraagd; `ingangsdatum` en `einddatum` leggen de feitelijke periode binnen dat jaar vast. Renseigneringen zijn meldingen van derden op grond van AWR art. 53 die binnenkomen ver voordat er een aanslag bestaat; ze hangen rechtstreeks aan de persoon.

## Toestemmingenmodel (pilot)

Nieuw in v0.4, en het eerste model in de repo dat expliciet als pilot is gepositioneerd. Het beschrijft de door een gemeentelijk bestuursorgaan verleende toestemmingen — vergunningen en ontheffingen — als één generiek objecttype `Toestemming` met zeven concrete soorten: evenementenvergunning, straatartiestenontheffing, standplaatsvergunning, marktvergunning, gehandicaptenparkeerkaart, parkeerontheffing en ligplaatsontheffing, plus `OverigeToestemming` als restcategorie. Daarnaast `OpenbareActiviteit` en `Vaartuig` voor de contexten waar een vergunning naar verwijst.

Het model heeft een eigen namespace (`https://lod.gbo-semantiek.nl/toestemmingen`) en een eigen OWL- en SHACL-artefact naast de kern, gegenereerd door de nieuwe task `generate:toestemmingen-lod`. Het schema importeert de kern zelf, zodat `NatuurlijkPersoon` oplost zonder dat het onderdeel van `gbo.yaml` wordt.

Er wordt uitsluitend op concrete toestemmingen bevraagd. Het supertype heeft geen eigen query: die zou de interface leveren en daarmee elke soort tegelijk, wat de soort-specifieke queries dubbelt en de afnemer een ongerichte bevraging geeft. `Toestemming` blijft wel als interface staan, waar de concrete soorten hun gedeelde velden van erven.

## Bronprofielen en bevraging

Het bron-profiel `bd` vervalt. De Belastingdienst levert via GBO nog twee ingangen: de VIA voor de voorinvulling, en `bri-plus` voor al het overige. Dat laatste profiel groeit daarmee van 7 naar 30 objecttypen en van 2 naar 7 benoemde queries, en dekt nu naast de inkomensketen ook de aanslag met haar rubrieken, de aangiften schenk- en erfbelasting, de toeslagen en de renseigneringen.

De vorm van die levering is bewust strak. De aanslag draagt de rubrieken en die zijn uitsluitend daaronder bereikbaar, via de inverse van `onderdeelVan`. De navigatie van persoon naar rubriek is onderdrukt, zodat er geen tweede, afwijkend pad naar dezelfde gegevens ontstaat. Alleen toeslagen en renseigneringen houden een veld op de persoon, omdat die los van de aanslag staan.

Daarvoor is het bronprofiel-meta-schema uitgebreid met `inverse` op `RelatieAfhandeling`. Zonder vermelding geldt het oude gedrag (de annotatie `gbo:inverseNaam` wordt gevolgd); met `inverse: false` blijft de gematerialiseerde inverse achterwege. De snoei-tool meldt elke onderdrukking als INFO-regel.

De VIA houdt bewust beide paden. Daar zijn de rubrieken zowel onder de aangifte bereikbaar (`omvatFiscaalFeit`, `omvatEigenWoning`, `omvatFiscaalPartnerschap`) als rechtstreeks vanaf de persoon, omdat de voorinvulling ook zinvol is los van een aangifteobject. De strakke snede geldt alleen voor `bri-plus`; of de VIA daarin meegaat is een open keuze.

Het nieuwe profiel `vth` ontsluit het Toestemmingenmodel met 8 queries, één per vergunningsoort, elk op dezelfde twee sleutels: het bsn van de houder en het vergunningnummer. Anders dan de overige profielen wijst het niet naar `gbo.yaml` maar naar `toestemmingen.yaml`.

Over alle profielen samen gaat het aantal benoemde queries van 38 naar 46.

## Build en publicatie

`publish:check` is nieuw en bewaakt drie dingen voordat er iets wordt gedeployed: de working tree moet schoon zijn, `VERSION` in `.env` moet overeenkomen met de hoogste versiemap, en HEAD mag niet al als die mike-versie op `gh-pages` staan. De eerste controle is de belangrijkste: mike schrijft de commit-sha in de deploy-boodschap, dus publiceren met ongecommitte wijzigingen maakt de gepubliceerde site onreproduceerbaar uit die commit. `FORCE_PUBLISH=1` negeert alle drie, met een expliciete melding.

Die controle stelde een eis aan de structuur van `publish:local`. De generate-stappen stonden als `deps` en draaien daarmee parallel; ze schrijven zelf in `v{VERSION}/` en `docs/`, dus een controle ernaast zou haar eigen output als vuile working tree zien. `publish:check` is nu de enige dep en de zeven generate-stappen staan sequentieel in `cmds`. Iets trager, maar de volgorde ligt vast.

Verder nieuw: `generate:toestemmingen-lod` voor de OWL en SHACL van het pilotmodel, en `publish:main`, die de stand van de hoofdbranch als `main` in het mike-versiemenu zet — bewust zonder alias en zonder `set-default`, zodat `latest` de vastgestelde versie blijft aanwijzen.

## Documentatie

De site krijgt een aparte kop **Informatiemodellen Pilots** naast de kern- en voorzieningenmodellen, met daaronder **Vergunningen en Ontheffingen**. Het pilotmodel staat daarmee niet langer tussen de vastgestelde modellen; `import:copy` kopieert het naar `docs/informatiemodel/pilots/`.

Het deelmodel Belastingen is in de documentatie meegegaan met de herstructurering: nieuwe secties voor `Aangifte`, `Aanslag`, `FiscaleOpgave`, `AangifteStatus` en `SoortAanslag`, de drie aangiftesoorten hernoemd, en het klassendiagram bijgewerkt met de rubriekrelaties en de nieuwe overervingsboom.

## Breaking changes en migratie

Voor afnemers van de GraphQL-SDL:

- **Het bron-profiel `bd` bestaat niet meer.** `v0.4/graphql/bd.graphql` is vervallen. Wie daartegen programmeerde, moet naar `bri-plus`. De queries `vermogensBestanddeelOverJaar`, `aftrekpostOverJaar`, `fiscalePartnerOverJaar` en `eigenWoningOverJaar` bestaan daar niet als eigen ingang: die rubrieken hangen onder `aanslagOverJaar`.
- **Vijf objecttypen zijn hernoemd of verdwenen.** `BelastingAangifte` en `BelastingjaarAangifte` zijn samengevoegd tot `Aangifte`; `AangifteIH`, `AangifteSchenk` en `AangifteErf` heten `AangifteInkomstenbelasting`, `AangifteSchenkbelasting` en `AangifteErfbelasting`. De bijbehorende `gbobegrip:`-URI's veranderen mee.
- **`belastingsoort` vervalt op de aangifte.** Het dubbelde de subtype-as; gebruik het concrete type.
- **`ingediendDoor` heet `betreft`.** Bij een vooringevulde aangifte heeft nog niemand ingediend, maar is de belastingplichtige wel bekend.
- **`status` is geen vrije tekst meer** maar de enum `AangifteStatus` met `Voorinvulling`, `Ingediend` en `Herzien`.
- **`belastingjaarAangifteOverJaar` heet `aangifteOverJaar`** in het VIA-profiel.
- **In `bri-plus` is er geen `ingeschrevenPersoon`-ingang meer.** Elke benoemde query neemt de bsn als argument; de persoon zelf is geen resultaat van deze bron. De velden `heeftVerzamelinkomen`, `heeftInkomstenverhouding`, `heeftVermogensBestanddeel`, `heeftAftrekpost`, `heeftEigenWoning` en `heeftFiscalePartner` zijn er niet meer; alleen `heeftToeslag` en `heeftRenseignering` blijven.
- **`toeslagOverJaar` en `renseigneringOverJaar` heten `toeslagenOverJaar` en `renseigneringenOverJaar`**, meervoud, omdat het er per jaar meerdere zijn. `toeslagenOverJaar` filtert op het nieuwe `berekeningsjaar` in plaats van op een ongebonden jaarargument.

Voor wie de build draait:

- **`publish:local` stopt bij een vuile working tree.** Commit eerst, of zet `FORCE_PUBLISH=1`. De generate-stappen draaien niet meer parallel als `deps` maar sequentieel in `cmds`.

## Cijfers

- Kernmodel plus deelmodellen: 159 klassen en 75 enumeraties, tegen 147 en 68 in v0.3.
- Deelmodel Belastingen: 32 klassen (was 31) en 12 enumeraties (was 10). Zes objecttypen toegevoegd, vijf verwijderd.
- Toestemmingenmodel: 11 klassen en 5 enumeraties, nieuw.
- Ontologie-artefacten: 6 (was 4); `GBO-Toestemmingen.ttl` en `GBO-Toestemmingen-Shapes.ttl` erbij.
- SKOS-begrippen in `GBO-Begrippenkader.ttl`: 119 (was 102).
- Bron-profielen: 13 (`bd` eruit, `vth` erin). Client-profielen: 1.
- Benoemde queries over alle profielen: 46 (was 38). `bri-plus` 7 (was 2), `vth` 8 (nieuw).
- `bri-plus` objecttypen: 30 (was 7).
- GraphQL-SDL-bestanden: 13.
- mike-versies live: 5 (v0.1, v0.2, v0.3, v0.4 en `main`; `latest` en default naar v0.4).

## Vooruitblik

Twee punten staan open en zijn als `needs-review` in de bron vastgelegd. De naam `BRI-plus` dekt de lading niet meer nu dat profiel naast de inkomensketen ook aanslagen, aangifterubrieken, toeslagen en renseigneringen levert — toeslagen vallen onder de Awir, niet onder de Basisregistratie Inkomen. En in de VIA-mapping moet worden geverifieerd of de rubriek "IB-gegevens VA" in de GSP voor *voorlopige aanslag* staat; is dat zo, dan hoort een deel van die rubriek bij `Aanslag` in plaats van bij `Aangifte`, want een aanslag heeft een dagtekening en geen indieningsdatum.

Fase 2 blijft staan zoals bij v0.3 beschreven: de synthese-documentatie wordt deterministisch uit de LinkML gegenereerd in plaats van AI-geschreven, de SKOS-semantiek uit `concepts/` gaat op in LinkML-annotaties, en de begrippen-TTL-build verhuist naar de publicatierepo.

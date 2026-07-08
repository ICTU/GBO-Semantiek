# GBO-Core v0.3

Deze release voert de Fase 1-herindeling door: het informatiemodel krijgt een canonieke, machine-leesbare modelbron in LinkML, en de modelleer- en publicatieverantwoordelijkheden worden over twee repositories verdeeld. De modelleerrepo (`llm-wiki`) levert voortaan alles op onder `publicatie/`; de publicatierepo (`gbo-semantiek`) kopieert die leverset via `task import:copy` en genereert daaruit GraphQL, OWL/SHACL en de site. Daarnaast scherpt v0.3 de semantiek aan: identificerende kenmerken krijgen eigen, getypeerde datatypes met formaatpatronen, de Partij-surrogaatsleutel wordt hernoemd en de MIM-annotaties worden uitgelijnd op de officiele MIM-metamodel-namen.

## In het kort

- LinkML is nieuw in v0.3 de canonieke modelbron: 13 gekoppelde modelschema's plus 2 meta-schema's voor profielen. Op de v0.2-tag bestond nog geen LinkML-model.
- De build importeert het model niet langer uit een QEA-bestand via crunch_uml, maar kopieert de canonieke LinkML-bron en de profielen uit de modelleerrepo; `import:copy` vervangt `import:model` en `import:previous`.
- Identificerende kenmerken krijgen eigen datatypes met formaatpatronen (BSN, KVKnummer, Vestigingsnummer, Kenteken, BRINcode, BAGID) i.p.v. generieke String; de patronen worden als `@restrictie`-directive in de GraphQL-SDL geprojecteerd.
- De betekenisloze Partij-surrogaatsleutel `partijnummer` is hernoemd naar `ID`; query-ingangen lopen voortaan via natuurlijke zoeksleutels (`bsn`, `kvkNummer`, `kenteken`).
- Profielen voor aanbod en vraag: 11 bron-profielen (per register) en het eerste client-profiel (`np-belastingdienst`).
- Een MIM-brug koppelt de GBO-lokale MIM-annotaties via `owl:equivalentProperty` aan de officiele Geonovum MIM-RDF-ontologie.

## Architectuur en build

De fundamentele wijziging van v0.3 is de knip tussen modelleren en bouwen. De modelleerrepo (`llm-wiki`) levert alles wat zij produceert onder `publicatie/`: de LinkML-modelbron, de bron- en client-profielen en de synthese-documentatie (`publicatie/informatiemodel/`). De publicatierepo (`gbo-semantiek`) bouwt en publiceert daaruit; zij genereert zelf niets meer uit een QEA-bestand.

De nieuwe task `import:copy` vervangt de verwijderde tasks `import:model` en `import:previous`. crunch_uml verdwijnt uit `prepare:check-tools`; daarvoor in de plaats komen `rsync`, `linkml`, `gen-owl`, `gen-shacl`, `gen-yaml` en `linkml-validate`. De `WIKI_REPO`-variabele (default `../llm-wiki-GBI-core-model`) wijst naar de modelleerrepo. `import:copy` doet vier `rsync -a --delete`-slagen: `publicatie/linkml/` naar `v0.3/informatiemodel/linkml/`, `publicatie/bronnen/` naar `v0.3/bronnen/`, `publicatie/clients/` naar `v0.3/clients/`, en `publicatie/informatiemodel/` naar `docs/informatiemodel/gbo-kern/`. De model-`.md` blijven in Fase 1 AI-geschreven in de modelleerrepo en worden meegekopieerd; `generate:docs` ververst via die copy-slag en vult versie-placeholders (`###VERSION###`).

De LOD-pijplijn is herschreven. OWL en SHACL worden niet meer via `crunch_uml export -t ttl` gemaakt, maar via `gen-owl` en `gen-shacl` op een LinkML-werkkopie. `tools/kwalificeer_uris.py` zet per deelmodel, klasse en attribuut een diepe, lowercase, gekwalificeerde URI, zodat gelijknamige attributen niet meer botsen; dit verving 271 "Ambiguous attribute"-meldingen. `gen-owl` draait met `--no-use-native-uris` (zodat die URI's worden gehonoreerd) plus `--skip-vacuous-min-zero-cardinality-axioms`, `--skip-vacuous-local-range-axioms` en `--consolidate-cardinality-axioms`, wat drie DeprecationWarnings opruimt. Class-URI's en enum-type-URI's zijn eveneens lowercase en deelmodel-gekwalificeerd; enum-permissible-values houden bewust hun code-vorm. De bron-LinkML blijft schoon: de kwalificatie draait alleen op de werkkopie.

De changelog (`GBO_Changes.md`) wordt via `tools/genereer_changelog.py` gemaakt, dat met `linkml_runtime` SchemaView twee LinkML-versies (vorige versus huidige `gbo.yaml`, gemerged over imports) vergelijkt op klassen, enums en directe attributen per klasse. Bij een ontbrekende vorige LinkML-versie schrijft het een nette notitie in plaats van te falen. `generate:graphql` is opgenomen in de `publish:local`-keten, zodat een full-deploy alle afgeleiden uit het model produceert (GraphQL-SDL, OWL/SHACL, changelog en site). De drawio-naar-SVG-export (`generate:diagrams`) is in Fase 1 uitgeschakeld; class-diagrammen komen nu als PlantUML-fences mee in de gekopieerde model-docs en worden door mkdocs gerenderd.

De MIM-brug hecht na `gen-owl` het fragment `tools/mim-mapping.ttl` aan `GBO-Linked-Data.ttl`. Dat koppelt 11 GBO-lokale MIM-annotatieproperties (`gbomim:`, `https://lod.gbo-semantiek.nl/def/mim#`) via `owl:equivalentProperty` en `rdfs:isDefinedBy` aan de officiele MIM-RDF-ontologie (`mimstd:`, `http://bp4mc2.org/def/mim#`). GBO-eigen annotaties zonder MIM-tegenhanger blijven ongekoppeld; `notation` is `skos:notation`, geen MIM. Een latere namespace-overstap wordt daarmee triviaal.

## Model en semantiek

LinkML is in v0.3 voor het eerst de canonieke modelbron. `publicatie/linkml/` bevat 15 YAML-bestanden: 13 gekoppelde modelschema's (`gbo.yaml` als hoofdschema, plus `datatypes`, `hoofdmodel` en 10 deelmodellen) en 2 meta-schema's (`bronprofiel.yaml`, `clientprofiel.yaml`). `gbo.yaml` importeert twaalf modules naast `linkml:types`. Het GraphQL-generatiespoor uit de modelleerrepo (`scripts/build-graphql.py` plus `scripts/graphql/`) is geretireerd; generatie van GraphQL en TTL gebeurt voortaan in `gbo-semantiek`. De deliverables `linkml/`, `bronnen/` en `clients/` zijn als git-renames onder `publicatie/` geplaatst.

De Partij-identifier `partijnummer` (een betekenisloos surrogaat, range UUID, op het abstracte supertype `Partij`) is hernoemd naar `ID`. Het slot blijft `identifier: true`, `required: true`, range UUID; subtypen erven dit. De natuurlijke zoeksleutels zijn expliciet als query-ingang gemarkeerd: `bsn` op `IngeschrevenPersoon` als `unique_keys`-blok (range BSN; `ID` blijft de technische identifier) en `kvkNummer` op `Inschrijving` (range KVKnummer).

Identificerende kenmerken krijgen eigen datatypes met formaatconstraints in plaats van generiek String. Zeven nieuwe datatypes zijn toegevoegd, waarvan zes met patroon:

- `BSN` (`^[0-9]{9}$`, herkomst BRP / Wet bsn)
- `KVKnummer` (`^[0-9]{8}$`, herkomst NHR / HRW 2007)
- `Vestigingsnummer` (`^[0-9]{12}$`, herkomst NHR / HRW 2007)
- `Kenteken` (`^[A-Z0-9-]{6,8}$`, herkomst BRV / RDW)
- `BRINcode` (`^[0-9]{2}[A-Z]{2}$`, herkomst DUO / BRIN; voorheen Alfanumeriek)
- `BAGID` (`^[0-9]{16}$`, herkomst BAG)
- `KadastraleAanduiding` (zonder patroon, herkomst BRK / Kadaster)

`BAGID` vervangt de generieke `NEN3610ID` voor BAG-objecten: de identificatie van `Pand`, `AdresseerbaarObject`, `Nummeraanduiding`, `OpenbareRuimte` en `Woonplaats` gaat naar range BAGID, evenals de koppeling `adresseerbaarObjectId` in `Vestiging`. `NEN3610ID` blijft ongewijzigd voor BRK-objecten. Daarnaast zijn interne, niet-natuurlijke identificaties omgezet van losse Tekst naar het al bestaande benoemde type `Identificatie` (vrije structuur, geen patroon).

De MIM-annotaties zijn uitgelijnd op de officiele MIM-metamodel-namen, over alle tien deelmodellen: `mim:materieleHistorie` naar `mim:indicatieMaterieleHistorie` (353 keer), `mim:formeleHistorie` naar `mim:indicatieFormeleHistorie` (353 keer) en `mim:notation` naar `skos:notation` (31 keer; notation is geen MIM-kenmerk). De `mim:`-namespace blijft voorlopig GBO-lokaal; de equivalentie naar de officiele ontologie wordt in `gbo-semantiek` gelegd via de MIM-brug.

Het profiel-spoor is nieuw. Aan de aanbod-kant dekken 11 bron-profielen (`bag`, `bd`, `bri`, `brk`, `brp`, `brv`, `cki`, `hr`, `rod`, `uwv`, `woz`) alle tien deelmodellen; elk profiel is LinkML-data conform `bronprofiel.yaml` (klasse `Bronprofiel`, `tree_root`) met velden voor bron, titel, schemabestand, ingangen (natuurlijke zoeksleutels), objecttypen, uitsluitingen en relatieafhandeling (default `sleutel`-referentie, alternatief `weglaten`). Aan de vraag-kant staat het spiegelbeeldige `clientprofiel.yaml` met het eerste client-profiel `np-belastingdienst.yaml` (afnemer BD, ingang `NatuurlijkPersoon`, zes geselecteerde objecttypen). Dit profiel is de opvolger van het geretireerde curated GraphQL-manifest: niet langer een standalone model-snede, maar een selectie van objecttypen uit het canonieke LinkML-model.

In de GraphQL-projectie gebruiken velden en query-args nu benoemde identifier-scalars in plaats van String. Omdat GraphQL-scalars opaak zijn, projecteert `tools/genereer_graphql.py` de pattern-, minimum- en maximum-constraints uit de LinkML-datatypes als `@restrictie(patroon, minimum, maximum)`-directive op de scalar-definitie, bijvoorbeeld `scalar BSN @restrictie(patroon: "^[0-9]{9}$")`. Scalars zonder LinkML-patroon (`KadastraleAanduiding`, `NEN3610ID`) krijgen geen `@restrictie`. De query-ingang gebruikt de natuurlijke zoeksleutel (`bsn`, `kvkNummer`, `kenteken`) in plaats van de geerfde technische `ID`.

## Inhoud en documentatie

Het eID-cluster is toegevoegd. `sources/eid-as-data.md` legt vast dat de gevraagde EDI-attestaties de 11 categorieen van de Minimum List of Attributes (Annex VI, eIDAS2 / Verordening (EU) 2024/1183) plus de PID zijn, met Birth Certificate als eerste concreet uitgewerkte eid.as-scheme (categorie 4, Civil status). `clients/eid/databehoefte.md` mapt elke categorie tegen de LinkML-bron op GBO-Core-objecttypen: 4 volledig (PID, Address, Gender, Nationality), 7 gedeeltelijk, 1 afwezig (Powers & mandates).

De OOTS-databehoefte is uitgewerkt in `clients/oots/`, met een overzicht, een crosswalk-mapping en 14 per-evidence-type-pagina's, gegenereerd uit `raw/oots/Data dictionary.xlsx` via `.claude/scripts/build-oots-evidence-pages.py`. 48 Information Requirements (`oots:ir/1000` t/m `oots:ir/1047`) hangen op 8 OOTS-hoofdconcepten die mappen op GBO-Core-objecttypen; de IR-dekking is 27 volledig, 13 gedeeltelijk, 8 afwezig. Disability is het enige resterende volledige hiaat. Het clients-overzicht positioneert drie afnemers: DvTP, OOTS en EID.

De gegevensarchitectuur is als wiki-kennispagina vastgelegd (`wiki/gbo-core/gegevensarchitectuur.md`, drie-lagen-architectuur met sector- en clientmodellen boven, GBO-Kern in het midden en GBO-Voorzieningen onder). Het bijbehorende diagram in de publicatierepo kreeg echte EDI- en OOTS-namen: de EDI/EUDI-wallet toont PID, Birth Certificate en Age plus een blok "... (o.a. Citizenship)"; OOTS toont Proof of birth, Proof of residence en Proof of roadworthiness plus "... (14 evidence types)".

De bronnenprioritering is geconsolideerd tot een enkele bron: de los onderhouden versie in de publicatierepo is verwijderd, en `import:copy` levert nu uitsluitend de versie uit de modelleerrepo (`wiki/gbo-core/bronnenprioritering.md`, vier-lagen-strategie L1 t/m L4). De documentatie is integraal op v0.3 gezet: het conceptfase-label, het VERSION-voorbeeld in de tooling-bijlage en de mike-publicatie-URL en mappenstructuur in de deployment-pagina (van het QEA-tijdperk naar de LinkML-pijplijn). De keten `import:copy` naar `generate:graphql/lod/diff` naar `build:validate` bouwt schoon met `mkdocs --strict`.

## Breaking changes en migratie

De architectuurwijziging van het importmechanisme is breaking voor wie de build draait:

- **`import:copy` vervangt `import:model` en `import:previous`.** De QEA-import via crunch_uml (`crunch_uml import -t qea`, `transform copy`) en de bijbehorende crunch-db-variabelen zijn vervallen. crunch_uml is geen tool-dependency meer; `prepare:check-tools` vereist nu `rsync` en de LinkML-toolchain. Wie de build draait, moet de modelleerrepo naast de publicatierepo checken (`WIKI_REPO`, default `../llm-wiki-GBI-core-model`) en `import:copy` aanroepen in plaats van de oude import-tasks.

Voor afnemers en bouwers van de afgeleide artefacten:

- **`partijnummer` heet nu `ID`.** Wie tegen de geerfde technische sleutel programmeerde, moet `partijnummer` vervangen door `ID`. Query-ingangen lopen niet meer via die technische sleutel maar via de natuurlijke zoeksleutels: `ingeschrevenPersoon` wordt op `bsn` opgevraagd, NNP via `inschrijving(kvkNummer)`.
- **Identifier-velden zijn niet meer String.** In de GraphQL-SDL zijn `bsn`, `kvkNummer`, `vestigingsnummer`, `kenteken`, `brincode` en de BAG-identificaties nu benoemde scalars (BSN, KVKnummer, Vestigingsnummer, Kenteken, BRINcode, BAGID) met een `@restrictie`-formaat, in plaats van het ongetypeerde String uit de v0.2-afronding. Clients die deze velden als String behandelen, moeten de nieuwe scalar-types en hun patronen overnemen.
- **BAG-identificaties dragen een strakkere constraint.** De identificatie van BAG-objecten gaat van `NEN3610ID` naar `BAGID` (16 cijfers). `NEN3610ID` blijft voor BRK-objecten.

Let op: de modelhernoemingen en typeringen (`partijnummer` naar `ID`, `NEN3610ID` naar `BAGID`, Tekst naar eigen datatype) spelen zich af binnen de in v0.3 nieuw toegevoegde LinkML-modelbron. Ten opzichte van de v0.2-baseline, die geen machine-leesbaar modelcontract had, is er op modelniveau dus geen breuk; de impact zit in de gegenereerde GraphQL-SDL en de buildketen.

## Cijfers

- LinkML in `publicatie/linkml/`: 15 YAML-bestanden = 13 modelschema's + 2 meta-schema's. `gbo.yaml` importeert 12 modules naast `linkml:types`.
- v0.2-baseline van `linkml/`, `bronnen/` en `clients/`: 0 bestanden (geen van deze directories bestond bij tag v0.2).
- Nieuwe identificerende datatypes: 7 (6 met patroon; `KadastraleAanduiding` zonder).
- Bron-profielen: 11. Client-profielen: 1.
- MIM-annotatie-hernoemingen: 353 keer `indicatieMaterieleHistorie`, 353 keer `indicatieFormeleHistorie`, 31 keer `skos:notation`, over 10 schemabestanden.
- MIM-brug: 11 `gbomim:`-properties via `owl:equivalentProperty` aan `mimstd:`.
- Opgeruimde build-warnings: 271 keer "Ambiguous attribute", 3 keer owlgen DeprecationWarning, 1 keer click `-V` UserWarning.
- GraphQL-SDL-bestanden met `@restrictie`-projectie: 11 (in `v0.3/graphql/`, nieuw t.o.v. v0.2).
- Bron-profielen v0.3 versus v0.2: 11 (`bag`, `bd`, `bri`, `brk`, `brp`, `brv`, `cki`, `hr`, `rod`, `uwv`, `woz`) tegenover 5 (`bag`, `bri`, `brp`, `brv`, `hr`).
- EUDI Annex VI tegen GBO-Core: 4 volledig, 7 gedeeltelijk, 1 afwezig (plus PID).
- OOTS: 14 evidence types, 8 hoofdconcepten, 48 Information Requirements; dekking 27 volledig, 13 gedeeltelijk, 8 afwezig.
- mike-versies live: 3 (v0.1, v0.2, v0.3; `latest` en default naar v0.3).

## Vooruitblik (Fase 2)

In Fase 2 wordt de synthese-documentatie (`publicatie/*.md`) niet langer AI-geschreven maar deterministisch uit de LinkML gegenereerd, in `gbo-semantiek`. De SKOS-semantiek uit `concepts/` gaat op in LinkML-annotaties, zodat de begripsdefinities en de modelstructuur uit een enkele bron komen. De begrippen-TTL-build (`scripts/build-ttl.py`), die in Fase 1 nog tijdelijk in de modelleerrepo draait, verhuist naar `gbo-semantiek`. Daarmee blijft de modelleerrepo de bron van het model en de begrippen, en wordt al het afgeleide werk geconcentreerd in de publicatierepo.

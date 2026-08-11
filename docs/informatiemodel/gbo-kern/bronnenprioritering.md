---
title: "Bronnenprioritering: beslisregels GBO-Kern"
description: "Vier-lagen-strategie L1 tot en met L4 voor het afleiden en refereren van GBO-Kern-elementen uit basisregistraties, sectorale registers, nationale ankers en internationale vocabulaires."
---

# Bronnenprioritering: beslisregels GBO-Kern

Voor de onderdelen waaruit GBO-Kern wordt opgebouwd zijn niet altijd
dezelfde of eenduidige bronnen. We hanteren een afwegingskader om
tot goede modelafleidingen te komen. Dat afwegingskader staat in
deze pagina.

**Doel**: GBO-Kern is compatibel met de bestaande informatiemodellen
en koppelvlakken van de basisregistraties, sectorale registers en
de DUO-, UWV- en Belastingdienst-administraties. Een afnemer die werkt
vanuit een catalogus of een API moet GBO-Kern direct herkennen.

We bereiken dat door voor elk UML-element (klasse, attribuut,
datatype, multipliciteit, omschrijving) systematisch uit de
bronregisters af te leiden. In principe komt de invulling uit L1; uit
L2 of L3 als L1 ontbreekt of als er een functionele behoefte is. Waar
bronnen onduidelijk zijn, formele modellen ontbreken, of registraties
elkaar tegenspreken, leiden we zelf af, met heldere bronvermelding.

## Vier lagen

Bij elk UML-element wordt de referentie-strategie afgepeld in deze
volgorde.

| Laag | Soort bron | Levert |
|---|---|---|
| L1 Authoritative | Datamodel van de registratie (voorkeur); anders functioneel ontwerp of catalogus | Inhoudelijke definitie en structurele eigenschappen |
| L2 Interface | Koppelvlak-specificatie | Naamgeving, datatype, uitwisselings-contract |
| L3 Nationaal anker | NL-overkoepelende begrippen, thesauri, referentiemodellen | Cross-registratie-binding |
| L4 Internationaal | Generieke EU-vocabulaires | Publicatie-binding en FAIR-conformiteit |

## Bronnen per laag

GBO-Kern dekt op dit moment tien bronregisters of equivalente
administraties:

- Vier basisregistraties met L1 datamodel: **BRP**, **BAG**, **BRK**,
  **BGT**.
- Twee basisregistraties zonder L1 datamodel: **HR** en **WOZ**;
  modellering via L2 en L3.
- Een basisregistratie met L1 als SKOS-begrip: **BRI** (een authentiek
  gegeven, gepubliceerd via de Stelselcatalogus).
- Drie sectorale registers en hun L1-bronnen: **ROD**
  (Register Onderwijsdeelnemers, DUO/OCW), **CKI** (Centraal Krediet
  Informatiesysteem, Stichting BKR), **SGR** (Suwi Gegevensregister,
  BKWI namens UWV).
- Twee L1+L2-bronnen die niet als register opereren maar wel
  definitief inhoudelijk-leidend zijn: **SBR-NT** (Nederlandse
  Taxonomie, Belastingdienst voor aangiften) en
  **Gegevensspecificaties aangifte loonheffingen** (Belastingdienst
  plus UWV voor de loonketen).

BRT, BRO en BRV blijven voorlopig buiten scope; bij toekomstige
ingest volgen zij hetzelfde patroon (L1 datamodel of catalogus,
L2 koppelvlak).

## L1 Authoritative

Per bronregister het officiele datamodel; bij ontbreken het
functionele ontwerp, de catalogus of (in bijzondere gevallen) een
SKOS-publicatie.

| Bronregister | Bron | URL |
|---|---|---|
| BAG | IMBAG met Catalogus BAG | `https://imbag.github.io/catalogus/` |
| BGT | IMGeo (Gegevenscatalogus BGT/IMGeo) | `https://docs.geostandaarden.nl/imgeo/catalogus/imgeo/` |
| BRI | Stelselcatalogus, begrip *authentiek_inkomen* (SKOS-RDF) | `https://opendata.stelselcatalogus.nl/bri/id/begrip/authentiek_inkomen` |
| BRK | IMKAD | `https://developer.kadaster.nl/schemas/imkad/20200130/cat/index.html` |
| BRK | BRK-Catalogus | `https://www.kadaster.nl/-/catalogus-brk` |
| BRP | LO BRP (Logisch Ontwerp BRP) | `https://www.rvig.nl/lo-brp` |
| CKI | Algemeen Reglement CKI | `https://www.bkr.nl/media/4dyezfiz/algemeen-reglement-cki-juli-2024.pdf` |
| HR | L1 ontbreekt; modellering via L2 en L3 | n.v.t. |
| Loonheffingen | Gegevensspecificaties aangifte loonheffingen | `https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/themaoverstijgend/brochures_en_publicaties/gegevensspecificaties-aangifte-loonheffingen` |
| ROD | Programma van Eisen ROD per sector (PO, VO, MBO/VAVO, HO) plus Gegevenswoordenboek DUO | `https://duo.nl/zakelijk/standaarden-ocw/canonieke-gegevensmodellen/duo-gegevenswoordenboek.jsp` |
| SBR-NT | Nederlandse Taxonomie NT20 (hoofdrelease en extensies) | `https://www.sbr-nl.nl/werken-met-sbr/taxonomie/documentatie-nederlandse-taxonomie` |
| SGR | Suwi Gegevensregister, beheerd door BKWI | `https://sgr.bkwi.nl/sgr/index.html` |
| WOZ | L1 ontbreekt; modellering via L2 en L3 | n.v.t. |

## L2 Interface

Koppelvlak-specificaties per registratie. Voor BRI is er geen
publiek koppelvlak; toegang verloopt via afnemers in het SUWI- en
toeslagen-stelsel. Voor CKI is de detail-koppelvlak-laag gated (alleen
voor erkende zakelijke klanten van Stichting BKR).

| Bronregister | Bron | URL |
|---|---|---|
| BAG | Haal Centraal BAG Individuele Bevragingen | `https://lvbag.github.io/BAG-API/Technische%20specificatie/` |
| BGT | PDOK BGT-services | `https://www.pdok.nl/introductie/-/article/basisregistratie-grootschalige-topografie-bgt-` |
| BRI | Geen publiek koppelvlak; afname via SUWI- en toeslagen-stelsel | n.v.t. |
| BRK | Haal Centraal BRK Bevragen | `https://kadaster.github.io/BRK-bevragen/` |
| BRP | Haal Centraal BRP-suite (Personen, Historie, Bewoning, Reisdocumenten, Tabellen, Update) | `https://developer.rvig.nl/brp-api/overview/` |
| CKI | Algemene Handleiding CKI (gated, alleen erkende zakelijke klanten) | `https://www.bkr.nl/nl/inloggen-portalen` |
| HR | KVK Developer Portal (Zoeken, Basisprofiel, Vestigingsprofiel, Naamgeving, Mutatieservice) | `https://developers.kvk.nl/documentation` |
| Loonheffingen | XSD-bijlage Gegevensspecificaties; transport via Digipoort | (onderdeel van L1-URL) |
| ROD | PvE ROD per sector via Edukoppeling 1.3 (WUS-profiel) | `https://duo.nl/zakelijk/` (per sectorpagina) |
| SBR-NT | XBRL-entrypoints per belastingsoort en jaar | `https://www.sbr-nl.nl/werken-met-sbr/taxonomie/documentatie-nederlandse-taxonomie` |
| SGR | SuwiML-berichten boven SGR (Polisadministratie-bevraging, Inkomstenopgaaf, Uitkeringsoverzicht) | `https://sgr.bkwi.nl/sgr/` |
| WOZ | Haal Centraal WOZ Bevragen | `https://kadaster.github.io/WOZ-bevragen/` |

Renseigneringen aan de Belastingdienst (Bankproducten,
Verzekeringsproducten, Pensioenproducten) verlopen via het ODB; de
detail-specificaties zijn gated achter een ondersteuningsabonnement.

## L3 Nationaal anker

NL-overkoepelende begrippen-bronnen voor cross-registratie-binding.

| Bron | Functie | URL |
|---|---|---|
| Stelselcatalogus | Cross-registratie-begrippen; ook publicatie van het BRI-begrip in SKOS-RDF | `https://www.stelselcatalogus.nl/` |
| CBS Begrippen | Statistische en afgeleide begrippen | `https://www.cbs.nl/nl-nl/onze-diensten/methoden/begrippen` |
| TOOI | Overheidsorganisaties, informatieobjecten, regelgevingstermen | `https://standaarden.overheid.nl/tooi` |
| GGM | Gemeentelijk gegevensmodel; sector-uitbreidingen | `https://www.gemeentelijkgegevensmodel.nl/` |
| RSGB | Historische gemeentelijke baseline (onder GEMMA) | `https://www.gemmaonline.nl/index.php/Referentiemodel_Stelsel_van_Gemeentelijke_Basisgegevens` |
| NORA | Nederlandse Overheid Referentie Architectuur; positionering sectorale registers | `https://www.noraonline.nl/` |

## L4 Internationaal

Generieke EU- en internationale vocabulaires voor publicatie-binding
en FAIR.

| Bron | Functie | URL |
|---|---|---|
| EU Core Vocabularies (SEMIC) | Persoon, onderneming, locatie, overheidsorganisatie | `https://semiceu.github.io/` |
| schema.org | SEO en AI-vindbaarheid bij publicatie | `https://schema.org/` |
| ELMO | Europees onderwijs-uitwisselings-format (Learner Mobility) | `https://elmo.eu/` |
| FIBO | Financial Industry Business Ontology (krediet, financiele verplichting) | `https://spec.edmcouncil.org/fibo/` |
| ESCO | European Skills, Competences, Qualifications and Occupations | `https://ec.europa.eu/esco/` |
| ISO 3166 | Landcodes (alpha-2, alpha-3, numeriek) | `https://www.iso.org/iso-3166-country-codes.html` |
| MCD 2014/17/EU | Richtlijn hypothecair krediet | `https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX%3A32014L0017` |

## Per registratie

Per bronregister of equivalente administratie de bronvolgorde van
L1 naar L4. Sub-secties alfabetisch.

### BAG: Basisregistratie Adressen en Gebouwen

**Beheerder**: Kadaster (LVBAG) met het Ministerie van BZK als
vaststeller van de catalogus.

| Laag | Bron | URL | Karakter |
|---|---|---|---|
| L1 | Catalogus BAG / IMBAG | `https://imbag.github.io/catalogus/` | Formeel IM plus objecttype-catalogus |
| L2 | Haal Centraal BAG Individuele Bevragingen | `https://lvbag.github.io/BAG-API/Technische%20specificatie/` | REST/OpenAPI met HAL |
| L2 | BAG 2.0 Extract / LVBAG-levering | via Kadaster-aansluiting | Bulk |
| L2 | PDOK BAG WMS/WFS | via PDOK-portaal | Geo-services voor geometrie |

**Advies**: IMBAG is volledig formeel (UML en XSD); gebruik
IMBAG-URI's direct als `bron-uri`. Wijk- en Buurt-data zitten niet in
BAG; daarvoor CBS. Het BAG-bitemporaliteits-patroon
(`voorkomen`-blok) is anker voor het GBO Voorkomen-mixin.

### BRI: Basisregistratie Inkomen

**Beheerder**: Belastingdienst (inhoudelijk); Logius beheert de
Stelselcatalogus-publicatie.

| Laag | Bron | URL | Karakter |
|---|---|---|---|
| L1 | Stelselcatalogus, begrip *authentiek_inkomen* (SKOS-RDF) | `https://opendata.stelselcatalogus.nl/bri/id/begrip/authentiek_inkomen` | Eén SKOS-Concept; content-negotiation ttl, jsonld, rdf |
| L1 | Wet basisregistratie inkomen | `https://wetten.overheid.nl/BWBR0028058` | Juridische definitie en aanwijzing als authentiek |
| L2 | Geen publiek koppelvlak | n.v.t. | Afname via SUWI- en toeslagen-stelsel |

**Advies**: BRI is een one-attribute-register; uitsluitend het
authentieke inkomen-gegeven is gedefinieerd. Citeer
*Wet BRI art. 4* en de Stelselcatalogus-URI in herkomst-velden.
Voeden van BRI gebeurt vanuit aangiften IH (SBR-NT) of vanuit de
loonketen (Loonheffingen).

### BRK: Basisregistratie Kadaster

**Beheerder**: Kadaster.

| Laag | Bron | URL | Karakter |
|---|---|---|---|
| L1 | IMKAD (Informatiemodel Kadaster) | `https://developer.kadaster.nl/schemas/imkad/20200130/cat/index.html` | UML conform MIM |
| L1 | BRK-Catalogus | `https://www.kadaster.nl/-/catalogus-brk` | Narratief plus objecttype-overzicht |
| L2 | Haal Centraal BRK Bevragen | `https://kadaster.github.io/BRK-bevragen/` | REST/OpenAPI |
| L2 | BRK-Levering (bulk-feed) | via Kadaster-aansluiting | XML-bulk inclusief Aantekening en akte-stukken |

**Advies**: IMKAD en de BRK-Catalogus zijn complementair: IMKAD voor
formele structuur, BRK-Catalogus voor wettelijk-juridische
definities. HC BRK plat `Tenaamstelling × ZakelijkRecht × Partij` tot
één resource; GBO splitst expliciet uit.

### BRP: Basisregistratie Personen

**Beheerder**: RvIG (Rijksdienst voor Identiteitsgegevens) onder het
Ministerie van BZK.

| Laag | Bron | URL | Karakter |
|---|---|---|---|
| L1 | Logisch Ontwerp BRP | `https://www.rvig.nl/lo-brp` | Narratief plus tabellen; geen UML of RDF |
| L1 | BRP Persoonslijst-categorieen | in LO BRP paragraaf 3 | Categorieen 01 t/m 63, historische +50 |
| L2 | Haal Centraal BRP-suite | `https://developer.rvig.nl/brp-api/overview/` | Zes REST/OpenAPI's |
| L2 | BRP-V berichtenverkeer (op basis van LO-A) | via RvIG-aansluiting | SOAP/XML, voor historie-rubrieken niet in HC |

**Advies**: LO BRP is dwingend voor definities; citeer altijd
`LO BRP §rubriek` in herkomst-veld. Voor attribuut-naamgeving volgt
GBO de HC-conventie tenzij L1 expliciet een Nederlandstalig
alternatief biedt dat semantisch sterker is.

### CKI: Centraal Krediet Informatiesysteem

**Beheerder**: Stichting BKR (Bureau Kredietregistratie) te Tiel,
privaatrechtelijke stichting.

| Laag | Bron | URL | Karakter |
|---|---|---|---|
| L1 | Algemeen Reglement CKI | `https://www.bkr.nl/media/4dyezfiz/algemeen-reglement-cki-juli-2024.pdf` | Juridisch reglement; 43 artikelen, 30 paginas |
| L1 | Wet op het financieel toezicht art. 4:32 | `https://wetten.overheid.nl/BWBR0020368` | Sectorregistratie-grondslag |
| L1 | Toelichtingsbrochure BKR | `https://www.bkr.nl/media/ssqbz200/kredietregistratie-bij-stichting-bkr.pdf` | Publieke uitleg met uitsluitings-lijst |
| L2 | Algemene Handleiding CKI | `https://www.bkr.nl/nl/inloggen-portalen` | Gated, alleen voor erkende zakelijke klanten |
| L3 | NORA-pagina CKI | `https://www.noraonline.nl/wiki/Centraal_Krediet_Informatiesysteem_(CKI)` | Sectorregistratie-positionering |

**Advies**: CKI is een private sectorregistratie. Wettelijk gegrondvest
in Wft art. 4:32; afname feitelijk verplicht via Wft art. 4:34 en
gedragsregels TRHK. L2 is permanent gated; voor GBO-Kern-modellering
volstaat L1 omdat alle concepten uit het reglement modelleerbaar zijn.

### HR: Handelsregister

**Beheerder**: KVK (Kamer van Koophandel) onder het Ministerie van EZ.

| Laag | Bron | URL | Karakter |
|---|---|---|---|
| L1 | L1 ontbreekt; modellering via L2 en L3 | n.v.t. | Geen publiek formeel HR-IM van KVK |
| L2 | KVK Developer Portal (vijf API's: Zoeken, Basisprofiel, Vestigingsprofiel, Naamgeving, Mutatieservice) | `https://developers.kvk.nl/documentation` | REST/OpenAPI |
| L2 | SBR-HR / XBRL | via SBR-banken | Optioneel, voor jaarverslag-keten |
| L3 | Handelsregisterwet 2007 + Handelsregisterbesluit 2008 | wetten.overheid.nl | Wettelijke definities Inschrijving, Onderneming, Vestiging |

**Substituutstrategie HR**: GBO leunt op een driepoot:
Handelsregisterwet 2007, de KVK-API-spec als surrogaat-IM, en
externe adviesmodellen als sanity-check. Citeer in elke
HR-attribuut: `herkomst: GBO-afleiding op basis van KVK Basisprofiel
en GGM Handelsregister-domein` (of relevante combinatie).

### Loonheffingen: Gegevensspecificaties aangifte loonheffingen

**Beheerder**: Belastingdienst en UWV gezamenlijk.

| Laag | Bron | URL | Karakter |
|---|---|---|---|
| L1+L2 | Gegevensspecificaties aangifte loonheffingen | `https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/themaoverstijgend/brochures_en_publicaties/gegevensspecificaties-aangifte-loonheffingen` | PDF met rubrieknummers plus XSD 1.0 |
| L1 | Wet LB 1964 | `https://wetten.overheid.nl/BWBR0002471` | Materiele loonheffing |
| L1 | Wfsv (Wet financiering sociale verzekeringen) | `https://wetten.overheid.nl/BWBR0017745` | Premiegrondslag |
| L1 | Besluit SUWI art. 5.1 | `https://wetten.overheid.nl/BWBR0013467` | Loonketen-governance (UWV operationeel) |

**Advies**: De loonketen-definities zijn inhoudelijk eigendom van de
Belastingdienst, ook al loopt de operationele keten via UWV. Modelleer
Inkomstenverhouding, Inkomstenopgave, Inkomstenperiode en
LoonBestanddeel daarom in deelmodel
[Belastingen](deelmodellen/belastingen.md), niet in
[Werk en Inkomen](deelmodellen/werk-en-inkomen.md). SGR ontsluit
dezelfde data operationeel.

### ROD: Register Onderwijsdeelnemers

**Beheerder**: DUO (Dienst Uitvoering Onderwijs) namens het
Ministerie van OCW.

| Laag | Bron | URL | Karakter |
|---|---|---|---|
| L1 | Wet op het onderwijsnummer | `https://wetten.overheid.nl/BWBR0014522` | Wettelijke basis voor het register |
| L1 | Sectorwetten WPO, WVO 2020, WEB, WHW | wetten.overheid.nl per wet | Inhoudelijke kaders per sector |
| L1 | Gegevenswoordenboek DUO | `https://duo.nl/zakelijk/standaarden-ocw/canonieke-gegevensmodellen/duo-gegevenswoordenboek.jsp` | Canoniek gegevensmodel; nog in bewerking |
| L2 | PvE ROD MBO en VAVO | `https://duo.nl/zakelijk/middelbaar-beroepsonderwijs/softwareleveranciers/softwareleveranciers-las.jsp` | PDF plus XSD; transport via Edukoppeling 1.3 |
| L2 | PvE ROD HO | `https://www.duo.nl/zakelijk/hoger-onderwijs/studentenadministratie/programma-van-eisen-rod-ho.jsp` | Idem |
| L2 | PvE ROD PO | `https://duo.nl/zakelijk/primair-onderwijs/softwareleveranciers/softwareleveranciers-las.jsp` | Idem |
| L2 | Handleiding ROD VO | `https://www.duo.nl/zakelijk/voortgezet-onderwijs/leerlingenadministratie/leerlinggegevens-uitwisselen-met-rod.jsp` | Idem |

**Advies**: ROD is geen basisregistratie maar wel een wettelijk
verplicht sectoraal register. Citeer per attribuut de sector-
specifieke PvE-rubriek. Wanneer het Gegevenswoordenboek DUO
formeel verschijnt, schuift L1 op van wettekst naar het
Gegevenswoordenboek.

### SBR-NT: Nederlandse Taxonomie (Belastingdienst-aangiften)

**Beheerder**: Belastingdienst CCT binnen SBR-NL governance,
samenwerking met Logius en KvK.

| Laag | Bron | URL | Karakter |
|---|---|---|---|
| L1+L2 | SBR-NT NT20 hoofdrelease (NT20_20251210) | `https://www.sbr-nl.nl/werken-met-sbr/taxonomie/documentatie-nederlandse-taxonomie` | XBRL-taxonomie; entrypoints voor IH 2025, VPB 2025, VIA, OWR |
| L1+L2 | SBR-NT NT20 1e extensie (NT20_20260218.a) | (zelfde portaal, alfaversie) | Entrypoints Schenk 2026, Erf 2026, Servicebericht Toeslagen 2026 |
| L1 | Wet IB 2001 | `https://wetten.overheid.nl/BWBR0011353` | Materiele wetgeving inkomstenbelasting |
| L1 | Successiewet 1956 | `https://wetten.overheid.nl/BWBR0002226` | Schenkbelasting, erfbelasting |
| L1 | Awir | `https://wetten.overheid.nl/BWBR0018472` | Toeslagen-grondslag |

**Advies**: Combineer L1 (materiele wet) en L2 (XBRL-conceptnaam) in
het herkomst-veld. Citeer release-naam expliciet (NT20_20251210 voor
hoofdrelease, NT20_20260218.a voor extensie). Vermeng labels en
references uit verschillende releases niet. Voor de
XBRL-naar-MIM-mapping geldt: `xbrl:label role=documentation` levert
de definitie, `xbrl:reference role=disclosure` levert de
wetreferentie, `xbrl:periodType` levert de tijdkarakteristiek.

### SGR: Suwi Gegevensregister

**Beheerder**: BKWI (Bureau Keteninformatisering Werk en Inkomen)
namens UWV.

| Laag | Bron | URL | Karakter |
|---|---|---|---|
| L1 | Suwi Gegevensregister | `https://sgr.bkwi.nl/sgr/index.html` | SuwiML XSD plus HTML-catalogus; circa 250 entiteiten |
| L1 | Bijlage 1 SGR (wettelijke grondslag per attribuut) | apart document op zelfde domein | Koppelt attribuut aan wetsartikel |
| L1 | Wet SUWI | `https://wetten.overheid.nl/BWBR0013060` | Stelselgrondslag UWV en SVB |
| L1 | Werknemers- en volksverzekeringswetten (WW, ZW, WIA, Wajong, AOW) | wetten.overheid.nl per wet | Inhoudelijke kaders per uitkering |
| L2 | SuwiML-berichten boven SGR (Polisadministratie-bevraging, Inkomstenopgaaf, Uitkeringsoverzicht) | `https://sgr.bkwi.nl/sgr/` | XML-payload boven SGR-entiteiten |

**Eigendomsverdeling binnen SGR**: SGR is L1 authoritative voor
UWV-eigen concepten (uitkeringen, beslissingen, dagloon,
arbeidsongeschiktheids-percentage, arbeidsverhouding). Voor
loonaangifteketen-afgeleide concepten (Inkomstenverhouding,
Inkomstenopgave, Inkomstenperiode, LoonBestanddeel) is de
Belastingdienst wettelijk eigenaar; SGR is daar een ontsluitings-
kanaal. AOW-administratie is operationeel SVB; SGR-dekking kan
beperkt zijn.

### WOZ: Waardering Onroerende Zaken

**Beheerder**: Waarderingskamer (toezicht), gemeenten (uitvoering),
Kadaster (LV-WOZ).

| Laag | Bron | URL | Karakter |
|---|---|---|---|
| L1 | L1 ontbreekt; modellering via L2 en L3 | n.v.t. | Geen vrij-toegankelijk WOZ-Gegevenswoordenboek |
| L2 | Haal Centraal WOZ Bevragen | `https://kadaster.github.io/WOZ-bevragen/` | REST/OpenAPI |
| L2 | LV-WOZ-bevraagservice (Kadaster) | via aansluiting | Bevraging |
| L3 | Wet WOZ en uitvoeringsbesluit | wetten.overheid.nl | Wettelijke definities WOZ-object, peildatum |
| L3 | Waarderingsinstructie (Waarderingskamer) | `https://www.waarderingskamer.nl/voor-gemeenten/hulpmiddelen/` | Beleidsmatige uitwerking |

**Substituutstrategie WOZ**: GBO leunt voor WOZ-objecttypering op de
combinatie Wet WOZ, Waarderingsinstructie en HC WOZ-schema. Geen van
drieën is L1; ze worden samen gebruikt conform de beslisregel "leid
zelf af bij gaten, niet ruimer dan de bron toelaat".

## Beslisregels

**L1 is default; L2 of L3 op functionele gronden.** De invulling van
elk UML-element komt in principe uit L1 zolang die beschikbaar is.
L2 of L3 wordt gebruikt wanneer L1 ontbreekt, niet voldoet, of wanneer
een functionele behoefte daarom vraagt (bijvoorbeeld afnemer-
herkenbaarheid in API-naamgeving, datatype-conventies, of
cross-registratie-binding).

**Leid zelf af bij gaten of conflicten.** Wanneer ook L2 en L3 geen
invulling leveren (HR en WOZ missen L1; sommige rubrieken zitten
alleen in legacy-koppelvlakken; twee L1's modelleren hetzelfde
concept anders), vul je de UML-eigenschap zelf in op basis van de
best beschikbare informatie. De afleiding moet semantisch passen bij
wat L1, L2 of L3 wel zegt, en mag niet ruimer zijn dan wat de bron
toelaat.

**Vermeld altijd de bron per UML-element.** Elke klasse en elk
attribuut krijgt verplichte herkomstvermelding waarin zichtbaar is
uit welke laag of welke combinatie de invulling komt. Zonder
bronverwijzing is een UML-element niet vastgesteld.

**Specifieke regels per bron-type**:

- Voor **basisregistraties** (BRP, BAG, BRK, BGT, WOZ, BRI) geldt de
  reguliere L1-default. Bij HR en WOZ leunt de eerste keus altijd
  op L2 wegens ontbrekend L1.
- Voor **sectorale registers** (ROD, CKI, SGR) wordt L1 ontleend
  aan het reglement of de catalogus van de beheerder. CKI heeft
  een gated L2; voor GBO-Kern-modellering is dat geen blokkade,
  alle concepten zijn modelleerbaar uit L1.
- Voor **SBR-NT en Loonheffingen** geldt L1+L2 gecombineerd: het
  document bevat zowel inhoudelijke definities als koppelvlak-
  specificaties. Citaten kunnen daarom van een PDF-pagina-anker zijn
  (definitie) of van een XBRL-conceptnaam (koppelvlak).
- Voor **InkomensOndersteuning** als cross-domein supertype boven
  Toeslag en Uitkering geldt een GBO-eigen afleiding op basis van
  Awir art. 1, Wet SUWI en de individuele werknemers- en
  volksverzekeringswetten. De koepel zelf staat niet in een enkele
  bron.

## Bronvermelding per UML-element

Per UML-element minimaal twee tagged-values:

| Tagged value | Wat | Voorbeeld |
|---|---|---|
| `herkomst:` | Verwijzing per eigenschap, of compact als een bron volstaat | "IMBAG paragraaf X (definitie, multipliciteit); HC BAG (naam, datatype)" |
| `bron-uri:` | Machine-leesbare bron-URI waar resolvable | "https://imbag.github.io/catalogus/objecttypen/Pand" |

Bij eigen afleiding (GBO-Kern-modellering zonder directe bron):

| Tagged value | Wat | Voorbeeld |
|---|---|---|
| `herkomst:` | Markeert afleiding plus gebruikte bronnen | "GBO-afleiding op basis van KVK Basisprofiel en GGM Handelsregister-domein" |

Voor cross-walks naar L3 en L4:

| Tagged value | Wat | Voorbeeld |
|---|---|---|
| `verwantBegrip:` | L3-binding | "https://standaarden.overheid.nl/tooi/id/" |
| `internationaal-equivalent:` | L4-binding via SKOS-mapping-relatie | "cpv:Person via skos:exactMatch" |

## Wat niet als bronlaag telt

De methodologische standaarden die GBO-Kern toepast zijn geen
inhoudelijke definitie-bronnen en horen niet als laag in dit
overzicht thuis:

- **MIM 1.2** is de modelleer-methodiek waarin GBO-Kern wordt
  uitgedrukt. Conformance-statement op model-niveau, geen referentie-
  laag.
- **SKOS** is het metamodel voor codelijsten. Per codelijst geldt
  een afzonderlijke L1- of L3-bron.
- **DCAT-AP-NL** is een dataset-metadata-standaard voor publicatie,
  niet voor inhoud.
- **StUF** is een legacy-transportlaag voor de gemeentelijke
  inkomende keten. Voor GBO-Kern de laagste terugval-bron.

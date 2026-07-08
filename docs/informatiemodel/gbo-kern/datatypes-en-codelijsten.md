---
title: "Datatypes en codelijsten"
description: "Gedeelde bouwstenen voor het hele model: simpele datatypes (MIM-primitieven), aanvullende datatypes (gestructureerd of domeinspecifiek) en stelselbrede codelijsten met cross-walks. Deelmodel-specifieke codelijsten staan bij het betreffende deelmodel."
---

# Datatypes en codelijsten

Bindende afspraken over de **typering van waarden** in alle deelmodellen.
Deze typen worden niet als objecttype gemodelleerd; ze zijn de
bouwstenen van attribuutsoorten en relatie-eigenschappen.

GBO volgt waar mogelijk het
[Metamodel voor Informatiemodellering (MIM) 1.2](https://docs.geostandaarden.nl/mim/mim/)
van [Geonovum](https://www.geonovum.nl/):

- **Datatypes** zijn MIM-primitieven (`CharacterString`, `Integer`,
  `Date`, `Boolean`, enzovoort) en aanvullende gestructureerde typen
  (`Geometrie`, `Codelijst~bron`, GBO- of BRP-specifieke typen). De
  MIM-naam is leidend; de Nederlandse synoniem die in de
  attribuut-tabellen van de deelmodellen wordt gebruikt staat als alias.
- **Codelijsten** (MIM-stereotype `«Codelijst»`) zijn extern beheerde
  value-sets bij houders als
  [CBS](https://www.cbs.nl/),
  [ISO](https://www.iso.org/),
  [Kadaster](https://www.kadaster.nl/),
  [KOOP](https://www.koopoverheid.nl/),
  [RvIG](https://www.rvig.nl/),
  [KVK](https://www.kvk.nl/),
  [IND](https://ind.nl/) en
  [Waarderingskamer](https://www.waarderingskamer.nl/). Stelselbrede
  codelijsten staan op deze pagina; deelmodel-specifieke codelijsten
  staan bij het betreffende deelmodel.
- **Enumeraties** (MIM-stereotype `«Enumeratie»`) zijn gesloten
  value-sets die in dit model zelf zijn vastgelegd; zie de
  `## Enumeraties`-sectie in elk deelmodel.

## Simpele datatypes

Eén-op-één afgeleid van de MIM 1.2-primitieve datatypes (zie
[MIM 1.2](https://docs.geostandaarden.nl/mim/mim/)).

| MIM-datatype | Alias (NL) | Definitie | Herkomst | Toelichting |
|---|---|---|---|---|
| `CharacterString` | `Tekst` | Reeks Unicode-tekens. | [MIM 1.2](https://docs.geostandaarden.nl/mim/mim/) | Lengte-varianten: `Tekst24` (max. 24 tekens). De alias `Alfanumeriek` wordt gebruikt voor reeksen uit het alfabet en de cijfers zonder leestekens, met varianten `Alfanumeriek10`, `AN40`, `AN80`. De alias `Identificatie` wordt gebruikt voor object- of documentidentificaties zonder vaste structuur; de alias `Postcode` voor de Nederlandse postcode in het formaat `9999 XX` (norm NEN 5825). |
| `Integer` | `Numeriek` (geheel) | Geheel getal zonder eenheid. | [MIM 1.2](https://docs.geostandaarden.nl/mim/mim/) | Varianten met vaste lengte: `N2`, `N4`, `N5`, `N6` (geheel getal van precies dat aantal cijfers); varianten met maximumlengte: `Numeriek8`, `Numeriek9`, `Numeriek12`. |
| `Real` | `Numeriek` (decimaal) / `Decimaal` | Decimaal getal zonder eenheid. | [MIM 1.2](https://docs.geostandaarden.nl/mim/mim/) | De alias `Decimaal` wordt in de deelmodellen gebruikt voor breuk-getallen zonder valuta-aanduiding, bijvoorbeeld `Schuld.rentepercentage` en `ModuleInschrijving.ects`. Voor bedragen wordt `Bedrag` gebruikt (zie aanvullende datatypes), niet `Real` direct, vanwege de verplichte valuta-aanduiding. |
| `Boolean` | `Indicatie` | Logische waarde waar/onwaar. | [MIM 1.2](https://docs.geostandaarden.nl/mim/mim/) | GBO hanteert als NL-conventie een drie-waardig type `Indicatie` (Ja / Nee / Onbekend), zodat onbekendheid expliciet kan worden vastgelegd. De waarde Onbekend is geen MIM-Boolean-waarde maar volgt de BRP-conventie voor afwezigheid (zie [Logisch Ontwerp BRP](https://www.rvig.nl/lo-brp)). Daarnaast bestaat de tweewaardige variant `IndicatieJaNee` (Ja / Nee) voor gegevens waarbij een afwezige waarde zelf betekenis draagt (niet vastgesteld of niet van toepassing), zoals de BRP-kiesrechtgegevens `uitsluitingKiesrecht` en `europeesKiesrecht`. |
| `Date` | `Datum` | Kalenderdatum in [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html), precisie tot op de dag (`jjjj-mm-dd`). | [MIM 1.2](https://docs.geostandaarden.nl/mim/mim/) / [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) | Gebruikt voor de materiële tijdlijn (geldigheid van een gegeven in de werkelijkheid). |
| `DateTime` | `DatumTijd` | Datum met tijdstip in [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html), precisie tot op de seconde (`jjjj-mm-ddThh:mm:ss`). | [MIM 1.2](https://docs.geostandaarden.nl/mim/mim/) / [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) | Gebruikt voor de formele tijdlijn (registratiemoment in een systeem). |
| `Year` | `Jaar` | Kalenderjaar in [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html), vier cijfers (`jjjj`). | [MIM 1.2](https://docs.geostandaarden.nl/mim/mim/) / [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) | Gebruikt voor `oorspronkelijkBouwjaar` op Pand en andere jaar-precieze gegevens. |
| `Duration` | `Duur` | Tijdsduur in [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html)-periode-notatie (`P5Y`, `P3M`, `P7D`). | [MIM 1.2](https://docs.geostandaarden.nl/mim/mim/) / [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) | Gebruikt voor bewaartermijnen en doorlooptijden, bijvoorbeeld `BijzonderheidsCodering.bewaartermijnPeriode` (vijf jaar conform Algemeen Reglement CKI). |
| `URI` | `URI` | Uniform Resource Identifier conform [RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986). | [MIM 1.2](https://docs.geostandaarden.nl/mim/mim/) / [RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986) | Gebruikt voor `begrip`-verwijzingen naar NL-SBB en andere semantische ankers. |

## Aanvullende datatypes

Samengestelde of domeinspecifieke datatypes. Waar een MIM- of
ISO-19107-equivalent bestaat staat dat in de tweede kolom; waar geen
MIM-equivalent bestaat is de notatie GBO-specifiek of BRP-specifiek.

| Datatype | MIM-equivalent | Definitie | Herkomst | Toelichting |
|---|---|---|---|---|
| `DatumIncompleet` | (geen) | Datum waarin jaar, maand of dag elk afzonderlijk onbekend kan zijn. Formaten: `jjjj`, `jjjj-mm` of `jjjj-mm-dd`; nullen op de onbekende positie. | [Logisch Ontwerp BRP](https://www.rvig.nl/lo-brp) | BRP-conventie voor geboortedatum, datum overlijden en datum verkrijging nationaliteit die onvolledig in de bronregistratie kunnen staan. MIM kent geen onvolledige datum als primitief. Volledige datum wordt gerepresenteerd als gewone `Date` / `Datum`. |
| `BAGID` | `Identificatie` | BAG-objectidentificatie: een 16-cijferige code, opgebouwd uit gemeentecode (4), objecttypecode (2) en objectvolgnummer (10). | [BAG-objecten (Kadaster)](https://www.kadaster.nl/-/bag-objecten) | Gebruikt voor de BAG-objecten Pand, Verblijfsobject, Standplaats, Ligplaats, Nummeraanduiding, Openbare ruimte en Woonplaats, voor verwijzingen daarnaar (zoals `adresseerbaarObjectId`), en voor `Binnenlandsadres.adresId` (gelijk aan de identificatie van de Nummeraanduiding). |
| `NEN3610ID` | `Identificatie` (in [NEN 3610](https://docs.geostandaarden.nl/nen3610/) als gestructureerd datatype) | Landelijke objectidentificatie voor stelselobjecten, opgebouwd uit `namespace : lokalID : versie`. | [NEN 3610 Basismodel Geo-informatie](https://www.geonovum.nl/geo-standaarden) ([documentatie](https://docs.geostandaarden.nl/nen3610/)) | Gebruikt voor BRK-objecten (KadastraleOnroerendeZaak, ZakelijkRecht) en publiekrechtelijke beperkingen. Garandeert uniciteit over registers heen. |
| `UUID` | (geen) | Universally Unique Identifier conform [RFC 4122](https://datatracker.ietf.org/doc/html/rfc4122) (128 bits, hex-genotat). | [RFC 4122](https://datatracker.ietf.org/doc/html/rfc4122) | Interne GBO-identifier voor objecten zonder externe authentieke identifier: `id`, `MaatschappelijkeActiviteit.identificatie` en het `adresId` van de niet-BAG-adresvormen (Buitenlandsadres, Locatie, Postadres, VerblijfplaatsOnbekend). |
| `BSN` | `Tekst` + patroon `^[0-9]{9}$` | Burgerservicenummer: 9 cijfers met geldige elfproef. | [Wet algemene bepalingen burgerservicenummer](https://wetten.overheid.nl/BWBR0024466) | Zoeksleutel van `IngeschrevenPersoon` (natuurlijk persoon). Als tekst getypeerd zodat een voorloopnul behouden blijft. |
| `KVKnummer` | `Tekst` + patroon `^[0-9]{8}$` | Identificatie van een inschrijving in het Handelsregister: 8 cijfers. | [Handelsregisterwet 2007](https://wetten.overheid.nl/BWBR0021777) | Zoeksleutel van `Inschrijving` (niet-natuurlijke persoon). |
| `Vestigingsnummer` | `Tekst` + patroon `^[0-9]{12}$` | Identificatie van een vestiging in het Handelsregister: 12 cijfers. | Handelsregister (NHR) | Zoeksleutel van `Vestiging`. |
| `Kenteken` | `Tekst` + patroon | Nederlands voertuigkenteken: zes posities (hoofdletters en cijfers) volgens het RDW-sidecodestelsel, optioneel met streepjes. | RDW (BRV) | Zoeksleutel van `Voertuig`. |
| `KadastraleAanduiding` | `Tekst` | Kadastrale gemeente, sectie en perceelnummer (bij een appartementsrecht aangevuld met een index), uniek binnen de BRK. | Kadaster (BRK) | Natuurlijke sleutel van `Perceel` en `Appartementsrecht`. |
| `BRINcode` | `Tekst` + patroon `^[0-9]{2}[A-Z]{2}$` | BRIN-nummer van een onderwijsinstelling: twee cijfers gevolgd door twee hoofdletters. | DUO (BRIN) | Natuurlijke sleutel van `OnderwijsInstelling`. |
| `Aangifteperiode` | `Tekst` + patroon `^[0-9]{4}(-[MW][0-9]{2})?$` | Aanduiding van het aangiftetijdvak loonheffingen: jaar plus tijdvak-code, bijvoorbeeld `2026-M01` (maand) of `2026-W04` (vier weken); de kale jaarvorm (`2026`) duidt een jaaraggregaat aan, zoals de vooringevulde aangifte die levert. | Gegevensspecificaties aangifte loonheffingen | Gebruikt voor `Inkomstenopgave.aangifteperiode` en `LoonAangifte.aangifteperiode`. |
| `Codelijst~bron` | MIM-stereotype `«Codelijst»` | Verwijzing naar een waarde uit een extern beheerde codelijst. De bron staat als suffix achter de tilde. | [MIM 1.2](https://docs.geostandaarden.nl/mim/mim/) | Voorbeelden: `Codelijst~ISO3166` (zie [ISO 3166-1 alpha-2](https://www.iso.org/iso-3166-country-codes.html)), `Codelijst~LT33` (BRP-gemeentecode, zie [Landelijke Tabel 33](https://publicaties.rvig.nl/home)), `Codelijst~CBS_SBI` ([CBS Standaard Bedrijfsindeling](https://www.cbs.nl/nl-nl/onze-diensten/methoden/classificaties/activiteiten/standaard-bedrijfsindeling--sbi--)), `Codelijst~KVK_Bedrijf` ([KVK-rechtsvorm](https://developers.kvk.nl/)). Stelselbrede codelijsten staan hieronder; deelmodel-specifieke codelijsten staan bij het betreffende deelmodel. |
| `Geometrie` | `GM_Object` ([ISO 19107](https://www.iso.org/standard/66175.html), in MIM opgenomen als gestructureerd datatype) | Ruimtelijke objectplaatsing. Abstract supertype met drie concrete subtypes: `Punt`, `Vlak` en `Lijn`. | [NEN 3610](https://docs.geostandaarden.nl/nen3610/) / [ISO 19107](https://www.iso.org/standard/66175.html) | Default-coördinatenstelsel: EPSG:28992 (RD-New) voor binnenlandse objecten; WGS84 (EPSG:4326) waar uitwisseling internationaal is. Het coördinatenstelsel staat als attribuut op `Geometrie` zelf, niet op elke toepassing. |
| `Punt` | `GM_Point` ([ISO 19107](https://www.iso.org/standard/66175.html)) | Geometrie als één coördinaat (`x`, `y`, optioneel `z`). | [NEN 3610](https://docs.geostandaarden.nl/nen3610/) / [ISO 19107](https://www.iso.org/standard/66175.html) | Gebruikt voor `Verblijfsobject.geometriePunt` (verblijfsobjectpunt-conventie). |
| `Vlak` | `GM_Surface` ([ISO 19107](https://www.iso.org/standard/66175.html)) | Geometrie als gesloten polygoon, eventueel met binnenringen voor uitsparingen. | [NEN 3610](https://docs.geostandaarden.nl/nen3610/) / [ISO 19107](https://www.iso.org/standard/66175.html) | Gebruikt voor Pand, Ligplaats, Standplaats, Perceel, Woonplaats, Gemeente, Wijk en Buurt. |
| `Lijn` | `GM_Curve` ([ISO 19107](https://www.iso.org/standard/66175.html)) | Geometrie als reeks aaneengesloten lijnsegmenten. | [NEN 3610](https://docs.geostandaarden.nl/nen3610/) / [ISO 19107](https://www.iso.org/standard/66175.html) | Gebruikt voor OpenbareRuimte van het type weg of water. |
| `Bedrag` | (geen; in MIM als gestructureerd datatype `«DataType» Bedrag` op te nemen) | Geldbedrag: numerieke waarde met expliciete valuta-aanduiding ([ISO 4217](https://www.iso.org/iso-4217-currency-codes.html)). | [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html) | Voor binnenlandse toepassingen impliciet EUR; de valuta wordt expliciet bij internationale uitwisseling. Gebruikt voor `WOZWaarde.vastgesteldeWaarde` en `Zekerheidsrecht.bedrag`. |
| `Breuk` | (geen) | Rationaal getal als teller / noemer. | GBO | Gebruikt voor `Tenaamstelling.aandeel` (bijvoorbeeld 1/2, 1/3) zodat mede-eigendom exact zonder afrondingsverlies wordt vastgelegd. |
| `ObjectAanduiding` | (geen) | Gestandaardiseerde samenstelling van gemeentecode en objectnummer als één string. | [Wet WOZ](https://wetten.overheid.nl/BWBR0007119) / [Waarderingskamer — gegevensbeheer](https://www.waarderingskamer.nl/voor-gemeenten/gegevensbeheer) | Gebruikt voor `WOZObject.aanduiding`. Maakt een WOZ-object uniek identificeerbaar buiten de eigen gemeentecontext, want het ruwe `wozObjectnummer` is alleen binnen één gemeente uniek. |

## Codelijst-strategie

GBO hanteert een **hybride** aanpak: internationale norm leidend voor
**semantiek** waar die bestaat
([ISO 3166](https://www.iso.org/iso-3166-country-codes.html));
[BRP-Landelijke Tabel](https://publicaties.rvig.nl/home) leidend voor
**uitwisseling** met de BRP-keten. Cross-walks tussen beide staan
hieronder voor de stelselbrede gevallen; deelmodel-specifieke
cross-walks staan bij het betreffende deelmodel.

## Stelselbrede codelijsten

Alfabetisch op bron. Elke rij verwijst direct naar de actuele lijst bij
de beheerder.

| Codelijst | Bron / beheerder | GBO-typering | Gebruikt door |
|---|---|---|---|
| [BRP-Landelijke Tabel 33 Gemeenten](https://publicaties.rvig.nl/home) | [RvIG](https://www.rvig.nl/landelijke-tabellen-en-besluiten) / BZK | `Codelijst~LT33` | Stelselbreed voor gemeente-codering. [Adressen en gebouwen](deelmodellen/adressen-en-gebouwen.md): `Gemeente.gemeentecode`. [Personen](deelmodellen/personen.md): `IngeschrevenPersoon.gemeenteVanInschrijving`. [Waarde onroerende zaken](deelmodellen/waarde-onroerende-zaken.md): `WOZObject.verantwoordelijkeGemeente`. Formeel een BRP-codelijst, feitelijk de stelselbrede gemeente-codering inclusief historische gemeenten met einddatum. |
| [CBS Standaard Bedrijfsindeling (SBI 2008 / 2025)](https://www.cbs.nl/nl-nl/onze-diensten/methoden/classificaties/activiteiten/standaard-bedrijfsindeling--sbi--) — [SBI-zoektool](https://www.cbs.nl/nl-nl/onze-diensten/methoden/classificaties/activiteiten/standaard-bedrijfsindeling--sbi--/sbi-code-zoeken) | [CBS](https://www.cbs.nl/) | `Codelijst~CBS_SBI` | Stelselbreed voor bedrijfsindeling; primair in [Bedrijven en instellingen](deelmodellen/bedrijven-en-instellingen.md) (`Activiteit.sbiCode`, `Activiteit.sbiVersie`, `NietNatuurlijkPersoon.hoofdSbiCode`, `MaatschappelijkeActiviteit.hoofdSbiCode`). |
| [CBS Wijk- en Buurtkaart](https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data) (jaarlijkse uitgave; [Kerncijfers wijken en buurten 2024](https://www.cbs.nl/nl-nl/maatwerk/2024/35/kerncijfers-wijken-en-buurten-2024)) | [CBS](https://www.cbs.nl/) | `Codelijst~CBS_WijkBuurt` | [Adressen en gebouwen](deelmodellen/adressen-en-gebouwen.md): `Wijk.wijkcode`, `Buurt.buurtcode`. |
| [ISO 3166-1 alpha-2 (landcodes)](https://www.iso.org/iso-3166-country-codes.html) | [ISO](https://www.iso.org/) | `Codelijst~ISO3166` | Stelselbreed voor land- en nationaliteit-typering. [Personen](deelmodellen/personen.md): `Nationaliteit.nationaliteit`, `NatuurlijkPersoon.geboorteland`, `NatuurlijkPersoon.landOverlijden`, `Immigratie.landVanwaar`, `Immigratie.landBinnenkomst`, `Huwelijk.landVoltrekking`, `NietIngezetene.landVanVerblijf`. [Bedrijven en instellingen](deelmodellen/bedrijven-en-instellingen.md): `BuitenlandseEntiteit.landVanOprichting`. [Adressen en gebouwen](deelmodellen/adressen-en-gebouwen.md): `Buitenlandsadres.land`, `Locatie.land`. |
| [Kadastrale aanduiding — kadastrale gemeente / sectie / perceelnummer](https://www.kadaster.nl/zakelijk/registraties/basisregistraties/brk) | [Kadaster](https://www.kadaster.nl/) | `Codelijst~Kadaster` | [Onroerende zaken](deelmodellen/onroerende-zaken.md): `Perceel.kadastraleGemeente`. De lijst kadastrale gemeenten is onderdeel van de [Basisregistratie Kadaster (BRK)](https://www.kadaster.nl/zakelijk/registraties/basisregistraties/brk) en wijzigt mee met gemeentelijke herindelingen. |
| [TOOI-waardelijsten — Register van Overheidsorganisaties](https://organisaties.overheid.nl/) ([standaard](https://standaarden.overheid.nl/tooi), [waardelijsten-documentatie](https://standaarden.overheid.nl/tooi/doc/tooi-waardelijsten/)) | [KOOP](https://www.koopoverheid.nl/) / [Logius](https://www.logius.nl/) | `Codelijst~TOOI` | [Bedrijven en instellingen](deelmodellen/bedrijven-en-instellingen.md): `Overheidsinstelling.bevoegdGezagCode`. |

## Cross-walks

De cross-walk-fragmenten hieronder tonen een handvol voorbeeldrijen per
groep; de volledige lijst telt honderden codes en wordt onderhouden
door [RvIG](https://www.rvig.nl/) op
[publicaties.rvig.nl](https://publicaties.rvig.nl/home). Volg de link
onder elke tabel voor het feitelijke bronbestand.

### ISO 3166 ↔ BRP-LT 32 (nationaliteit)

[BRP-Landelijke Tabel 32 Nationaliteiten](https://publicaties.rvig.nl/home)
levert per nationaliteit een 4-cijferige BRP-code, een omschrijving en,
waar van toepassing, een 2-letterige ISO-code. GBO modelleert het
attribuut `Nationaliteit.nationaliteit` als
[`Codelijst~ISO3166`](https://www.iso.org/iso-3166-country-codes.html)
(semantiek leidend) met cross-walk naar LT 32 voor BRP-uitwisseling.

| BRP-code (LT 32) | ISO 3166-1 alpha-2 | Omschrijving |
|---|---|---|
| 0001 | NL | Nederlandse |
| 0026 | DE | Duitse |
| 0027 | BE | Belgische |
| 0083 | FR | Franse |
| 0125 | GB | Britse |
| 0337 | US | Amerikaanse |
| 0498 | (geen) | Statenloos / vluchteling-status (geen ISO-equivalent) |
| … | … | … |

LT 32 bevat codes zonder ISO-equivalent (statenloos, Behandeld als
Nederlander, vluchteling-status). Deze blijven via BRP-code zichtbaar;
de cross-walk-tabel registreert dit als `(geen)` aan de ISO-zijde.

**Volledige lijsten**:

- [Tabel 32 Nationaliteiten — directe download (publicaties.rvig.nl)](https://publicaties.rvig.nl/media/13281/download).
- [BRP Landelijke Tabellen — overzicht (RvIG)](https://www.rvig.nl/landelijke-tabellen-en-besluiten).
- [ISO 3166-1 alpha-2 (iso.org)](https://www.iso.org/iso-3166-country-codes.html).

### ISO 3166 ↔ BRP-LT 34 (landen)

[BRP-Landelijke Tabel 34 Landen](https://publicaties.rvig.nl/home)
gebruikt 4-cijferige BRP-codes; ISO 3166 gebruikt 2-letterige
alpha-2-codes.

| BRP-code (LT 34) | ISO 3166-1 alpha-2 | Omschrijving |
|---|---|---|
| 6030 | NL | Nederland |
| 5005 | DE | Duitsland |
| 5010 | BE | België |
| 4030 | FR | Frankrijk |
| 9000 | (escape) | Onbekend |
| … | … | … |

**Volledige lijsten**:

- [Tabel 34 Landen — directe download (publicaties.rvig.nl)](https://publicaties.rvig.nl/media/13285/download).
- [BRP Landelijke Tabellen — overzicht (RvIG)](https://www.rvig.nl/landelijke-tabellen-en-besluiten).
- [ISO 3166-1 alpha-2 (iso.org)](https://www.iso.org/iso-3166-country-codes.html).

### IND ↔ BRP-LT 56 (verblijfstitel)

[BRP-Landelijke Tabel 56 Verblijfstitels](https://publicaties.rvig.nl/home)
levert per verblijfstitel een BRP-code met IND-cross-link. GBO
modelleert `Verblijfstitel.aanduiding` als
[`Codelijst~IND`](https://ind.nl/nl/verblijfsvergunningen) (autoritatief
vanuit [IND](https://ind.nl/)) met cross-walk naar LT 56 voor
BRP-uitwisseling. De cross-walk evolueert mee met IND-beleidswijzigingen.

| BRP-code (LT 56) | IND-aanduiding | Omschrijving |
|---|---|---|
| 9 | (geen verblijfstitel) | Onderdaan EU / EER, geen titel nodig |
| 10 | verblijf onbeperkt | Verblijfsvergunning regulier voor onbepaalde tijd |
| 11 | verblijf bepaald | Verblijfsvergunning regulier voor bepaalde tijd |
| 12 | asiel onbeperkt | Verblijfsvergunning asiel onbepaalde tijd |
| 13 | asiel bepaald | Verblijfsvergunning asiel bepaalde tijd |
| … | … | … |

**Volledige lijsten**:

- [BRP-LT 56 Verblijfstitel — publicaties.rvig.nl](https://publicaties.rvig.nl/home), ook beschikbaar via de [Haal Centraal BRP Tabellen-API](https://developer.rvig.nl/brp-api/).
- [Logisch Ontwerp BRP](https://www.rvig.nl/lo-brp) §11.10.
- [IND Verblijfsvergunningen](https://ind.nl/nl/verblijfsvergunningen).

## Versionering en herindelingen

### CBS Wijk en Buurt: jaarlijkse herziening

CBS herziet Wijk- en Buurtgrenzen jaarlijks via de
[Wijk- en Buurtkaart](https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data).
Modellering via het `Voorkomen`-mixin op Wijk en Buurt; bij
grens-mutatie ontstaat een nieuwe versie. Er is geen
`nieuweCode`-mechanisme: CBS-codes zijn stabiel, alleen de geometrie
muteert.

### CBS SBI: verplicht versie-attribuut

De overgang van
[SBI 2008 naar SBI 2025](https://www.cbs.nl/nl-nl/onze-diensten/methoden/classificaties/activiteiten/standaard-bedrijfsindeling--sbi--)
maakt versie-aanduiding noodzakelijk. GBO modelleert `Activiteit.sbiCode`
met een verplicht `sbiVersie` zodat code en versie samen blijven.

## Onderhoudsritme

Stelselbrede codelijsten. Voor deelmodel-specifieke codelijsten staat
het onderhoudsritme bij het betreffende deelmodel.

| Codelijst | Mutatieritme | Bron |
|---|---|---|
| [BRP-LT 32 Nationaliteiten](https://publicaties.rvig.nl/home) | Halfjaarlijks | [RvIG](https://www.rvig.nl/landelijke-tabellen-en-besluiten) |
| [BRP-LT 33 Gemeenten](https://publicaties.rvig.nl/home) | Jaarlijks (1 januari, gemeentelijke herindelingen) | [RvIG](https://www.rvig.nl/landelijke-tabellen-en-besluiten) |
| [BRP-LT 34 Landen](https://publicaties.rvig.nl/home) | Halfjaarlijks | [RvIG](https://www.rvig.nl/landelijke-tabellen-en-besluiten) |
| [BRP-LT 56 Verblijfstitels](https://publicaties.rvig.nl/home) | Per IND-beleidswijziging | [RvIG](https://www.rvig.nl/landelijke-tabellen-en-besluiten) (afstemming met IND) |
| [CBS SBI](https://www.cbs.nl/nl-nl/onze-diensten/methoden/classificaties/activiteiten/standaard-bedrijfsindeling--sbi--) | Per SBI-revisie | [CBS](https://www.cbs.nl/) |
| [CBS Wijk- en Buurtkaart](https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data) | Jaarlijks | [CBS Open Data](https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data) |
| [ISO 3166](https://www.iso.org/iso-3166-country-codes.html) | Sporadisch (paar keer per decennium) | [ISO](https://www.iso.org/) |
| [Kadastrale Gemeenten (BRK)](https://www.kadaster.nl/zakelijk/registraties/basisregistraties/brk) | Periodiek (volgt gemeentelijke herindeling) | [Kadaster](https://www.kadaster.nl/) |
| [TOOI](https://standaarden.overheid.nl/tooi) | Continu | [Register van Overheidsorganisaties](https://organisaties.overheid.nl/) |

Codelijsten worden bij afnemers als **referentie-bestand** gehouden,
niet hard-gecodeerd. Synchronisatie via de bron-publicatie of de
[Haal Centraal BRP Tabellen-API](https://developer.rvig.nl/brp-api/),
met verifiërende re-resolve bij sleutelmoment (verstrekking,
beschikking, inschrijving).

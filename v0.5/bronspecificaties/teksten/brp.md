---
# Handgeschreven delen van de GBO Bronspecificatie BRP. Alle modelfeiten
# komen uit publicatie/linkml/ en publicatie/bronnen/brp.yaml; dit
# bestand levert alleen de context, de brondocumentenlijst, de
# toetsvragen en de open punten. Zie README.md in deze map.
bron: BRP
status: consultatieversie
consultatieronde: 1
reactietermijn: "n.t.b."
contact:
  naam: "n.t.b."
  organisatie: "n.t.b."
  email: "n.t.b."
bronhouder: >-
  Rijksdienst voor Identiteitsgegevens (RvIG), ministerie van
  Binnenlandse Zaken en Koninkrijksrelaties
brondocumenten:
  - laag: L1
    titel: Logisch Ontwerp BRP
    uitgever: RvIG
    versie: "2026.Q3"
    datum: 2026-07-01
    vindplaats: https://www.rvig.nl/lo-brp2026Q3
    gebruik: >-
      Definities en structuur van de persoonslijst (categorieën,
      groepen, elementen) en de structuur van de landelijke tabellen.
    toelichting: >-
      De herkomstverwijzingen in dit document citeren deze versie. Het
      model is opgebouwd uit versie 4.3.0 (15 mei 2023); hoofdstuk 4
      van beide versies is vergeleken en de geciteerde paragrafen,
      categorieën, groepen en elementen zijn ongewijzigd.
  - laag: L1
    titel: Wet basisregistratie personen
    uitgever: Rijksoverheid
    vindplaats: https://wetten.overheid.nl/BWBR0033715
    gebruik: >-
      Wettelijke grondslag van de objecttypen en van de aanduiding
      van authentieke gegevens.
  - laag: L2
    titel: Haal Centraal BRP Personen Bevragen (OpenAPI)
    uitgever: RvIG
    versie: "2.7.0"
    vindplaats: https://brp-api.github.io/Haal-Centraal-BRP-bevragen/
    gebruik: >-
      Naamgeving van attributen, datatypen en de herleiding per
      element naar het koppelvlak (bijlage B).
  - laag: L2
    titel: Haal Centraal BRP Tabellen Bevragen
    uitgever: RvIG
    versie: "1.0"
    vindplaats: https://developer.rvig.nl/brp-api/overview/
    gebruik: >-
      Surrogaat voor de inhoud van de landelijke tabellen (LT 32 tot
      en met 61), waarvan RvIG geen vrij toegankelijke publicatie
      biedt.
# Mapping-pagina's in de wiki waaruit bijlage B het koppelvlakpad per
# element overneemt. Paden zijn relatief aan de wortel van de wiki-repo.
herleiding:
  - pad: wiki/gbo-core/api-compatibiliteit/brp-personen.md
    koppelvlak: HC BRP Personen Bevragen 2.7.0
---

## Context

De Basisregistratie Personen (BRP) is in GBO de bron voor de
natuurlijke persoon zoals die op een persoonslijst is geregistreerd:
ingezetenen van een Nederlandse gemeente en, via de Registratie
Niet-Ingezetenen (RNI), personen buiten Nederland met een relatie tot
de Nederlandse overheid. GBO ontsluit uit deze bron de kern van de
persoonslijst: identificatie, naam, geboorte, geslacht, overlijden,
nationaliteit, huwelijk en geregistreerd partnerschap, verblijfstitel,
gezag, immigratie, inschrijving en bijhoudingsstatus, en het actuele
verblijfadres. Gegevens over reisdocumenten, afnemersindicaties en
verwijsgegevens blijven buiten deze bron.

De bevraging loopt via het burgerservicenummer van de ingeschreven
persoon. Gerelateerden (ouders en partners) worden geleverd zoals zij
op de eigen persoonslijst voorkomen, als natuurlijk persoon zonder
doorverwijzing naar hun eigen persoonslijst. Een afnemer die gegevens
van een gerelateerde nodig heeft, doet daarvoor een eigen bevraging
met een eigen grondslag.

De modellering is afgeleid van het Logisch Ontwerp BRP en getoetst
aan de Haal Centraal BRP Personen Bevragen API, zodat de naamgeving
herkenbaar is voor afnemers die dat koppelvlak kennen. Waar het LO en
Haal Centraal verschillen, volgt de definitie het LO en de naamgeving
Haal Centraal; bijlage B toont per element beide.

## Toetsvragen

### Algemeen

- Zijn de definities en de herkomstverwijzingen (categorie, groep en
  element van de persoonslijst) juist en volledig? Waar wijkt een
  GBO-definitie zo af van het LO dat dit tot misverstanden leidt?
- Klopt de aanduiding Authentiek per gegeven? Zijn er gegevens die
  volgens de Wet BRP authentiek zijn maar hier als Basisgegeven staan,
  of omgekeerd?
- GBO levert via deze bron de actuele stand van nationaliteit,
  huwelijk, verblijfstitel en gezag; de historische categorieën
  (54, 55, 60 en 61) worden niet ontsloten. Is dat voor de beoogde
  afnemers voldoende, of moet de historie van deze categorieën worden
  opgenomen?
- Ontbreken er gegevens uit de persoonslijst die afnemers via GBO
  nodig hebben en die niet in de open punten (bijlage D) staan?

### NatuurlijkPersoon

- Ouders worden geleverd als twee gerelateerde personen zonder het
  onderscheid Ouder1 en Ouder2 en zonder de datum van ingang van de
  familierechtelijke betrekking. Is dat voor afnemers werkbaar?
- Een gerelateerde (ouder, partner) draagt in het model geen
  burgerservicenummer. Mag het BSN van een gerelateerde, zoals het op
  de eigen persoonslijst staat, worden geleverd zonder dat daarmee de
  persoonslijst van die gerelateerde opvraagbaar wordt?
- Het geboorteland en het land van overlijden zijn getypeerd als
  ISO 3166-code, terwijl de persoonslijst Tabel 34 gebruikt. Tabel 34
  draagt sinds 2025 zelf de ISO-codes. Is de ISO-code als
  uitwisselvorm akkoord, of moet de Tabel 34-code worden geleverd?

### IngeschrevenPersoon

- De indicatie geheimhouding is gemodelleerd als een enkelvoudige
  indicatie, waar het LO zeven niveaus kent. Is er een afnemer die
  meer nodig heeft dan de indicatie?
- De opschorting van de bijhouding levert de reden (element 67.20)
  maar nog niet de datum (67.10). Is de datum voor afnemers nodig?
- Onderzoek naar gegevens is één indicatie op de persoon, niet per
  gegevensgroep zoals in het LO en in Haal Centraal. Is dat aanvaardbaar
  voor een eerste versie?
- Het A-nummer wordt bewust niet geleverd. Zijn er afnemers die het
  A-nummer nodig hebben?
- Het buitenlands persoonsnummer (groep 73) staat op de persoon, terwijl
  het LO het onder de nationaliteit plaatst. Is die vereenvoudiging
  houdbaar?

### Ingezetene en verblijfadres

- Het verblijfadres wordt geleverd als een binnenlands adres met de
  identificatie van de nummeraanduiding uit de BAG. De functie van het
  adres (woon- of briefadres), de datum aanvang adreshouding en de
  identificatie van het adresseerbaar object ontbreken nog. Welke
  daarvan zijn voor afnemers onmisbaar?
- Personen zonder adres (locatieomschrijving of verblijfplaats
  onbekend) worden nog niet onderscheiden. Hoe vaak komt dit voor bij
  de beoogde afnemers en hoe moet GBO het tonen?
- Het briefadres wordt niet via deze bron ontsloten. Is dat juist?

### NietIngezetene

- Voor niet-ingezetenen levert GBO het land van verblijf, het
  buitenlands adres, de RNI-deelnemer (Tabel 60) en de verificatie.
  De omschrijving van het verdrag (element 88.20) ontbreekt. Is die
  nodig?
- Het tijdelijk verblijfsadres en de contactgegevens van
  niet-ingezetenen (categorieën 16 en 17) zijn niet via Haal Centraal
  beschikbaar en zijn daarom niet opgenomen. Is er een afnemer voor wie
  deze gegevens noodzakelijk zijn?

### Nationaliteit

- De nationaliteit is getypeerd als ISO 3166-code; de persoonslijst
  gebruikt Tabel 32, die ook staatloos en niet-landgebonden waarden
  kent. Welke codering moet GBO leveren?
- Bijzonder Nederlanderschap, staatloosheid en de aanduiding dat de
  nationaliteit onbekend is, ontbreken nog. In welke vorm verwacht de
  bronhouder deze?

### Huwelijk

- Huwelijk en geregistreerd partnerschap zijn één objecttype met twee
  gelijkwaardige partners; de ontbinding staat op het huwelijk zelf.
  Plaats en land van ontbinding zijn niet opgenomen. Is dat voldoende?

### Verblijfstitel

- De aanduiding verblijfstitel is getypeerd als IND-codelijst, waar de
  persoonslijst Tabel 56 gebruikt. Welke lijst is leidend, en is de
  uitbreiding van Tabel 56 door het Migratiepact al verwerkt in de
  door GBO gebruikte lijst?

### Gezagsverhouding

- Het gezag is één indicatie (Tabel 61) plus de indicatie curatele.
  Haal Centraal levert gezagsrelaties per minderjarige met
  betrokkenen en datums. Moet GBO wachten op de wijziging van het
  gezagsregister (W214) of nu de Haal Centraal-vorm volgen?

### Immigratie

- Van de immigratie worden het land vanwaar ingeschreven en de datum
  vestiging in Nederland geleverd. Is dat voldoende voor de beoogde
  afnemers?

## Open punten

- **Verblijfplaats en gerelateerden.** In voorbereiding voor de
  volgende modelversie: een eigen gegevensgroep voor het verblijf
  (functie adres, datum aanvang adreshouding, historie), de
  identificatie van het adresseerbaar object op het binnenlands adres,
  ouderschap als eigen gegevensgroep met de aanduiding Ouder1/Ouder2
  en de datum van ingang van de familierechtelijke betrekking, de
  relatie naar kinderen, een optioneel burgerservicenummer op
  gerelateerden, de aanduiding naamgebruik, de datum van opschorting
  en de einddatums van de uitsluiting van het kiesrecht.
- **Nationaliteit en gezag.** Te beslissen: soort nationaliteitsgegeven
  (bijzonder Nederlanderschap, staatloos, onbekend), verplaatsing van
  het buitenlands persoonsnummer naar de nationaliteit, gezagsrelaties
  conform W214, en onderzoek per gegevensgroep in plaats van één
  indicatie op de persoon.
- **Alleen in het LO.** Nog niet besloten: categorieën 16 en 17 voor
  niet-ingezetenen, plaats en land van ontbinding van een huwelijk,
  aangifte adreshouding en het niveau van geheimhouding.
- **Coderingen.** Af te stemmen met de bronhouder: ISO 3166 tegenover
  Tabel 32 en 34, en IND-codelijst tegenover Tabel 56.
- **Logisch Ontwerp.** De herkomstverwijzingen citeren LO 2026.Q3.
  Twee inhoudelijke wijzigingen sinds versie 4.3.0 zijn nog niet in de
  modellering verwerkt: de vaste koppeling van het BRP-adres aan de
  BAG (categorie 08) en het verwijderen van beëindigde vreemde
  nationaliteiten van de persoonslijst (LO-444). Zij lopen mee met de
  punten Verblijfplaats en Nationaliteit hierboven.

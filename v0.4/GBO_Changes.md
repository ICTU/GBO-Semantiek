# Wijzigingen v0.3 → v0.4

## Kernmodel

### Toegevoegde objecttypen

- `Aangifte`
- `AangifteErfbelasting`
- `AangifteInkomstenbelasting`
- `AangifteSchenkbelasting`
- `Aanslag`
- `FiscaleOpgave`
- `KadastraleAanduiding`
- `OnroerendeZaak`
- `Splitsingsakte`

### Verwijderde objecttypen

- `AangifteErf`
- `AangifteIH`
- `AangifteSchenk`
- `Appartementsrechtsplitsing`
- `BelastingAangifte`
- `BelastingjaarAangifte`
- `KadastraleOnroerendeZaak`

### Toegevoegde codelijsten/enumeraties

- `AangifteStatus`
- `OnroerendeZaakStatus`
- `SoortAanslag`

### Verwijderde codelijsten/enumeraties

- `KOZStatus`

### Gewijzigde objecttypen (attributen)

**Aantekening**
  - + `rustOp`
  - − `opKadastraleOnroerendeZaak`
**Appartementsrecht**
  - + `grondperceel`
  - − `indexnummer`
**EigenWoning**
  - + `onderdeelVan`
**FiscaalFeit**
  - + `onderdeelVan`
**FiscalePartner**
  - + `onderdeelVan`
**HypothecairKredietEigenWoning**
  - + `onderpand`
  - − `gevestigdOp`
**HypothecairKredietOverigeOnroerendeZaken**
  - + `onderpand`
  - − `gevestigdOp`
**Perceel**
  - − `kadastraleGemeente`
  - − `perceelnummer`
  - − `sectie`
**PubliekrechtelijkeBeperking**
  - + `rustOp`
  - − `opKadastraleOnroerendeZaak`
**Tenaamstelling**
  - + `tenNameVan`
  - + `van`
  - − `tenaamgesteldOp`
  - − `voorZakelijkRecht`
**Toeslag**
  - + `berekeningsjaar`
**ZakelijkRecht**
  - + `rustOp`
  - − `opKadastraleOnroerendeZaak`
**Zekerheidsrecht**
  - + `aardBezwaardRecht`
  - + `rustOpObject`
  - + `tenGunsteVan`
  - − `opKadastraleOnroerendeZaak`

## Voorzieningenmodel

_Geen structurele wijzigingen gedetecteerd._

## Toestemmingenmodel

Nieuw in v0.4; er is geen voorganger in v0.3 om mee te vergelijken.

### Toegevoegde objecttypen

- `Evenementenvergunning`
- `Gehandicaptenparkeerkaart`
- `Ligplaatsontheffing`
- `Marktvergunning`
- `OpenbareActiviteit`
- `OverigeToestemming`
- `Parkeerontheffing`
- `Standplaatsvergunning`
- `Straatartiestenontheffing`
- `Toestemming`
- `Vaartuig`

### Toegevoegde codelijsten/enumeraties

- `Productstatus`
- `SoortGehandicaptenparkeerkaart`
- `SoortMarktplaats`
- `SoortStandplaats`
- `SoortToestemming`

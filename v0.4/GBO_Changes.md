# Wijzigingen v0.3 → v0.4

## Kernmodel

### Toegevoegde objecttypen

- `Aangifte`
- `AangifteErfbelasting`
- `AangifteInkomstenbelasting`
- `AangifteSchenkbelasting`
- `Aanslag`
- `FiscaleOpgave`

### Verwijderde objecttypen

- `AangifteErf`
- `AangifteIH`
- `AangifteSchenk`
- `BelastingAangifte`
- `BelastingjaarAangifte`

### Toegevoegde codelijsten/enumeraties

- `AangifteStatus`
- `SoortAanslag`

### Gewijzigde objecttypen (attributen)

**EigenWoning**
  - + `onderdeelVan`
**FiscaalFeit**
  - + `onderdeelVan`
**FiscalePartner**
  - + `onderdeelVan`
**Toeslag**
  - + `berekeningsjaar`

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

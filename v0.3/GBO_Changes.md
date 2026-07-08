# Wijzigingen v0.2 → v0.3

### Toegevoegde objecttypen

- `Handelsnaam`
- `Kentekentenaamstelling`
- `Onderneming`

### Verwijderde objecttypen

- `Bedrijf`
- `BuitenlandseEntiteit`
- `Inschrijving`
- `Instelling`
- `MaatschappelijkeInstelling`
- `Overheidsinstelling`
- `OverigeNietNatuurlijkPersoon`
- `Voertuigtenaamstelling`

### Toegevoegde codelijsten/enumeraties

- `NietNatuurlijkPersoonClassificatie`
- `SoortInsolventie`
- `StatusInsolventie`

### Verwijderde codelijsten/enumeraties

- `Sector`
- `TypeBuitenlandseEntiteit`

### Gewijzigde objecttypen (attributen)

**MaatschappelijkeActiviteit**
  - + `datumEersteInschrijving`
  - + `documentdatum`
  - + `documentnummer`
  - + `heeftVestiging`
  - + `kvkNummer`
  - + `naam`
  - + `nonMailing`
  - + `voertOnderneming`
  - − `geregistreerdVia`
  - − `hoofdSbiCode`
  - − `identificatie`
  - − `omschrijving`
**Naamgeving**
  - − `handelsnamen`
**NietNatuurlijkPersoon**
  - + `anbiStatus`
  - + `bevoegdGezagCode`
  - + `classificatie`
  - + `heeftActiviteit`
  - + `heeftNaamgeving`
  - + `heeftOnderneming`
  - + `heeftRechtstoestand`
  - + `kvkNummer`
  - + `landVanOprichting`
  - + `rechtsvorm`
  - + `rechtsvormBuitenland`
  - + `rechtsvormOmschrijving`
  - + `typeMaatschappelijk`
  - + `typeOverheid`
  - + `voertMaatschappelijkeActiviteit`
  - − `sector`
  - − `voertUit`
**Partij**
  - + `ID`
  - − `partijnummer`
**Rechtstoestand**
  - + `insolventieStatus`
  - + `soortInsolventie`
  - − `insolventieCode`
**Vestiging**
  - + `heeftHandelsnaam`

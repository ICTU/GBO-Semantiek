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

- `IndicatieJaNee`
- `NietNatuurlijkPersoonClassificatie`
- `SoortInsolventie`
- `StatusInsolventie`
- `VaststellingsbronInkomen`

### Verwijderde codelijsten/enumeraties

- `EuropeesKiesrecht`
- `Sector`
- `TypeBuitenlandseEntiteit`
- `UitsluitingKiesrecht`

### Gewijzigde objecttypen (attributen)

**Adres**
  - − `adresId`
**Aftrekpost**
  - + `opgevoerdDoor`
**Arbeidsverhouding**
  - + `redenEinde`
  - − `codeRedenEinde`
**Belegging**
  - + `iban`
  - + `land`
**Binnenlandsadres**
  - + `adresId`
**Buitenlandsadres**
  - + `adresId`
**EigenWoning**
  - + `bewoonbaarVoor`
**Inkomstenopgave**
  - + `binnenLoonAangifte`
**Inkomstenverhouding**
  - + `aardArbeidsverhouding`
  - + `begindatum`
  - + `einddatum`
  - + `redenEinde`
  - + `soortInkomstenverhouding`
  - − `begindatumIkv`
  - − `codeAardArbeidsverhouding`
  - − `codeRedenEinde`
  - − `codeSoortInkomstenverhouding`
  - − `einddatumIkv`
**Locatie**
  - + `adresId`
**LoonBestanddeel**
  - + `soortInkomen`
  - − `codeSoortInkomen`
  - − `valuta`
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
  - + `id`
  - − `partijnummer`
**Postadres**
  - + `adresId`
**Rechtstoestand**
  - + `insolventieStatus`
  - + `soortInsolventie`
  - − `insolventieCode`
**Renseignering**
  - + `betreft`
**VerblijfplaatsOnbekend**
  - + `adresId`
**VermogensBestanddeel**
  - + `bronInstelling`
  - + `productId`
**Vestiging**
  - + `heeftHandelsnaam`

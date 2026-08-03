# Bron-profielen

Deze map bevat per bron een **bron-profiel**: een beschrijving van
welke onderdelen van het GBO-informatiemodel die bron via GBO
beschikbaar stelt. De profielen zijn LinkML-*data*, conform het schema
[bronprofiel.yaml](../informatiemodel/linkml/bronprofiel.yaml)
(klasse `Bronprofiel`).

| Bestand | Bron |
|---|---|
| `bag.yaml` | Basisregistratie Adressen en Gebouwen |
| `bri.yaml` | Basisregistratie Inkomen (inclusief inkomensbestanddelen) |
| `brp.yaml` | Basisregistratie Personen |
| `hr.yaml`  | Handelsregister |

## Werking

Een profiel benoemt expliciet de `objecttypen` die de bron levert en
de `ingangen` waarop bevraagd kan worden. De snoei-tool
(`tools/genereer_bronschema.py`) neemt supertypen, mixins en
gestructureerde datatypes automatisch mee, past `uitsluitingen` toe en
handelt relaties naar objecttypen buiten het profiel af: default als
sleutel-referentie naar de identifier van het doelobject, of met
`afhandeling: weglaten` in `relatieAfhandeling`.

## Filterargumenten

Een attribuut met de annotatie `gbo:filterbaar` levert een optioneel
argument op elk multivalued object-veld dat naar die klasse verwijst:

```yaml
belastingjaar:
  range: Numeriek
  required: true
  annotations:
    gbo:filterbaar: true
```

levert

```graphql
heeftBelastingjaarAangifte(belastingjaar: [Int!]): [BelastingjaarAangifte!]
```

Het argument houdt de naam van het attribuut, in **enkelvoud**. De
lijstnotatie drukt de meervoudigheid al uit; een meervoudsvorm in de
naam zou die informatie verdubbelen.

**Het argument is altijd een lijst**, ook wanneer er één waarde wordt
gevraagd. Enkelvoudige en meervoudige selectie hebben daarmee dezelfde
vorm, en een policy-beslispunt kan de gevraagde verzameling
rechtstreeks uit de operatie aflezen zonder een filter-inputobject te
moeten uitpakken. Dat laatste is de reden om hier geen
`filter: XFilter`-input te gebruiken: die vorm wordt pas overwogen
zodra er meerdere, onderling onafhankelijke filters op één veld nodig
zijn.

### Semantiek

| Vorm | Betekenis |
|---|---|
| Argument weggelaten | Geen beperking; de bron levert alle voorkomens die binnen het profiel en de autorisatie vallen. Een beslispunt kan zo'n operatie weigeren, omdat niet aantoonbaar is dat elk teruggegeven voorkomen gedekt is. |
| Eén waarde, `[2024]` | Alleen voorkomens met die waarde. |
| Meerdere waarden, `[2023, 2024]` | De vereniging van die waarden. Volgorde is niet betekenisvol en duplicaten worden genegeerd. |
| Lege lijst, `[]` | Selecteert niets en levert een lege lijst. De gevraagde verzameling is leeg en daarmee triviaal gedekt. |
| Onbekende waarde | Geen fout; die waarde levert eenvoudigweg niets op. |
| Losse waarde, `2024` | Geldig: GraphQL coerceert een enkele waarde naar een lijst van één. Een beslispunt dat de gevraagde verzameling uit de operatie afleidt, moet dus zowel de lijst- als de losse notatie aankunnen, en ook de vorm waarin de waarden via een variabele binnenkomen. |

Het filter beperkt uitsluitend de directe verzameling van het veld
waarop het staat. Het werkt niet door in geneste velden: die hebben zo
nodig hun eigen filterargument.

### Voorbeeld

```graphql
query AangiftenPerJaar($bsn: BSN!, $jaren: [Int!]) {
  ingeschrevenPersoon(bsn: $bsn) {
    heeftBelastingjaarAangifte(belastingjaar: $jaren) {
      belastingjaar
      belastingsoort
      status
    }
  }
}
```

Met `$jaren = [2023, 2024]` levert dit uitsluitend de aangiften over
die twee jaren, en zijn de gevraagde jaren af te lezen uit de
operatie.

## Commando's

```bash
# Eén profiel valideren
linkml-validate -s v0.2/informatiemodel/linkml/bronprofiel.yaml \
    -C Bronprofiel v0.2/bronnen/brp.yaml

# Alle profielen valideren, materialiseren en omzetten naar
# GraphQL SDL (in v0.2/graphql/)
task generate:graphql
```

De gegenereerde SDL-bestanden in `../graphql/` zijn afgeleide
artefacten: bewerk de profielen, nooit de SDL.

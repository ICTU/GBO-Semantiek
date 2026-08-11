# URI-strategie

## Uitgangspunten

GBO-Semantiek hanteert een URI-strategie voor de identificatie van begrippen, klassen en eigenschappen. De strategie volgt de [aanbevelingen van het Platform Linked Data Nederland](https://www.pldn.nl/), de [URI-strategie voor de Nederlandse overheid](https://www.pilod.nl/wiki/Boek/URI-strategie), en de TOOI URI-strategie.

De URI-strategie is de concrete uitwerking van het ontwerpprincipe [S-02 FAIR als basisraamwerk](../uitgangspunten/ontwerpprincipes.md#s-02-fair-als-basisraamwerk).

## Principes

De URI-strategie bouwt voort op de volgende principes:

- **Persistentie**, URI's veranderen niet na publicatie; gebruik een stabiel domein dat los staat van technische implementatie
- **Uniekheid**, elke URI identificeert precies één ding (klasse, begrip, property, instantie); geen hergebruik van URI's voor meerdere concepten
- **Dereferenceerbaarheid**, elke URI is opvraagbaar via HTTP en levert nuttige informatie terug
- **Onderscheid document vs. ding**, gebruik aparte URI's voor een real-world concept en het document dat het beschrijft (via `303 redirect` of `#hash URI`)
- **Leesbaarheid**, geef URI-paden een beschrijvende naam (bijv. `/ontologie/Zaak` in plaats van `/id/a4f2`), maar houd namen stabiel bij naamswijzigingen via `owl:sameAs`
- **Naamruimte-consistentie**, een consistente naamruimte per artefacttype (ontologie, begrippenkader, context-bestanden, instanties)
- **Geen technische details**, URI's bevatten geen bestandsextensies, database-ID's of andere implementatiedetails
- **Geen versie in de URI**, URI's verwijzen naar de meest actuele definitie; eerdere versies zijn opvraagbaar via een versieparameter of via de repository

NORA stelt als implicatie van principe 1.1 dat *"gegevens en hun metagegevens zijn voorzien van wereldwijd unieke en stabiele identificaties"*, wat direct aansluit bij deze URI-eisen.

## URI-patronen

Het basis-URI-patroon voor GBO-Semantiek volgt een driedeling conform W3C Best Practices:

| Type artefact | URI-patroon | Voorbeeld |
|---------------|-------------|-----------|
| Ontologie (klassen, properties) | `https://lod.gbo-semantiek.nl/{Klasse}` | `https://lod.gbo-semantiek.nl/Zaak` |
| Begrippen (SKOS concepten) | `https://begrippen.gbo-semantiek.nl/id/begrip/{Begrip}` | `https://begrippen.gbo-semantiek.nl/id/begrip/Zaak` |
| JSON-LD context | `https://lod.gbo-semantiek.nl/context/{usecase}.jsonld` | `https://lod.gbo-semantiek.nl/context/kern.jsonld` |
| Instanties | `https://lod.gbo-semantiek.nl/id/{type}/{id}` | `https://lod.gbo-semantiek.nl/id/zaak/12345` |

Conventies voor paden en elementnamen (lowercase paden, CamelCase klassen, lowerCamelCase properties) staan in [Naamgeving](naamgeving.md).

## Content negotiation

Bij het opvragen van een ontologie- of begrip-URI levert de server het juiste formaat op basis van het `Accept`-header:

| Accept header | Response |
|---------------|----------|
| `text/html` | HTML-documentatie (voor mensen) |
| `text/turtle` | Turtle (voor RDF-tooling) |
| `application/ld+json` | JSON-LD (voor API-integratie) |

Dit maakt URI's **dereferenceable**: bij het opvragen levert de server altijd nuttige informatie, ongeacht of de consument een mens of een machine is.

## Relatie tot TOOI

De GBO URI-strategie is compatibel met de TOOI-aanpak, waarin ontologieën, thesauri en registers elk een eigen URI-namespace krijgen. Dit maakt het mogelijk om GBO-begrippen te koppelen aan begrippen in TOOI of andere stelsels via `skos:exactMatch` of `skos:closeMatch`.

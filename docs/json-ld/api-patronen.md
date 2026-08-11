# Patronen voor JSON-LD gebruik in API-responses

## Uitgangspunt

API's die GBO-gegevens ontsluiten kunnen JSON-LD gebruiken om hun responses machine-leesbaar te maken. Dit vereist minimale aanpassingen aan bestaande JSON-API's: het toevoegen van een `@context`-verwijzing is vaak voldoende.

## Patroon 1: Inline @context

De eenvoudigste aanpak — een `@context`-verwijzing toevoegen aan de bestaande JSON-response:

```json
{
  "@context": "https://lod.gbo-semantiek.nl/context/kern.jsonld",
  "@type": "Persoon",
  "@id": "https://lod.gbo-semantiek.nl/id/persoon/12345",
  "geboortedatum": "1990-01-15",
  "achternaam": "Jansen"
}
```

## Patroon 2: Link header

Voor API's die de body niet willen aanpassen, kan de `@context` via een HTTP Link header worden meegegeven:

```http
Link: <https://lod.gbo-semantiek.nl/context/kern.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"
```

## Patroon 3: Collecties

Bij het teruggeven van meerdere objecten wordt `@graph` gebruikt:

```json
{
  "@context": "https://lod.gbo-semantiek.nl/context/kern.jsonld",
  "@graph": [
    {
      "@type": "Persoon",
      "@id": "https://lod.gbo-semantiek.nl/id/persoon/12345",
      "achternaam": "Jansen"
    },
    {
      "@type": "Persoon",
      "@id": "https://lod.gbo-semantiek.nl/id/persoon/67890",
      "achternaam": "De Vries"
    }
  ]
}
```

## Patroon 4: Gecombineerde contexts

OSLO publiceert per vocabularium een herbruikbaar context-bestand dat door meerdere API's gedeeld kan worden. GBO volgt dit patroon — kern- en use-case-contexts worden gecombineerd:

```json
{
  "@context": [
    "https://lod.gbo-semantiek.nl/context/kern.jsonld",
    "https://lod.gbo-semantiek.nl/context/zaakgericht-werken.jsonld"
  ],
  "@type": "gbo:Zaak",
  "gbo:status": {
    "@id": "https://begrippen.gbo-semantiek.nl/id/begrip/zaakstatus/afgerond"
  }
}
```

## Content negotiation

API's worden aanbevolen om content negotiation te ondersteunen:

| Accept header | Response |
|---------------|----------|
| `application/json` | Reguliere JSON (zonder @context) |
| `application/ld+json` | JSON-LD (met @context) |
| `text/turtle` | RDF/Turtle |

Dit volgt de W3C Best Practices voor Linked Data publicatie en maakt dezelfde URI bruikbaar voor zowel mensen (HTML) als machines (RDF/JSON-LD).

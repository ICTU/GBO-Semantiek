# @context-definitie

## Doel

De JSON-LD `@context` koppelt JSON-sleutels aan termen in de gepubliceerde ontologie. Hierdoor worden reguliere JSON-objecten automatisch interpreteerbaar als Linked Data, zonder dat de JSON-structuur zelf hoeft te veranderen.

## Structuur

De GBO `@context` volgt het OSLO-patroon van context-bestanden per informatiemodel:

- **Kern-context:** `https://lod.gbo-semantiek.nl/context/kern.jsonld` — de basismapping voor het generieke informatiemodel
- **Use-case-context:** `https://lod.gbo-semantiek.nl/context/{usecase}.jsonld` — aanvullende mappings per applicatieprofiel

De kern-context bevat:

```json
{
  "@context": {
    "@vocab": "https://lod.gbo-semantiek.nl/",
    "gbo": "https://lod.gbo-semantiek.nl/",
    "gbobegrip": "https://begrippen.gbo-semantiek.nl/id/begrip/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  }
}
```

## Typisch GBO JSON-LD patroon

Een API-response die GBO-gegevens als JSON-LD publiceert:

```json
{
  "@context": [
    "https://lod.gbo-semantiek.nl/context/kern.jsonld",
    "https://lod.gbo-semantiek.nl/context/zaakgericht-werken.jsonld"
  ],
  "@type": "gbo:Zaak",
  "@id": "https://bronhouder.nl/zaken/12345",
  "gbo:status": {
    "@id": "https://begrippen.gbo-semantiek.nl/id/begrip/zaakstatus/afgerond"
  },
  "gbo:datumIngang": "2024-01-15"
}
```

Hierbij:

- De `@context` combineert de kern-context met een use-case-specifieke context
- De `@type` verwijst naar een OWL-klasse in de ontologie
- De `gbo:status` verwijst als URI naar een SKOS-concept in de gepubliceerde thesaurus — waardoor de waarde de-referenceable en machine-leesbaar is
- Context-bestanden voor het generieke deel en per use case kunnen afzonderlijk worden bijgehouden en gecombineerd in een payload (zoals OSLO dat doet)

## Publicatie

De `@context`-bestanden worden gepubliceerd op:

- **URL:** `https://lod.gbo-semantiek.nl/context/`
- **Repository:** `v{versie}/ontologie/context/`

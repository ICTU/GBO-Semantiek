# Publicatie

## Informatiemodel → Gepubliceerde ontologie

Het informatiemodel wordt via een geautomatiseerde transformatie gepubliceerd als OWL/RDF-ontologie. De toolchain volgt het OSLO-patroon:

![OSLO toolchain patroon](../assets/diagrams/oslo-patroon.svg)

GBO gebruikt [crunch_uml](https://github.com/brienen/crunch_uml) voor deze transformatie:

```bash
task generate:lod
```

De transformatieregels:

| MIM-element | OWL-equivalent |
|-------------|---------------|
| Objecttype | `owl:Class` |
| Attribuutsoort | `owl:DatatypeProperty` |
| Relatiesoort | `owl:ObjectProperty` |
| Generalisatie | `rdfs:subClassOf` |
| Enumeratie | `skos:ConceptScheme` |

## Gepubliceerde ontologie → JSON-LD @context

De JSON-LD `@context` definieert een mapping van JSON-sleutels naar ontologie-URI's. OSLO publiceert per vocabularium een herbruikbaar context-bestand; GBO volgt hetzelfde patroon:

- **Kern-context:** `https://lod.gbo-semantiek.nl/context/kern.jsonld`
- **Use-case-context:** `https://lod.gbo-semantiek.nl/context/{usecase}.jsonld`

Meerdere context-bestanden kunnen worden gecombineerd in een API-response.

## Begrippenkader in datapayloads

SKOS-concept-URI's kunnen als **attribuutwaarden** in JSON-LD payloads verschijnen. Bijvoorbeeld: een `status`-veld verwijst naar een SKOS-concept in de gepubliceerde thesaurus. Hierdoor worden waardelijsten de-referenceable en machine-leesbaar, conform de OSLO-aanpak voor codelijsten.

```json
{
  "gbo:status": {
    "@id": "https://begrippen.gbo-semantiek.nl/id/begrip/zaakstatus/afgerond"
  }
}
```

## SHACL → Ontologie

SHACL shapes valideren instantiedata tegen de ontologie. De shapes verwijzen naar OWL-klassen en -eigenschappen om structuur- en cardinaliteitseisen af te dwingen.

# Semantisch raamwerk

## Overzicht

De onderstaande architectuurplaat toont het GBO Semantisch Raamwerk: de samenhang tussen begrippenkader, informatiemodel, ontologie en JSON-LD datapublicatie.

![GBO Semantisch Raamwerk](../assets/diagrams/semantisch-raamwerk.svg)

## Componenten

Het raamwerk bestaat uit zes componenten die elk een eigen doel en doelgroep hebben:

| # | Component | Technologie | Doel |
|---|-----------|-------------|------|
| 1 | **Begrippenkader** | SKOS ConceptScheme | Eenduidige definities en hiërarchische relaties tussen domeinbegrippen |
| 2 | **Informatiemodel generiek** | MIM/UML (QEA) | De GBO-kern: klassen, attributen en relaties die over alle use cases geldig zijn |
| 3 | **Informatiemodel use-case** | MIM/UML (QEA) | Applicatieprofielen die het generieke model uitbreiden of beperken per use case |
| 4 | **Gepubliceerde ontologie** | OWL/RDF (Turtle) | Machine-leesbare formalisering van het informatiemodel |
| 5 | **JSON-LD @context** | JSON-LD | Mapping van JSON-sleutels naar ontologie-URI's |
| 6 | **JSON-LD data payload** | JSON-LD | De feitelijke data in API-responses, voorzien van semantische context |

## Relaties

Elke pijl in het diagram vertegenwoordigt een concrete relatie:

### Begrippenkader → Informatiemodel

Het begrippenkader (SKOS, MIM niveau I) legt de *betekenis* vast van domeinbegrippen, bedoeld voor domeinexperts en beleidsmakers. Het informatiemodel (MIM niveau II/III) formaliseert deze begrippen tot klassen en attributen. De koppeling loopt via `skos:exactMatch` (begrip = ontologie-klasse) of `rdfs:isDefinedBy` (ontologie-term verwijst naar begrippenkader). Zo correspondeert een `skos:Concept` met `skos:prefLabel "Zaak"` met een `owl:Class gbo:Zaak` in de ontologie.

### Informatiemodel generiek → use-case-specifiek

Het generieke model bevat klassen en attributen die over alle GBO use-cases heen herbruikbaar zijn — vergelijkbaar met de OSLO-kernvocabularia. Use-case-specifieke uitbreidingen (applicatieprofielen) voegen beperkingen toe (cardinaliteiten, waardelijsten) of nieuwe klassen, zonder het generieke model te doorbreken. Dit is hetzelfde patroon als de OSLO-splitsing tussen *vocabularium* en *applicatieprofiel*, of de ISA Core Vocabularies versus nationale uitbreidingen.

### Informatiemodel → Gepubliceerde ontologie

Het informatiemodel wordt via een **geautomatiseerde transformatie** gepubliceerd als OWL/RDF-ontologie. GBO gebruikt hiervoor [crunch_uml](https://github.com/brienen/crunch_uml), vergelijkbaar met OSLO's `EA-to-RDF` tool. De ontologie wordt via een stabiele URI gepubliceerd met content negotiation (HTML voor mensen, Turtle/JSON-LD voor machines).

### Gepubliceerde ontologie → JSON-LD @context

De JSON-LD `@context` definieert een mapping van JSON-sleutelwoorden naar de URI's van klassen en properties in de ontologie. Wanneer een API een JSON-LD payload stuurt met `"@context": "https://lod.gbo-semantiek.nl/context/kern.jsonld"`, weet elke ontvanger precies wat elke sleutel semantisch betekent. Naar het OSLO-voorbeeld publiceert GBO per informatiemodel een herbruikbaar context-bestand dat door meerdere API's gedeeld kan worden.

### Begrippenkader → JSON-LD data payload

SKOS-concept-URI's verschijnen als **attribuutwaarden** in JSON-LD payloads — bijvoorbeeld wanneer een `statusCode`-veld verwijst naar een SKOS-concept in de gepubliceerde thesaurus. Dit maakt het begrippenkader een levend onderdeel van de datapublicatie, niet alleen een documentatieartefact.

### Begrippenkader → Ontologie

Begrippen en ontologie-termen worden bidirectioneel gekoppeld: `skos:exactMatch` (van begrip naar ontologie-term) en `rdfs:isDefinedBy` (van ontologie-term naar begrippenkader). Zo is er altijd traceerbaarheid van formele structuur naar menselijke betekenis.

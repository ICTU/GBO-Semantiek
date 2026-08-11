# Koppeling met SKOS begrippenkader

## Principe

De ontologie en het begrippenkader zijn **twee afzonderlijke artefacten** die expliciet aan elkaar worden gekoppeld — conform de TOOI-aanpak waarin thesauri en ontologieën gescheiden documenten zijn, verbonden via URI's. De ontologie beschrijft de formele structuur (voor machines); het begrippenkader beschrijft de menselijke betekenis (voor domeinexperts).

## Koppelingsproperties

| Property | Richting | Beschrijving |
|----------|----------|-------------|
| `skos:exactMatch` | Begrip → Ontologie-term | Het begrip correspondeert exact met een OWL-klasse |
| `rdfs:isDefinedBy` | Ontologie-term → Begrippenkader | De ontologie-term verwijst naar de gezaghebbende definitie |
| `rdfs:seeAlso` | Beide richtingen | Verwijzing naar gerelateerde documentatie |

## Voorbeeld

```turtle
# In het begrippenkader:
gbobegrip:Zaak a skos:Concept ;
    skos:prefLabel "Zaak"@nl ;
    skos:definition "Een samenhangende hoeveelheid werk met een gedefinieerde aanleiding en een gedefinieerd eindresultaat."@nl ;
    skos:exactMatch gbo:Zaak .

# In de ontologie:
gbo:Zaak a owl:Class ;
    rdfs:label "Zaak"@nl ;
    rdfs:isDefinedBy gbobegrip:Zaak .
```

## Waardelijsten als SKOS ConceptScheme

Enumeraties en waardelijsten uit het informatiemodel worden gepubliceerd als SKOS `ConceptScheme`. Hierdoor zijn individuele waarden **de-referenceable** via HTTP en kunnen ze als URI-waarden voorkomen in JSON-LD payloads:

```json
{
  "gbo:status": {
    "@id": "https://begrippen.gbo-semantiek.nl/id/begrip/zaakstatus/afgerond"
  }
}
```

Dit volgt de OSLO-aanpak voor codelijsten.

## Richtlijnen

1. Elke OWL-klasse **moet** een `rdfs:isDefinedBy` verwijzing hebben naar het begrippenkader
2. Elk SKOS-concept dat correspondeert met een ontologie-term **moet** een `skos:exactMatch` bevatten
3. Labels in de ontologie (`rdfs:label`) komen overeen met de voorkeurstterm (`skos:prefLabel`) in het begrippenkader
4. Waardelijsten worden als SKOS `ConceptScheme` gepubliceerd, niet als OWL `oneOf` enumeraties

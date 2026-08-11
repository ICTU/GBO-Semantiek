# JSON-LD framing

## Wat is JSON-LD framing?

[JSON-LD Framing](https://www.w3.org/TR/json-ld11-framing/) is een W3C-specificatie waarmee je kunt bepalen **hoe** Linked Data wordt gepresenteerd in JSON-vorm. Een frame definieert de gewenste structuur van het JSON-document.

OSLO beschrijft JSON-LD framing als basis voor testen en consistentieborging van API-responses.

## Gebruik voor validatie

Framing kan worden ingezet om te valideren dat inkomende JSON-data de verwachte structuur heeft:

```json
{
  "@context": "https://lod.gbo-semantiek.nl/context/kern.jsonld",
  "@type": "Zaak",
  "onderwerp": {},
  "datumIngang": {
    "@type": "xsd:date"
  },
  "status": {
    "@type": "skos:Concept"
  },
  "heeftBetrokkene": {
    "@type": "Persoon"
  }
}
```

Dit frame specificeert dat een `Zaak` een `onderwerp`, `datumIngang` (als datum), een `status` (als SKOS-concept) en een geneste `Persoon` als betrokkene moet hebben.

## Gebruik voor inputstructuur

API's kunnen frames publiceren als specificatie van de verwachte inputstructuur:

- **Request frame:** beschrijft welke velden een POST/PUT-request moet bevatten
- **Response frame:** beschrijft de structuur van het antwoord

Dit biedt een alternatief voor of aanvulling op JSON Schema-validatie, met het voordeel dat de validatie direct is gekoppeld aan de ontologie.

## Voordelen

- Duidelijke, machine-leesbare documentatie van datastructuur
- Automatische validatie van in- en output tegen de ontologie
- Hergebruik van dezelfde ontologie voor meerdere API-views
- Complementair aan SHACL-validatie (SHACL op RDF-niveau, framing op JSON-niveau)

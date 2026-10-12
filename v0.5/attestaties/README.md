# Attestatieprofielen

Deze map bevat per attestatietype een **attestatieprofiel**: een
LinkML-schema met één klasse die de claims van een elektronische
attestatie van attributen beschrijft. Het profiel legt vast welke claims
de attestatie draagt, wat ze betekenen, welke verplicht zijn en uit welk
gegeven van GBO-Kern ze komen.

| Bestand | Inhoud |
|---|---|
| `attestatie.yaml` | Basisschema: de abstracte klasse `Attestatie` en de metadataclaims die de uitgever vult |
| `inkomensverklaring.yaml` | Inkomensverklaring, vastgelegd uit de GBO-demo |

## Het profiel als rulebook

Een Attestation Rulebook (ARF, Topic 12) bestaat uit acht hoofdstukken.
Het attestatieprofiel dekt hoofdstuk 3, attributen en metadata, en de
regels voor subtypen. De andere hoofdstukken (codering, gebruik,
vertrouwensankers, intrekking, compliance) gaan over het walletstelsel en
de uitgever; die horen in het rulebook van het scheme.

| Rulebook | LinkML |
|---|---|
| Mandatory attribute | `required: true` |
| Optional attribute | geen `required` |
| Conditional attribute | `rules` |
| Vaste waarde, zoals de juridische categorie | `equals_string` in `slot_usage` |
| Definitie, voorbeeldwaarde, label | `description`, `examples`, `title` |
| Attribuut of metadata | `in_subset: [attribuut]` of `[metadata]` |
| Semantisch anker | `exact_mappings` of `close_mappings` naar GBO-Kern |
| Basis- en subtype-rulebook | `is_a` en `slot_usage` |

Een subtype mag een claim aanscherpen, bijvoorbeeld van optioneel naar
verplicht, maar niet verruimen. LinkML dwingt dat niet af; de generator
weigert een subtype dat het toch doet.

## Koppeling aan de bron

De koppeling aan de bron staat in annotaties. Een subtype erft de
klasseannotaties van zijn supertype, behalve `gbo:typeId`.

**Op de klasse:**

| Annotatie | Betekenis |
|---|---|
| `gbo:typeId`, `gbo:typeVersie` | Type-id en versie; het uitgifteplatform maakt daar de `vct` van |
| `gbo:bronprofiel` | Het bronprofiel waarvan de GraphQL-SDL de query levert |
| `gbo:serviceReferentie` | FSC-servicenaam bij de uitgifte; zonder vermelding het bronprofiel |
| `gbo:query` | Het Query-veld in dat bronprofiel |
| `gbo:bronType` | Concreet type in het resultaat, als de query een interface levert |
| `gbo:subject` | Het argument dat de wallet uit de PID vult, meestal `bsn` |
| `gbo:aanbiedingParameter`, `gbo:aanbiedingWaarden` | De parameter die per aanbieding vastligt en de waarden ervan |
| `gbo:aanbiedingLabel`, `gbo:aanbiedingOmschrijving` | Label en omschrijving per aanbieding; `{parameter}` wordt ingevuld |
| `gbo:weergaveNaam`, `gbo:weergaveOmschrijving`, `gbo:typeOmschrijving` | Weergave in de wallet |
| `gbo:samenvatting` | Samenvatting met `{{claim}}`-plaatshouders |
| `gbo:achtergrondkleur`, `gbo:tekstkleur` | Kleuren van de kaart in de wallet |

**Op een claim:**

| Annotatie | Betekenis |
|---|---|
| `gbo:bronpad` | Pad in het queryresultaat, met punten, zoals `verzamelinkomen.waarde` |
| `gbo:formaat` | `gYear` voor een jaartal |
| `gbo:eenheid` | Valuta volgens ISO 4217, zoals `EUR` |
| `gbo:weergaveOmschrijving` | Toelichting bij de claim in de wallet |
| `gbo:selectieveOnthulling` | `always`, `allowed` of `never`; zonder vermelding `always` |
| `gbo:geheleWaarde` | Motivering waarom een Float uit de bron als geheel getal mag worden geleverd |
| `gbo:gevuldDoor` | Bij metadata: wie de claim vult, meestal `uitgever` |

## Wat gbo-semantiek ermee doet

`tools/genereer_attestatie.py` in gbo-semantiek maakt per attestatietype
twee bestanden in `<versie>/eudi/`:

- `<typeId>.gbo-attestatie.json`: het element voor
  `capabilities.eudi.attestations` in het bronmetadata-document
  `/.well-known/gbo` van de GBO-demo (schema `gbo-source-metadata-v1`), met
  query, `gbo-simple-v1`-mapping, `attribute_schema`, aanbiedingen en SD-JWT
  VC Type Metadata. Het JSON Schema in de Type Metadata komt uit LinkML
  `gen-json-schema`.
- `<typeId>.rulebook-h3.md`: hoofdstuk 3 van het rulebook, met per claim
  het semantisch anker en het bronpad.

De GraphQL-query wordt niet met de hand geschreven. De generator bouwt hem
uit de bronpaden en valideert hem tegen de SDL van het bronprofiel; een
query kan dus niet uit de pas lopen met het model. Hij controleert ook dat
het brontype op het claimtype past en dat de semantische ankers in de
ontologie bestaan, en waarschuwt als een verplichte claim uit een veld komt
dat leeg kan zijn.

## Verhouding tot de GBO-demo en ARC

| Laag | Waar | Wat |
|---|---|---|
| Semantiek | GBO-Semantiek, dit profiel | Claims, betekenis, verplichting, bronquery |
| Uitgifteconfiguratie | GBO-demo, `/.well-known/gbo` van de bron | Query, mapping, aanbiedingen, Type Metadata; gegenereerd uit het profiel |
| Scheme | ARC (Gemeente Nijmegen) | Rulebook hoofdstuk 1 tot en met 9, uitgifte, registratie en intrekking |

Hoofdstuk 3 van een ARC-rulebook kan uit het profiel komen. ARC vertaalt
brongegevens nu met een handgeschreven `map()` per attestatie; met een
bron die de GBO-demo-mapping uitvoert, zou die vertaling uit hetzelfde
profiel komen.

## Beperkingen

- `gbo-simple-v1` kent geen conditionele claims, conversies of selectie.
  Een regel in `rules` komt in het rulebook, maar de uitgifte dwingt hem
  niet af.
- Eén aanbiedingsparameter per attestatietype, zoals het belastingjaar.
- `gen-yaml` van LinkML 1.11.1 kan een profiel met `slot_usage` en
  geërfde annotaties niet serialiseren. `linkml lint` en `gen-json-schema`
  werken wel.

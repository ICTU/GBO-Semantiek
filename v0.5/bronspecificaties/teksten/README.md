# Bronspecificaties: handgeschreven delen

Per bron één Markdown-bestand (`<bron>.md`, zelfde naam als het
bronprofiel in `../bronnen/`) met de delen van de **GBO Bronspecificatie**
die niet uit het model komen. Het document zelf wordt in gbo-semantiek
gegenereerd (`task generate:bronspecificaties`,
`tools/genereer_bronspecificatie.py`): alle modelfeiten komen uit
`../linkml/` en `../bronnen/<bron>.yaml`, zodat er geen tweede waarheid
ontstaat. Een bron zonder tekstbestand krijgt geen document.

## Opbouw

Frontmatter (YAML):

| Veld | Betekenis |
|---|---|
| `bron` | Code van de bron, gelijk aan `bron:` in het bronprofiel |
| `status` | Bijvoorbeeld `consultatieversie` |
| `consultatieronde` | Volgnummer van de consultatieronde |
| `reactietermijn`, `contact` | Voor het voorblad; `contact` met `naam`, `organisatie`, `email` |
| `bronhouder` | Organisatie die de registratie beheert |
| `brondocumenten` | Lijst met `laag` (L1 t/m L4), `titel`, `uitgever`, `versie`, `datum`, `vindplaats`, `gebruik`, `toelichting` |
| `herleiding` | Lijst met `pad` (API-compatibiliteitspagina in de wiki, relatief aan de repo-wortel) en `koppelvlak`; levert de koppelvlakkolom in bijlage B |

Secties (koppen op niveau 2, andere secties worden genegeerd):

| Sectie | Landt in het document als |
|---|---|
| `## Context` | 2.4 Deze bron in GBO |
| `## Toetsvragen` | Hoofdstuk 4; per `### Kop` een groep, elke `- ` een vraag; de generator nummert T1, T2, … |
| `## Open punten` | Bijlage D, Bekende open punten |

## Conventies

Dezelfde als voor `../informatiemodel/`: geen versie-aanduidingen (de
generator voegt modelversie, commit en datum zelf toe), geen
`[[wiki-links]]`, Nederlandstalig. Modelfeiten (definities, kardinaliteit,
herkomst) horen niet in dit bestand maar in de LinkML; redenen voor
uitsluitingen en relatieafhandeling horen in het bronprofiel
(`toelichting`).

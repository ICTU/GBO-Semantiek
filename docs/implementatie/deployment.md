# Publicatiestrategie en versioning

## Modulair publiceren

Naar het voorbeeld van TOOI publiceert GBO elk artefact als apart document met een stabiele URI:

| Artefact | Formaat | URI-patroon |
|----------|---------|-------------|
| Begrippenkader | SKOS (Turtle) | `https://begrippen.gbo-semantiek.nl/id/begrip/` |
| Informatiemodel | MIM/UML (QEA) | Repository: `v{versie}/informatiemodel/` |
| Ontologie | OWL (Turtle) | `https://lod.gbo-semantiek.nl/` |
| JSON-LD context | JSON-LD | `https://lod.gbo-semantiek.nl/context/{usecase}.jsonld` |
| Waardelijsten | SKOS (Turtle) | `https://begrippen.gbo-semantiek.nl/id/begrip/{waardelijst}/` |

## Automatisch genereren

GBO volgt het OSLO-patroon waarin vanuit **een bronmodel meerdere artefacten** worden gegenereerd. De toolchain gebruikt [crunch_uml](https://github.com/brienen/crunch_uml) als centraal transformatiemiddel:

```
QEA-model → crunch_uml → Turtle ontologie
                        → Markdown definities
                        → JSON-LD context (toekomstig)
                        → SHACL shapes (toekomstig)
```

Dit garandeert consistentie: er is een bron van waarheid (het QEA-model) waaruit alle afgeleide artefacten voortkomen.

## Koppeling tussen artefacten

De koppelingen worden expliciet vastgelegd:

| Van | Naar | Via |
|----|------|-----|
| `skos:Concept` | `owl:Class` | `skos:exactMatch` of `owl:equivalentClass` |
| `owl:Class` | JSON-LD `@type` | De `@context`-mapping |
| Waardelijstwaarde in data | `skos:Concept` URI | De-referenceable URI |
| `owl:Class` | `skos:Concept` | `rdfs:isDefinedBy` |

## Versiebeheer

GBO hanteert **twee afzonderlijke versieringssystematieken**:

### Documentatieversies (via mike)

De documentatiewebsite wordt gepubliceerd met [mike](https://github.com/jimporter/mike), dat meerdere versies naast elkaar beheert op GitHub Pages:

- `https://ictu.github.io/GBO-Semantiek/v0.3/`
- `https://ictu.github.io/GBO-Semantiek/latest/`

### Artefactversies (via repository-mappen)

Modelartefacten worden opgeslagen in genummerde mappen in de repository-root:

```
/v0.3/
  informatiemodel/linkml/  ← LinkML-model (gekopieerd uit de wiki-repo)
  bronnen/                 ← bron-profielen
  clients/                 ← client-profielen
  graphql/                 ← GraphQL-SDL's (gegenereerd)
  ontologie/               ← OWL + SHACL (gegenereerd)
```

Versienummering volgt [Semantic Versioning](https://semver.org/lang/nl/): `MAJOR.MINOR`. Een versiegerelateerde map wordt niet gewijzigd na publicatie.

## Publicatieproces

Het publicatieproces wordt aangestuurd via de Taskfile. Dankzij de dependency-graaf hoef je in de regel maar één commando aan te roepen — de voorafgaande stappen worden automatisch uitgevoerd wanneer hun bronbestanden zijn gewijzigd.

| Stap | Task | Beschrijving | Trigger |
|------|------|-------------|---------|
| 1 | `task import:model` | QEA-model inladen in crunch_uml | automatisch via elke `generate:*` |
| 2 | `task import:previous` | Vorige QEA-versie inladen | automatisch via `generate:diff` |
| 3 | `task generate:docs` | Markdown definities genereren | automatisch via `publish:local` |
| 4 | `task generate:lod` | Linked Data (TTL) genereren | automatisch via `publish:local` |
| 5 | `task generate:diff` | Verschilrapport t.o.v. vorige versie | automatisch via `publish:local` |
| 6 | `task generate:diagrams` | `.drawio` → SVG exporteren | automatisch via `publish:local` |
| 7 | `task publish:local` | Versioned docs bouwen via mike | trekt alle `generate:*` mee |
| 8 | `task publish:github` | Publiceren naar GitHub Pages | trekt `publish:local` mee |

Een volledige publicatie naar GitHub Pages komt daarmee neer op één commando:

```bash
task publish:github
```

De alias `task full-deploy` roept `publish:local` aan en is bedoeld voor een lokale deploy zonder `git push`. Voor een snelle preview tijdens het schrijven kun je `task build:serve` gebruiken; deze heeft bewust geen dependencies en draait dus direct `mkdocs serve` op wat er in `docs/` staat. Wijzig je het UML-model of een `.drawio`-bestand, draai dan eerst `task generate:docs` respectievelijk `task generate:diagrams`.

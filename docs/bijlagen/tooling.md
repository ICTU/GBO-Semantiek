# Bijlage C: Tooling en ontwikkelomgeving

## Overzicht

| Tool | Versie | Doel | Installatie |
|------|--------|------|-------------|
| [go-task](https://taskfile.dev/) | 3.x | Task-runner | `brew install go-task` |
| [crunch_uml](https://github.com/brienen/crunch_uml) | latest | Model import/export | `pip install crunch_uml` |
| [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) | latest | Documentatiesite | `pip install mkdocs-material` |
| [mike](https://github.com/jimporter/mike) | latest | Versioned documentatie | `pip install mike` |
| [jq](https://stedolan.github.io/jq/) | latest | JSON-processor | `brew install jq` |
| [drawio desktop](https://github.com/jgraph/drawio-desktop/releases) | latest | Diagram-export naar SVG (optioneel) | `brew install --cask drawio` |
| Python | 3.9+ | Runtime | [python.org](https://www.python.org/downloads/) |

## Taskfile

Alle taken worden aangestuurd via de `Taskfile.yml` in de repository-root:

```bash
# Controleer of alle tools geïnstalleerd zijn
task prepare:check-tools

# Bekijk alle beschikbare taken
task --list
```

### Taken per fase

| Fase | Commando | Beschrijving |
|------|----------|-------------|
| Prepare | `task prepare:check-tools` | Controleer vereiste tools |
| Prepare | `task prepare:check-vars` | Valideer versie-instellingen |
| Import | `task import:model` | QEA-model importeren |
| Import | `task import:previous` | Vorige versie importeren |
| Generate | `task generate:docs` | Markdown documentatie genereren |
| Generate | `task generate:lod` | Linked Data (TTL) genereren |
| Generate | `task generate:diff` | Verschilrapport genereren |
| Generate | `task generate:diagrams` | `.drawio`-bestanden naar SVG exporteren |
| Build | `task build:validate` | Docs valideren (strict mode) |
| Build | `task build:site` | MkDocs site bouwen |
| Build | `task build:serve` | Lokale dev-server starten (snelle preview) |
| Publish | `task publish:local` | Lokaal deployen via mike |
| Publish | `task publish:github` | Publiceren naar GitHub Pages |
| | `task full-deploy` | Volledige deployment |

### Afhankelijkheden tussen taken

De taken zijn via `deps` met elkaar verbonden, zodat elke fase automatisch doet wat nodig is. De belangrijkste keten:

```
prepare:check-tools ─┐
prepare:check-vars ──┴─► import:model ─┬─► generate:docs ─────┐
                                        ├─► generate:lod ──────┤
                                        └─► import:previous ──► generate:diff ─┤
                                                                                ├─► publish:local ─► publish:github
generate:diagrams ─────────────────────────────────────────────────────────────┘
                                                                                │
                           build:validate / build:site ◄───────────────────────┘
```

Concreet betekent dit dat je in de praktijk bijna altijd met één commando toekunt:

- `task publish:local` draait automatisch alle `generate:*`-taken en daarmee ook `import:model` en `import:previous`.
- `task build:validate` en `task build:site` trekken `generate:docs` en `generate:diagrams` mee.
- `task build:serve` heeft bewust géén deps voor een snelle dev-loop; draai zelf `task generate:docs` of `task generate:diagrams` als de bronbestanden zijn gewijzigd.
- `task full-deploy` is nu een dunne alias voor `publish:local`; de orkestratie zit in de dependency-graaf.
- `task generate:diagrams` draait alleen wanneer een `.drawio`-bestand nieuwer is dan zijn `.svg` (`run: when_changed`), dus herhaald aanroepen is goedkoop.

## Configuratie

De configuratie staat in `.env` in de repository-root:

| Variabele | Beschrijving |
|-----------|-------------|
| `VERSION` | Huidige versie (bijv. `v0.4`) |
| `PREVIOUS_VERSION` | Vorige versie (voor diff) |
| `GBO_FILE` | Naam van het QEA-bestand |
| `LOD_FILE` | Naam van het Linked Data-bestand |
| `LINKED_DATA_NS` | Basis-namespace voor Linked Data |
| `ROOT_NODE_GBO` | Root package GUID in Enterprise Architect |

## Optionele tools

| Tool | Doel |
|------|------|
| [Apache Jena (`riot`)](https://jena.apache.org/) | RDF/Turtle validatie |
| [Protege](https://protege.stanford.edu/) | Ontologie-editor en reasoner |
| [OOPS!](https://oops.linkeddata.es/) | Ontology Pitfall Scanner |
| Enterprise Architect | UML-modellering (QEA-bestanden) |

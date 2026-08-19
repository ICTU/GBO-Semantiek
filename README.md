# GBO-Semantiek

> **Gemeenschappelijke Bronontsluiting – Semantiek**
> Versie: v0.2 | Status: Concept

---

## Over dit repository

Dit repository bevat het **GBO-Semantiek informatiemodel**: een open specificatie voor de semantische beschrijving van basisgegevens uit overheidsregistraties. Het doel is om een gedeeld begrippenkader en gegevensmodel te bieden dat overheidsorganisaties en ketenpartners kunnen gebruiken voor interoperabiliteit en datakwaliteit.

Dit repository is opgezet conform het principe *documentation-first*: de documentatie is de primaire bron van waarheid voor de specificatie. Artefacten zoals UML-modellen, JSON Schema's en RDF/OWL-beschrijvingen worden afgeleid van de documentatie.

### Gebaseerd op GGM

De opzet van dit repository is **geïnspireerd op het [Gemeentelijk Gegevensmodel (GGM)](https://github.com/gemeenteshertogenbosch/GGM)**, een open informatiemodel dat als referentie geldt voor gemeentelijke gegevensuitwisseling. Wij volgen eenzelfde documentatie- en governance-aanpak, maar passen deze toe op het bredere domein van GBO-Semantiek.

---

## Versiebeheer

Er zijn **twee afzonderlijke versieringssystematieken** in dit repository:

### 1. Documentatieversiebeheer (via mike)

De documentatiewebsite wordt beheerd met [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) en gepubliceerd via [mike](https://github.com/jimporter/mike). Hierdoor kunnen meerdere versies van de documentatie naast elkaar gepubliceerd worden op GitHub Pages:

- `v0.1` → `https://<organisatie>.github.io/GBO-Semantiek/v0.1/`
- `v0.2` → `https://<organisatie>.github.io/GBO-Semantiek/v0.2/`

Mike beheert de gepubliceerde documentatieversies en staat los van de inhoudelijke modelversies.

### 2. Datamodelversiebeheer (via root-mappen)

De daadwerkelijke modelartefacten (UML, JSON Schema, RDF) worden **niet** via mike beheerd, maar via aparte mappen in de repository-root:

```
/v0.1/
  uml/
  jsonschema/
  rdf/
/v0.2/          ← toekomstige versie
  ...
```

Dit onderscheid is bewust: documentatieversies kunnen los van modelversies evolueren. Een documentatie-update vereist niet altijd een nieuwe modelversie, en vice versa.

---

## Directory-structuur

```
gbo-semantiek/
├── docs/                        # MkDocs documentatiebron (in het Nederlands)
│   ├── index.md                 # Introductie
│   ├── doel-en-scope.md
│   ├── begrippen.md
│   ├── architectuur.md
│   ├── versiebeheer.md
│   ├── governance.md
│   └── roadmap.md
├── v0.1/                        # Datamodel artefacten versie 0.1
│   ├── uml/
│   ├── jsonschema/
│   └── rdf/
├── tools/                       # Hulpscripts en templates
│   ├── gbo_markdown.j2          # Jinja2-template voor definitie-generatie
│   ├── validate_docs.sh
│   └── deploy_docs.sh
├── .github/
│   └── workflows/               # CI/CD workflows
├── Taskfile.yml                 # Task-runner configuratie (go-task)
├── .env                         # Omgevingsvariabelen (versie, bestandsnamen)
├── mkdocs.yml                   # MkDocs configuratie
├── CHANGELOG.md
├── CONTRIBUTING.md
└── README.md
```

---

## Aan de slag

### Vereisten

- [go-task](https://taskfile.dev/) — task-runner
- [crunch_uml](https://github.com/brienen/crunch_uml) — model import/export
- Python 3.9+ met `mkdocs-material` en `mike`
- `jq` — JSON-processor

Controleer of alles geïnstalleerd is:

```bash
task prepare:check-tools
```

### Documentatiewebsite lokaal draaien

```bash
# Start lokale ontwikkelserver
task build:serve
```

### Beschikbare taken

Alle taken zijn gegroepeerd per fase:

| Fase | Taken | Beschrijving |
|------|-------|-------------|
| **prepare** | `prepare:check-tools`, `prepare:check-vars` | Voorwaarden valideren |
| **import** | `import:model`, `import:previous` | Model(len) inladen in crunch_uml |
| **generate** | `generate:docs`, `generate:lod`, `generate:diff` | Artifacts genereren uit het model |
| **build** | `build:validate`, `build:site`, `build:serve` | MkDocs bouwen, valideren, serveren |
| **publish** | `publish:local`, `publish:github` | Mike deploy (lokaal) of push naar gh-pages |
| | `full-deploy` | Volledige deployment van import t/m publish |

```bash
# Bekijk alle beschikbare taken
task --list

# Volledige deployment
task full-deploy

# Alleen documentatie genereren
task generate:docs

# Publiceren naar GitHub Pages
task publish:github
```

Zie [docs/versiebeheer.md](docs/versiebeheer.md) voor een uitgebreide uitleg over het versiebeleid.

---

## Bijdragen

Bijdragen zijn van harte welkom! Lees [CONTRIBUTING.md](CONTRIBUTING.md) voor de richtlijnen.

Kort samengevat:
1. Fork dit repository
2. Maak een feature branch aan (`git checkout -b feature/mijn-wijziging`)
3. Commit je wijzigingen (`git commit -m 'feat: beschrijving'`)
4. Open een Pull Request

---

## Licentie

Dit repository valt onder de **EUPL-1.2 licentie**, conform de standaard voor open source software bij Nederlandse overheidsorganisaties. De volledige licentietekst staat in [`LICENSE`](LICENSE); zie ook de [toelichting op joinup.ec.europa.eu](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12).

---

## Contact

**Repository-eigenaar:** Arjen Brienen (ICTU) — arjen.brienen@ictu.nl

Voor vragen en suggesties kun je een [issue aanmaken](../../issues), een [discussie starten](../../discussions) of rechtstreeks contact opnemen met de repository-eigenaar. Beveiligingskwesties meld je volgens het [beveiligingsbeleid](SECURITY.md).

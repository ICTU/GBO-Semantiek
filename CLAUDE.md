# CLAUDE.md — Werkinstructies voor Claude

Dit bestand helpt Claude (en andere AI-assistenten) om efficiënt en consistent mee te werken aan dit repository. Lees dit eerst voordat je wijzigingen voorstelt of bestanden aanmaakt.

---

## 1. Over dit project

**Naam:** GBO-Semantiek, het semantisch raamwerk van de Gemeenschappelijke Bronontsluiting (GBO).
**Status:** Concept, versie v0.1.
**Doel:** Een landelijke, sectoroverstijgende open specificatie voor de semantische beschrijving van basisgegevens uit overheidsregistraties, met een gedeeld begrippenkader en informatiemodel voor interoperabiliteit en datakwaliteit tussen overheidsorganisaties en ketenpartners.
**Inhoudelijke bronnen:** GBO put uit meerdere bronmodellen. Een belangrijk deel komt uit gemeentelijke referentiemodellen, met name het Gemeentelijk Gegevensmodel (GGM, oorspronkelijk gemeente 's-Hertogenbosch) en het Referentiemodel Stelsel van Gemeentelijke Basisgegevens (RSGB). Daarnaast worden de officiële catalogi en modellen van de landelijke basisregistraties (BRP, BAG, BRK, BGT, HR, WOZ) gevolgd.
**Licentie:** EUPL-1.2.

### Kernprincipe: model komt uit de wiki-repo

Het informatiemodel is **niet** in deze repo de bron van waarheid. De canonieke
LinkML (`v{VERSION}/informatiemodel/linkml/`), de bron- en client-profielen
(`v{VERSION}/bronnen/`, `v{VERSION}/clients/`) en de model-documentatie
(`docs/informatiemodel/gbo-kern/`) worden via `task import:copy` gekopieerd uit
de modelleer-/bronrepo **`llm-wiki-GBI-core-model`**. Bewerk ze hier niet met de hand.

Wat je hier wél schrijft (voorlopig met AI) is de **kader-documentatie** rondom
het model: `docs/architectuur/`, `docs/uitgangspunten/`, `docs/begrippen/`,
`docs/implementatie/`, `docs/ontologie/` en `docs/bijlagen/`. De afgeleide
artefacten (GraphQL, OWL/SHACL-TTL, changelog, mkdocs-site) worden via de
Taskfile gegenereerd/gebouwd uit de gekopieerde LinkML.

---

## 2. Repository-structuur

```
gbo-semantiek/
├── docs/                MkDocs documentatiebron (Nederlandstalig) — bron van waarheid
│   ├── architectuur/    Architectuurbeschrijving (componenten, toepassing)
│   ├── begrippen/       Begrippenkader (kader, structuur, beheer, relatie informatiemodel)
│   ├── bijlagen/        Woordenlijst, tooling, URI-namespace
│   ├── implementatie/   URI-strategie, naamgeving, deployment, publicatie
│   ├── json-ld/         JSON-LD context, framing, API-patronen (concept, nog niet in nav)
│   ├── ontologie/       SKOS, kwaliteit, publicatie
│   ├── uitgangspunten/  Ontwerpprincipes, kaders en standaarden, inspiratie
│   ├── assets/          Diagrammen (.drawio + .svg), CSS, icon
│   └── informatiemodel.md
├── v0.2/                Datamodel-artefacten per versie
│   ├── informatiemodel/linkml/  LinkML-model — GEKOPIEERD uit de wiki-repo
│   ├── bronnen/         Bron-profielen (aanbod) — GEKOPIEERD uit de wiki-repo
│   ├── clients/         Client-profielen (vraag) — GEKOPIEERD uit de wiki-repo
│   ├── graphql/         GraphQL SDL's (gegenereerd)
│   └── ontologie/       OWL + SHACL (gegenereerd)
├── tools/               Hulpscripts (generatoren, changelog, deploy)
├── site/                Gebouwde MkDocs-site (NIET handmatig bewerken)
├── Taskfile.yml         go-task runner met alle build/deploy-taken
├── mkdocs.yml           MkDocs Material-configuratie
├── .env                 Omgevingsvariabelen (VERSION, namespace; WIKI_REPO te overriden)
├── CHANGELOG.md
├── CONTRIBUTING.md
└── README.md
```

### Versiebeheer — twee sporen

Belangrijk om te onthouden: dit project hanteert **twee onafhankelijke versies**.

1. **Documentatieversies** worden beheerd via `mike` (gepubliceerd op GitHub Pages, één URL per versie).
2. **Datamodelversies** worden beheerd via aparte mappen in de root (`v0.1/`, `v0.2/`, ...).

Een documentatie-update vereist niet altijd een nieuwe modelversie en omgekeerd. Maak deze afweging expliciet bij wijzigingen.

---

## 3. Werkvoorkeuren — hoe Claude mag helpen

### Taal en stijl

- **Antwoord altijd in het Nederlands**, tenzij ik expliciet om Engels vraag.
- Alle documentatie, commit-boodschappen, issue-titels en code-commentaar in dit repository zijn ook in het Nederlands.
- Houd antwoorden in chat **bondig en zakelijk**. Geen lange samenvattingen achteraf van wat je gedaan hebt — ik kan de diff zelf lezen.
- Gebruik geen emoji's, tenzij ik daar zelf om vraag.

### Werkwijze

- **Stel verhelderende vragen** vóór je begint aan een niet-triviale taak. Liever één keer goed dan twee keer half.
- **Lees eerst de relevante bestanden** voordat je voorstellen doet. Vermijd aannames over de inhoud.
- **Volg bestaande conventies** in dit repository (Markdown-stijl, mappenstructuur, naamgeving). Wijk alleen af met goede reden.
- **Eén ding tegelijk:** liever een kleine, gefocuste wijziging dan een grote refactor. Stel grote refactors altijd eerst voor.
- **Bewerk nooit handmatig wat door tooling of de copy-slag komt.** Gegenereerd via `Taskfile.yml`: `site/`, `v{VERSION}/graphql/`, `v{VERSION}/ontologie/`, `v{VERSION}/begrippen/`, `v{VERSION}/GBO_Changes.md`. Gekopieerd uit de wiki-repo (`task import:copy`): `v{VERSION}/informatiemodel/linkml/`, `v{VERSION}/bronnen/`, `v{VERSION}/clients/`, `docs/informatiemodel/gbo-kern/` en `docs/informatiemodel/gbo-voorzieningen.md`.
- **Diagrammen** komen als PlantUML-fences mee in de gekopieerde model-docs en worden door mkdocs gerenderd. Het oude drawio→SVG-spoor (`task generate:diagrams`) is **voorlopig uitgeschakeld** (Fase 1).

### Wat NIET doen

- Geen bestanden in `site/` aanpassen — dat is gegenereerde output.
- Geen `.env` of `crunch_uml.db` committen of wijzigen zonder overleg.
- Geen Engelse documentatie toevoegen aan `docs/`.
- Geen nieuwe top-level mappen aanmaken zonder overleg.
- Geen README of CHANGELOG bijwerken op eigen initiatief — dat doe ik liever zelf of na expliciet verzoek.

---

## 4. Tooling en commando's

Dit repository gebruikt [go-task](https://taskfile.dev/) als task-runner. Alle taken staan in `Taskfile.yml` en zijn gegroepeerd per fase.

| Fase | Belangrijkste taken | Doel |
|------|---------------------|------|
| `prepare` | `prepare:check-tools`, `prepare:check-vars` | Voorwaarden valideren |
| `import` | `import:copy` | Model + bron-/client-profielen kopiëren uit de wiki-repo |
| `generate` | `generate:docs`, `generate:lod`, `generate:voorzieningen-lod`, `generate:begrippen`, `generate:diff` | Artefacten uit het model genereren |
| `build` | `build:validate`, `build:site`, `build:serve` | MkDocs valideren, bouwen, serveren |
| `publish` | `publish:local`, `publish:github` | Mike-deploy lokaal of naar gh-pages |
| — | `full-deploy` | Volledige pipeline van import t/m publish |

Veelgebruikte commando's:

```bash
task --list              # alle beschikbare taken
task build:serve         # lokale documentatieserver
task generate:docs       # documentatie regenereren uit het model
task full-deploy         # volledige pipeline draaien
```

### Omgevingsvariabelen (`.env`)

De `.env` wordt geladen door Taskfile.yml en bevat onder andere:

- `VERSION` — huidige modelversie (bijv. `v0.1`)
- `PREVIOUS_VERSION` — vorige versie voor diff-generatie
- `GBO_FILE` — bestandsnaam van het informatiemodel (.qea)
- `LOD_FILE` — bestandsnaam van de Linked Data export (.ttl)
- `LINKED_DATA_NS` — namespace voor Linked Data (`https://lod.gbo-semantiek.nl`)
- `ROOT_NODE_GBO` — Enterprise Architect root-package GUID

### Vereiste tools

- `go-task`
- `rsync` (voor `task import:copy`)
- `linkml` (incl. `gen-owl`, `gen-shacl`, `gen-yaml`, `linkml-validate`)
- Python 3.9+ met `mkdocs-material` en `mike`
- `jq`

---

## 5. Conventies

### Commit-boodschappen

Volg [Conventional Commits](https://www.conventionalcommits.org/nl/v1.0.0/) in het Nederlands:

- `feat:` — nieuwe functionaliteit of inhoud
- `fix:` — bugfix of correctie
- `docs:` — alleen documentatiewijzigingen
- `chore:` — onderhoud, tooling, build
- `refactor:` — herstructurering zonder gedragsverandering

### Branches en PR's

- Feature branches: `feature/<korte-beschrijving>`
- Fix branches: `fix/<korte-beschrijving>`
- Pull requests gaan naar `main`.

### Markdown-conventies

- Nederlandstalig.
- Gebruik ATX-headers (`#`, `##`).
- Tabellen voor gestructureerde opsomming.
- Verwijs naar andere documenten met relatieve links.

---

## 6. Terminologie (kort)

| Term | Betekenis |
|------|-----------|
| **GBO** | Gemeenschappelijke Bronontsluiting |
| **GGM** | Gemeentelijk Gegevensmodel — referentiemodel waarop GBO gebaseerd is |
| **Informatiemodel** | Conceptueel model van begrippen, objecten en relaties |
| **Begrippenkader** | Set van gedefinieerde begrippen met onderlinge relaties (vaak SKOS) |
| **LinkML** | Modelleertaal; canonieke modelbron, gekopieerd uit de wiki-repo |
| **import:copy** | Taskfile-taak die model + profielen uit de wiki-repo kopieert (vervangt de oude crunch_uml/QEA-import) |
| **Mike** | Versietool bovenop MkDocs voor meerdere documentatieversies naast elkaar |

---

## 7. Snelle checklist voor Claude vóór een wijziging

1. Heb ik de betreffende bestanden gelezen?
2. Pas ik de **bron** aan (documentatie of model) en niet de gegenereerde output?
3. Volgt mijn wijziging de bestaande conventies (Nederlands, Markdown-stijl, mappenstructuur)?
4. Is mijn wijziging klein en gefocust, of moet ik eerst een plan voorleggen?
5. Heb ik onnodige aanpassingen in andere bestanden vermeden?
6. Begrijp ik of dit een documentatiewijziging, modelwijziging, of beide is?

---

*Houd dit bestand actueel. Als werkafspraken of structuur veranderen, werk dan eerst dit bestand bij voordat je verder werkt.*

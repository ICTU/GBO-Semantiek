# Changelog — GBO-Semantiek

Alle noemenswaardige wijzigingen in dit project worden bijgehouden in dit bestand.

De indeling is gebaseerd op [Keep a Changelog](https://keepachangelog.com/nl/1.0.0/).
De versienummering volgt [Semantic Versioning](https://semver.org/lang/nl/).

---

## [Niet uitgebracht]

### Toegevoegd
- `Taskfile.yml` met gegroepeerde taken (prepare, import, generate, build, publish, full-deploy)
- `.env` configuratiebestand voor versie- en bestandsnaamvariabelen
- `tools/gbo_markdown.j2` Jinja2-template voor definitie-generatie via crunch_uml
- Crunch UML-integratie: model import, Linked Data export, versievergelijking
- `.gitignore` uitgebreid met `.task/` en `crunch_uml.db`
- Eerste concept begrippenkader (SKOS/Turtle) *(gepland)*
- Eerste MIM-conform informatiemodel *(gepland)*

---

## [v0.3] - 2026-06-26

Fase 1 van de repo-herindeling: LinkML wordt de canonieke modelbron en de
modelleer- en publicatieverantwoordelijkheden worden over twee repositories
verdeeld. Deze versie vervangt de op crunch_uml/QEA gebaseerde aanpak die eerder
onder "Niet uitgebracht" stond.

### Toegevoegd
- Canonieke LinkML-modelbron in de modelleerrepo (`publicatie/linkml/`): 13 gekoppelde modelschema's (`gbo.yaml`, `datatypes`, `hoofdmodel` en 10 deelmodellen) plus 2 meta-schema's (`bronprofiel.yaml`, `clientprofiel.yaml`).
- Profiel-spoor: 11 bron-profielen (`bag`, `bd`, `bri`, `brk`, `brp`, `brv`, `cki`, `hr`, `rod`, `uwv`, `woz`) en het eerste client-profiel (`np-belastingdienst`).
- Eigen, getypeerde identifier-datatypes met formaatpatroon: `BSN`, `KVKnummer`, `Vestigingsnummer`, `Kenteken`, `BRINcode` en `BAGID`, plus `KadastraleAanduiding` zonder patroon.
- `@restrictie`-directive in de GraphQL-SDL die de pattern-, minimum- en maximum-facetten van de identifier-scalars projecteert.
- MIM-brug (`tools/mim-mapping.ttl`): 11 GBO-lokale MIM-annotaties via `owl:equivalentProperty` gekoppeld aan de officiele Geonovum MIM-RDF-ontologie (`http://bp4mc2.org/def/mim#`).
- Build-hulpmiddelen: LinkML-changeloggenerator (`tools/genereer_changelog.py`, SchemaView-diff) en URI-kwalificatie (`tools/kwalificeer_uris.py`).
- Inhoud: eID/EUDI Annex VI-attestatie-inventaris met GBO-Core-mapping, OOTS-databehoefte (14 evidence types, 48 information requirements) en de gegevensarchitectuur als kennispagina.

### Gewijzigd
- De build importeert het model via `task import:copy` (rsync van `publicatie/linkml`, `bronnen`, `clients` en `informatiemodel` uit de modelleerrepo) in plaats van een QEA-import.
- OWL en SHACL worden via `gen-owl` en `gen-shacl` op een LinkML-werkkopie gegenereerd, met diepe, lowercase, deelmodel-gekwalificeerde URI's (`gen-owl --no-use-native-uris`).
- `partijnummer`, een betekenisloos surrogaat op `Partij`, is hernoemd naar `ID`; query-ingangen lopen via de natuurlijke zoeksleutels `bsn` en `kvkNummer`.
- BAG-identificaties gaan van `NEN3610ID` naar `BAGID` (16 cijfers); `NEN3610ID` blijft voor BRK-objecten.
- MIM-annotaties uitgelijnd op de officiele metamodelnamen: `materieleHistorie` wordt `indicatieMaterieleHistorie`, `formeleHistorie` wordt `indicatieFormeleHistorie`, `notation` wordt `skos:notation`.
- Documentatie integraal op v0.3 gezet; `generate:graphql` opgenomen in de `publish:local`-keten.

### Verwijderd
- crunch_uml/QEA-import (`import:model`, `import:previous`) en crunch_uml als tool-dependency; `prepare:check-tools` vereist nu `rsync` en de LinkML-toolchain.
- Het curated GraphQL-manifest in de modelleerrepo (`scripts/build-graphql.py` en `scripts/graphql/`), opgevolgd door het client-profiel.
- De drawio-naar-SVG-export (`generate:diagrams`) is in Fase 1 uitgeschakeld; class-diagrammen komen als PlantUML mee in de docs.

### Migratie
- Wie de build draait: check de modelleerrepo naast de publicatierepo uit (`WIKI_REPO`, default `../llm-wiki-GBI-core-model`) en gebruik `task import:copy` in plaats van de oude import-taken.
- Afnemers van de GraphQL-SDL: vervang `partijnummer` door `ID`; vraag `IngeschrevenPersoon` op via `bsn` en niet-natuurlijke personen via `kvkNummer`; neem de benoemde identifier-scalars (`BSN`, `KVKnummer`, en verder) met hun `@restrictie`-patronen over in plaats van String.

---

## [0.1.0] — 2024

### Toegevoegd

- Initiële repository-structuur opgezet gebaseerd op GGM-aanpak
- `docs/` documentatiestructuur aangemaakt in het Nederlands:
  - `index.md` — Introductie
  - `doel-en-scope.md` — Doel en scope van de standaard
  - `begrippen.md` — Initiële begrippenlijst
  - `architectuur.md` — Architectuurbeschrijving en aansluiting op standaarden
  - `versiebeheer.md` — Versiebeleid (documentatie én datamodel)
  - `governance.md` — Governance-structuur en rollen
  - `roadmap.md` — Geplande ontwikkelingen
- `mkdocs.yml` geconfigureerd met Material-thema, Nederlandse navigatie en mike-integratie
- `v0.1/` versiegerelateerde map aangemaakt met placeholder-submappen:
  - `v0.1/uml/` — voor UML-modellen en XMI-exports
  - `v0.1/jsonschema/` — voor JSON Schema-bestanden
  - `v0.1/rdf/` — voor RDF/OWL-ontologieën
- `tools/` map aangemaakt met hulpscripts:
  - `tools/validate_docs.sh` — MkDocs-validatiescript
  - `tools/deploy_docs.sh` — Publicatiescript via mike
- GitHub Actions workflows:
  - `.github/workflows/docs-build.yml` — documentatievalidatie bij PR/push
  - `.github/workflows/docs-deploy.yml` — versioned publicatie via mike
- `README.md` in het Nederlands met uitleg over doel, GGM-inspiratie en versiebeheer
- `CONTRIBUTING.md` in het Nederlands met bijdragerichtlijnen
- `CHANGELOG.md` — dit bestand
- `.gitignore` voor Python/MkDocs-gerelateerde bestanden

---

[Niet uitgebracht]: https://github.com/ICTU/gbo-semantiek/compare/v0.3...HEAD
[v0.3]: https://github.com/ICTU/gbo-semantiek/compare/v0.2...v0.3
[0.1.0]: https://github.com/ICTU/gbo-semantiek/releases/tag/v0.1.0

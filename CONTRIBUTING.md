# Bijdragen aan GBO-Semantiek

Dank voor je interesse in het bijdragen aan GBO-Semantiek! Dit document beschrijft hoe je kunt bijdragen aan de standaard.

---

## Gedragscode

Door bij te dragen aan dit project, ga je akkoord met respectvol en constructief samenwerken. Wij hanteren de [Gedragscode](CODE_OF_CONDUCT.md), gebaseerd op de [Contributor Covenant](https://www.contributor-covenant.org/nl/version/2/0/code_of_conduct/) versie 2.0.

---

## Manieren om bij te dragen

### 1. Issues aanmaken

Heb je een fout gevonden, een vraag of een verbetervoorstel? Open dan een [issue](https://github.com/ICTU/GBO-Semantiek/issues).

Gebruik de beschikbare issue-templates:
- **Bug report** — voor fouten in de documentatie of artefacten
- **Feature request** — voor nieuwe functionaliteit of uitbreiding
- **Vraag** — voor vragen over de standaard

### 2. Pull Requests indienen

Wil je direct een bijdrage leveren? Volg dan deze stappen:

1. **Fork** dit repository
2. Maak een **feature branch** aan:
   ```bash
   git checkout -b feature/mijn-wijziging
   ```
3. Maak je wijzigingen en test lokaal:
   ```bash
   task build:serve
   ```
4. **Commit** je wijzigingen met een beschrijvende commit-boodschap:
   ```bash
   git commit -m "feat: beschrijving van de wijziging"
   ```
5. **Push** je branch naar je fork:
   ```bash
   git push origin feature/mijn-wijziging
   ```
6. Open een **Pull Request** naar de `main`-branch van dit repository

### 3. Deelnemen aan consultatierondes

Bij grote wijzigingen organiseert de werkgroep consultatierondes. Je kunt deelnemen via GitHub Discussions of via de contactgegevens in de README.

---

## Commit-boodschappen

Wij volgen de [Conventional Commits](https://www.conventionalcommits.org/nl/v1.0.0/) standaard:

| Prefix | Gebruik |
|--------|---------|
| `feat:` | Nieuwe functionaliteit of inhoud |
| `fix:` | Bugfix of correctie |
| `docs:` | Documentatiewijziging |
| `chore:` | Onderhoud (dependencies, configuratie) |
| `refactor:` | Herstructurering zonder gedragswijziging |

**Voorbeelden:**
```
feat: begrippendefinitie voor 'Basisgegeven' toegevoegd
fix: gebroken link in architectuur.md hersteld
docs: versiebeheerbeleid verduidelijkt
```

---

## Documentatie aanpassen

De documentatie staat in de `docs/`-map en is geschreven in Markdown (MkDocs).

### Lokaal draaien

```bash
# Controleer of alle tools geïnstalleerd zijn
task prepare:check-tools

# Start lokale ontwikkelserver
task build:serve
# Open http://127.0.0.1:8000 in je browser

# Valideer de documentatie (strict mode)
task build:validate
```

### Taalbeleid

- Alle documentatie is in het **Nederlands**
- Technische termen mogen Engelstalig zijn (bijv. JSON Schema, RDF, UML)
- Code-voorbeelden en configuratiebestanden mogen Engelstalig zijn

---

## Datamodel bijdragen

Artefacten voor het datamodel (UML, JSON Schema, RDF) staan in versiegerelateerde mappen:

```
v0.1/
  uml/
  jsonschema/
  rdf/
```

Bijdragen aan het datamodel vereisen overleg met de werkgroep. Open eerst een issue of start een discussie voordat je een Pull Request indient.

---

## Code review-proces

1. Een werkgroeplid reviewt je Pull Request binnen 5 werkdagen
2. Je ontvangt feedback via GitHub-opmerkingen
3. Verwerk de feedback en update je branch
4. Bij akkoord wordt de Pull Request samengevoegd door de beheerder

---

## Licentie

Door bij te dragen, ga je ermee akkoord dat je bijdrage wordt gepubliceerd onder de **[EUPL-1.2 licentie](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12)**.

---

## Vragen?

Heb je vragen over het bijdrageproces? Open een [issue](https://github.com/ICTU/GBO-Semantiek/issues) of start een [discussie](https://github.com/ICTU/GBO-Semantiek/discussions).

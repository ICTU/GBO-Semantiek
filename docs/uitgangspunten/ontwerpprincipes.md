# Ontwerpprincipes

Ontwerpprincipes zijn de richtinggevende uitgangspunten voor alle keuzes bij het ontwerp van het semantisch raamwerk van GBO. Ze beschrijven *waarom* we iets op een bepaalde manier doen en vormen de toetssteen bij het maken van het begrippenkader en het informatiemodel.

Waar deze principes vandaan komen — welk PSA-ontwerpprincipe aan welk
semantiek-principe ten grondslag ligt — staat in de
[overzichtstabel achteraan dit hoofdstuk](#herkomst-koppeling-met-de-psa).

## S-01 — Data bij de bron

**PSA:** [D-05 — Gegevens bij de bron](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-05-gegevens-bij-de-bron-geen-onnodige-kopieen) — direct. Hier ook toegepast op de semantiek zelf: ook begrippen en definities kennen één bron.

Gegevens worden uitsluitend beheerd en gemuteerd bij de (authentieke) bron. GBO-Semantiek sluit aan bij het NORA-principe *"eenmalige registratie, meervoudig gebruik"* en bij het stelsel van basisregistraties: voor elk type gegeven is één bronhouder verantwoordelijk voor de kwaliteit, actualiteit en betekenis. Kopieën in data-lakes, caches, zoekindexen of read-models zijn toegestaan maar nooit gezaghebbend; zij ontlenen hun betekenis aan de bron en worden van daaruit geactualiseerd.

!!! info "Wat betekent dit voor GBO-Semantiek?"
    - Per objecttype is er één aangewezen authentieke bron (bronhouder)
    - Mutaties vinden uitsluitend plaats bij de bron; andere systemen nemen over, synchroniseren of cachen
    - Kopieën, caches en afgeleide representaties zijn toegestaan, maar nooit gezaghebbend
    - Ook de semantiek zelf (begrippen, definities, ontologie) wordt bij één bron beheerd en van daaruit hergebruikt

## S-02 — FAIR als basisraamwerk

**PSA:** [D-14 — Interoperabiliteit](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-14-interoperabiliteit-semantische-en-technische-afstemming) en [D-08 — Pas toe of leg uit](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-08-pas-toe-of-leg-uit-verplichte-open-standaarden) — direct. D-14 dekt *Interoperable* en *Reusable*, D-08 maakt *Accessible* concreet via verplichte open standaarden.

De [FAIR-principes](https://www.go-fair.org/fair-principles/) (Findable, Accessible, Interoperable, Reusable) vormen de overkoepelende basis voor alle ontwerpkeuzes rond data en semantische artefacten. NORA vertaalt deze principes expliciet naar de Nederlandse overheidscontext als architectuurprincipe 1.1: *"Gegevens die kunnen worden gedeeld zijn vindbaar, toegankelijk, interoperabel en herbruikbaar"*.

Voor ontologieën geldt dat FAIR niet alleen op data maar ook op de semantische artefacten zelf van toepassing is: de ontologie, het begrippenkader en de context-bestanden moeten zelf ook FAIR zijn.

De vier FAIR-dimensies vertalen zich concreet naar semantiek en informatiemodellen:

| FAIR-principe | Implicatie voor semantiek en informatiemodel |
|---|---|
| **Findable** | Globaal unieke, persistente URI's voor alle modelelementen; publicatie in doorzoekbare catalogus |
| **Accessible** | De-referenceable URI's via HTTP; content-negotiation (HTML voor mensen, Turtle voor machines) |
| **Interoperable** | Formele taal (OWL, SHACL, SKOS); gebruik van gedeelde informatiemodellen; gekwalificeerde links |
| **Reusable** | Rijke metadata bij artefacten; expliciete licenties; herkomst traceerbaar; conform domeinstandaarden |

NORA stelt als implicatie van principe 1.1 dat *"gegevens en hun metagegevens zijn voorzien van wereldwijd unieke en stabiele identificaties"*. GBO geeft hier invulling aan via een expliciete URI- en naamgevingsstrategie, die zorgt dat elk modelelement vindbaar, opvraagbaar en herbruikbaar is.

!!! info "Wat betekent dit voor GBO-Semantiek?"
    GBO geeft vorm aan FAIR via een consistente URI- en naamgevingsstrategie:

    - **Persistent**: URI's veranderen niet na publicatie en gebruiken een stabiel domein, los van technische implementatie
    - **Uniek**: elke URI identificeert precies één ding; geen hergebruik voor meerdere concepten
    - **Dereferenceerbaar**: elke URI is opvraagbaar via HTTP met content-negotiation (HTML, Turtle, JSON-LD)
    - **Onderscheid document vs. ding**: aparte URI's voor een real-world concept en het document dat het beschrijft (via `303 redirect` of `#hash URI`)
    - **Leesbaar**: URI-paden en elementnamen zijn betekenisvol; naamswijzigingen worden afgevangen met `owl:sameAs`
    - **Naamruimte-consistent**: één consistente naamruimte per artefacttype (ontologie, begrippenkader, context, instanties)
    - **Rijke metadata**: elk artefact heeft expliciete licentie, versie, herkomst en publicatiedatum
    - **Formele talen**: OWL, SHACL en SKOS voor machine-verwerkbaarheid

    De concrete uitwerking staat in [URI-strategie](../implementatie/uri-strategie.md) en [Naamgeving](../implementatie/naamgeving.md).

## S-03 — Modulariteit: generiek vs. use-case-specifiek

**PSA:** [D-04 — Robuust, modulair en flexibel ontwerp](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-04-robuust-modulair-en-flexibel-ontwerp) en [D-06 — Componentgebaseerd werken](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-06-componentgebaseerd-werken-herbruikbare-bouwstenen) — direct. Dezelfde separation of concerns, maar toegepast op modelniveau in plaats van op componenten.

### Informatiemodel en applicatieprofiel

Het [OSLO](https://data.vlaanderen.be/)-initiatief introduceert het patroon van *vocabularia* (generiek, herbruikbaar) versus *applicatieprofielen* (use-case-specifiek, beperkingen opleggen). Dit is een directe toepassing van het separation of concerns-principe: generieke kennis wordt een keer gedefinieerd en door meerdere applicatieprofielen hergebruikt.

Een applicatieprofiel kan nieuwe klassen en eigenschappen introduceren, maar uitsluitend binnen het eigen use-case-domein. Het profiel legt daarnaast beperkingen op (cardinaliteiten, waardelijsten) en combineert klassen uit meerdere informatiemodellen. De koppeling met de onderliggende generieke modellen loopt via expliciete relaties — overerving (`rdfs:subClassOf`), equivalentie of andere semantische verbanden — zodat de herkomst en samenhang traceerbaar blijven.

GBO past dit patroon toe:

- Het **generieke informatiemodel** (GBO-kern) bevat klassen en attributen die over alle use cases heen geldig zijn
- **Applicatieprofielen** per use case verfijnen het generieke model met specifieke beperkingen

## Principes voor het begrippenkader

Het begrippenkader als SKOS-thesaurus volgt zeven principes. Drie daarvan zijn een verbijzondering van een PSA-principe; de overige vier zijn eigen aanvullingen zonder PSA-pendant.

### S-04 — Begrippen-first

**PSA:** [D-14 — Interoperabiliteit](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-14-interoperabiliteit-semantische-en-technische-afstemming) — direct. Semantische afstemming begint bij gedeelde begripsvorming.

NORA-principe 3.1 stelt dat *"gemeenschappelijke begripsvorming het startpunt is"*: begrippen worden geëxpliciteerd voordat informatiemodellen worden gemaakt.

### S-05 — Eén gezaghebbende definitie per begrip

**PSA:** [D-14 — Interoperabiliteit](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-14-interoperabiliteit-semantische-en-technische-afstemming) — direct. Invulling van de eis van semantische eenduidigheid.

Elk `skos:Concept` heeft precies één `skos:prefLabel` per taal en één `skos:definition`; meerdere namen zijn synoniemen (`skos:altLabel`).

### S-06 — Hiërarchische coherentie

**PSA:** geen. Eigen SKOS-regel; de PSA doet geen uitspraak over modelhygiëne.

`skos:broader`- en `skos:narrower`-relaties zijn transitief en mogen geen cycli bevatten.

### S-07 — Expliciete scopeNotes

**PSA:** geen. Eigen SKOS-regel voor GBO-specifieke afbakening.

Gebruik `skos:scopeNote` voor het afbakenen van het gebruik van een begrip in de specifieke GBO-context, naast een algemene definitie.

### S-08 — Scheiding begrip en waardelijst

**PSA:** geen. Eigen modelleerregel.

Gebruik `skos:ConceptScheme` voor begrippenkaders en aparte schemes voor codelijsten en enumeraties; vermeng ze niet.

### S-09 — Koppeling aan bronwetgeving

**PSA:** geen. Eigen herkomsteis; volgt uit *Reusable*, niet uit een PSA-principe.

Leg via `skos:exactMatch` of `dct:source` vast welke wet of regeling aan de grondslag ligt van een definitie.

### S-10 — Publiceer als Linked Data

**PSA:** [D-08 — Pas toe of leg uit](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-08-pas-toe-of-leg-uit-verplichte-open-standaarden) — direct. SKOS en RDF staan op de pas-toe-of-leg-uit-lijst.

Het begrippenkader is de-referenceable, conform NORA-principe 3.5: *"Metagegevens zijn beschikbaar als Linked Data"*.

!!! info "Wat betekent dit voor GBO-Semantiek?"
    - Het informatiemodel verwijst naar het begrippenmodel
    - Eén gezaghebbende definitie per begrip; synoniemen via `skos:altLabel`
    - Hiërarchie is acyclisch; GBO-specifieke afbakening via `skos:scopeNote`
    - Begrippen en waardelijsten staan in aparte `skos:ConceptScheme`s
    - Herkomst uit wet- of regelgeving wordt expliciet vastgelegd via `dct:source`
    - Het begrippenkader wordt als Linked Data gepubliceerd

## Principes voor het informatiemodel

### S-11 — Minimale ontologische committering

**PSA:** [D-01 — Decentraal wat kan, centraal wat moet](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-01-decentraal-wat-kan-centraal-wat-moet) — naar analogie. D-01 gaat over taken en voorzieningen; dezelfde subsidiariteitsgedachte is hier toegepast op modelinhoud.

Definieer in het generieke informatiemodel alleen wat door alle use cases gedeeld wordt. Het principe van *minimal ontological commitment* stelt: modeleer alleen wat noodzakelijk is en laat de rest open voor applicatieprofielen. Te veel beperkingen in het generieke model maakt hergebruik moeilijk.

!!! info "Wat betekent dit voor GBO-Semantiek?"
    - Alleen wat alle use cases delen, zit in het generieke model
    - Specifieke beperkingen horen thuis in een applicatieprofiel, niet in de kern
    - Bij twijfel: laat open in het generieke model en leg pas vast in het profiel

### S-12 — Hergebruik boven herontwikkeling

**PSA:** [D-13 — Standaardiseer waar mogelijk](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-13-standaardiseer-waar-mogelijk-maak-uitzonderingen-expliciet-en-zorg-dat-deze-in-bestaande-gremia-landen) — direct. Vertaald naar hergebruik van MIM-conforme modellen en bestaande ontologieën.

Bestaande informatiemodellen en ontologieën worden hergebruikt boven het opnieuw ontwikkelen van dezelfde kennis. De LOT-methodologie (Linked Open Terms) formaliseert dit als kernprincipe.

**Hergebruik van informatiemodellen**

GBO bouwt voort op bestaande, MIM-conforme informatiemodellen in plaats van modellen from scratch te ontwikkelen:

!!! info "Wat betekent dit voor GBO-Semantiek?"
    - Hergebruik van bestaande MIM-conforme modellen gaat vóór herontwikkeling
    - Nieuwe termen worden alleen gedefinieerd waar geen passend bestaand alternatief is

### S-13 — Versioning en evolutie

**PSA:** [D-04 — Robuust, modulair en flexibel ontwerp](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-04-robuust-modulair-en-flexibel-ontwerp) — naar analogie. De PSA kent versiebeheer niet als eigen principe; de koppeling loopt via de eis dat een component onafhankelijk doorontwikkeld kan worden.

Modellen evolueren. GBO hanteert versiebeheer op twee niveaus:

**Informatiemodel (MIM/UML)**

Het informatiemodel volgt [Semantic Versioning](https://semver.org/lang/nl/) (`MAJOR.MINOR.PATCH`):

- **MAJOR**, achterwaarts incompatibele wijzigingen (bijv. verwijderen of hernoemen van objecttypen)
- **MINOR**, achterwaarts compatibele uitbreidingen (bijv. nieuwe objecttypen of optionele attributen)
- **PATCH**, correcties zonder structuurwijziging (bijv. aangepaste definities of typfouten)

Elke versie wordt opgeslagen in een eigen map in de repository (`/v0.1/`, `/v0.2/`, etc.) en is daarmee onveranderlijk na publicatie.

**Ontologie (OWL/RDF)**

De gepubliceerde ontologie legt versie-informatie vast via standaard metadata-properties:

- `owl:versionInfo`, het versienummer van de ontologie
- `dct:issued`, de publicatiedatum
- `dct:modified`, de datum van de laatste wijziging

Verouderde klassen en properties worden gemarkeerd met `owl:deprecated` in plaats van verwijderd, zodat bestaande data geldig blijft en verwijzingen niet breken. Dit garandeert dat historische JSON-LD payloads ook na een modelwijziging interpreteerbaar blijven.

!!! info "Wat betekent dit voor GBO-Semantiek?"
    - Het informatiemodel volgt Semantic Versioning (`MAJOR.MINOR.PATCH`)
    - Elke versie wordt onveranderlijk opgeslagen in een eigen map (`/v0.1/`, `/v0.2/`, ...)
    - De ontologie legt versie-informatie vast via `owl:versionInfo`, `dct:issued` en `dct:modified`
    - Verouderde elementen worden gemarkeerd met `owl:deprecated` en nooit verwijderd
    - Definities zijn in het Nederlands en gekoppeld aan het begrippenkader; conventies staan in [Naamgeving](../implementatie/naamgeving.md)

## Herkomst: koppeling met de PSA

De [GBO PSA](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/) stelt veertien ontwerpprincipes vast voor de architectuur als geheel. De semantiek-principes hieronder zijn daarvan de verbijzondering naar begrippenkader en informatiemodel; bij elk principe staat vermeld waar het vandaan komt.

Een koppeling is **direct** wanneer het semantiek-principe hetzelfde stelt als het PSA-principe, toegepast op semantiek, en **naar analogie** wanneer de PSA het onderwerp niet als eigen principe benoemt en alleen de redenering wordt overgenomen. Een deel van de principes is een eigen aanvulling zonder PSA-herkomst; die staan er ook in, zodat de tabel alle semantiek-principes toont.

| # | Semantiek-principe | PSA-herkomst | Koppeling |
|---|---|---|---|
| **S-01** | [Data bij de bron](#s-01-data-bij-de-bron) | [D-05](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-05-gegevens-bij-de-bron-geen-onnodige-kopieen) | Direct; hier ook toegepast op de semantiek zelf |
| **S-02** | [FAIR als basisraamwerk](#s-02-fair-als-basisraamwerk) | [D-14](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-14-interoperabiliteit-semantische-en-technische-afstemming), [D-08](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-08-pas-toe-of-leg-uit-verplichte-open-standaarden) | Direct; D-14 dekt *Interoperable* en *Reusable*, D-08 maakt *Accessible* concreet |
| **S-03** | [Modulariteit: generiek vs. use-case-specifiek](#s-03-modulariteit-generiek-vs-use-case-specifiek) | [D-04](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-04-robuust-modulair-en-flexibel-ontwerp), [D-06](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-06-componentgebaseerd-werken-herbruikbare-bouwstenen) | Direct; separation of concerns op modelniveau in plaats van op componenten |
| **S-04** | [Begrippen-first](#principes-voor-het-begrippenkader) | [D-14](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-14-interoperabiliteit-semantische-en-technische-afstemming) | Direct; semantische afstemming begint bij gedeelde begripsvorming |
| **S-05** | [Eén gezaghebbende definitie per begrip](#principes-voor-het-begrippenkader) | [D-14](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-14-interoperabiliteit-semantische-en-technische-afstemming) | Direct; invulling van de eis van semantische eenduidigheid |
| **S-06** | [Hiërarchische coherentie](#principes-voor-het-begrippenkader) | Geen | Eigen SKOS-regel; de PSA doet geen uitspraak over modelhygiëne |
| **S-07** | [Expliciete scopeNotes](#principes-voor-het-begrippenkader) | Geen | Eigen SKOS-regel voor GBO-specifieke afbakening |
| **S-08** | [Scheiding begrip en waardelijst](#principes-voor-het-begrippenkader) | Geen | Eigen modelleerregel |
| **S-09** | [Koppeling aan bronwetgeving](#principes-voor-het-begrippenkader) | Geen | Eigen herkomsteis; volgt uit *Reusable*, niet uit een PSA-principe |
| **S-10** | [Publiceer als Linked Data](#principes-voor-het-begrippenkader) | [D-08](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-08-pas-toe-of-leg-uit-verplichte-open-standaarden) | Direct; SKOS en RDF staan op de pas-toe-of-leg-uit-lijst |
| **S-11** | [Minimale ontologische committering](#s-11-minimale-ontologische-committering) | [D-01](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-01-decentraal-wat-kan-centraal-wat-moet) | Naar analogie; subsidiariteit toegepast op modelinhoud |
| **S-12** | [Hergebruik boven herontwikkeling](#s-12-hergebruik-boven-herontwikkeling) | [D-13](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-13-standaardiseer-waar-mogelijk-maak-uitzonderingen-expliciet-en-zorg-dat-deze-in-bestaande-gremia-landen) | Direct; vertaald naar MIM-conforme modellen en bestaande ontologieën |
| **S-13** | [Versioning en evolutie](#s-13-versioning-en-evolutie) | [D-04](https://ictu.github.io/GBO-PSA/main/ontwerpprincipes/#d-04-robuust-modulair-en-flexibel-ontwerp) | Naar analogie; de PSA kent versiebeheer niet als eigen principe |

Omgekeerd hebben zeven PSA-principes geen semantiek-pendant, omdat ze de architectuur en de uitvoering betreffen en niet de betekenis van gegevens: D-02 (ordening van het stelsel), D-03 (GDI-bouwstenen), D-07 (open source), D-09 (API-first) en D-10 tot en met D-12 (beveiliging, least privilege, aantoonbare veiligheid).

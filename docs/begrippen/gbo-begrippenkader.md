# GBO-Begrippenkader

Het GBO-Begrippenkader definieert de **betekenis** van de objecttypen uit het
[GBO-Kernmodel](../informatiemodel/gbo-kern/hoofdmodel.md) en het
[GBO-Voorzieningenmodel](../informatiemodel/gbo-voorzieningen.md). Elk objecttype
verwijst via `class_uri` naar precies een concept in dit begrippenkader.

Het begrippenkader wordt **gegenereerd** uit de `skos:`-annotaties in de
LinkML-modelbron en gepubliceerd als [SKOS ConceptScheme](https://www.w3.org/2004/02/skos/)
in Turtle-formaat: `v0.4/begrippen/GBO-Begrippenkader.ttl`. Bewerk dat bestand
niet met de hand; pas de annotaties in het model aan en draai
`task generate:begrippen`.

Zie [Structuur en publicatie](structuur.md) voor de technische SKOS-structuur en
[Relatie tot het informatiemodel](relatie_informatiemodel.md) voor het
koppelingsmechanisme.

## Scope en status

Dit begrippenkader is een **voorstel (concept)**. Alle begrippen dragen
`adms:status "proposed"` zolang ze niet formeel zijn vastgesteld.

| | Aantal |
|---|---|
| Begrippen uit het kernmodel (de inhoudelijke deelmodellen) | 78 |
| Begrippen uit het voorzieningenmodel | 23 |
| **Totaal** | **101** |

Attribuutsoorten en relatiesoorten krijgen nog geen eigen begrip; die volgen in
een latere versie.

## Begrippen van het voorzieningenmodel

Het voorzieningenmodel beschrijft de uitwisseling zelf: wie vraagt op, op welke
grondslag, en wat er geleverd wordt.

| Begrip | Definitie |
|:---|:---|
| **Rol** | De functie die een partij in een specifieke context vervult, zoals bronhouder van een register, dienstverlener in een transactie of afnemer van een levering. |
| **Rolsoort** | De functies die een partij binnen de bronontsluiting kan vervullen. |
| **Betrokkene** | De natuurlijke persoon om wiens gegevens het in een gegevensverzoek gaat. |
| **Burger** | De persoon om wiens gegevens het gaat en die deze wil gebruiken om een dienst af te nemen; in de Nederlandse context altijd identificeerbaar met een burgerservicenummer. |
| **Buitenlandse betrokkene** | De persoon om wiens gegevens het gaat en die door een EU-overheidsdienst is geïdentificeerd, zonder dat een burgerservicenummer beschikbaar hoeft te zijn. |
| **Grondslag** | De juridische basis voor gegevensuitwisseling: toestemming van de betrokkene of een wettelijke verplichting. |
| **Toestemming** | Het expliciete akkoord van de betrokkene dat een specifieke partij een specifieke set gegevens mag opvragen, gebonden aan een scope en een geldigheidsduur. |
| **Toestemmingsstatus** | De statussen die een toestemming kan doorlopen. |
| **Wettelijke verplichting** | De wettelijke bepaling op grond waarvan gegevens zonder toestemming van de betrokkene mogen of moeten worden verstrekt. |
| **Gegevenselement** | De kleinste adresseerbare eenheid van data, die naar precies een begrip verwijst en daar structuurinformatie aan toevoegt. |
| **Bron** | Een registratie of gegevensverzameling bij een bronhouder, met een wettelijke grondslag. |
| **Dienst** | Een afgebakend doel waarvoor gegevens mogen worden opgevraagd, wettelijk verankerd en met een maximale scope. |
| **Scope** | Een benoemde verzameling gegevenselementen; de maximale scope wordt bepaald door wetgeving, een afnemer kan een kleinere scope vragen. |
| **Dienstencatalogus** | Het register van alle beschikbare diensten met hun scopes. |
| **Interactiepatroon** | Een van de manieren waarop een gegevensverzoek tot stand komt en wordt beantwoord, met vaste afspraken over wie initieert, wie ontvangt en welke grondslag geldt. |
| **Patroonsoort** | De drie interactiepatronen die de GBO PSA onderscheidt. |
| **Gegevensverzoek** | De transactie waarmee brondata wordt opgevraagd, op basis van precies een grondslag. |
| **Levering** | Het resultaat dat op een gegevensverzoek wordt teruggegeven. |
| **Gegevensset** | Levering als verzameling gegevenselementen in het GBO-formaat, zonder juridische waarmerking. |
| **Attestatie** | Levering als gekwalificeerde verklaring die in een EUDI-wallet kan worden opgeslagen en later zelfstandig verifieerbaar is. |
| **Attestatiesoort** | De twee manieren waarop een attestatie onder eIDAS2 gekwalificeerd kan worden. |
| **Evidence** | Levering als bewijsstuk in de vorm die het Once-Only Technical System voorschrijft, bestemd voor een bevoegde autoriteit in een andere lidstaat. |
| **Mapping** | De vastgelegde omzetting tussen gegevenselementen uit een bron en de structuur die een leveringsvorm voorschrijft. |

## Voorbeeld

```turtle
gbobegrip:Toestemming a skos:Concept ;
    dcterms:source "GBO PSA; AVG art. 4 lid 11 voor het toestemmingsbegrip" ;
    skos:definition "Het expliciete akkoord van de betrokkene dat een specifieke
        partij een specifieke set gegevens mag opvragen, gebonden aan een scope
        en een geldigheidsduur."@nl ;
    skos:inScheme <https://begrippen.gbo-semantiek.nl/id/conceptscheme/gbo-kern> ;
    skos:prefLabel "Toestemming"@nl ;
    adms:status "proposed" .
```

## Volgende stappen

1. **Attribuutbegrippen toevoegen**: begrippen voor attribuutsoorten (identificatie, naam, datatype) en relatiesoorten (bevat, beheert, ontsluit)
2. **Externe matches**: `skos:closeMatch` naar begrippen in TOOI, Stelselcatalogus en OSLO
3. **Governance**: vaststelling van het wijzigingsproces conform [Beheer en governance](beheer.md)
4. **Openstaande punten wegwerken**: `task generate:begrippen` rapporteert per begrip de resterende `needs_review`-notities uit het model

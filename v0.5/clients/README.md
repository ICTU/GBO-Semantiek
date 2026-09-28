# Client-profielen (vraag-kant)

Een **client-profiel** beschrijft welke onderdelen van het GBO-informatiemodel
één *afnemer* nodig heeft. Het is de spiegel van een [bron-profiel](../bronnen/README.md):
waar een bron-profiel de **aanbod**-kant vastlegt (welk objecttype een register
ontsluit), legt een client-profiel de **vraag**-kant vast (welk objecttype een
afnemer afneemt).

Beide zijn gedestilleerde, machine-leesbare projectie-configuratie, geauthored
vanuit de afnemer-kennis in `wiki/gbo-core/clients/` (DVTP, OOTS, eID). De rijke
analyse-documenten (databehoefte-mappings, evidence-pagina's) blijven in de wiki;
alleen het profiel verlaat de repo.

## Canonieke bron & generatie

- **Bron**: dit `clients/`-spoor en `bronnen/` zijn samen met `linkml/` de enige
  artefacten die `gbo-semantiek` uit deze repo kopieert (`task import:copy`).
- **Generatie** (GraphQL, per afnemer) gebeurt in `gbo-semantiek`, niet hier. Het
  oude standalone GraphQL-manifest (`scripts/graphql/`) en `build-graphql.py` zijn
  daarmee vervallen; de mapping-conventies wonen in
  `gbo-semantiek/tools/genereer_graphql.py`.

## Schema

Een profiel valideert tegen `../informatiemodel/linkml/clientprofiel.yaml`
(klasse `Clientprofiel`). De `schemabestand`- en `../`-paden zijn relatief aan de
`v{VERSION}`-layout van `gbo-semantiek`, waar de generatie draait.

| Profiel | Snede | Deelmodellen |
|---|---|---|
| `np-belastingdienst.yaml` | Natuurlijk Persoon × Belastingdienst (demo) | personen, adressen-en-gebouwen, belastingen |

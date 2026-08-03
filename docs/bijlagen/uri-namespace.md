# Bijlage B: Overzicht URI-namespaces

## GBO-Semantiek namespaces

| Prefix | Namespace | Beschrijving |
|--------|-----------|-------------|
| `gbo:` | `https://lod.gbo-semantiek.nl/` | Ontologie-definities van het kernmodel (klassen, eigenschappen) |
| `gbovz:` | `https://lod.gbo-semantiek.nl/voorzieningen/` | Ontologie-definities van het [voorzieningenmodel](../informatiemodel/gbo-voorzieningen.md) |
| `gbobegrip:` | `https://begrippen.gbo-semantiek.nl/id/begrip/` | Begrippenkader (SKOS concepten) |
| `mim:` | `https://lod.gbo-semantiek.nl/def/mim#` | GBO-lokale MIM-annotaties |
| `gboid:` | `https://lod.gbo-semantiek.nl/id/` | Instantie-identificaties |

Het kernmodel laat de ontologie-URI van een klasse samenvallen met de
begrip-URI (`class_uri: gbobegrip:...`). Het voorzieningenmodel houdt de twee
gescheiden: de klasse leeft in `gbovz:` en verwijst via `skos:exactMatch` naar
het begrip. Die tweede vorm is de bedoelde richting; het kernmodel volgt nog de
oudere conventie.

## Externe namespaces

| Prefix | Namespace | Standaard |
|--------|-----------|-----------|
| `owl:` | `http://www.w3.org/2002/07/owl#` | OWL |
| `rdf:` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` | RDF |
| `rdfs:` | `http://www.w3.org/2000/01/rdf-schema#` | RDF Schema |
| `skos:` | `http://www.w3.org/2004/02/skos/core#` | SKOS |
| `xsd:` | `http://www.w3.org/2001/XMLSchema#` | XML Schema Datatypes |
| `shacl:` | `http://www.w3.org/ns/shacl#` | SHACL |
| `dcat:` | `http://www.w3.org/ns/dcat#` | DCAT |
| `dcterms:` | `http://purl.org/dc/terms/` | Dublin Core Terms |

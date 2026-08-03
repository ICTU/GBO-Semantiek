#!/usr/bin/env python3
"""Genereer het GBO-begrippenkader als NL-SBB-compatibele SKOS-Turtle.

Bron zijn de `skos:`-annotaties op klassen en enums in de gekopieerde
LinkML-schema's. Dit is de Fase-2-route: de SKOS-semantiek staat in de
modelbron, niet meer in losse concept-pagina's, en de TTL wordt hier
gebouwd in plaats van in de wiki-repo.

Gebruik:
    genereer_begrippen.py --linkml-dir v0.3/informatiemodel/linkml \\
        --output v0.3/begrippen/GBO-Begrippenkader.ttl --versie v0.3
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, SKOS

ADMS = Namespace("http://www.w3.org/ns/adms#")
BEGRIP = Namespace("https://begrippen.gbo-semantiek.nl/id/begrip/")
SCHEME = URIRef("https://begrippen.gbo-semantiek.nl/id/conceptscheme/gbo-kern")

# Schema's die geen eigen begrippen dragen: het hoofdschema bundelt
# alleen imports, de profielen zijn meta-schema's.
OVERSLAAN = {"gbo", "bronprofiel", "clientprofiel"}

GELDIGE_STATUS = {"concept", "proposed", "accepted", "deprecated"}

ALT_LABEL_RE = re.compile(r"^skos:altLabel_([a-z]{2})_(\d+)_value$")
MATCH_RE = re.compile(r"^skos:(exactMatch|closeMatch|relatedMatch|broader|narrower)_(\d+)$")


def begrip_uri(element: dict) -> URIRef | None:
    """Leid de begrip-URI af.

    Twee conventies naast elkaar:

    - Het kernmodel laat de ontologie-URI samenvallen met de begrip-URI:
      `class_uri: gbobegrip:<Naam>`.
    - Het voorzieningenmodel heeft een eigen ontologie-namespace
      (`gbovz:`) en koppelt aan het begrip via `exact_mappings`.

    Enums kennen geen `enum_uri` en gebruiken in beide gevallen
    `exact_mappings`. Verwijzingen naar *andere* begrippen worden in de
    modelbron als volledige URI genoteerd, niet als CURIE, zodat de
    CURIE-vorm eenduidig het eigen begrip aanduidt.
    """
    eigen = element.get("class_uri")
    if isinstance(eigen, str) and eigen.startswith("gbobegrip:"):
        return BEGRIP[eigen.split(":", 1)[1]]
    for mapping in element.get("exact_mappings") or []:
        if isinstance(mapping, str) and mapping.startswith("gbobegrip:"):
            return BEGRIP[mapping.split(":", 1)[1]]
    return None


def annotatiewaarde(annotations: dict, sleutel: str):
    """LinkML normaliseert annotaties soms naar {'tag':..,'value':..}."""
    waarde = annotations.get(sleutel)
    if isinstance(waarde, dict):
        return waarde.get("value")
    return waarde


def emit_element(g: Graph, naam: str, element: dict, meldingen: list[str]) -> bool:
    annotations = element.get("annotations") or {}
    annotations = {
        k: annotatiewaarde(annotations, k) for k in annotations
    }
    if not any(k.startswith("skos:") for k in annotations):
        return False

    uri = begrip_uri(element)
    if uri is None:
        meldingen.append(f"{naam}: skos-annotaties zonder gbobegrip-mapping, overgeslagen.")
        return False

    g.add((uri, RDF.type, SKOS.Concept))
    g.add((uri, SKOS.inScheme, SCHEME))

    status = annotations.get("skos:status") or "concept"
    if status not in GELDIGE_STATUS:
        meldingen.append(f"{naam}: status '{status}' is niet geldig.")
    g.add((uri, ADMS.status, Literal(status)))

    for taal in ("nl", "en"):
        if label := annotations.get(f"skos:prefLabel_{taal}"):
            g.add((uri, SKOS.prefLabel, Literal(label, lang=taal)))
        if definitie := annotations.get(f"skos:definition_{taal}"):
            g.add((uri, SKOS.definition, Literal(definitie, lang=taal)))
        if notitie := annotations.get(f"skos:scopeNote_{taal}"):
            g.add((uri, SKOS.scopeNote, Literal(notitie, lang=taal)))

    if bron := annotations.get("skos:definitionSource"):
        g.add((uri, DCTERMS.source, Literal(bron)))
    if bron_uri := annotations.get("skos:definitionSourceUri"):
        g.add((uri, DCTERMS.source, URIRef(bron_uri)))

    for sleutel, waarde in annotations.items():
        if (m := ALT_LABEL_RE.match(sleutel)) and waarde:
            g.add((uri, SKOS.altLabel, Literal(waarde, lang=m.group(1))))
        elif (m := MATCH_RE.match(sleutel)) and waarde:
            predicaat = getattr(SKOS, m.group(1))
            g.add((uri, predicaat, URIRef(waarde)))
        elif sleutel.startswith("skos:needsReview_") and waarde:
            meldingen.append(f"{naam}: {waarde}")

    if not annotations.get("skos:prefLabel_nl"):
        meldingen.append(f"{naam}: geen Nederlandse voorkeursterm.")
    if not annotations.get("skos:definition_nl"):
        meldingen.append(f"{naam}: geen Nederlandse definitie.")
    return True


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--linkml-dir", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--versie", required=True)
    args = p.parse_args()

    g = Graph()
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)
    g.bind("adms", ADMS)
    g.bind("owl", OWL)
    g.bind("gbobegrip", BEGRIP)

    g.add((SCHEME, RDF.type, SKOS.ConceptScheme))
    g.add((SCHEME, DCTERMS.title, Literal("GBO-begrippenkader", lang="nl")))
    g.add((SCHEME, DCTERMS.description, Literal(
        "Begrippenkader van de Gemeenschappelijke Bronontsluiting, "
        "gegenereerd uit de SKOS-annotaties in de LinkML-modelbron.",
        lang="nl")))
    g.add((SCHEME, OWL.versionInfo, Literal(args.versie)))

    meldingen: list[str] = []
    aantal = 0
    bestanden = 0
    for pad in sorted(args.linkml_dir.glob("*.yaml")):
        if pad.stem in OVERSLAAN:
            continue
        schema = yaml.safe_load(pad.read_text(encoding="utf-8")) or {}
        bestanden += 1
        for soort in ("classes", "enums"):
            for naam, element in (schema.get(soort) or {}).items():
                if isinstance(element, dict) and emit_element(g, naam, element, meldingen):
                    aantal += 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=str(args.output), format="turtle")

    print(f"Schema's gelezen: {bestanden}")
    print(f"Begrippen geserialiseerd: {aantal}")
    if meldingen:
        print(f"Aandachtspunten: {len(meldingen)}")
        for melding in meldingen[:15]:
            print(f"  - {melding}")
        if len(meldingen) > 15:
            print(f"  ... en nog {len(meldingen) - 15}")
    if aantal == 0:
        print("FOUT: geen begrippen gevonden.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

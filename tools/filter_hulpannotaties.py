#!/usr/bin/env python3
"""Verwijder de platte SKOS-hulpannotaties uit een LinkML-schema.

De modelbron draagt de SKOS-semantiek van een begrip als platte annotaties,
zoals `skos:prefLabel_nl`, `skos:altLabel_nl_0_source` en
`skos:needsReview_0`. Die codering is bedoeld voor `genereer_begrippen.py`,
dat er het begrippenkader uit bouwt.

`gen-owl` neemt elke annotatie letterlijk over als tripel. Zonder dit filter
krijgt de ontologie daardoor eigenschappen in de SKOS-namespace die in SKOS
niet bestaan, en komen interne werknotities en bronverwijzingen uit de
wiki-repo in de publicatie terecht. Wat de annotaties betekenen staat al in
het begrippenkader, in de vorm die SKOS voorschrijft.

Dit script haalt ze uit de werkkopie die naar gen-owl en gen-shacl gaat; de
modelbron zelf blijft ongewijzigd. Annotaties met een bestaande
SKOS-eigenschap als sleutel, zoals `skos:notation`, blijven staan, net als
alle annotaties buiten de SKOS-namespace (`mim:`, `gbo:`).

Gebruik (op de werkkopie, in-place):
    python3 tools/filter_hulpannotaties.py personen.yaml --in-place
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

# De eigenschappen die SKOS zelf definieert. Een annotatie met een andere
# sleutel onder `skos:` is een hulpannotatie van de modelbron.
SKOS_EIGENSCHAPPEN = {
    "prefLabel", "altLabel", "hiddenLabel", "notation",
    "definition", "scopeNote", "note", "example",
    "historyNote", "editorialNote", "changeNote",
    "broader", "narrower", "related",
    "broaderTransitive", "narrowerTransitive", "semanticRelation",
    "exactMatch", "closeMatch", "broadMatch", "narrowMatch", "relatedMatch",
    "mappingRelation", "inScheme", "topConceptOf", "hasTopConcept",
    "member", "memberList",
}


def is_hulpannotatie(sleutel) -> bool:
    tekst = str(sleutel)
    return tekst.startswith("skos:") and tekst[len("skos:"):] not in SKOS_EIGENSCHAPPEN


def filter_annotaties(knoop) -> int:
    """Loop het hele schema door en verwijder hulpannotaties op elk niveau:
    klassen, attributen, slots, enums en hun waarden. Geeft het aantal
    verwijderde annotaties terug."""
    verwijderd = 0
    if isinstance(knoop, dict):
        annotaties = knoop.get("annotations")
        if isinstance(annotaties, dict):
            for sleutel in [s for s in annotaties if is_hulpannotatie(s)]:
                del annotaties[sleutel]
                verwijderd += 1
            if not annotaties:
                del knoop["annotations"]
        for sleutel, waarde in knoop.items():
            if sleutel != "annotations":
                verwijderd += filter_annotaties(waarde)
    elif isinstance(knoop, list):
        for waarde in knoop:
            verwijderd += filter_annotaties(waarde)
    return verwijderd


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("schema", type=Path, help="LinkML-schemabestand")
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="uitvoerbestand (default: stdout)")
    ap.add_argument("--in-place", action="store_true",
                    help="schrijf terug naar het invoerbestand")
    args = ap.parse_args()

    schema = yaml.safe_load(args.schema.read_text(encoding="utf-8")) or {}
    aantal = filter_annotaties(schema)

    tekst = yaml.dump(schema, sort_keys=False, allow_unicode=True)
    if args.in_place:
        args.schema.write_text(tekst, encoding="utf-8")
    elif args.output:
        args.output.write_text(tekst, encoding="utf-8")
    else:
        sys.stdout.write(tekst)
    print(f"{args.schema.name}: {aantal} hulpannotaties verwijderd",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

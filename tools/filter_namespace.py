#!/usr/bin/env python3
"""Beperk een gegenereerde TTL tot de elementen die een schema zelf declareert.

`gen-owl` en `gen-shacl` nemen alle geimporteerde schema's mee. Voor een
model met een eigen namespace levert dat twee problemen op: de kern wordt
gedupliceerd, en geimporteerde elementen zonder expliciete URI krijgen de
namespace van het importerende schema toegewezen.

Dit script leest het bronschema, verzamelt de namen die daar zelf in
staan (klassen, enums en hun attributen) en houdt alleen de tripels over
waarvan het subject bij een van die elementen hoort.

Gebruik:
    filter_namespace.py --schema voorzieningen.yaml \\
        --namespace https://lod.gbo-semantiek.nl/voorzieningen \\
        --input volledig.ttl --output GBO-Voorzieningen.ttl
"""
from __future__ import annotations

import argparse

import yaml
from rdflib import BNode, Graph, URIRef


def gedeclareerd(schema_pad) -> tuple[set[str], set[str]]:
    """Geef (alle elementnamen, klassenamen) uit het schema zelf."""
    schema = yaml.safe_load(open(schema_pad, encoding="utf-8")) or {}
    klassen = set((schema.get("classes") or {}).keys())
    namen = set(klassen) | set((schema.get("enums") or {}).keys())
    namen |= set((schema.get("slots") or {}).keys())
    for definitie in (schema.get("classes") or {}).values():
        if isinstance(definitie, dict):
            namen |= set((definitie.get("attributes") or {}).keys())
    return {n.lower() for n in namen}, {k.lower() for k in klassen}


def hoort_erbij(subject, namespace: str, namen: set[str], klassen: set[str]) -> bool:
    if not isinstance(subject, URIRef):
        return False
    uri = str(subject)
    if uri == namespace:  # de ontologie-declaratie zelf
        return True
    prefix = namespace.rstrip("/") + "/"
    if not uri.startswith(prefix):
        return False
    # Enum-URI's worden kleingeschreven gegenereerd (KOZStatus -> kozstatus),
    # vandaar de ongevoelige vergelijking. Waarde-URI's van een enumeratie
    # hangen als fragment aan die URI: <enum>#<waarde>.
    rest = uri[len(prefix):].split("#", 1)[0].lower()
    if rest in namen:
        return True
    # Gekwalificeerde attribuut-URI's: <Klasse>/<attribuut>
    return rest.split("/", 1)[0] in klassen


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--schema", required=True)
    p.add_argument("--namespace", required=True)
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    namen, klassen = gedeclareerd(args.schema)

    bron = Graph()
    bron.parse(args.input, format="turtle")

    doel = Graph()
    for prefix, uri in bron.namespaces():
        doel.bind(prefix, uri)

    for triple in bron:
        if hoort_erbij(triple[0], args.namespace, namen, klassen):
            doel.add(triple)

    # Blank-node-sluiting. De inhoud van een klasse-axioma zit in anonieme
    # knopen: owl:Restriction bij de ontologie, sh:property bij de shapes,
    # plus de RDF-lijsten van owl:unionOf en sh:ignoredProperties. Die hebben
    # een BNode als subject en vallen dus buiten de namespace-toets. Zonder
    # deze stap blijven alleen de verwijzingen over en verdwijnen de
    # constraints, wat een leeg ogend maar formeel geldig artefact oplevert.
    grens = {o for _, _, o in doel if isinstance(o, BNode)}
    gezien: set[BNode] = set()
    while grens:
        knoop = grens.pop()
        if knoop in gezien:
            continue
        gezien.add(knoop)
        for predicaat, obj in bron.predicate_objects(knoop):
            doel.add((knoop, predicaat, obj))
            if isinstance(obj, BNode):
                grens.add(obj)

    doel.serialize(destination=args.output, format="turtle")
    print(f"Tripels behouden: {len(doel)} van {len(bron)} "
          f"(waarvan {len(gezien)} anonieme knopen meegenomen)")
    print(f"Elementen in schema: {len(namen)} ({len(klassen)} klassen)")
    return 0 if len(doel) else 1


if __name__ == "__main__":
    raise SystemExit(main())

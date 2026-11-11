#!/usr/bin/env python3
"""Genereer het GBO-begrippenkader als NL-SBB-compatibele SKOS-Turtle.

Bron zijn de `skos:`-annotaties en de mapping-slots op klassen en enums in
de gekopieerde LinkML-schema's. Dit is de Fase-2-route: de SKOS-semantiek
staat in de modelbron, niet meer in losse concept-pagina's, en de TTL wordt
hier gebouwd in plaats van in de wiki-repo.

De modelbron gebruikt de hybride codering uit de wiki-repo
(`scripts/migrate-skos-to-linkml.py`):

- platte annotaties `skos:status`, `skos:prefLabel_<taal>`,
  `skos:definition_<taal>`, `skos:altLabel_<taal>_<n>_value`;
- `skos:additional_<n>_as|nl|en` voor toelichtingen (`scopeNote`) en extra
  definities (`definition`);
- bronvermeldingen in `skos:definitionSource`, `skos:definitionSourceUri`,
  `skos:altLabel_<taal>_<n>_source` en `skos:additional_<n>_source`; ze
  worden `dcterms:source` op het begrip. Een bron die naar de interne wiki
  verwijst (`[[...]]`) wordt niet gepubliceerd en als aandachtspunt gemeld;
- de mapping-slots van LinkML voor relaties tussen begrippen:
  `broad_mappings` (skos:broader), `narrow_mappings` (skos:narrower),
  `close_mappings` (skos:closeMatch), `related_mappings`
  (skos:relatedMatch) en `exact_mappings` (skos:exactMatch, behalve de
  verwijzing naar het eigen begrip).

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
ALT_SOURCE_RE = re.compile(r"^skos:altLabel_([a-z]{2})_(\d+)_source$")
ADDITIONAL_RE = re.compile(r"^skos:additional_(\d+)_(as|nl|en|source)$")
REVIEWED_RE = re.compile(r"^skos:(exactMatch|closeMatch|relatedMatch|broader|narrower)_(\d+)_reviewed$")

# Mapping-slots van LinkML en het SKOS-predicaat dat de modelbron ermee
# bedoelt. De hiërarchie en de matches staan in deze slots, niet in
# annotaties; de sleutel is de naam die de `_reviewed`-annotaties gebruiken.
MAPPING_SLOTS = {
    "broader": ("broad_mappings", SKOS.broader),
    "narrower": ("narrow_mappings", SKOS.narrower),
    "exactMatch": ("exact_mappings", SKOS.exactMatch),
    "closeMatch": ("close_mappings", SKOS.closeMatch),
    "relatedMatch": ("related_mappings", SKOS.relatedMatch),
}
RELATIES = tuple(predicaat for _, predicaat in MAPPING_SLOTS.values())


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


def verwijzing(waarde, prefixes: dict) -> URIRef | None:
    """Zet een mapping-waarde om naar een URI: een volledige URI of een CURIE."""
    tekst = str(waarde)
    if tekst.startswith(("http://", "https://")):
        return URIRef(tekst)
    prefix, scheiding, lokaal = tekst.partition(":")
    if not scheiding:
        return None
    if prefix == "gbobegrip":
        return BEGRIP[lokaal]
    basis = prefixes.get(prefix)
    if isinstance(basis, dict):
        basis = basis.get("prefix_reference")
    return URIRef(f"{basis}{lokaal}") if basis else None


def relaties(element: dict, eigen: URIRef, prefixes: dict,
             naam: str, meldingen: list[str]) -> dict[str, list[URIRef]]:
    """Lees de mapping-slots als relaties van het begrip.

    Modellen met een eigen ontologie-namespace noteren ook het eigen begrip
    in `exact_mappings`; dat is identiteit en geen exactMatch, en valt hier
    dus weg.
    """
    gevonden: dict[str, list[URIRef]] = {}
    for sleutel, (slot, _) in MAPPING_SLOTS.items():
        for waarde in element.get(slot) or []:
            doel = verwijzing(waarde, prefixes)
            if doel is None:
                meldingen.append(
                    f"{naam}: waarde '{waarde}' in {slot} is geen URI of bekende CURIE, overgeslagen.")
            elif doel != eigen:
                gevonden.setdefault(sleutel, []).append(doel)
    return gevonden


def annotatiewaarde(annotations: dict, sleutel: str):
    """LinkML normaliseert annotaties soms naar {'tag':..,'value':..}."""
    waarde = annotations.get(sleutel)
    if isinstance(waarde, dict):
        return waarde.get("value")
    return waarde


def bronvermelding(g: Graph, uri: URIRef, waarde, naam: str, meldingen: list[str]) -> None:
    """Schrijf een bronvermelding als `dcterms:source` op het begrip.

    De modelbron verwijst soms naar een pagina in de interne wiki
    (`[[...]]`). Zo'n verwijzing is buiten de wiki niet te volgen en hoort
    niet in de publicatie; ze wordt gemeld in plaats van geschreven.
    """
    tekst = str(waarde).strip()
    if not tekst:
        return
    if "[[" in tekst:
        meldingen.append(
            f"{naam}: bron '{tekst}' verwijst naar de interne wiki en is niet gepubliceerd.")
        return
    g.add((uri, DCTERMS.source, Literal(tekst)))


def emit_element(g: Graph, naam: str, element: dict, meldingen: list[str],
                 prefixes: dict | None = None) -> bool:
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
        bronvermelding(g, uri, bron, naam, meldingen)
    if bron_uri := annotations.get("skos:definitionSourceUri"):
        g.add((uri, DCTERMS.source, URIRef(bron_uri)))

    for sleutel, waarde in annotations.items():
        if (m := ALT_LABEL_RE.match(sleutel)) and waarde:
            g.add((uri, SKOS.altLabel, Literal(waarde, lang=m.group(1))))
        elif ALT_SOURCE_RE.match(sleutel) and waarde:
            bronvermelding(g, uri, waarde, naam, meldingen)
        elif (m := MATCH_RE.match(sleutel)) and waarde:
            predicaat = getattr(SKOS, m.group(1))
            g.add((uri, predicaat, URIRef(waarde)))
        elif sleutel.startswith("skos:needsReview_") and waarde:
            meldingen.append(f"{naam}: {waarde}")

    # Toelichtingen en extra definities: per volgnummer een soort en een
    # tekst per taal.
    aanvullend: dict[int, dict] = {}
    for sleutel, waarde in annotations.items():
        if (m := ADDITIONAL_RE.match(sleutel)) and waarde:
            aanvullend.setdefault(int(m.group(1)), {})[m.group(2)] = waarde
    for _, deel in sorted(aanvullend.items()):
        predicaat = SKOS.definition if deel.get("as") == "definition" else SKOS.scopeNote
        for taal in ("nl", "en"):
            if tekst := deel.get(taal):
                g.add((uri, predicaat, Literal(tekst, lang=taal)))
        if bron := deel.get("source"):
            bronvermelding(g, uri, bron, naam, meldingen)

    # Hiërarchie en matches uit de mapping-slots.
    gevonden = relaties(element, uri, prefixes or {}, naam, meldingen)
    for sleutel, doelen in gevonden.items():
        for doel in doelen:
            g.add((uri, MAPPING_SLOTS[sleutel][1], doel))
    for sleutel, waarde in annotations.items():
        if (m := REVIEWED_RE.match(sleutel)) and str(waarde).lower() == "false":
            doelen = gevonden.get(m.group(1)) or []
            index = int(m.group(2))
            doel = doelen[index] if index < len(doelen) else "onbekend"
            meldingen.append(f"{naam}: {m.group(1)} naar {doel} is nog niet beoordeeld.")

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
        prefixes = schema.get("prefixes") or {}
        for soort in ("classes", "enums"):
            for naam, element in (schema.get(soort) or {}).items():
                if isinstance(element, dict) and emit_element(g, naam, element, meldingen, prefixes):
                    aantal += 1

    # Een relatie naar een GBO-begrip dat zelf niet in het kader staat, is een
    # losse verwijzing: het doel heeft dan nog geen skos-annotaties in het model.
    begrippen = set(g.subjects(RDF.type, SKOS.Concept))
    los: dict[URIRef, int] = {}
    for predicaat in RELATIES:
        for _, doel in g.subject_objects(predicaat):
            if str(doel).startswith(str(BEGRIP)) and doel not in begrippen:
                los[doel] = los.get(doel, 0) + 1
    # Vooraan in de lijst: de uitvoer toont alleen de eerste meldingen.
    meldingen[:0] = [
        f"{str(doel).rsplit('/', 1)[-1]}: {keren} relatie(s) verwijzen naar dit begrip, "
        "maar het staat niet in het begrippenkader."
        for doel, keren in sorted(los.items())
    ]

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

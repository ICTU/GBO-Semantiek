#!/usr/bin/env python3
"""Genereer een Markdown-changelog tussen twee versies van het GBO LinkML-model.

Vervangt de oude crunch_uml-diff (`-t diff_md`). Vergelijkt klassen, enums en
attributen (gemerged over imports) tussen de vorige en de huidige
LinkML-versie en schrijft een Markdown-overzicht.

Gebruik:
    python tools/genereer_changelog.py \
        --previous v0.1/informatiemodel/linkml/gbo.yaml --previous-version v0.1 \
        --current  v0.2/informatiemodel/linkml/gbo.yaml --current-version  v0.2 \
        --output   v0.2/GBO_Changes.md

Als de vorige versie geen LinkML-model heeft, wordt een nette notitie
geschreven in plaats van een diff (exit 0).
"""
from __future__ import annotations

import argparse
from pathlib import Path


def _view(path: str):
    from linkml_runtime import SchemaView

    return SchemaView(path)


def _collect(sv, alleen_eigen: bool = False):
    """Verzamel klassen, enums en directe attributen per klasse.

    Met alleen_eigen blijven de geimporteerde elementen buiten beschouwing.
    Nodig voor een model naast de kern (voorzieningen, toestemmingen): dat
    importeert gbo.yaml, dus zonder filter zou het hele kernmodel als
    toegevoegd in de changelog belanden. Voor gbo.yaml zelf moet het filter
    juist uit blijven: dat schema declareert niets en bundelt alleen.
    """
    imports = not alleen_eigen
    classes = set(sv.all_classes(imports=imports).keys())
    enums = set(sv.all_enums(imports=imports).keys())
    class_attrs: dict[str, set[str]] = {}
    for cname in classes:
        try:
            class_attrs[cname] = set(sv.class_slots(cname, direct=True))
        except Exception:
            class_attrs[cname] = set()
    return classes, enums, class_attrs


def _section(titel: str, items) -> list[str]:
    items = sorted(items)
    if not items:
        return []
    out = [f"### {titel}", ""]
    out += [f"- `{i}`" for i in items]
    out += [""]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--previous", required=True)
    ap.add_argument("--previous-version", required=True)
    ap.add_argument("--current", required=True)
    ap.add_argument("--current-version", required=True)
    ap.add_argument("--output", required=True)
    # Een versie bevat meer dan een schema: naast het kernmodel staan het
    # voorzieningen- en het toestemmingenmodel, die gbo.yaml niet importeert
    # en die dus onzichtbaar blijven in een diff op gbo.yaml alleen. Met
    # --model krijgt elk schema een eigen sectie; met --append schrijven de
    # volgende aanroepen in hetzelfde bestand verder.
    ap.add_argument("--model", default=None,
                    help="Kop van de sectie voor dit schema, bijvoorbeeld "
                         "Kernmodel. Zonder deze optie krijgt het bestand "
                         "alleen de versiekop.")
    ap.add_argument("--alleen-eigen", action="store_true",
                    help="Vergelijk alleen wat het schema zelf declareert, "
                         "zonder geimporteerde elementen. Gebruik dit voor "
                         "een model naast de kern; niet voor gbo.yaml.")
    ap.add_argument("--append", action="store_true",
                    help="Voeg toe aan een bestaand changelog-bestand in "
                         "plaats van het te overschrijven; onderdrukt de "
                         "versiekop.")
    args = ap.parse_args()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    if not args.append:
        lines += [f"# Wijzigingen {args.previous_version} → {args.current_version}", ""]
    if args.model:
        lines += [f"## {args.model}", ""]
    kop_regels = len(lines)

    if Path(args.previous).is_file():
        prev_classes, prev_enums, prev_attrs = _collect(
            _view(args.previous), args.alleen_eigen)
    else:
        # Nieuw schema in deze versie: alles telt als toegevoegd. Dat is
        # informatiever dan melden dat er niets te vergelijken viel.
        prev_classes, prev_enums, prev_attrs = set(), set(), {}
        lines += [f"Nieuw in {args.current_version}; er is geen voorganger in "
                  f"{args.previous_version} om mee te vergelijken.", ""]
        kop_regels = len(lines)

    cur_classes, cur_enums, cur_attrs = _collect(
        _view(args.current), args.alleen_eigen)

    lines += _section("Toegevoegde objecttypen", cur_classes - prev_classes)
    lines += _section("Verwijderde objecttypen", prev_classes - cur_classes)
    lines += _section("Toegevoegde codelijsten/enumeraties", cur_enums - prev_enums)
    lines += _section("Verwijderde codelijsten/enumeraties", prev_enums - cur_enums)

    # Gewijzigde attributen per gedeeld objecttype.
    gewijzigd: list[str] = []
    for cname in sorted(cur_classes & prev_classes):
        toegevoegd = cur_attrs.get(cname, set()) - prev_attrs.get(cname, set())
        verwijderd = prev_attrs.get(cname, set()) - cur_attrs.get(cname, set())
        if toegevoegd or verwijderd:
            gewijzigd.append(f"**{cname}**")
            for a in sorted(toegevoegd):
                gewijzigd.append(f"  - + `{a}`")
            for a in sorted(verwijderd):
                gewijzigd.append(f"  - − `{a}`")
    if gewijzigd:
        lines += ["### Gewijzigde objecttypen (attributen)", ""]
        lines += gewijzigd
        lines += [""]

    if len(lines) <= kop_regels:
        lines += ["_Geen structurele wijzigingen gedetecteerd._", ""]

    tekst = "\n".join(lines).rstrip("\n") + "\n"
    if args.append:
        with out_path.open("a", encoding="utf-8") as f:
            f.write("\n" + tekst)
    else:
        out_path.write_text(tekst, encoding="utf-8")
    print(f"Changelog geschreven naar {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

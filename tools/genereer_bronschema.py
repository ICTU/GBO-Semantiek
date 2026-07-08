#!/usr/bin/env python3
"""Genereer een gematerialiseerd per-bron LinkML-schema uit een bron-profiel.

Een bron-profiel (LinkML-data conform bronprofiel.yaml, zie
v0.2/informatiemodel/linkml/bronprofiel.yaml) beschrijft welke
onderdelen van het GBO-informatiemodel één bron beschikbaar stelt.
Dit script materialiseert daaruit een zelfstandig LinkML-schema
waarop de standaard-generatoren (gen-graphql, gen-owl, ...) draaien.

Regels:
- Supertypen en mixins van geselecteerde objecttypen worden
  automatisch meegenomen (overerving); subtypen niet.
- Gestructureerde datatypes (klassen met annotatie
  mim:stereotype: DataType, zoals Bedrag) worden automatisch
  meegenomen wanneer een attribuut ernaar verwijst.
- Relaties naar objecttypen buiten het profiel worden default
  vervangen door de identificerende sleutel van het doelobject
  (afhandeling "sleutel"); met afhandeling "weglaten" vervalt de
  relatie geheel; met afhandeling "vernauwen" (veld "naar") wordt de
  range vernauwd naar een subtype dat wél in het profiel staat.
- Uitsluitingen gelden op het objecttype waar het attribuut is
  gedeclareerd; geërfde attributen kunnen niet per subtype worden
  uitgesloten (LinkML-beperking).
- Insluitingen (whitelist) werken op eigen én geërfde attributen; de
  overerving wordt daarbij uitgevlakt (is_a/mixins vervallen en
  supertypen worden niet automatisch meegenomen).
- Relaties met de annotatie gbo:inverseNaam krijgen op het doelobject
  een gematerialiseerde inverse (multivalued), zodat de SDL-navigatie
  ook van doel naar bron kan lopen.

Gebruik:
    python3 tools/genereer_bronschema.py v0.2/bronnen/brp.yaml \
        [-o build/brp-schema.yaml]

Zonder -o gaat het resultaat naar stdout; meldingen gaan naar stderr.
"""

import argparse
import copy
import sys
from pathlib import Path

import yaml

AFHANDELING_SLEUTEL = "sleutel"
AFHANDELING_WEGLATEN = "weglaten"
AFHANDELING_VERNAUWEN = "vernauwen"
DATATYPE_STEREOTYPE = "DataType"


def melding(soort: str, tekst: str) -> None:
    print(f"{soort}: {tekst}", file=sys.stderr)


def fout(tekst: str) -> None:
    melding("FOUT", tekst)
    sys.exit(1)


def laad_yaml(pad: Path) -> dict:
    try:
        with open(pad, encoding="utf-8") as f:
            inhoud = yaml.safe_load(f)
    except FileNotFoundError:
        fout(f"bestand niet gevonden: {pad}")
    except yaml.YAMLError as e:
        fout(f"ongeldige YAML in {pad}: {e}")
    if not isinstance(inhoud, dict):
        fout(f"{pad} bevat geen YAML-mapping")
    return inhoud


class Modelindex:
    """Index over de raw YAML van het hoofdschema en zijn imports."""

    def __init__(self, hoofdschema: Path):
        self.hoofdschema = hoofdschema
        self.raw = laad_yaml(hoofdschema)
        self.classes: dict[str, dict] = {}
        self.enums: dict[str, dict] = {}
        self.types: dict[str, dict] = {}
        self.herkomst: dict[str, str] = {}  # elementnaam -> bestandsnaam

        bestanden = [hoofdschema]
        for imp in self.raw.get("imports", []):
            if ":" in imp:  # linkml:types en andere externe imports
                continue
            bestanden.append(hoofdschema.parent / f"{imp}.yaml")

        for pad in bestanden:
            deel = laad_yaml(pad) if pad != hoofdschema else self.raw
            for sectie, index in (("classes", self.classes),
                                  ("enums", self.enums),
                                  ("types", self.types)):
                for naam, definitie in (deel.get(sectie) or {}).items():
                    if naam in index:
                        fout(f"element '{naam}' is dubbel gedefinieerd "
                             f"({self.herkomst[naam]} en {pad.name})")
                    index[naam] = definitie or {}
                    self.herkomst[naam] = pad.name

    # -- hiërarchie-hulpfuncties (overerving) --------------------------------

    def voorouders(self, klasse: str) -> list[str]:
        """is_a-keten plus mixins, recursief, exclusief de klasse zelf."""
        resultaat: list[str] = []
        stapel = [klasse]
        gezien = {klasse}
        while stapel:
            huidige = self.classes.get(stapel.pop(0), {})
            ouders = []
            if huidige.get("is_a"):
                ouders.append(huidige["is_a"])
            ouders.extend(huidige.get("mixins") or [])
            for ouder in ouders:
                if ouder not in self.classes:
                    fout(f"superklasse of mixin '{ouder}' bestaat niet in "
                         f"het informatiemodel")
                if ouder not in gezien:
                    gezien.add(ouder)
                    resultaat.append(ouder)
                    stapel.append(ouder)
        return resultaat

    def afstammelingen(self, klasse: str) -> list[str]:
        directe = [n for n, d in self.classes.items()
                   if d.get("is_a") == klasse]
        alle = list(directe)
        for sub in directe:
            alle.extend(self.afstammelingen(sub))
        return alle

    def is_datatype_klasse(self, klasse: str) -> bool:
        annotaties = self.classes.get(klasse, {}).get("annotations") or {}
        return annotaties.get("mim:stereotype") == DATATYPE_STEREOTYPE

    def identifier_slot(self, klasse: str) -> tuple[str, str] | None:
        """(slotnaam, range) van de identifier, eigen of geërfd."""
        for kandidaat in [klasse] + self.voorouders(klasse):
            for naam, attr in (self.classes[kandidaat].get("attributes")
                               or {}).items():
                if (attr or {}).get("identifier"):
                    return naam, (attr or {}).get("range", "string")
        return None

    def sleutel_slot(self, klasse: str) -> tuple[str, str] | None:
        """Natuurlijke sleutel voor een sleutel-referentie.

        Zelfde prioriteit als de zoeksleutel van de Query-ingangen in
        genereer_graphql: (1) een eigen identifier op de klasse zelf;
        anders (2) een enkelvoudige unique_key (eigen of geërfd) als
        natuurlijke sleutel, zo krijgt een verwijzing naar
        NietNatuurlijkPersoon de rsin in plaats van de geërfde
        technische id; anders (3) de geërfde identifier."""
        for naam, attr in self.eigen_attributen(klasse).items():
            if (attr or {}).get("identifier"):
                return naam, (attr or {}).get("range", "string")
        induced = self.induced_attributen(klasse)
        for kandidaat in [klasse] + self.voorouders(klasse):
            for uk in ((self.classes.get(kandidaat) or {})
                       .get("unique_keys") or {}).values():
                slots = uk.get("unique_key_slots") or []
                if len(slots) == 1 and slots[0] in induced:
                    attr = induced[slots[0]] or {}
                    return slots[0], attr.get("range", "string")
        return self.identifier_slot(klasse)

    def eigen_attributen(self, klasse: str) -> dict:
        return self.classes.get(klasse, {}).get("attributes") or {}

    def induced_attributen(self, klasse: str) -> dict:
        """Eigen plus geërfde attributen; eigen definitie wint."""
        resultaat: dict[str, dict] = {}
        for voorouder in reversed(self.voorouders(klasse)):
            resultaat.update(self.eigen_attributen(voorouder))
        resultaat.update(self.eigen_attributen(klasse))
        return resultaat


def valideer_profiel(profiel: dict, index: Modelindex) -> None:
    for veld in ("bron", "titel", "schemabestand", "ingangen",
                 "objecttypen"):
        if not profiel.get(veld):
            fout(f"verplicht profielveld '{veld}' ontbreekt of is leeg")

    onbekend = [c for c in profiel["objecttypen"]
                if c not in index.classes]
    if onbekend:
        fout(f"objecttype(n) niet gevonden in het informatiemodel: "
             f"{', '.join(onbekend)}")

    buiten = [c for c in profiel["ingangen"]
              if c not in profiel["objecttypen"]]
    if buiten:
        fout(f"ingang(en) staan niet in objecttypen: {', '.join(buiten)}")

    for uitsluiting in profiel.get("uitsluitingen") or []:
        klasse = uitsluiting.get("objecttype")
        if klasse not in profiel["objecttypen"]:
            fout(f"uitsluiting verwijst naar objecttype '{klasse}' dat "
                 f"niet in het profiel staat")
        eigen = index.eigen_attributen(klasse)
        for attr in uitsluiting.get("attributen") or []:
            if attr in eigen:
                continue
            # Geërfd attribuut? Leg uit waarom dat niet kan.
            for ouder in index.voorouders(klasse):
                if attr in index.eigen_attributen(ouder):
                    fout(f"uitsluiting '{klasse}.{attr}': attribuut is "
                         f"gedeclareerd op '{ouder}'; een geërfd "
                         f"attribuut kan niet per subtype worden "
                         f"uitgesloten — sluit het uit op '{ouder}' of "
                         f"laat de hele klasse weg")
            fout(f"uitsluiting '{klasse}.{attr}': attribuut bestaat niet")

    uitgesloten_typen = {u.get("objecttype")
                         for u in profiel.get("uitsluitingen") or []}
    for insluiting in profiel.get("insluitingen") or []:
        klasse = insluiting.get("objecttype")
        if klasse not in profiel["objecttypen"]:
            fout(f"insluiting verwijst naar objecttype '{klasse}' dat "
                 f"niet in het profiel staat")
        if klasse in uitgesloten_typen:
            fout(f"objecttype '{klasse}' staat in insluitingen én "
                 f"uitsluitingen; kies één mechanisme")
        induced = index.induced_attributen(klasse)
        for attr in insluiting.get("attributen") or []:
            if attr not in induced:
                fout(f"insluiting '{klasse}.{attr}': attribuut bestaat "
                     f"niet (eigen noch geërfd)")

    for regel in profiel.get("relatieAfhandeling") or []:
        klasse = regel.get("objecttype")
        relatie = regel.get("relatie")
        wijze = regel.get("afhandeling")
        if klasse not in profiel["objecttypen"]:
            fout(f"relatieAfhandeling verwijst naar objecttype "
                 f"'{klasse}' dat niet in het profiel staat")
        if relatie not in index.eigen_attributen(klasse):
            fout(f"relatieAfhandeling '{klasse}.{relatie}': relatie "
                 f"bestaat niet op dit objecttype")
        if wijze not in (AFHANDELING_SLEUTEL, AFHANDELING_WEGLATEN,
                         AFHANDELING_VERNAUWEN):
            fout(f"relatieAfhandeling '{klasse}.{relatie}': onbekende "
                 f"afhandeling '{wijze}'")
        if wijze == AFHANDELING_VERNAUWEN:
            naar = regel.get("naar")
            doel = (index.eigen_attributen(klasse).get(relatie)
                    or {}).get("range")
            if not naar:
                fout(f"relatieAfhandeling '{klasse}.{relatie}': "
                     f"afhandeling 'vernauwen' vereist het veld 'naar'")
            if naar not in profiel["objecttypen"]:
                fout(f"relatieAfhandeling '{klasse}.{relatie}': "
                     f"'naar: {naar}' staat niet in objecttypen")
            if naar != doel and naar not in index.afstammelingen(doel):
                fout(f"relatieAfhandeling '{klasse}.{relatie}': "
                     f"'{naar}' is geen subtype van '{doel}'")


def bepaal_selectie(profiel: dict, index: Modelindex) -> list[str]:
    """Objecttypen plus automatisch meegenomen voorouders en mixins.

    Objecttypen met een insluiting (whitelist) worden uitgevlakt: hun
    geërfde attributen materialiseren op het objecttype zelf, dus hun
    supertypen en mixins worden niet meegenomen."""
    ingesloten = {i["objecttype"]
                  for i in profiel.get("insluitingen") or []}
    selectie: list[str] = []
    for klasse in profiel["objecttypen"]:
        if klasse not in selectie:
            selectie.append(klasse)
    for klasse in list(selectie):
        if klasse in ingesloten:
            melding("INFO", f"insluiting op '{klasse}': overerving "
                            f"uitgevlakt, supertypen niet meegenomen")
            continue
        for ouder in index.voorouders(klasse):
            if ouder not in selectie:
                selectie.append(ouder)
                melding("INFO", f"supertype/mixin '{ouder}' automatisch "
                                f"meegenomen (overerving)")
    return selectie


def verwerk_klassen(profiel: dict, index: Modelindex,
                    selectie: list[str]) -> dict[str, dict]:
    """Snoei en transformeer de geselecteerde klassen."""
    uitsluitingen = {(u["objecttype"], a)
                     for u in profiel.get("uitsluitingen") or []
                     for a in u.get("attributen") or []}
    afhandeling = {(r["objecttype"], r["relatie"]): r
                   for r in profiel.get("relatieAfhandeling") or []}
    insluitingen = {i["objecttype"]: set(i.get("attributen") or [])
                    for i in profiel.get("insluitingen") or []}

    resultaat: dict[str, dict] = {}
    wachtrij = list(selectie)
    while wachtrij:
        klasse = wachtrij.pop(0)
        if klasse in resultaat:
            continue
        definitie = copy.deepcopy(index.classes[klasse])
        if klasse in insluitingen:
            # Overerving uitvlakken: geërfde attributen materialiseren
            # op de klasse zelf; de is_a/mixins-koppeling vervalt.
            attributen = copy.deepcopy(index.induced_attributen(klasse))
            definitie.pop("is_a", None)
            definitie.pop("mixins", None)
        else:
            attributen = definitie.get("attributes") or {}
        nieuwe_attributen = {}

        for naam, attr in attributen.items():
            attr = attr or {}
            if klasse in insluitingen \
                    and naam not in insluitingen[klasse]:
                continue
            if (klasse, naam) in uitsluitingen:
                melding("INFO", f"uitgesloten: {klasse}.{naam}")
                continue
            doel = attr.get("range")
            regel = afhandeling.get((klasse, naam))
            if regel and regel["afhandeling"] == AFHANDELING_VERNAUWEN:
                attr["range"] = regel["naar"]
                attr.setdefault("comments", []).append(
                    f"Range vernauwd van {doel} naar {regel['naar']} "
                    f"binnen dit bronprofiel (populatie-beperking).")
                melding("INFO", f"vernauwd: {klasse}.{naam}: "
                                f"{doel} -> {regel['naar']}")
                doel = regel["naar"]
            if doel in index.classes and doel not in selectie:
                if index.is_datatype_klasse(doel):
                    # Gestructureerd datatype: automatisch meenemen.
                    if doel not in resultaat and doel not in wachtrij:
                        wachtrij.append(doel)
                        selectie.append(doel)
                        melding("INFO", f"gestructureerd datatype "
                                        f"'{doel}' automatisch meegenomen")
                elif (regel or {}).get("afhandeling",
                                       AFHANDELING_SLEUTEL) \
                        == AFHANDELING_WEGLATEN:
                    melding("INFO", f"weggelaten relatie: {klasse}.{naam} "
                                    f"-> {doel}")
                    continue
                else:
                    ident = index.sleutel_slot(doel)
                    if ident is None:
                        melding("INFO",
                                f"{klasse}.{naam}: doelobjecttype "
                                f"'{doel}' heeft geen eigen identifier "
                                f"(navigatie-only); sleutel-referentie "
                                f"als Tekst")
                        slotnaam, slotrange = None, "Tekst"
                    else:
                        slotnaam, slotrange = ident
                    attr["range"] = slotrange
                    attr.setdefault("annotations", {})
                    attr["annotations"]["gbo:sleutelreferentie"] = doel
                    attr.setdefault("comments", []).append(
                        f"Sleutel-referentie naar {doel}"
                        + (f".{slotnaam}" if slotnaam else "")
                        + " (doelobjecttype buiten dit bronprofiel).")
                    melding("INFO", f"sleutel-referentie: {klasse}.{naam} "
                                    f"-> {doel}"
                                    + (f".{slotnaam}" if slotnaam else ""))
            nieuwe_attributen[naam] = attr

        if klasse in insluitingen:
            melding("INFO", f"insluiting {klasse}: "
                            f"{len(nieuwe_attributen)} van "
                            f"{len(attributen)} attributen geleverd")
        if nieuwe_attributen:
            definitie["attributes"] = nieuwe_attributen
        else:
            definitie.pop("attributes", None)

        # unique_keys die naar verwijderde attributen wijzen vervallen.
        for sleutelnaam, sleutel in list(
                (definitie.get("unique_keys") or {}).items()):
            slots = sleutel.get("unique_key_slots") or []
            if klasse in insluitingen:
                vervalt = any(s not in nieuwe_attributen for s in slots)
            else:
                vervalt = any(s not in nieuwe_attributen
                              and (klasse, s) in uitsluitingen
                              for s in slots)
            if vervalt:
                melding("WAARSCHUWING",
                        f"unique_key '{sleutelnaam}' op {klasse} vervalt: "
                        f"verwijst naar een niet-geleverd attribuut")
                del definitie["unique_keys"][sleutelnaam]
        if not definitie.get("unique_keys"):
            definitie.pop("unique_keys", None)

        resultaat[klasse] = definitie

    # Inverse relaties materialiseren (annotatie gbo:inverseNaam) zodat
    # de navigatie ook van doel naar bron kan lopen; nodig nu de
    # Query-root van een profiel tot de natuurlijke sleutel beperkt kan
    # zijn (lijstQueries: false).
    for klasse in list(resultaat):
        for naam, attr in list(
                (resultaat[klasse].get("attributes") or {}).items()):
            ann = (attr or {}).get("annotations") or {}
            inverse = ann.get("gbo:inverseNaam")
            doel = (attr or {}).get("range")
            if not inverse or doel not in resultaat:
                continue
            doel_attrs = resultaat[doel].setdefault("attributes", {})
            if inverse in doel_attrs:
                fout(f"inverse '{doel}.{inverse}' botst met een "
                     f"bestaand attribuut")
            doel_attrs[inverse] = {
                "range": klasse,
                "multivalued": True,
                "description": ann.get("gbo:inverseBeschrijving")
                or f"Inverse van {klasse}.{naam}.",
                "annotations": {"gbo:inverseVan": f"{klasse}.{naam}"},
            }
            melding("INFO", f"inverse gematerialiseerd: "
                            f"{doel}.{inverse} <- {klasse}.{naam}")

    # Abstracte klassen zonder concreet subtype in het profiel.
    for klasse in resultaat:
        if index.classes[klasse].get("abstract"):
            concreet = [s for s in index.afstammelingen(klasse)
                        if s in resultaat
                        and not index.classes[s].get("abstract")]
            if not concreet and klasse in profiel["objecttypen"]:
                melding("INFO",
                        f"abstract objecttype '{klasse}' is ingang zonder "
                        f"concreet subtype in dit profiel "
                        f"(interface-query)")
    return resultaat


def verzamel_enums_en_types(klassen: dict[str, dict],
                            index: Modelindex) -> tuple[dict, dict]:
    enums: dict[str, dict] = {}
    typen: dict[str, dict] = {}

    def voeg_type_toe(naam: str) -> None:
        if naam in typen or naam not in index.types:
            return
        typen[naam] = copy.deepcopy(index.types[naam])
        basis = index.types[naam].get("typeof")
        if basis:
            voeg_type_toe(basis)

    for definitie in klassen.values():
        for attr in (definitie.get("attributes") or {}).values():
            doel = (attr or {}).get("range")
            if doel in index.enums:
                enums[doel] = copy.deepcopy(index.enums[doel])
            elif doel in index.types:
                voeg_type_toe(doel)
    return enums, typen


def bouw_schema(profiel: dict, index: Modelindex, klassen: dict,
                enums: dict, typen: dict) -> dict:
    bron = profiel["bron"]
    schema = {
        "id": f"https://lod.gbo-semantiek.nl/bronnen/{bron.lower()}",
        "name": f"gbo-bron-{bron.lower()}",
        "title": f"GBO bronprofiel: {profiel['titel']}",
        "description": profiel.get("beschrijving",
                                   f"Bronprofiel {bron}."),
        "license": index.raw.get("license"),
        "version": index.raw.get("version"),
        "prefixes": copy.deepcopy(index.raw.get("prefixes") or {}),
        "default_prefix": index.raw.get("default_prefix", "gbo"),
        "default_range": index.raw.get("default_range", "string"),
        "imports": ["linkml:types"],
        "annotations": {
            "gbo:bron": bron,
            "gbo:ingangen": ", ".join(profiel["ingangen"]),
            "gbo:objecttypen": ", ".join(profiel["objecttypen"]),
            "gbo:lijstQueries": bool(profiel.get("lijstQueries", True)),
        },
        "classes": klassen,
    }
    if enums:
        schema["enums"] = enums
    if typen:
        schema["types"] = typen
    return {k: v for k, v in schema.items() if v is not None}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genereer een per-bron LinkML-schema uit een "
                    "bron-profiel.")
    parser.add_argument("profiel", type=Path,
                        help="pad naar het bron-profiel (YAML)")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="uitvoerbestand (default: stdout)")
    parser.add_argument("-s", "--schema", type=Path, default=None,
                        help="hoofdschema; overschrijft 'schemabestand' "
                             "uit het profiel")
    args = parser.parse_args()

    profiel = laad_yaml(args.profiel)
    schemapad = args.schema or (args.profiel.parent
                                / profiel.get("schemabestand", ""))
    index = Modelindex(schemapad.resolve())

    valideer_profiel(profiel, index)
    selectie = bepaal_selectie(profiel, index)
    klassen = verwerk_klassen(profiel, index, selectie)
    enums, typen = verzamel_enums_en_types(klassen, index)
    schema = bouw_schema(profiel, index, klassen, enums, typen)

    kop = (f"# GEGENEREERD BESTAND — niet handmatig bewerken.\n"
           f"# Bron-profiel: {args.profiel.name}; informatiemodel: "
           f"{schemapad.name}.\n"
           f"# Regenereer met: python3 tools/genereer_bronschema.py "
           f"{args.profiel}\n")
    tekst = kop + yaml.dump(schema, sort_keys=False, allow_unicode=True,
                            width=72, default_flow_style=False)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(tekst, encoding="utf-8")
    else:
        print(tekst)

    melding("KLAAR", f"bronprofiel {profiel['bron']}: "
                     f"{len(klassen)} klassen, {len(enums)} enums, "
                     f"{len(typen)} typen")


if __name__ == "__main__":
    main()

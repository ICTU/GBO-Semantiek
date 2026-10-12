#!/usr/bin/env python3
"""Genereer uitgifteconfiguratie en rulebook-hoofdstuk uit een attestatieprofiel.

Een attestatieprofiel (LinkML-schema in <versie>/attestaties/) beschrijft één
attestatietype als subklasse van Attestatie: de claims, hun betekenis,
verplichting en herkomst in GBO-Kern. De koppeling aan de bron staat in
annotaties (zie attestaties/README.md). Dit script maakt daar per
attestatietype twee artefacten van:

1. <typeId>.gbo-attestatie.json: één element van
   capabilities.eudi.attestations in het bronmetadata-document
   /.well-known/gbo (schema gbo-source-metadata-v1 van de GBO-demo), met
   GraphQL-query, gbo-simple-v1-mapping, attribute_schema, aanbiedingen en
   SD-JWT VC Type Metadata. De vct kent het uitgifteplatform toe.
2. <typeId>.rulebook-h3.md: hoofdstuk 3 van een Attestation Rulebook
   (attributen en metadata), met per claim het semantisch anker en het
   bronpad.

De GraphQL-query wordt niet met de hand geschreven: het script bouwt hem uit
de bronpaden van de claims en valideert hem tegen de gegenereerde SDL van
het bronprofiel. Zo kan de query niet uit de pas lopen met het model.

Controles (fout = afbreken, waarschuwing = melden):
- elke attribuutclaim heeft een bronpad, geen metadataclaim heeft er een;
- query, subject- en aanbiedingsargument bestaan in de SDL, het bronpad
  bestaat en eindigt op een scalar of enum, en de query is geldig GraphQL;
- het brontype past op het claimtype; Float naar integer alleen met een
  gemotiveerde annotatie gbo:geheleWaarde;
- een subtype verruimt geen claim die een supertype verplicht stelt;
- waarschuwing als een verplichte claim uit een pad komt dat leeg kan zijn,
  of als het profiel regels (rules) heeft die gbo-simple-v1 niet uitvoert;
- met --ontologie: elk semantisch anker bestaat in de opgegeven TTL's.

Gebruik:
    python3 tools/genereer_attestatie.py v0.5/attestaties/inkomensverklaring.yaml \\
        --graphql-dir v0.5/graphql -o v0.5/eudi \\
        [--ontologie v0.5/ontologie/GBO-Linked-Data.ttl ...]
"""

import argparse
import json
import re
import sys
from pathlib import Path

from graphql import (build_schema, get_named_type, is_abstract_type,
                     is_enum_type, is_list_type, is_non_null_type,
                     is_scalar_type, parse, validate)
from linkml.generators.jsonschemagen import JsonSchemaGenerator
from linkml_runtime import SchemaView

BASISKLASSE = "Attestatie"
SUBSET_ATTRIBUUT = "attribuut"
SUBSET_METADATA = "metadata"
TAAL = "nl-NL"
MAPPINGPROFIEL = "gbo-simple-v1"

# Claimtype (LinkML-range, eventueel met gbo:formaat) naar het datatype van
# gbo-simple-v1 en het attribute_schema van de EUDI-capability.
DATATYPEN = {
    "string": "string", "integer": "integer", "boolean": "boolean",
    "date": "date", "float": "number", "double": "number",
    "decimal": "number",
}

# GraphQL-leaftypen die op een claimdatatype passen. Datum is de GBO-scalar
# voor een kalenderdatum; overige benoemde scalars zijn tekst.
PASSEND = {
    "Int": {"integer", "gYear", "number"},
    "Float": {"number"},
    "Boolean": {"boolean"},
    "Datum": {"date", "string"},
}

# GraphQL-argumenttype van de aanbiedingsparameter naar het parametertype
# van gbo-source-metadata-v1.
PARAMETERTYPEN = {"Int": "integer", "String": "string",
                  "Boolean": "boolean", "Datum": "date"}

PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def melding(soort: str, tekst: str) -> None:
    print(f"{soort}: {tekst}", file=sys.stderr)


def fout(tekst: str) -> None:
    melding("FOUT", tekst)
    sys.exit(1)


def annotatie(element, naam: str, verplicht: bool = False,
              context: str = "") -> str | None:
    ann = getattr(element, "annotations", None) or {}
    # SchemaView levert eigen annotaties als dict, maar die van een
    # geïnduceerd slot als JsonObj (jsonasobj2); beide vormen lezen.
    waarde = ann.get(naam) if isinstance(ann, dict) else \
        ann._get(naam, None)
    if waarde is not None and hasattr(waarde, "value"):
        waarde = waarde.value
    elif waarde is not None and hasattr(waarde, "_get"):
        waarde = waarde._get("value", None)
    if waarde is None and verplicht:
        fout(f"{context}: annotatie '{naam}' ontbreekt")
    return None if waarde is None else " ".join(str(waarde).split())


class Profiel:
    """Eén attestatietype uit een attestatieprofiel."""

    def __init__(self, sv: SchemaView, klasse: str):
        self.sv = sv
        self.klasse = klasse
        self.definitie = sv.get_class(klasse)
        ctx = f"attestatietype '{klasse}'"
        # De typeId is van het type zelf; de overige klasseannotaties erft
        # een subtype van zijn supertype, zodat bron en weergave niet
        # herhaald hoeven te worden.
        self.type_id = annotatie(self.definitie, "gbo:typeId", True, ctx)
        self.type_versie = self.ann("gbo:typeVersie", True)
        self.bronprofiel = self.ann("gbo:bronprofiel", True)
        self.service = self.ann("gbo:serviceReferentie") or self.bronprofiel
        self.query = self.ann("gbo:query", True)
        self.brontype = self.ann("gbo:bronType")
        self.subject = self.ann("gbo:subject", True)
        self.parameter = self.ann("gbo:aanbiedingParameter", True)
        self.waarden = [w.strip() for w in (self.ann(
            "gbo:aanbiedingWaarden", True) or "").split(",") if w.strip()]
        self.slots = sv.class_induced_slots(klasse)
        self.attributen = [s for s in self.slots
                           if SUBSET_METADATA not in (s.in_subset or [])]
        self.metadata = [s for s in self.slots
                         if SUBSET_METADATA in (s.in_subset or [])]

    def ann(self, naam: str, verplicht: bool = False) -> str | None:
        """Klasseannotatie, eigen of geërfd van het dichtstbijzijnde
        supertype dat haar draagt."""
        for voorouder in self.sv.class_ancestors(self.klasse):
            waarde = annotatie(self.sv.get_class(voorouder), naam)
            if waarde is not None:
                return waarde
        if verplicht:
            fout(f"attestatietype '{self.klasse}': annotatie '{naam}' "
                 f"ontbreekt, ook bij de supertypen")
        return None

    def datatype(self, slot) -> str:
        bereik = str(slot.range or "string")
        if bereik not in DATATYPEN:
            fout(f"claim '{slot.name}': range '{bereik}' is geen "
                 f"datatype dat een attestatie kan dragen")
        formaat = annotatie(slot, "gbo:formaat")
        if formaat == "gYear":
            if bereik != "integer":
                fout(f"claim '{slot.name}': formaat gYear vraagt range "
                     f"integer")
            return "gYear"
        return DATATYPEN[bereik]


# -- controles op het profiel ------------------------------------------------

def controleer_profiel(p: Profiel) -> None:
    for slot in p.attributen:
        if not annotatie(slot, "gbo:bronpad"):
            fout(f"claim '{slot.name}': annotatie 'gbo:bronpad' ontbreekt")
    for slot in p.metadata:
        if annotatie(slot, "gbo:bronpad"):
            fout(f"metadataclaim '{slot.name}' heeft een bronpad; metadata "
                 f"vult de uitgever, niet de bron")
    if p.definitie.rules:
        melding("WAARSCHUWING", f"'{p.klasse}' heeft regels (rules); "
                                f"{MAPPINGPROFIEL} kent geen conditionele "
                                f"claims, de uitgifte dwingt ze niet af")
    # Een subtype mag aanscherpen, niet verruimen.
    for ouder in p.sv.class_ancestors(p.klasse)[1:]:
        ouderslots = {s.name: s for s in p.sv.class_induced_slots(ouder)}
        for slot in p.slots:
            voorganger = ouderslots.get(slot.name)
            if voorganger is not None and voorganger.required \
                    and not slot.required:
                fout(f"claim '{slot.name}' is verplicht in '{ouder}' en "
                     f"optioneel in '{p.klasse}'; een subtype mag een "
                     f"claim niet verruimen")


def controleer_ankers(sv: SchemaView, klassen: list[str],
                      ontologieen: list[Path]) -> None:
    from rdflib import Graph, URIRef
    graaf = Graph()
    for pad in ontologieen:
        graaf.parse(pad)
    bekend = {str(s) for s in graaf.subjects() if isinstance(s, URIRef)}
    for klasse in klassen:
        elementen = [(klasse, sv.get_class(klasse))] + [
            (s.name, s) for s in sv.class_induced_slots(klasse)]
        for naam, element in elementen:
            for soort in ("exact_mappings", "close_mappings",
                          "related_mappings"):
                for curie in getattr(element, soort, None) or []:
                    uri = sv.expand_curie(curie)
                    if uri not in bekend:
                        fout(f"'{naam}': {soort} '{curie}' ({uri}) komt in "
                             f"geen van de ontologieën voor")
    melding("INFO", f"semantische ankers gecontroleerd tegen "
                    f"{len(ontologieen)} ontologie(ën)")


# -- GraphQL -------------------------------------------------------------------

def zonder_nonnull(t):
    return t.of_type if is_non_null_type(t) else t


class Selectie:
    """Boom van geselecteerde velden, met inline fragment per typeconditie."""

    def __init__(self):
        self.velden: dict[str, "Selectie"] = {}
        self.fragmenten: dict[str, "Selectie"] = {}

    def regels(self, inspring: str) -> list[str]:
        uit = []
        for naam, sub in self.velden.items():
            if sub.velden or sub.fragmenten:
                uit.append(f"{inspring}{naam} {{")
                uit += sub.regels(inspring + "  ")
                uit.append(f"{inspring}}}")
            else:
                uit.append(f"{inspring}{naam}")
        for typenaam, sub in self.fragmenten.items():
            uit.append(f"{inspring}... on {typenaam} {{")
            uit += sub.regels(inspring + "  ")
            uit.append(f"{inspring}}}")
        return uit


def bouw_query(p: Profiel, schema) -> tuple[str, dict, dict]:
    """GraphQL-document, argumentinfo en per claim de padinformatie."""
    veld = schema.query_type.fields.get(p.query)
    if veld is None:
        fout(f"query '{p.query}' bestaat niet in de SDL van bronprofiel "
             f"'{p.bronprofiel}'")
    resultaat = get_named_type(veld.type)
    brontype = resultaat
    if p.brontype:
        brontype = schema.get_type(p.brontype)
        if brontype is None:
            fout(f"bronType '{p.brontype}' bestaat niet in de SDL")
        if brontype is not resultaat and not (
                is_abstract_type(resultaat)
                and schema.is_sub_type(resultaat, brontype)):
            fout(f"bronType '{p.brontype}' is geen subtype van "
                 f"'{resultaat.name}', het resultaat van '{p.query}'")

    for arg in (p.subject, p.parameter):
        if arg not in veld.args:
            fout(f"argument '{arg}' bestaat niet op query '{p.query}'")
    for naam, arg in veld.args.items():
        if naam not in (p.subject, p.parameter) \
                and is_non_null_type(arg.type) \
                and arg.default_value is None:
            fout(f"verplicht argument '{naam}' van '{p.query}' wordt niet "
                 f"gevuld; alleen subject en aanbiedingsparameter")

    # Het subject komt uit de PID en gaat ongewijzigd door. De
    # aanbiedingsparameter is één waarde; is het argument een lijst, dan
    # gaat die waarde als lijst van één in de query.
    subject_type = str(veld.args[p.subject].type)
    param_type = zonder_nonnull(veld.args[p.parameter].type)
    als_lijst = is_list_type(param_type)
    element_type = param_type.of_type if als_lijst else \
        veld.args[p.parameter].type
    parameter_scalar = get_named_type(element_type).name
    if parameter_scalar not in PARAMETERTYPEN:
        fout(f"aanbiedingsparameter '{p.parameter}' heeft type "
             f"'{parameter_scalar}'; ondersteund: "
             f"{', '.join(PARAMETERTYPEN)}")

    boom = Selectie()
    paden: dict[str, dict] = {}
    for slot in p.attributen:
        segmenten = annotatie(slot, "gbo:bronpad").split(".")
        huidig_type, knoop = resultaat, boom
        eerste = segmenten[0]
        if eerste not in huidig_type.fields:
            if brontype is resultaat or eerste not in brontype.fields:
                fout(f"claim '{slot.name}': veld '{eerste}' bestaat niet "
                     f"op '{resultaat.name}' of '{brontype.name}'")
            huidig_type = brontype
            knoop = boom.fragmenten.setdefault(brontype.name, Selectie())
        kan_leeg = False
        for i, segment in enumerate(segmenten):
            f = huidig_type.fields.get(segment)
            if f is None:
                fout(f"claim '{slot.name}': veld '{segment}' bestaat niet "
                     f"op '{huidig_type.name}'")
            if not is_non_null_type(f.type):
                kan_leeg = True
            if is_list_type(zonder_nonnull(f.type)):
                fout(f"claim '{slot.name}': veld '{segment}' is een lijst; "
                     f"{MAPPINGPROFIEL} projecteert alleen enkelvoudige "
                     f"waarden")
            knoop = knoop.velden.setdefault(segment, Selectie())
            huidig_type = get_named_type(f.type)
            laatste = i == len(segmenten) - 1
            if laatste and not (is_scalar_type(huidig_type)
                                or is_enum_type(huidig_type)):
                fout(f"claim '{slot.name}': bronpad eindigt op objecttype "
                     f"'{huidig_type.name}'; kies een scalair veld")
            if not laatste and (is_scalar_type(huidig_type)
                                or is_enum_type(huidig_type)):
                fout(f"claim '{slot.name}': '{segment}' is scalair en kan "
                     f"geen deelveld hebben")
        leaf = huidig_type.name if is_scalar_type(huidig_type) else "String"
        paden[slot.name] = {"pointer": "/" + "/".join(segmenten),
                            "leaf": leaf, "kan_leeg": kan_leeg}

    variabelen = [f"${p.subject}: {subject_type}",
                  f"${p.parameter}: {element_type}"]
    argumenten = [f"{p.subject}: ${p.subject}",
                  f"{p.parameter}: " + (f"[${p.parameter}]" if als_lijst
                                        else f"${p.parameter}")]
    regels = [f"query {p.klasse}({', '.join(variabelen)}) {{",
              f"  {p.query}({', '.join(argumenten)}) {{",
              *boom.regels("    "), "  }", "}"]
    document = "\n".join(regels)
    fouten = validate(schema, parse(document))
    if fouten:
        for f in fouten:
            melding("FOUT", f"query: {f.message}")
        fout(f"de gegenereerde query voor '{p.klasse}' is geen geldige "
             f"GraphQL tegen bronprofiel '{p.bronprofiel}'")
    info = {"parametertype": PARAMETERTYPEN[parameter_scalar]}
    return document, info, paden


def controleer_typen(p: Profiel, paden: dict) -> None:
    for slot in p.attributen:
        datatype = p.datatype(slot)
        leaf = paden[slot.name]["leaf"]
        passend = PASSEND.get(leaf, {"string"})
        if datatype not in passend:
            if leaf == "Float" and datatype == "integer":
                if not annotatie(slot, "gbo:geheleWaarde"):
                    fout(f"claim '{slot.name}': de bron levert Float en de "
                         f"claim is integer; motiveer dat met "
                         f"'gbo:geheleWaarde' of kies number")
            else:
                fout(f"claim '{slot.name}': brontype '{leaf}' past niet op "
                     f"claimtype '{datatype}'")
        if datatype == "number":
            fout(f"claim '{slot.name}': de EUDI-capability kent geen "
                 f"niet-gehele getallen (nl-wallet v0.5)")
        if slot.required and paden[slot.name]["kan_leeg"]:
            melding("WAARSCHUWING",
                    f"claim '{slot.name}' is verplicht maar het bronpad "
                    f"kan leeg zijn; dan breekt de uitgifte af")


# -- uitvoer: attestation-blok -------------------------------------------------

def type_metadata_schema(sv_pad: Path, p: Profiel) -> dict:
    """JSON Schema van de attribuutclaims, via LinkML gen-json-schema.

    Metadataclaims vult de uitgever; die horen niet in het schema dat de
    wallet op de bronclaims toepast. Een optionele claim ontbreekt in de
    credential in plaats van null te zijn (gbo-simple-v1 slaat hem over),
    dus het type blijft enkelvoudig."""
    volledig = json.loads(JsonSchemaGenerator(
        str(sv_pad), top_class=p.klasse).serialize())
    namen = [s.name for s in p.attributen]
    eigenschappen = {}
    for naam in namen:
        eig = dict(volledig["properties"][naam])
        if isinstance(eig.get("type"), list):
            eig["type"] = next(t for t in eig["type"] if t != "null")
        eigenschappen[naam] = eig
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": p.definitie.title or p.klasse,
        "type": "object",
        "properties": eigenschappen,
        "required": [n for n in volledig.get("required", []) if n in namen],
    }


def attestation_blok(sv_pad: Path, p: Profiel, document: str, info: dict,
                     paden: dict) -> dict:
    samenvatting = p.ann("gbo:samenvatting")
    in_samenvatting = set(PLACEHOLDER.findall(samenvatting or ""))
    onbekend = in_samenvatting - {s.name for s in p.attributen}
    if onbekend:
        fout(f"gbo:samenvatting verwijst naar onbekende claim(s): "
             f"{', '.join(sorted(onbekend))}")

    mapping, attribute_schema, claims = {}, {}, []
    for slot in p.attributen:
        datatype = p.datatype(slot)
        regel = {"pointer": paden[slot.name]["pointer"],
                 "datatype": datatype}
        if not slot.required:
            regel["optional"] = True
        mapping[slot.name] = regel

        eenheid = annotatie(slot, "gbo:eenheid")
        schema = {"type": "string" if datatype == "date" else
                  "integer" if datatype == "gYear" else datatype}
        if datatype in ("date", "gYear"):
            schema["format"] = datatype
        elif eenheid:
            schema["unit"] = eenheid
        attribute_schema[slot.name] = schema

        weergave = {"lang": TAAL, "label": slot.title or slot.name}
        omschrijving = annotatie(slot, "gbo:weergaveOmschrijving")
        if omschrijving:
            weergave["description"] = omschrijving
        claim = {"path": [slot.name], "display": [weergave],
                 "sd": annotatie(slot, "gbo:selectieveOnthulling")
                 or "always"}
        if slot.name in in_samenvatting:
            claim["svg_id"] = slot.name
        claims.append(claim)

    display = {"lang": TAAL,
               "name": p.ann("gbo:weergaveNaam")
               or p.definitie.title or p.klasse}
    omschrijving = p.ann("gbo:weergaveOmschrijving")
    if omschrijving:
        display["description"] = omschrijving
    if samenvatting:
        display["summary"] = samenvatting
    achtergrond = p.ann("gbo:achtergrondkleur")
    tekst = p.ann("gbo:tekstkleur")
    if achtergrond or tekst:
        display["rendering"] = {"simple": {
            k: v for k, v in (("background_color", achtergrond),
                              ("text_color", tekst)) if v}}

    label = p.ann("gbo:aanbiedingLabel", True)
    omschr = p.ann("gbo:aanbiedingOmschrijving")
    offers = []
    for waarde in p.waarden:
        vervang = f"{{{p.parameter}}}"
        offer = {"id": f"{p.type_id}_{waarde}".lower(),
                 "label": label.replace(vervang, waarde)}
        if omschr:
            offer["description"] = omschr.replace(vervang, waarde)
        offer["parameters"] = {p.parameter: int(waarde)
                               if info["parametertype"] == "integer"
                               else waarde}
        offers.append(offer)

    return {
        "type_id": p.type_id,
        "type_version": p.type_versie,
        "offers": offers,
        "graphql": {
            "service_reference": p.service,
            "endpoint": "/graphql",
            "document": document,
            "subject_variable": p.subject,
            "parameters": {p.parameter: {"type": info["parametertype"],
                                         "required": True}},
            "result_pointer": f"/data/{p.query}",
        },
        "mapping_profile": MAPPINGPROFIEL,
        "mapping": mapping,
        "attribute_schema": attribute_schema,
        "type_metadata": {
            "name": p.definitie.title or p.klasse,
            "description": p.ann("gbo:typeOmschrijving")
            or " ".join((p.definitie.description or "").split()),
            "display": [display],
            "claims": claims,
            "schema": type_metadata_schema(sv_pad, p),
        },
    }


# -- uitvoer: rulebook hoofdstuk 3 ------------------------------------------

def cel(tekst) -> str:
    return " ".join(str(tekst or "").split()).replace("|", "\\|")


def rulebook_h3(p: Profiel, paden: dict, profielbestand: str) -> str:
    sv = p.sv

    def anker(slot) -> str:
        curies = [*(slot.exact_mappings or []), *(slot.close_mappings or [])]
        soort = "exact" if slot.exact_mappings else "close"
        return "<br>".join(f"[`{c}`]({sv.expand_curie(c)}) ({soort})"
                           for c in curies) or "-"

    def voorbeeld(slot) -> str:
        return cel(slot.examples[0].value) if slot.examples else "-"

    def weergavetype(slot) -> str:
        return {"date": "full-date", "gYear": "integer (jaar)"}.get(
            p.datatype(slot), p.datatype(slot))

    def attributentabel(slots) -> list[str]:
        if not slots:
            return ["Niet gespecificeerd.", ""]
        regels = ["| Data identifier | Definitie | Datatype | Voorbeeld "
                  "| Semantisch anker | Bronpad |",
                  "|---|---|---|---|---|---|"]
        for s in slots:
            eenheid = annotatie(s, "gbo:eenheid")
            regels.append(
                f"| `{s.name}` | {cel(s.description)} | "
                f"{weergavetype(s)}{f' ({eenheid})' if eenheid else ''} | "
                f"{voorbeeld(s)} | {anker(s)} | "
                f"`{annotatie(s, 'gbo:bronpad')}` |")
        return regels + [""]

    def metadatatabel(slots) -> list[str]:
        if not slots:
            return ["Niet gespecificeerd.", ""]
        regels = ["| Data identifier | Definitie | Datatype | Vaste waarde "
                  "| Gevuld door |", "|---|---|---|---|---|"]
        for s in slots:
            regels.append(
                f"| `{s.name}` | {cel(s.description)} | string | "
                f"{('`' + s.equals_string + '`') if s.equals_string else '-'}"
                f" | {annotatie(s, 'gbo:gevuldDoor') or '-'} |")
        return regels + [""]

    verplicht = [s for s in p.attributen if s.required]
    optioneel = [s for s in p.attributen if not s.required]
    meta_v = [s for s in p.metadata if s.required]
    meta_o = [s for s in p.metadata if not s.required]
    categorie = next((s.equals_string for s in p.metadata
                      if s.name == "attestation_legal_category"), None)
    titel = p.definitie.title or p.klasse
    uit = [
        f"# {titel}: attributen en metadata",
        "",
        "!!! note \"Gegenereerd\"",
        f"    Gegenereerd uit het attestatieprofiel `{profielbestand}` met",
        "    `tools/genereer_attestatie.py`. Dit is hoofdstuk 3 van een",
        "    Attestation Rulebook (ARF-sjabloon): de claims, los van hun",
        "    codering. Codering, gebruik, vertrouwensankers, intrekking en",
        "    compliance staan niet in het profiel.",
        "",
        "| Kenmerk | Waarde |",
        "|---|---|",
        f"| Attestatietype | `{p.klasse}` ({sv.get_uri(p.klasse, expand=True)}) |",
        f"| Type-id en versie | `{p.type_id}` {p.type_versie} |",
        f"| Juridische categorie | {categorie or '-'} |",
        f"| Bron | bronprofiel `{p.bronprofiel}`, query `{p.query}`"
        + (f", type `{p.brontype}`" if p.brontype else "") + " |",
        f"| Subject | `{p.subject}`, uit de PID |",
        f"| Aanbiedingen | `{p.parameter}` = {', '.join(p.waarden)} |",
        "",
        "## 3.1 Inleiding",
        "",
        cel(p.definitie.description),
        "",
        *[f"{cel(c)}\n" for c in (p.definitie.comments or [])],
        "## 3.2 Verplichte attributen",
        "",
        *attributentabel(verplicht),
        "## 3.3 Optionele attributen",
        "",
        *attributentabel(optioneel),
        "## 3.4 Conditionele attributen",
        "",
        *(["Regels in het profiel: "
           + "; ".join(cel(r.description or r.title or "regel")
                       for r in p.definitie.rules), ""]
          if p.definitie.rules else ["Niet gespecificeerd.", ""]),
        "## 3.5 Verplichte metadata",
        "",
        *metadatatabel(meta_v),
        "## 3.6 Optionele metadata",
        "",
        *metadatatabel(meta_o),
        "## 3.7 Conditionele metadata",
        "",
        "Niet gespecificeerd.",
        "",
    ]
    return "\n".join(uit)


# -- hoofdprogramma ----------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genereer uitgifteconfiguratie en rulebook-hoofdstuk 3 "
                    "uit een attestatieprofiel.")
    parser.add_argument("profiel", type=Path,
                        help="attestatieprofiel (LinkML-schema)")
    parser.add_argument("--graphql-dir", type=Path, required=True,
                        help="map met de gegenereerde SDL per bronprofiel")
    parser.add_argument("-o", "--output-dir", type=Path, required=True,
                        help="uitvoermap")
    parser.add_argument("--ontologie", type=Path, nargs="*", default=[],
                        help="TTL-bestanden waartegen de semantische "
                             "ankers worden gecontroleerd")
    args = parser.parse_args()

    sv = SchemaView(str(args.profiel))
    eigen = sv.schema.classes or {}
    klassen = [k for k in eigen
               if not sv.get_class(k).abstract
               and BASISKLASSE in sv.class_ancestors(k)]
    if not klassen:
        fout(f"{args.profiel.name} bevat geen concrete subklasse van "
             f"{BASISKLASSE}")
    if args.ontologie:
        controleer_ankers(sv, klassen, args.ontologie)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for klasse in klassen:
        p = Profiel(sv, klasse)
        controleer_profiel(p)
        sdl = args.graphql_dir / f"{p.bronprofiel}.graphql"
        if not sdl.exists():
            fout(f"SDL van bronprofiel '{p.bronprofiel}' niet gevonden: "
                 f"{sdl}")
        schema = build_schema(sdl.read_text(encoding="utf-8"))
        document, info, paden = bouw_query(p, schema)
        controleer_typen(p, paden)

        blok = attestation_blok(args.profiel, p, document, info, paden)
        json_pad = args.output_dir / f"{p.type_id}.gbo-attestatie.json"
        json_pad.write_text(json.dumps(blok, indent=2, ensure_ascii=False)
                            + "\n", encoding="utf-8")
        md_pad = args.output_dir / f"{p.type_id}.rulebook-h3.md"
        md_pad.write_text(rulebook_h3(p, paden, args.profiel.name),
                          encoding="utf-8")
        melding("KLAAR", f"{klasse}: {len(p.attributen)} attribuutclaims, "
                         f"{len(p.metadata)} metadataclaims, query "
                         f"'{p.query}' gevalideerd tegen {sdl.name}; "
                         f"{json_pad.name}, {md_pad.name}")


if __name__ == "__main__":
    main()

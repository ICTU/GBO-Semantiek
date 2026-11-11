#!/usr/bin/env python3
"""Genereer per bron de GBO Bronspecificatie (consultatieversie) als Markdown en Word.

De bronspecificatie is het document waarmee een bronhouder de
GBO-uitsnede van zijn registratie toetst. Alle modelfeiten komen uit
het bronprofiel en de LinkML: dit script materialiseert met
genereer_bronschema.py exact dezelfde uitsnede als de GraphQL-SDL en
zet die om in een MIM 1.2-geordend document. Alleen de verhalende
delen (context, brondocumenten, toetsvragen, open punten) komen uit een
klein handgeschreven tekstbestand per bron, dat via 'task import:copy'
uit de wiki-repo wordt gekopieerd.

Uitvoer, in de uitvoermap:
    GBO-Bronspecificatie-<BRON>-<versie>.md     tussenvorm (ook bruikbaar op de site)
    GBO-Bronspecificatie-<BRON>-<versie>.docx   via pandoc, met huisstijl-sjabloon
    assets/<bron>-overzicht.png                 overzichtsdiagram (PlantUML)

Gebruik:
    genereer_bronspecificatie.py v0.5/bronnen/brp.yaml \\
        --tekst v0.5/bronspecificaties/teksten/brp.md \\
        --output-dir v0.5/bronspecificaties --versie v0.5 \\
        --changelog v0.5/GBO_Changes.md --wiki-repo ../llm-wiki-GBI-core-model

Het Word-sjabloon wordt niet als binair bestand bewaard maar bij elke
run opgebouwd uit het pandoc-standaardsjabloon plus de huisstijl
(koppen in GBO-blauw, A4, tabelstijl, voettekst met bron, modelversie,
commit en datum). Zo blijft het sjabloon reviewbaar in code.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import genereer_bronschema as gb  # noqa: E402

BASE_LOD = "https://lod.gbo-semantiek.nl"
BASE_BEGRIP = "https://begrippen.gbo-semantiek.nl/id/begrip/"
MIM_NS_GBO = "https://lod.gbo-semantiek.nl/def/mim#"
MIM_NS_BP4MC2 = "http://bp4mc2.org/def/mim#"
MIM_NS_12 = "http://modellen.mim-standaard.nl/def/mim#"
REPO_URL = "https://github.com/ICTU/GBO-Semantiek"
SITE_URL = "https://ictu.github.io/GBO-Semantiek/"
HUISSTIJL_BLAUW = "2E62E6"
LEEG = "–"

# A4 in twips (1/1440 inch).
A4_B, A4_H = 11906, 16838
MARGE = 1418  # 2,5 cm
MARGE_KOP = 709


# ---------------------------------------------------------------------------
# Hulpfuncties
# ---------------------------------------------------------------------------

def melding(soort: str, tekst: str) -> None:
    print(f"[{soort}] {tekst}", file=sys.stderr)


def fout(tekst: str) -> None:
    melding("FOUT", tekst)
    sys.exit(1)


_ESC = re.compile(r"([\\`*_{}\[\]<>#~^$|])")


def md(tekst) -> str:
    """Maak platte tekst veilig voor pandoc-Markdown (geen opmaak uit data)."""
    if tekst is None:
        return ""
    t = str(tekst).replace("\r", "").strip()
    t = re.sub(r"\s*\n\s*", " ", t)
    return _ESC.sub(r"\\\1", t)


def code(tekst) -> str:
    if tekst is None or str(tekst) == "":
        return ""
    t = str(tekst).replace("`", "'")
    return f"`{t}`"


def cel(tekst) -> str:
    t = md(tekst) if not (isinstance(tekst, str) and tekst.startswith("\x00")) \
        else tekst[1:]
    return t if t else LEEG


def rauw(tekst: str) -> str:
    """Markeer een celinhoud als al opgemaakte Markdown (niet escapen)."""
    return "\x00" + tekst


def tabel(koppen: list[str], rijen: list[list], breedtes: list[int] | None = None) -> list[str]:
    """Pipe-tabel; de streepjes bepalen de relatieve kolombreedtes in Word."""
    n = len(koppen)
    breedtes = breedtes or [1] * n
    tot = sum(breedtes)
    streepjes = [max(3, round(140 * b / tot)) for b in breedtes]
    out = ["| " + " | ".join(cel(k) for k in koppen) + " |",
           "|" + "|".join("-" * d for d in streepjes) + "|"]
    for r in rijen:
        r = list(r) + [""] * (n - len(r))
        out.append("| " + " | ".join(cel(c) for c in r[:n]) + " |")
    out.append("")
    return out


def ja_nee(waarde) -> str:
    if waarde is None or waarde == "":
        return LEEG
    if isinstance(waarde, bool):
        return "Ja" if waarde else "Nee"
    return {"true": "Ja", "false": "Nee", "ja": "Ja", "nee": "Nee"}.get(
        str(waarde).strip().lower(), str(waarde))


def eerste_zin(tekst: str | None, maxlen: int = 160) -> str:
    if not tekst:
        return ""
    t = re.sub(r"\s+", " ", str(tekst)).strip()
    m = re.match(r"(.+?\.)(\s|$)", t)
    zin = m.group(1) if m else t
    if len(zin) > maxlen:
        zin = zin[:maxlen].rsplit(" ", 1)[0] + " …"
    return zin


def autolink(uri: str | None) -> str:
    if not uri:
        return LEEG
    return rauw(f"<{uri}>")


def git_stand(pad: Path | None) -> tuple[str, bool]:
    """Korte commit-hash en of de werkkopie niet-vastgelegde wijzigingen heeft."""
    if pad is None or not (pad / ".git").exists():
        return "onbekend", False
    try:
        sha = subprocess.run(["git", "-C", str(pad), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, check=True).stdout.strip()
        vuil = subprocess.run(["git", "-C", str(pad), "status", "--porcelain"],
                              capture_output=True, text=True, check=True).stdout.strip()
        return sha, bool(vuil)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "onbekend", False


def tool_versie(cmd: list[str]) -> str:
    try:
        uit = subprocess.run(cmd, capture_output=True, text=True, check=False,
                             timeout=60)
        regel = (uit.stdout or uit.stderr).strip().splitlines()
        return regel[0].strip() if regel else "onbekend"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "niet gevonden"


# ---------------------------------------------------------------------------
# Invoer: profiel + bronschema, tekstbestand, herleiding, changelog
# ---------------------------------------------------------------------------

def materialiseer(profielpad: Path, schemapad: Path | None):
    """Zelfde pijplijn als genereer_bronschema.main, maar in-process."""
    profiel = gb.laad_yaml(profielpad)
    schemapad = schemapad or (profielpad.parent / profiel.get("schemabestand", ""))
    index = gb.Modelindex(schemapad.resolve())
    gb.valideer_profiel(profiel, index)
    selectie = gb.bepaal_selectie(profiel, index)
    klassen = gb.verwerk_klassen(profiel, index, selectie)
    klassen.update(gb.maak_invoertypen(profiel, index, klassen))
    toetsen = gb.codeer_toetsen(profiel, index)
    enums, typen = gb.verzamel_enums_en_types(klassen, index, toetsen)
    schema = gb.bouw_schema(profiel, index, klassen, enums, typen, toetsen)
    return profiel, index, schema, schemapad


def laad_tekst(pad: Path | None) -> tuple[dict, dict[str, list[str]]]:
    """Frontmatter + secties (## Kop) van het handgeschreven tekstbestand."""
    if pad is None:
        return {}, {}
    if not pad.exists():
        fout(f"tekstbestand niet gevonden: {pad}")
    inhoud = pad.read_text(encoding="utf-8")
    meta: dict = {}
    body = inhoud
    if inhoud.startswith("---"):
        delen = inhoud.split("\n---", 1)
        if len(delen) == 2:
            meta = yaml.safe_load(delen[0][3:]) or {}
            body = delen[1].lstrip("\n")
    secties: dict[str, list[str]] = {}
    huidige = None
    for regel in body.splitlines():
        m = re.match(r"^## (.+?)\s*$", regel)
        if m:
            huidige = m.group(1).strip().lower()
            secties[huidige] = []
            continue
        if huidige is not None:
            secties[huidige].append(regel)
    for k in secties:
        while secties[k] and not secties[k][-1].strip():
            secties[k].pop()
    bekend = {"context", "toetsvragen", "open punten"}
    for k in secties:
        if k not in bekend:
            melding("WAARSCHUWING", f"onbekende sectie '## {k}' in {pad.name} wordt genegeerd")
    return meta, secties


def parse_toetsvragen(regels: list[str]) -> list[tuple[str, list[str]]]:
    """### Kop + '- vraag' (met inspringende vervolgregels) -> [(kop, [vragen])]."""
    groepen: list[tuple[str, list[str]]] = []
    kop = "Algemeen"
    vragen: list[str] = []
    for regel in regels + [""]:
        m = re.match(r"^### (.+?)\s*$", regel)
        if m:
            if vragen:
                groepen.append((kop, vragen))
            kop, vragen = m.group(1).strip(), []
            continue
        if re.match(r"^- ", regel):
            vragen.append(regel[2:].strip())
        elif regel.startswith("  ") and vragen:
            vragen[-1] += " " + regel.strip()
    if vragen:
        groepen.append((kop, vragen))
    return groepen


_HC_CEL = re.compile(r"`([^`]+)`")
_KLASSE_ATTR = re.compile(r"^([A-Z][A-Za-z0-9]*)\.([a-z][A-Za-z0-9]*)")
_ATTR = re.compile(r"^[a-z][A-Za-z0-9]*$")


def laad_herleiding(wiki_repo: Path | None, opgaven: list[dict]) -> dict[tuple[str, str], list[tuple[str, str, str]]]:
    """Lees de API-compatibiliteitstabellen uit de wiki: (Klasse, attr) -> [(veld, status, koppelvlak)]."""
    resultaat: dict[tuple[str, str], list[tuple[str, str, str]]] = {}
    for opgave in opgaven or []:
        rel = opgave.get("pad") if isinstance(opgave, dict) else str(opgave)
        koppelvlak = (opgave.get("koppelvlak") if isinstance(opgave, dict) else None) or rel
        if wiki_repo is None:
            melding("WAARSCHUWING", f"geen --wiki-repo; herleiding '{rel}' overgeslagen")
            continue
        pad = wiki_repo / rel
        if not pad.exists():
            melding("WAARSCHUWING", f"herleidingsbestand niet gevonden: {pad}")
            continue
        for regel in pad.read_text(encoding="utf-8").splitlines():
            if not regel.startswith("|"):
                continue
            cellen = [c.strip() for c in regel.strip().strip("|").split("|")]
            if len(cellen) < 3 or set(cellen[1]) <= set("-: "):
                continue
            if "GBO" in cellen[1] and ("veld" in cellen[0].lower() or "resource" in cellen[0].lower()):
                continue  # kopregel
            veld = re.sub(r"`", "", cellen[0]).strip()
            status = re.sub(r"\*", "", cellen[2]).strip()
            klasse = None
            for segment in _HC_CEL.findall(cellen[1]):
                m = _KLASSE_ATTR.match(segment)
                if m:
                    klasse, attr = m.group(1), m.group(2)
                elif klasse and _ATTR.match(segment):
                    attr = segment
                else:
                    continue
                resultaat.setdefault((klasse, attr), []).append((veld, status, koppelvlak))
    return resultaat


def laad_changelog(pad: Path | None, namen: set[str]) -> list[tuple[str, str]]:
    """Filter GBO_Changes.md (sectie Kernmodel) op de elementen van deze bron."""
    if pad is None or not pad.exists():
        return []
    regels = pad.read_text(encoding="utf-8").splitlines()
    uit: list[tuple[str, str]] = []
    in_kern = False
    rubriek = ""
    klasse = None
    for regel in regels:
        if regel.startswith("## "):
            in_kern = regel.strip() == "## Kernmodel"
            continue
        if not in_kern:
            continue
        if regel.startswith("### "):
            rubriek = regel[4:].strip()
            klasse = None
            continue
        m = re.match(r"^\*\*(.+?)\*\*", regel.strip())
        if m:
            klasse = m.group(1)
            continue
        m = re.match(r"^\s*-\s*([+−-])\s*`([^`]+)`", regel)
        if m and klasse:
            if klasse in namen:
                teken = "toegevoegd" if m.group(1) == "+" else "verwijderd"
                uit.append((rubriek, f"{klasse}: {m.group(2)} {teken}"))
            continue
        m = re.match(r"^\s*-\s*`([^`]+)`", regel)
        if m and m.group(1) in namen:
            uit.append((rubriek, m.group(1)))
    return uit


# ---------------------------------------------------------------------------
# Model-uitsnede ordenen
# ---------------------------------------------------------------------------

class Uitsnede:
    """Leesbare ordening van het gematerialiseerde bronschema."""

    def __init__(self, profiel: dict, index: gb.Modelindex, schema: dict):
        self.profiel = profiel
        self.index = index
        self.schema = schema
        self.prefixes = schema.get("prefixes") or {}
        self.klassen: dict[str, dict] = schema.get("classes") or {}
        self.enums: dict[str, dict] = schema.get("enums") or {}
        self.typen: dict[str, dict] = schema.get("types") or {}

        self.objecttypen: list[str] = []
        self.datatypen_klassen: list[str] = []
        self.mixins: list[str] = []
        for naam, k in self.klassen.items():
            ann = k.get("annotations") or {}
            if ann.get("gbo:graphql") == "invoer":
                continue
            if k.get("mixin"):
                self.mixins.append(naam)
            elif ann.get("mim:stereotype") == "DataType":
                self.datatypen_klassen.append(naam)
            else:
                self.objecttypen.append(naam)
        # Volgorde: profielvolgorde eerst, automatisch meegenomen supertypen erna.
        volgorde = list(profiel.get("objecttypen") or [])
        self.objecttypen.sort(key=lambda n: (volgorde.index(n) if n in volgorde else 999, n))

        self.codelijsten = {n: t for n, t in self.typen.items()
                            if (t.get("annotations") or {}).get("mim:stereotype") == "Codelijst"}
        self.basistypen = {n: t for n, t in self.typen.items() if n not in self.codelijsten}

    # -- eigenschappen van elementen --------------------------------------

    def deelmodel(self, naam: str) -> str:
        bestand = self.index.herkomst.get(naam, "")
        return Path(bestand).stem if bestand else ""

    def expand(self, curie: str | None) -> str | None:
        if not curie:
            return None
        if ":" in curie and not curie.startswith("http"):
            pre, rest = curie.split(":", 1)
            if pre in self.prefixes:
                return self.prefixes[pre] + rest
        return curie

    def begrip(self, element: dict) -> str | None:
        for m in element.get("exact_mappings") or []:
            if str(m).startswith("gbobegrip:"):
                return self.expand(m)
        return None

    def klasse_uri(self, naam: str) -> str:
        """URI van het objecttype in de Linked Data (class_uri als het model die zet)."""
        k = self.klassen.get(naam) or {}
        if k.get("class_uri"):
            return self.expand(k["class_uri"]) or k["class_uri"]
        return self.element_basis(naam)

    def element_basis(self, naam: str) -> str:
        """Basis van de element-URI's, zoals kwalificeer_uris.py die zet."""
        dm = self.deelmodel(naam)
        return f"{BASE_LOD}/{dm}/{naam}" if dm else f"{BASE_LOD}/{naam}"

    def attribuut_uri(self, klasse: str, attr: str) -> str:
        return f"{self.element_basis(klasse)}/{attr.lower()}"

    def is_objecttype(self, naam: str | None) -> bool:
        return naam in self.objecttypen or naam in self.mixins

    def is_datatype_klasse(self, naam: str | None) -> bool:
        return naam in self.datatypen_klassen

    def soort(self, attr: dict) -> str:
        """attribuut | gegevensgroep | relatie | sleutel | inverse"""
        ann = attr.get("annotations") or {}
        if ann.get("gbo:inverseVan"):
            return "inverse"
        if ann.get("gbo:sleutelreferentie"):
            return "sleutel"
        rng = attr.get("range")
        if self.is_objecttype(rng):
            return "relatie"
        if self.is_datatype_klasse(rng):
            return "gegevensgroep"
        return "attribuut"

    def typenaam(self, attr: dict) -> str:
        rng = attr.get("range") or self.schema.get("default_range", "string")
        t = self.typen.get(rng)
        if t and rng in self.codelijsten:
            alias = (t.get("aliases") or [rng])[0]
            return alias.replace("~", " ")
        if rng in self.enums:
            return f"{rng} (enumeratie)"
        if rng in self.datatypen_klassen:
            return f"{rng} (gestructureerd)"
        return rng

    @staticmethod
    def kardinaliteit(attr: dict) -> str:
        ann = attr.get("annotations") or {}
        k = ann.get("mim:kardinaliteit")
        if k:
            k = str(k)
            return k.split("->")[-1].strip() if "->" in k else k
        req, multi = bool(attr.get("required")), bool(attr.get("multivalued"))
        return {(True, False): "1", (False, False): "0..1",
                (True, True): "1..*", (False, True): "0..*"}[(req, multi)]

    @staticmethod
    def definitie(element: dict) -> str:
        if element.get("description"):
            return str(element["description"])
        ann = element.get("annotations") or {}
        return str(ann.get("skos:definition_nl") or "")

    def voorouders(self, naam: str) -> list[str]:
        keten = []
        k = self.klassen.get(naam) or {}
        while k.get("is_a"):
            keten.append(k["is_a"])
            k = self.klassen.get(k["is_a"]) or {}
        return keten

    def subtypen(self, naam: str) -> list[str]:
        return [n for n, k in self.klassen.items() if k.get("is_a") == naam
                and n in self.objecttypen]

    def attributen(self, naam: str) -> dict[str, dict]:
        return (self.klassen.get(naam) or {}).get("attributes") or {}

    def geerfde_namen(self, naam: str) -> list[tuple[str, list[str]]]:
        uit = []
        for v in self.voorouders(naam):
            uit.append((v, list(self.attributen(v).keys())))
        k = self.klassen.get(naam) or {}
        for m in k.get("mixins") or []:
            if m in self.klassen:
                uit.append((m, list(self.attributen(m).keys())))
        return uit

    def tellingen(self) -> dict[str, int]:
        t = {"objecttypen": 0, "abstract": 0, "attribuutsoorten": 0,
             "relatiesoorten": 0, "sleutelreferenties": 0, "inverses": 0,
             "gegevensgroepen": len(self.datatypen_klassen),
             "enumeraties": len(self.enums), "codelijsten": len(self.codelijsten),
             "datatypen": len(self.basistypen)}
        for naam in self.objecttypen:
            t["objecttypen"] += 1
            if (self.klassen[naam]).get("abstract"):
                t["abstract"] += 1
            for attr in self.attributen(naam).values():
                s = self.soort(attr)
                if s in ("attribuut", "gegevensgroep"):
                    t["attribuutsoorten"] += 1
                elif s == "relatie":
                    t["relatiesoorten"] += 1
                elif s == "sleutel":
                    t["sleutelreferenties"] += 1
                elif s == "inverse":
                    t["inverses"] += 1
        return t

    def niet_geleverd(self) -> list[str]:
        """Objecttypen uit het deelmodel van de ingang(en) die deze bron niet levert."""
        basis = self.profiel.get("ingangen") or self.profiel.get("objecttypen") or []
        bestanden = {self.index.herkomst.get(n) for n in basis}
        bestanden.discard(None)
        uit = []
        for naam, k in self.index.classes.items():
            if naam in self.klassen or self.index.herkomst.get(naam) not in bestanden:
                continue
            ann = k.get("annotations") or {}
            if k.get("mixin") or ann.get("mim:stereotype") == "DataType":
                continue
            uit.append(naam)
        return sorted(uit)


# ---------------------------------------------------------------------------
# Vaste teksten
# ---------------------------------------------------------------------------

LEESWIJZER = """\
Dit document beschrijft welke gegevens de Gemeenschappelijke
Bronontsluiting (GBO) uit deze bron ontsluit en hoe die gegevens zijn
gedefinieerd. Het is een consultatieversie: wij vragen de bronhouder en
andere betrokkenen de inhoud te toetsen en van opmerkingen te voorzien.

**Wat wij vragen te toetsen**

- Kloppen de definities en de herkomstverwijzingen per objecttype en per
  gegeven?
- Kloppen kardinaliteit, datatype en de aanduiding Authentiek?
- Ontbreken er gegevens die afnemers uit deze bron nodig hebben, of staan
  er gegevens in die de bron niet kan leveren?
- Zijn de afbakeningskeuzes (hoofdstuk 3.7) en de open punten (bijlage D)
  herkenbaar en juist?

**Hoe te reageren**

Reageer met opmerkingen in dit Word-document, of vul de reactietabel in
hoofdstuk 4 in. Verwijs waar mogelijk naar het objecttype en het gegeven
(bijvoorbeeld *IngeschrevenPersoon.indicatieGeheim*) of naar een
toetsvraag (T1, T2, …). Stuur de reactie vóór de reactietermijn aan de
contactpersoon op het voorblad.

**Wat er met reacties gebeurt**

Elke reactie wordt vastgelegd in het consultatielog van GBO met een
dispositie (overgenomen, afgewezen met reden, of uitgesteld naar een
volgende versie). Overgenomen wijzigingen landen in het model, waarna
een nieuwe versie van dit document wordt gegenereerd; bijlage D toont
dan wat er is veranderd. Dit document wordt niet met de hand bewerkt.

**Opbouw**

De hoofdtekst (hoofdstuk 1 tot en met 4) bevat de kerngegevens: per
objecttype de definitie, herkomst en populatie, en per gegeven naam,
definitie, type, kardinaliteit, authentiek en herkomst. De bijlagen
bevatten alle overige MIM-metagegevens, de volledige herleiding naar de
brondocumenten en het koppelvlak, de datatypen en codelijsten, de
wijzigingen en open punten, en de verantwoording.
"""

GBO_KORT = """\
De Gemeenschappelijke Bronontsluiting (GBO) is een landelijke,
sectoroverstijgende specificatie voor de semantische beschrijving van
basisgegevens uit overheidsregistraties. GBO legt per bron vast welke
objecttypen en gegevens worden ontsloten, met één gedeeld
begrippenkader en informatiemodel, zodat afnemers uit verschillende
sectoren dezelfde gegevens op dezelfde manier begrijpen. GBO vervangt
de bronregistraties niet en definieert niets opnieuw: waar de bron een
definitie heeft, neemt GBO die over en verwijst ernaar.
"""

LAGEN = [
    ("L1", "Gezaghebbend", "Het datamodel van de registratie zelf; anders het functioneel ontwerp of de catalogus.", "Inhoudelijke definitie en structurele eigenschappen."),
    ("L2", "Koppelvlak", "De koppelvlakspecificatie waarmee afnemers de bron bevragen.", "Naamgeving, datatype, uitwisselingscontract."),
    ("L3", "Nationaal anker", "Overheidsbrede begrippen, thesauri en referentiemodellen (NL-SBB, TOOI, GGM/RSGB, CBS).", "Binding tussen registraties."),
    ("L4", "Internationaal", "Generieke Europese vocabulaires (Core Vocabularies, schema.org).", "Publicatie en vindbaarheid."),
]

BESLISREGELS = """\
Bij elk element is de bronkeuze in deze volgorde afgepeld, met drie
beslisregels:

1. **L1 is de standaard.** De definitie komt uit het gezaghebbende
   document van de registratie zolang dat beschikbaar is. L2 of L3 wordt
   gebruikt als L1 ontbreekt of niet voldoet, of als een functionele
   behoefte daarom vraagt (zoals herkenbare naamgeving voor afnemers van
   het koppelvlak).
2. **Bij gaten of conflicten wordt zelf afgeleid**, niet ruimer dan de
   bron toelaat. Zo'n eigen afleiding is in de kolom Herkomst herkenbaar
   aan de aanduiding "GBO" of "GBO-afleiding".
3. **Elk element draagt een herkomst.** Zonder bronverwijzing is een
   element niet vastgesteld. De kolom Herkomst in hoofdstuk 3 geeft de
   vindplaats in het brondocument; bijlage B geeft de volledige
   herleiding.
"""

MIM_TEKST = """\
GBO is opgesteld conform het **Metamodel voor Informatiemodellen (MIM),
versie 1.2** (Geonovum, vastgesteld 13 juni 2024). De metagegevens in dit
document zijn de MIM-metagegevens voor objecttypen, attribuutsoorten en
relatiesoorten (MIM 1.2, paragraaf 2.4.3 en 3.2.1); zij dragen de
MIM-naam en staan in de MIM-volgorde. Metagegevens die GBO niet
vastlegt, staan niet in dit document. Binnen de keuzeruimte van MIM heeft
GBO de volgende keuzes gemaakt (vastgesteld 13 mei 2026):
"""

MIM_KEUZES = [
    ("Relatiemodellering", "Relatiesoort leidend: relaties zijn benoemd vanuit de relatienaam (heeftOuder, woontOp) met de kardinaliteit aan de doelzijde; relatierollen worden niet apart gevoerd."),
    ("Historie-indicaties", "Standaard Nee/Nee. Objecttypen die het patroon Voorkomen dragen (bitemporele historie) krijgen Ja/Ja op hun attribuut- en relatiesoorten."),
    ("Begrip", "Elk objecttype, elke enumeratie en elk gedeeld begrip heeft een begrip-URI onder begrippen.gbo-semantiek.nl/id/begrip/, waaronder het begrip als SKOS wordt gepubliceerd."),
    ("Definitie", "De definitie staat altijd als tekst in het model; de begrip-URI is een aanvullende, machineleesbare verwijzing (MIM-extensie: begrip of definitie)."),
    ("Authentiek", "Authentiek: uit L1 en daar als authentiek aangemerkt. Basisgegeven: uit L1 zonder authentiek-merk. Landelijk kerngegeven: uit L2 of L3. Overig: GBO-eigen of L4."),
    ("Datum opname", "De basis van het model draagt één opnamedatum (28 april 2026); later toegevoegde elementen dragen hun werkelijke datum, wijzigingen een datum wijziging."),
    ("Indicatie abstract object", "Alleen ingevuld (Ja) bij abstracte supertypen; concrete objecttypen voeren het veld niet."),
    ("Alias", "Alleen bij een echt naamsverschil met de bronregistratie."),
    ("Populatie en kwaliteit", "Populatie is op elk objecttype ingevuld; Kwaliteit alleen waar de bronregistratie een kwaliteitsnorm kent."),
]

LD_TEKST = """\
GBO publiceert hetzelfde model ook als **Linked Data**, volgens MIM 1.2
hoofdstuk 4 (metamodel in Linked Data) en bijlage 6.4 (transformatie naar
RDFS/OWL en SHACL). Elk objecttype en elk gegeven heeft een URI onder
`lod.gbo-semantiek.nl` (bijvoorbeeld {voorbeeld_uri}); de
MIM-metagegevens zijn daar RDF-eigenschappen in de namespace
`{mim_ns_gbo}`, die via `owl:equivalentProperty` zijn gekoppeld aan de
MIM-ontologie (`{mim_ns_std}`). De begrippen staan als SKOS onder
`begrippen.gbo-semantiek.nl`. Wie dat wil, kan de feiten in dit document
zo ook machinaal toetsen; de vindplaatsen staan in bijlage E. Afgeleide
technische vormen (het GraphQL-schema per bron, OWL, SHACL en JSON-LD)
worden daar genoemd, niet beschreven.
"""

KETEN_TEKST = """\
Dit document is gegenereerd en wordt niet met de hand bewerkt. De keten:

1. Het **informatiemodel** staat in LinkML, per deelmodel één bestand, met
   per element de MIM-metagegevens als annotaties.
2. Het **bronprofiel** van deze bron benoemt welke objecttypen de bron
   levert, de ingangen voor bevraging, benoemde queries en toetsen, en
   wat bewust wordt uitgesloten.
3. Uit beide wordt de **bronuitsnede** gematerialiseerd: dezelfde uitsnede
   waaruit ook het GraphQL-schema van deze bron wordt gegenereerd.
4. De generator zet de uitsnede om in dit document en voegt de
   handgeschreven context, toetsvragen en open punten toe.

Voettekst en bijlage E vermelden de modelversie, de commit van de
modelbron en de generatiedatum, zodat elke opmerking aan een exacte
modelstand is te koppelen.
"""

MIM_TERMEN = """\
**Objecttype**: een soort object in de werkelijkheid waarvan de
registratie gegevens bijhoudt (bijvoorbeeld Huwelijk). Een *abstract*
objecttype heeft zelf geen exemplaren; alleen zijn subtypen.

**Attribuutsoort**: een eigenschap van een objecttype met een datatype,
enumeratie of codelijst als waarde. **Relatiesoort**: een verband tussen
twee objecttypen; in dit document benoemd vanuit het bron-objecttype,
met de kardinaliteit aan de doelzijde.

**Gestructureerd datatype**: een samengesteld gegeven (zoals Verificatie
met datum en omschrijving) dat als geheel aan een attribuutsoort hangt.

**Kardinaliteit**: hoeveel waarden toegestaan zijn. 1 = precies één,
0..1 = hoogstens één, 1..\\* = één of meer, 0..\\* = nul of meer, 2 =
precies twee.

**Authentiek**: *Authentiek* = een authentiek gegeven in de zin van de
wet op de basisregistratie; *Basisgegeven* = gegeven uit de
basisregistratie zonder dat merk; *Landelijk kerngegeven* = gegeven uit
een landelijke voorziening of koppelvlak; *Overig* = al het andere,
waaronder GBO-eigen afleidingen.

**Indicatie materiële historie**: of de registratie bijhoudt wanneer een
waarde in de werkelijkheid gold. **Indicatie formele historie**: of de
registratie bijhoudt wanneer een waarde geregistreerd was. MIM 1.2
kondigt aan dat beide indicaties in MIM 2.x worden vervangen door
tijdlijnen voor geldigheid en registratie; GBO volgt die wijziging zodra
MIM 2 is vastgesteld.

**Herkomst**: de vindplaats in het brondocument waaruit het element is
overgenomen (bijvoorbeeld een categorie en groep van de persoonslijst).
**Herkomst definitie**: het document en de wettelijke grondslag waaruit
de definitie komt. **Populatie**: welke exemplaren onder het objecttype
vallen. **Unieke aanduiding**: het gegeven dat een exemplaar
identificeert.
"""

PAGINA_EINDE = ["```{=openxml}", '<w:p><w:r><w:br w:type="page"/></w:r></w:p>', "```", ""]


def sectie_einde_portret(footer_rid: str) -> list[str]:
    """Sluit de staande sectie af; wat volgt staat in de (liggende) eindsectie."""
    return [
        "```{=openxml}",
        f'<w:p><w:pPr><w:sectPr><w:footerReference w:type="default" r:id="{footer_rid}"/>'
        f'<w:pgSz w:w="{A4_B}" w:h="{A4_H}"/>'
        f'<w:pgMar w:top="{MARGE}" w:right="{MARGE}" w:bottom="{MARGE}" w:left="{MARGE}" '
        f'w:header="{MARGE_KOP}" w:footer="{MARGE_KOP}" w:gutter="0"/>'
        f'</w:sectPr></w:pPr></w:p>',
        "```", "",
    ]


# ---------------------------------------------------------------------------
# Diagram
# ---------------------------------------------------------------------------

def maak_diagram(u: Uitsnede, doel_png: Path, plantuml: str | None) -> bool:
    regels = ["@startuml", "!pragma layout elk", "skinparam dpi 140",
              "skinparam classAttributeIconSize 0", "skinparam shadowing false",
              "skinparam roundCorner 6", "skinparam ClassBackgroundColor #FAFAFA",
              "skinparam ClassBorderColor #555555", "skinparam ArrowColor #444444",
              "skinparam ArrowFontColor #333333", "skinparam ClassFontSize 12",
              "hide empty members", "hide circle", ""]
    for naam in u.objecttypen:
        k = u.klassen[naam]
        soort = "abstract class" if k.get("abstract") else "class"
        regels.append(f'{soort} {naam} <<{u.deelmodel(naam) or "model"}>>')
    for naam in u.datatypen_klassen:
        regels.append(f"class {naam} <<datatype>>")
    regels.append("")
    for naam in u.objecttypen:
        k = u.klassen[naam]
        if k.get("is_a") in u.objecttypen:
            regels.append(f"{k['is_a']} <|-- {naam}")
    regels.append("")
    for naam in u.objecttypen:
        for an, attr in u.attributen(naam).items():
            s = u.soort(attr)
            if s == "relatie":
                regels.append(f'{naam} --> "{u.kardinaliteit(attr)}" {attr["range"]} : {an}')
            elif s == "gegevensgroep":
                regels.append(f'{naam} ..> "{u.kardinaliteit(attr)}" {attr["range"]} : {an}')
    regels += ["", "@enduml", ""]
    puml = doel_png.with_suffix(".puml")
    doel_png.parent.mkdir(parents=True, exist_ok=True)
    puml.write_text("\n".join(regels), encoding="utf-8")
    if not plantuml:
        melding("WAARSCHUWING", "geen plantuml; diagram overgeslagen")
        return False
    uit = subprocess.run([plantuml, "-tpng", "-o", str(doel_png.parent.resolve()), str(puml)],
                         capture_output=True, text=True)
    if uit.returncode != 0 or not puml.with_suffix(".png").exists():
        melding("WAARSCHUWING", f"plantuml mislukt: {uit.stderr.strip()[:300]}")
        return False
    gemaakt = puml.with_suffix(".png")
    if gemaakt != doel_png:
        gemaakt.replace(doel_png)
    puml.unlink()
    return True


# ---------------------------------------------------------------------------
# Word-sjabloon (reference.docx) opbouwen
# ---------------------------------------------------------------------------

FOOTER_STAAND = "rIdGboFooterStaand"
FOOTER_LIGGEND = "rIdGboFooterLiggend"


def _footer_xml(identiteit: str, tabpos: int) -> str:
    rpr = '<w:rPr><w:color w:val="595959"/><w:sz w:val="16"/><w:szCs w:val="16"/></w:rPr>'
    ident = (identiteit.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<w:p><w:pPr><w:tabs><w:tab w:val="right" w:pos="{tabpos}"/></w:tabs>'
        '<w:spacing w:before="0" w:after="0"/></w:pPr>'
        f'<w:r>{rpr}<w:t xml:space="preserve">{ident}</w:t></w:r>'
        f'<w:r>{rpr}<w:tab/><w:t xml:space="preserve">Pagina </w:t></w:r>'
        f'<w:fldSimple w:instr=" PAGE "><w:r>{rpr}<w:t>1</w:t></w:r></w:fldSimple>'
        f'<w:r>{rpr}<w:t xml:space="preserve"> van </w:t></w:r>'
        f'<w:fldSimple w:instr=" NUMPAGES "><w:r>{rpr}<w:t>1</w:t></w:r></w:fldSimple>'
        '</w:p></w:ftr>'
    )


def bouw_reference_docx(doel: Path, identiteit: str, pandoc: str) -> None:
    """Pandoc-standaardsjabloon + GBO-huisstijl, zonder binair bestand in de repo."""
    basis = doel.with_name("pandoc-standaard.docx")
    subprocess.run([pandoc, "-o", str(basis), "--print-default-data-file", "reference.docx"],
                   check=True)
    with zipfile.ZipFile(basis) as zin:
        delen = {naam: zin.read(naam) for naam in zin.namelist()}
    basis.unlink()

    styles = delen["word/styles.xml"].decode("utf-8")
    # Taal, lettertype (vast, niet thema-afhankelijk) en basisgrootte (11 pt).
    styles = styles.replace('w:lang w:val="en-US"', 'w:lang w:val="nl-NL"')
    styles = re.sub(r'<w:rFonts w:asciiTheme="minorHAnsi"[^>]*/>',
                    '<w:rFonts w:ascii="Calibri" w:eastAsia="Calibri" w:hAnsi="Calibri" w:cs="Calibri" />',
                    styles)
    styles = re.sub(r'<w:rFonts w:asciiTheme="majorHAnsi"[^>]*/>',
                    '<w:rFonts w:ascii="Calibri Light" w:eastAsia="Calibri Light" '
                    'w:hAnsi="Calibri Light" w:cs="Calibri Light" />', styles)
    styles = re.sub(r'(<w:rPrDefault>.*?)<w:sz w:val="24" />\s*<w:szCs w:val="24" />',
                    r'\1<w:sz w:val="22" /><w:szCs w:val="22" />', styles, count=1, flags=re.S)
    # Koppen en titel in huisstijlblauw.
    styles = re.sub(r'<w:color w:val="(0F4761|365F91)"[^/]*/>', f'<w:color w:val="{HUISSTIJL_BLAUW}"/>', styles)

    def patch_stijl(xml: str, stijl: str, fn) -> str:
        m = re.search(rf'<w:style [^>]*w:styleId="{stijl}".*?</w:style>', xml, re.S)
        if not m:
            melding("WAARSCHUWING", f"stijl {stijl} niet in sjabloon")
            return xml
        return xml[:m.start()] + fn(m.group(0)) + xml[m.end():]

    def titel(blok: str) -> str:
        blok = blok.replace('<w:jc w:val="center" />', '<w:jc w:val="left" />')
        return blok.replace('<w:sz w:val="56" />',
                            f'<w:color w:val="{HUISSTIJL_BLAUW}"/><w:b/><w:sz w:val="52" />')

    def subtitel(blok: str) -> str:
        return blok.replace('<w:jc w:val="center" />', '<w:jc w:val="left" />')

    def tabelstijl(blok: str) -> str:
        randen = ('<w:tblBorders>'
                  '<w:top w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/>'
                  '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/>'
                  '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="D9D9D9"/>'
                  '</w:tblBorders>')
        blok = blok.replace('<w:tblPr>', '<w:rPr><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>'
                            '<w:tblPr>' + randen, 1)
        blok = blok.replace('<w:tblCellMar>',
                            '<w:tblCellMar><w:top w:w="40" w:type="dxa" /><w:bottom w:w="40" w:type="dxa" />', 1)
        blok = re.sub(r'<w:tblStylePr w:type="firstRow">.*?</w:tblStylePr>',
                      '<w:tblStylePr w:type="firstRow"><w:rPr><w:b/><w:color w:val="FFFFFF"/></w:rPr>'
                      f'<w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="{HUISSTIJL_BLAUW}"/>'
                      '<w:vAlign w:val="bottom"/></w:tcPr></w:tblStylePr>', blok, flags=re.S)
        return blok

    def abstract(blok: str) -> str:
        # Colofon: links uitgelijnd, zonder inspringing, iets kleiner.
        blok = re.sub(r'<w:ind [^>]*/>', '', blok)
        blok = re.sub(r'<w:jc [^>]*/>', '<w:jc w:val="left" />', blok)
        return blok.replace('</w:style>', '<w:rPr><w:sz w:val="20" /><w:szCs w:val="20" /></w:rPr></w:style>') \
            if '<w:rPr>' not in blok else blok

    def abstract_titel(blok: str) -> str:
        blok = re.sub(r'<w:jc [^>]*/>', '<w:jc w:val="left" />', blok)
        return blok

    styles = patch_stijl(styles, "Title", titel)
    styles = patch_stijl(styles, "Subtitle", subtitel)
    styles = patch_stijl(styles, "Date", subtitel)
    styles = patch_stijl(styles, "Abstract", abstract)
    styles = patch_stijl(styles, "AbstractTitle", abstract_titel)
    styles = patch_stijl(styles, "Table", tabelstijl)
    delen["word/styles.xml"] = styles.encode("utf-8")

    # Word moet bij openen de velden (inhoudsopgave, paginatelling) bijwerken.
    settings = delen["word/settings.xml"].decode("utf-8")
    settings = settings.replace('<w:themeFontLang w:val="en-US" />', '<w:themeFontLang w:val="nl-NL" />')
    if "updateFields" not in settings:
        settings = settings.replace("<w:footnotePr>", '<w:updateFields w:val="true" /><w:footnotePr>', 1)
    delen["word/settings.xml"] = settings.encode("utf-8")

    # Eindsectie: liggend A4 (de bijlagen), met eigen voettekst. De staande
    # hoofdtekst wordt afgesloten met een inline sectPr (sectie_einde_portret).
    document = delen["word/document.xml"].decode("utf-8")
    sectpr = (f'<w:sectPr><w:footerReference w:type="default" r:id="{FOOTER_LIGGEND}"/>'
              '<w:footnotePr><w:numRestart w:val="eachSect" /></w:footnotePr>'
              f'<w:pgSz w:w="{A4_H}" w:h="{A4_B}" w:orient="landscape"/>'
              f'<w:pgMar w:top="{MARGE}" w:right="{MARGE}" w:bottom="{MARGE}" w:left="{MARGE}" '
              f'w:header="{MARGE_KOP}" w:footer="{MARGE_KOP}" w:gutter="0"/></w:sectPr>')
    document, n = re.subn(r"<w:sectPr>.*?</w:sectPr>", sectpr, document, count=1, flags=re.S)
    if n != 1:
        fout("geen sectPr in pandoc-standaardsjabloon gevonden")
    delen["word/document.xml"] = document.encode("utf-8")

    delen["word/footer1.xml"] = _footer_xml(identiteit, A4_B - 2 * MARGE).encode("utf-8")
    delen["word/footer2.xml"] = _footer_xml(identiteit, A4_H - 2 * MARGE).encode("utf-8")

    rels = delen["word/_rels/document.xml.rels"].decode("utf-8")
    rel_type = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer"
    rels = rels.replace("</Relationships>",
                        f'<Relationship Type="{rel_type}" Id="{FOOTER_STAAND}" Target="footer1.xml" />'
                        f'<Relationship Type="{rel_type}" Id="{FOOTER_LIGGEND}" Target="footer2.xml" />'
                        "</Relationships>")
    delen["word/_rels/document.xml.rels"] = rels.encode("utf-8")

    ct = delen["[Content_Types].xml"].decode("utf-8")
    ct_footer = "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"
    ct = ct.replace("</Types>",
                    f'<Override PartName="/word/footer1.xml" ContentType="{ct_footer}" />'
                    f'<Override PartName="/word/footer2.xml" ContentType="{ct_footer}" />'
                    "</Types>")
    delen["[Content_Types].xml"] = ct.encode("utf-8")

    with zipfile.ZipFile(doel, "w", zipfile.ZIP_DEFLATED) as zuit:
        for naam, inhoud in delen.items():
            zuit.writestr(naam, inhoud)


# ---------------------------------------------------------------------------
# Document samenstellen
# ---------------------------------------------------------------------------

class Document:
    def __init__(self, u: Uitsnede, meta: dict, secties: dict, ctx: dict,
                 herleiding: dict, changelog: list):
        self.u = u
        self.meta = meta
        self.secties = secties
        self.ctx = ctx
        self.herleiding = herleiding
        self.changelog = changelog
        self.r: list[str] = []

    def w(self, *regels: str) -> None:
        self.r.extend(regels)

    def tekst(self, blok: str) -> None:
        self.r.extend(blok.rstrip("\n").split("\n"))
        self.r.append("")

    # -- voorwerk -----------------------------------------------------------

    def kop(self) -> None:
        p, c = self.u.profiel, self.ctx
        contact = self.meta.get("contact") or {}
        rijen = [
            ("Bron", f"{p['bron']}, {p['titel']}"),
            ("Bronhouder", self.meta.get("bronhouder") or LEEG),
            ("Status", f"{self.meta.get('status', 'consultatieversie')}, ronde {self.meta.get('consultatieronde', 1)}"),
            ("Reactietermijn", self.meta.get("reactietermijn") or LEEG),
            ("Contact", ", ".join(dict.fromkeys(str(v) for v in (contact.get("naam"), contact.get("organisatie"), contact.get("email")) if v)) or LEEG),
            ("Modelversie", c["versie"]),
            ("Modelstand", c["modelstand"]),
            ("Gegenereerd", f"{c['datum']} door {Path(sys.argv[0]).name}"),
            ("Licentie", "EUPL-1.2"),
        ]
        # Het colofon gaat als 'abstract' mee in het titelblok: pandoc zet het
        # vóór de inhoudsopgave, zodat voorblad = titel + colofon + inhoud.
        colofon = [f"  **{md(k)}:** {md(v)}\\" for k, v in rijen]
        colofon.append("  Dit document is gegenereerd uit het GBO-informatiemodel en het "
                       "bronprofiel van deze bron. Reacties graag als Word-opmerking of in "
                       "de reactietabel van hoofdstuk 4.")
        self.w("---",
               f"title: \"GBO Bronspecificatie {p['bron']}\"",
               f"subtitle: \"{p['titel']}, {self.meta.get('status', 'consultatieversie')}\"",
               f"date: \"{c['datum_lang']}\"",
               "lang: nl-NL",
               "toc-title: Inhoud",
               "abstract-title: Colofon",
               "abstract: |",
               *colofon,
               "---", "")
        self.r += PAGINA_EINDE

    def leeswijzer(self) -> None:
        self.w("# Leeswijzer", "")
        self.tekst(LEESWIJZER)
        self.r += PAGINA_EINDE

    # -- 1 Samenvatting -------------------------------------------------------

    def samenvatting(self) -> None:
        u, p = self.u, self.u.profiel
        t = u.tellingen()
        self.w("# 1 Samenvatting", "")
        self.w(f"{md(p.get('beschrijving') or '')}", "")
        self.w(f"GBO ontsluit uit de {md(p['titel'])} ({md(p['bron'])}):", "")
        self.r += tabel(["Onderdeel", "Aantal", "Toelichting"], [
            ("Objecttypen", t["objecttypen"], f"waarvan {t['abstract']} abstract (supertypen zonder eigen exemplaren)"),
            ("Attribuutsoorten", t["attribuutsoorten"], "eigen attributen van de objecttypen, inclusief gestructureerde datatypen"),
            ("Relatiesoorten", t["relatiesoorten"], "verbanden tussen objecttypen binnen deze bron"),
            ("Sleutelverwijzingen", t["sleutelreferenties"], "relaties naar objecttypen buiten deze bron, geleverd als sleutel"),
            ("Gestructureerde datatypen", t["gegevensgroepen"], ", ".join(u.datatypen_klassen) or LEEG),
            ("Enumeraties", t["enumeraties"], ", ".join(u.enums) or LEEG),
            ("Codelijsten", t["codelijsten"], ", ".join(u.typenaam({"range": n}) for n in u.codelijsten) or LEEG),
        ], [3, 1, 8])
        ingangen = p.get("ingangen") or []
        self.w("**Bevraging.** " + (
            f"Ingang: {md(', '.join(ingangen))}" if ingangen else "Geen directe ingang") +
            (", alleen op de natuurlijke sleutel, zonder lijstbevraging." if p.get("lijstQueries") is False
             else ".") + (f" Benoemde queries: {md(', '.join(q['naamQuery'] for q in p.get('queries') or []))}."
                          if p.get("queries") else "") +
            (f" Toetsen: {md(', '.join(q['naamQuery'] for q in p.get('toetsen') or []))}."
             if p.get("toetsen") else ""), "")
        uitsl = [f"{x['objecttype']}.{a}" for x in p.get("uitsluitingen") or [] for a in x.get("attributen") or []]
        weg = [f"{x['objecttype']}.{x['relatie']}" for x in p.get("relatieAfhandeling") or []
               if x.get("afhandeling") == "weglaten"]
        if uitsl or weg:
            self.w("**Bewust niet ontsloten.** " +
                   (f"Attributen: {md(', '.join(uitsl))}. " if uitsl else "") +
                   (f"Relaties: {md(', '.join(weg))}. " if weg else "") +
                   "Zie 3.7 voor de redenen.", "")
        rijen = []
        for naam in u.objecttypen:
            k = u.klassen[naam]
            n_attr = sum(1 for a in u.attributen(naam).values() if u.soort(a) in ("attribuut", "gegevensgroep"))
            n_rel = sum(1 for a in u.attributen(naam).values() if u.soort(a) in ("relatie", "sleutel"))
            if naam in ingangen:
                rol = "ingang"
            elif naam not in (p.get("objecttypen") or []):
                rol = "supertype, automatisch meegenomen"
            elif k.get("abstract"):
                rol = "abstract supertype"
            elif k.get("is_a"):
                rol = f"subtype van {k['is_a']}"
            else:
                rol = "eigen objecttype"
            rijen.append((naam, rol, n_attr, n_rel, (k.get("annotations") or {}).get("mim:herkomst") or LEEG))
        self.r += tabel(["Objecttype", "Rol", "Attr.", "Rel.", "Herkomst"], rijen, [4, 4.5, 1.3, 1.3, 5])
        self.r += PAGINA_EINDE

    # -- 2 Totstandkoming -----------------------------------------------------

    def totstandkoming(self) -> None:
        u, c = self.u, self.ctx
        self.w("# 2 Totstandkoming", "")
        self.w("## 2.1 GBO in het kort", "")
        self.tekst(GBO_KORT)
        self.w("## 2.2 Bronnenkeuze", "")
        self.w("GBO put per registratie uit bronnen in vier lagen:", "")
        self.r += tabel(["Laag", "Soort bron", "Wat", "Levert"],
                        [list(x) for x in LAGEN], [1, 2, 6, 4])
        self.tekst(BESLISREGELS)
        self.w("## 2.3 Brondocumenten voor deze bron", "")
        docs = self.meta.get("brondocumenten") or []
        if docs:
            rijen = []
            for d in docs:
                versie = " ".join(str(x) for x in (d.get("versie"), d.get("datum")) if x)
                rijen.append((d.get("laag", ""), d.get("titel", ""), versie or LEEG,
                              d.get("uitgever", ""), d.get("gebruik", "")))
            self.r += tabel(["Laag", "Document", "Versie, datum", "Uitgever", "Gebruik in GBO"],
                            rijen, [1, 4, 2, 2, 6])
            for d in docs:
                if d.get("toelichting"):
                    self.w(f"*{md(d['titel'])}*: {md(d['toelichting'])}", "")
            self.w("Vindplaatsen staan in bijlage E.", "")
        else:
            self.w("*Geen brondocumenten opgegeven in het tekstbestand van deze bron.*", "")
        if self.secties.get("context"):
            self.w(f"## 2.4 Deze bron in GBO", "")
            self.r += self.secties["context"] + [""]
        self.w("## 2.5 Conformiteit met MIM 1.2", "")
        self.tekst(MIM_TEKST)
        self.r += tabel(["Keuze", "Invulling in GBO"], [list(x) for x in MIM_KEUZES], [2, 9])
        self.w("## 2.6 Publicatie als Linked Data", "")
        voorbeeld = u.klasse_uri(u.objecttypen[0]) if u.objecttypen else BASE_LOD
        self.tekst(LD_TEKST.format(voorbeeld_uri=voorbeeld, mim_ns_gbo=MIM_NS_GBO,
                                   mim_ns_std=MIM_NS_BP4MC2))
        self.w("## 2.7 Van model naar dit document", "")
        self.tekst(KETEN_TEKST)
        self.r += PAGINA_EINDE

    # -- 3 Specificatie -------------------------------------------------------

    def specificatie(self, diagram: str | None) -> None:
        u = self.u
        self.w("# 3 Specificatie", "")
        self.w("## 3.1 Overzicht", "")
        if diagram:
            self.w(f"![Overzicht van de objecttypen in de bronuitsnede {md(u.profiel['bron'])}]({diagram}){{width=100%}}", "")
        self.w("Objecttypen in deze bron, in de volgorde van het bronprofiel; "
               "supertypen die het model automatisch meeneemt staan achteraan.", "")
        for naam in u.objecttypen:
            k = u.klassen[naam]
            extra = []
            if k.get("abstract"):
                extra.append("abstract")
            if k.get("is_a"):
                extra.append(f"subtype van {k['is_a']}")
            self.w(f"- **{md(naam)}**{' (' + md(', '.join(extra)) + ')' if extra else ''}: {md(eerste_zin(u.definitie(k)))}")
        self.w("")
        self.w("## 3.2 Objecttypen", "")
        for naam in u.objecttypen:
            self.objecttype(naam)
        if u.datatypen_klassen or u.mixins:
            self.w("## 3.3 Gestructureerde datatypen en patronen", "")
            for naam in u.datatypen_klassen:
                self.objecttype(naam, stereotype="Gestructureerd datatype")
            for naam in u.mixins:
                self.patroon(naam)
        self.w("## 3.4 Enumeraties", "")
        if not u.enums:
            self.w("*Geen enumeraties in deze bron.*", "")
        for naam, e in u.enums.items():
            ann = e.get("annotations") or {}
            self.w(f"### {md(naam)}", "")
            self.w(f"{md(u.definitie(e))}" + (f" Herkomst: {md(ann['mim:herkomst'])}." if ann.get("mim:herkomst") else ""), "")
            rijen = []
            for wnaam, w in (e.get("permissible_values") or {}).items():
                w = w or {}
                rijen.append((wnaam, w.get("description") or "", " ".join(w.get("comments") or [])))
            self.r += tabel(["Waarde", "Betekenis", "Toelichting, broncode"], rijen, [3, 6, 5])
        self.w("## 3.5 Codelijsten", "")
        if not u.codelijsten:
            self.w("*Geen externe codelijsten in deze bron.*", "")
        else:
            self.w("Codelijsten worden buiten GBO beheerd; GBO neemt de code over en "
                   "verwijst naar de beheerder. Details in bijlage C.", "")
            rijen = []
            for naam, t in u.codelijsten.items():
                rijen.append((u.typenaam({"range": naam}), t.get("description") or "",
                              rauw(", ".join(f"<{s}>" for s in t.get("see_also") or [])) if t.get("see_also") else LEEG))
            self.r += tabel(["Codelijst", "Omschrijving", "Beheerder, vindplaats"], rijen, [3, 7, 5])
        self.bevraging()
        self.afbakening()
        self.r += PAGINA_EINDE

    def objecttype(self, naam: str, stereotype: str = "Objecttype") -> None:
        u = self.u
        k = u.klassen[naam]
        ann = k.get("annotations") or {}
        self.w(f"### {md(naam)}", "")
        regel = [f"«{stereotype}»"]
        if k.get("abstract"):
            regel.append("abstract")
        if k.get("is_a"):
            regel.append(f"subtype van {k['is_a']}")
        sub = u.subtypen(naam)
        if sub:
            regel.append(f"subtypen: {', '.join(sub)}")
        if u.deelmodel(naam):
            regel.append(f"deelmodel {u.deelmodel(naam)}")
        self.w(f"*{md(', '.join(regel))}*", "")
        rijen = [("Naam", naam), ("Definitie", u.definitie(k) or LEEG)]
        if k.get("aliases"):
            rijen.append(("Alias", ", ".join(k["aliases"])))
        rijen.append(("Herkomst", ann.get("mim:herkomst") or LEEG))
        rijen.append(("Herkomst definitie", eerste_zin(ann.get("mim:herkomstDefinitie"), 220) or LEEG))
        if ann.get("mim:populatie"):
            rijen.append(("Populatie", ann["mim:populatie"]))
        if ann.get("mim:kwaliteit"):
            rijen.append(("Kwaliteit", ann["mim:kwaliteit"]))
        if stereotype == "Objecttype":
            rijen.append(("Unieke aanduiding", ann.get("mim:uniekeAanduiding") or self._unieke_aanduiding(naam) or "geen"))
        if k.get("abstract"):
            rijen.append(("Indicatie abstract object", "Ja"))
        if k.get("mixins"):
            rijen.append(("Patronen", ", ".join(k["mixins"])))
        b = u.begrip(k)
        if b:
            rijen.append(("Begrip", rauw(f"<{b}>")))
        self.r += tabel(["MIM-metagegeven", "Waarde"], rijen, [3, 11])
        for c in k.get("comments") or []:
            self.w(f"*Toelichting.* {md(c)}", "")
        geerfd = u.geerfde_namen(naam)
        if geerfd:
            delen = [f"{v}: {', '.join(a) if a else '(geen eigen attributen)'}" for v, a in geerfd]
            self.w(f"Erft daarnaast van {md('; '.join(delen))}.", "")
        attrs = u.attributen(naam)
        a_rijen, r_rijen = [], []
        for an, attr in attrs.items():
            aann = attr.get("annotations") or {}
            s = u.soort(attr)
            if s in ("attribuut", "gegevensgroep"):
                a_rijen.append((an, u.definitie(attr), u.typenaam(attr), u.kardinaliteit(attr),
                                aann.get("mim:authentiek") or LEEG, aann.get("mim:herkomst") or LEEG))
            elif s == "relatie":
                r_rijen.append((an, attr.get("range"), u.kardinaliteit(attr),
                                aann.get("mim:authentiek") or LEEG, aann.get("mim:herkomst") or LEEG,
                                u.definitie(attr)))
            elif s == "sleutel":
                r_rijen.append((an, f"{aann['gbo:sleutelreferentie']} (buiten deze bron; geleverd als sleutel van type {attr.get('range')})",
                                u.kardinaliteit(attr), aann.get("mim:authentiek") or LEEG,
                                aann.get("mim:herkomst") or LEEG, u.definitie(attr)))
            elif s == "inverse":
                r_rijen.append((f"{an} (afgeleide inverse van {aann['gbo:inverseVan']})", attr.get("range"),
                                u.kardinaliteit(attr), LEEG, "GBO-afleiding", u.definitie(attr)))
        if a_rijen:
            self.w("**Attribuutsoorten**", "")
            self.r += tabel(["Naam", "Definitie", "Type", "Kard.", "Authentiek", "Herkomst"],
                            a_rijen, [3.0, 5.4, 2.4, 1.4, 3.0, 2.8])
        if r_rijen:
            self.w("**Relatiesoorten**", "")
            self.r += tabel(["Naam", "Doel", "Kard.", "Authentiek", "Herkomst", "Definitie"],
                            r_rijen, [3.2, 3.2, 1.4, 3.0, 3.0, 6.2])
        if not a_rijen and not r_rijen:
            self.w("*Geen eigen attribuut- of relatiesoorten; zie de supertypen.*", "")

    def _unieke_aanduiding(self, naam: str) -> str:
        k = self.u.klassen[naam]
        for an, a in (k.get("attributes") or {}).items():
            if a.get("identifier"):
                return an
        uk = k.get("unique_keys") or {}
        for v in uk.values():
            return ", ".join(v.get("unique_key_slots") or [])
        return ""

    def patroon(self, naam: str) -> None:
        u = self.u
        k = u.klassen[naam]
        self.w(f"### Patroon {md(naam)}", "")
        self.w(f"{md(u.definitie(k))}", "")
        for c in k.get("comments") or []:
            self.w(f"*Toelichting.* {md(c)}", "")
        dragers = [n for n in u.objecttypen if naam in ((u.klassen[n]).get("mixins") or [])]
        if dragers:
            self.w(f"Gedragen door: {md(', '.join(dragers))}.", "")
        rijen = [(an, u.definitie(a), u.typenaam(a), u.kardinaliteit(a))
                 for an, a in u.attributen(naam).items()]
        self.r += tabel(["Naam", "Definitie", "Type", "Kard."], rijen, [4, 8, 3, 1.5])

    def bevraging(self) -> None:
        u, p = self.u, self.u.profiel
        self.w("## 3.6 Bevraging", "")
        ingangen = p.get("ingangen") or []
        if ingangen:
            for ing in ingangen:
                sleutel = self._unieke_aanduiding(ing) or "natuurlijke sleutel"
                self.w(f"- **Ingang {md(ing)}**, bevraagbaar op {md(sleutel)}"
                       + (" (geen lijstbevraging)." if p.get("lijstQueries") is False else " en als lijst."))
            self.w("")
        for z in p.get("zoeksleutels") or []:
            self.w(f"- Zoeksleutels op {md(z['objecttype'])}: {md(', '.join(z.get('sleutels') or []))}.")
        if p.get("zoeksleutels"):
            self.w("")
        if p.get("queries"):
            self.w("**Benoemde queries**", "")
            rijen = []
            for q in p["queries"]:
                pars = ", ".join((x if isinstance(x, str) else x.get("naam", "")) for x in q.get("parameters") or [])
                rijen.append((q["naamQuery"], q.get("levert", ""), ", ".join(q.get("vanaf") or []), pars,
                              q.get("toelichting") or ""))
            self.r += tabel(["Query", "Levert", "Vanaf", "Parameters", "Toelichting"], rijen, [3, 3, 3, 3, 6])
        if p.get("toetsen"):
            self.w("**Toetsen (ja/nee-vragen)**", "")
            rijen = []
            for q in p["toetsen"]:
                pars = ", ".join((x if isinstance(x, str) else x.get("naam", "")) for x in q.get("parameters") or [])
                rijen.append((q["naamQuery"], pars, ", ".join(q.get("raadpleegt") or []),
                              q.get("uitkomst") or "", q.get("toelichting") or ""))
            self.r += tabel(["Toets", "Parameters", "Raadpleegt", "Uitkomst", "Toelichting"], rijen, [3, 3, 3, 4, 5])
        self.w(f"Het bijbehorende GraphQL-schema staat als {md(self.ctx['versie'])}/graphql/{md(p['bron'].lower())}.graphql "
               f"in de publicatierepository (bijlage E).", "")

    def afbakening(self) -> None:
        u, p = self.u, self.u.profiel
        self.w("## 3.7 Afbakening", "")
        rijen = []
        for x in p.get("uitsluitingen") or []:
            for a in x.get("attributen") or []:
                rijen.append((x["objecttype"], a, x.get("toelichting") or LEEG))
        if rijen:
            self.w("**Niet geleverde attributen**", "")
            self.r += tabel(["Objecttype", "Attribuut", "Reden"], rijen, [3, 3, 8])
        rijen = []
        for x in p.get("relatieAfhandeling") or []:
            hoe = x.get("afhandeling", "")
            if hoe == "vernauwen":
                hoe = f"vernauwd naar {x.get('naar')}"
            if x.get("inverse") is False:
                hoe += ", zonder inverse"
            rijen.append((x["objecttype"], x["relatie"], hoe, x.get("toelichting") or LEEG))
        if rijen:
            self.w("**Afwijkend afgehandelde relaties**", "")
            self.r += tabel(["Objecttype", "Relatie", "Afhandeling", "Reden"], rijen, [3, 3, 3, 7])
        rijen = []
        for naam in u.objecttypen:
            for an, attr in u.attributen(naam).items():
                if u.soort(attr) == "sleutel":
                    aann = attr.get("annotations") or {}
                    rijen.append((naam, an, aann["gbo:sleutelreferentie"], attr.get("range")))
        if rijen:
            self.w("**Relaties naar objecttypen buiten deze bron**", "")
            self.w("Deze relaties worden geleverd als sleutel van het doelobject; het "
                   "doelobject zelf komt uit een andere bron.", "")
            self.r += tabel(["Objecttype", "Relatie", "Doelobjecttype", "Sleuteltype"], rijen, [3, 3, 4, 3])
        rest = u.niet_geleverd()
        if rest:
            self.w("**Objecttypen uit het deelmodel van de ingang die deze bron niet levert**", "")
            self.w(md(", ".join(rest)) + ".", "")

    # -- 4 Toetsvragen --------------------------------------------------------

    def toetsvragen(self) -> None:
        self.w("# 4 Toetsvragen en reacties", "")
        groepen = parse_toetsvragen(self.secties.get("toetsvragen") or [])
        if not groepen:
            self.w("*Voor deze bron zijn nog geen toetsvragen opgesteld.*", "")
        n = 0
        for kop, vragen in groepen:
            self.w(f"**{md(kop)}**", "")
            for v in vragen:
                n += 1
                self.w(f"**T{n}.** {v}", "")
        self.w("## Reactietabel", "")
        self.w("Vul per opmerking een regel in, of gebruik Word-opmerkingen in de tekst.", "")
        leeg = rauw(" ")
        self.r += tabel(["Nr", "Objecttype.gegeven of toetsvraag", "Opmerking", "Voorstel", "Indiener"],
                        [(str(i), leeg, leeg, leeg, leeg) for i in range(1, 9)], [1, 4, 6, 6, 3])

    # -- Bijlagen -------------------------------------------------------------

    def bijlage_a(self) -> None:
        u = self.u
        self.w("# Bijlage A. Volledige MIM-metagegevens", "")
        self.w("Per objecttype alle vastgelegde metagegevens die niet in de "
               "hoofdtekst staan. Elk element heeft in de Linked Data een URI van "
               "de vorm lod.gbo-semantiek.nl/\\<deelmodel\\>/\\<Objecttype\\>/\\<element\\>, "
               f"bijvoorbeeld {md(u.attribuut_uri(u.objecttypen[0], next(iter(u.attributen(u.objecttypen[0])), 'x')) if u.objecttypen else '')}. "
               "Patronen van datatypen staan in bijlage C.", "")
        for naam in u.objecttypen + u.datatypen_klassen:
            k = u.klassen[naam]
            ann = k.get("annotations") or {}
            self.w(f"## {md(naam)}", "")
            kop = [f"URI: {u.klasse_uri(naam)}"]
            for label, sleutel in (("Datum opname", "mim:datumOpname"), ("Datum wijziging", "mim:datumWijziging"),
                                   ("Kwaliteit", "mim:kwaliteit")):
                if ann.get(sleutel):
                    kop.append(f"{label}: {ann[sleutel]}")
            self.w(md("; ".join(kop)) + ".", "")
            rijen = []
            for an, attr in u.attributen(naam).items():
                aann = attr.get("annotations") or {}
                soort = {"attribuut": "Attribuutsoort", "gegevensgroep": "Attribuutsoort (gestructureerd)",
                         "relatie": "Relatiesoort", "sleutel": "Relatiesoort (sleutel)",
                         "inverse": "Relatiesoort (inverse)"}[u.soort(attr)]
                opname = " / ".join(str(x) for x in (aann.get("mim:datumOpname"), aann.get("mim:datumWijziging")) if x)
                lengte = str(aann.get("mim:lengte") or "")
                rijen.append((an, soort, ja_nee(aann.get("mim:indicatieMaterieleHistorie")),
                              ja_nee(aann.get("mim:indicatieFormeleHistorie")),
                              aann.get("mim:kardinaliteit") or u.kardinaliteit(attr),
                              opname or LEEG, lengte or LEEG,
                              " ".join(attr.get("comments") or []) or LEEG))
            if rijen:
                self.r += tabel(["Element", "Soort", "Mat. hist.", "Form. hist.", "Kard. (bron -> doel)",
                                 "Opname / wijziging", "Lengte", "Toelichting"],
                                rijen, [4, 3.2, 1.3, 1.3, 2.2, 2.4, 1.3, 10])
            else:
                self.w("*Geen eigen elementen.*", "")

    def bijlage_b(self) -> None:
        u = self.u
        self.w("# Bijlage B. Herleiding per element", "")
        self.w("Per element de herkomst in het brondocument en, waar bekend, het "
               "corresponderende veld in het koppelvlak. De koppelvlakkolom komt uit "
               "de GBO-compatibiliteitsanalyse van het koppelvlak; de status geeft "
               "aan of naam en betekenis overeenkomen (match), de naam verschilt "
               "(rename) of de dekking gedeeltelijk is (partial, conflict).", "")
        bronnen = sorted({kv for lijst in self.herleiding.values() for (_, _, kv) in lijst})
        if bronnen:
            self.w(f"Koppelvlakken: {md('; '.join(bronnen))}.", "")
        else:
            self.w("*Voor deze bron is geen koppelvlakmapping beschikbaar; de kolom Koppelvlak blijft leeg.*", "")
        for naam in u.objecttypen + u.datatypen_klassen:
            k = u.klassen[naam]
            ann = k.get("annotations") or {}
            self.w(f"## {md(naam)}", "")
            if ann.get("mim:herkomstDefinitie"):
                self.w(f"*Herkomst definitie (objecttype):* {md(ann['mim:herkomstDefinitie'])}", "")
            rijen = []
            for an, attr in u.attributen(naam).items():
                aann = attr.get("annotations") or {}
                hd = aann.get("mim:herkomstDefinitie") or "zie objecttype"
                treffers = self.herleiding.get((naam, an)) or []
                if not treffers:
                    for v in u.voorouders(naam):
                        treffers = self.herleiding.get((v, an)) or []
                        if treffers:
                            break
                kv = "; ".join(f"{veld} ({status})" for veld, status, _ in treffers) or LEEG
                rijen.append((an, aann.get("mim:herkomst") or LEEG, hd, kv))
            if rijen:
                self.r += tabel(["Element", "Herkomst", "Herkomst definitie", "Koppelvlak (status)"],
                                rijen, [4, 4, 8, 6])
            else:
                self.w("*Geen eigen elementen.*", "")

    def bijlage_c(self) -> None:
        u = self.u
        self.w("# Bijlage C. Datatypen en codelijsten", "")
        self.w("## Datatypen", "")
        rijen = []
        for naam, t in u.basistypen.items():
            ann = t.get("annotations") or {}
            rijen.append((naam, t.get("typeof") or t.get("base") or "", t.get("description") or "",
                          rauw(code(t.get("pattern"))) if t.get("pattern") else LEEG,
                          ann.get("mim:herkomst") or LEEG, " ".join(t.get("comments") or []) or LEEG))
        self.r += tabel(["Datatype", "Basis", "Definitie", "Patroon", "Herkomst", "Toelichting"],
                        rijen, [3, 2, 7, 3, 3, 6])
        self.w("## Codelijsten", "")
        rijen = []
        for naam, t in u.codelijsten.items():
            ann = t.get("annotations") or {}
            rijen.append((u.typenaam({"range": naam}), naam, t.get("description") or "",
                          rauw(code(t.get("pattern"))) if t.get("pattern") else LEEG,
                          rauw(", ".join(f"<{s}>" for s in t.get("see_also") or [])) if t.get("see_also") else LEEG,
                          " ".join(t.get("comments") or []) or LEEG))
        if rijen:
            self.r += tabel(["Codelijst", "Modelnaam", "Definitie", "Patroon", "Beheerder, vindplaats", "Toelichting"],
                            rijen, [3, 3, 7, 2, 5, 5])
        else:
            self.w("*Geen externe codelijsten.*", "")
        self.w("## Enumeraties: herkomst en toelichting", "")
        rijen = []
        for naam, e in u.enums.items():
            ann = e.get("annotations") or {}
            rijen.append((naam, ann.get("mim:herkomst") or LEEG, ann.get("mim:herkomstDefinitie") or LEEG,
                          " ".join(e.get("comments") or []) or LEEG, rauw(f"<{u.begrip(e)}>") if u.begrip(e) else LEEG))
        if rijen:
            self.r += tabel(["Enumeratie", "Herkomst", "Herkomst definitie", "Toelichting", "Begrip"],
                            rijen, [3, 4, 6, 7, 4])

    def bijlage_d(self) -> None:
        self.w("# Bijlage D. Wijzigingen en open punten", "")
        self.w(f"## Wijzigingen ten opzichte van {md(self.ctx.get('vorige_versie') or 'de vorige modelversie')}", "")
        if self.changelog:
            self.r += tabel(["Rubriek", "Wijziging"], self.changelog, [4, 10])
        else:
            self.w("*Geen structurele wijzigingen in de elementen van deze bron, of geen changelog beschikbaar.*", "")
        self.w("## Bekende open punten", "")
        if self.secties.get("open punten"):
            self.r += self.secties["open punten"] + [""]
        else:
            self.w("*Geen open punten opgegeven.*", "")

    def bijlage_e(self) -> None:
        c = self.ctx
        self.w("# Bijlage E. Verantwoording", "")
        self.w("## Brondocumenten", "")
        docs = self.meta.get("brondocumenten") or []
        rijen = []
        for d in docs:
            versie = " ".join(str(x) for x in (d.get("versie"), d.get("datum")) if x)
            rijen.append((d.get("laag", ""), d.get("titel", ""), versie or LEEG, d.get("uitgever", ""),
                          autolink(d.get("vindplaats")), d.get("toelichting") or ""))
        if rijen:
            self.r += tabel(["Laag", "Document", "Versie, datum", "Uitgever", "Vindplaats", "Toelichting"],
                            rijen, [1, 4, 2, 2, 5, 6])
        else:
            self.w("*Geen brondocumenten opgegeven.*", "")
        self.w("## MIM-keuzes", "")
        self.w("De keuzes binnen de keuzeruimte van MIM 1.2 staan in paragraaf 2.5; "
               "zij zijn vastgesteld op 13 mei 2026 en worden alleen gewijzigd via een "
               "nieuwe, gedateerde beslissing.", "")
        self.w("## Generatiegegevens", "")
        self.r += tabel(["Gegeven", "Waarde"], [
            ("Modelversie (publicatie)", c["versie"]),
            ("Modelstand", c["modelstand"]),
            ("Stand publicatierepository", c["stand_publicatie"]),
            ("Bronprofiel", c["profielbestand"]),
            ("Informatiemodel", c["schemabestand"]),
            ("Tekstbestand", c["tekstbestand"]),
            ("Generator", f"{Path(sys.argv[0]).name}, {c['python']}"),
            ("Pandoc", c["pandoc"]),
            ("PlantUML", c["plantuml"]),
            ("Gegenereerd op", c["datum_tijd"]),
            ("Linked Data", f"{c['versie']}/ontologie/GBO-Linked-Data.ttl en GBO-Shapes.ttl"),
            ("Begrippenkader", f"{c['versie']}/begrippen/GBO-Begrippenkader.ttl"),
            ("GraphQL-schema", f"{c['versie']}/graphql/{self.u.profiel['bron'].lower()}.graphql"),
            ("Publicatierepository", rauw(f"<{REPO_URL}>")),
            ("Documentatiesite", rauw(f"<{SITE_URL}>")),
        ], [3, 10])
        self.w(f"De MIM-metagegevens zijn in de Linked Data gepubliceerd als eigenschappen in "
               f"{md(MIM_NS_GBO)}, gekoppeld aan {md(MIM_NS_BP4MC2)}. MIM 1.2 publiceert het "
               f"vocabulaire tevens als {md(MIM_NS_12)}.", "")

    def bijlage_f(self) -> None:
        self.w("# Bijlage F. MIM-termen in het kort", "")
        self.tekst(MIM_TERMEN)

    # -- geheel ---------------------------------------------------------------

    def bouw(self, diagram: str | None) -> str:
        self.kop()
        self.leeswijzer()
        self.samenvatting()
        self.totstandkoming()
        self.specificatie(diagram)
        self.toetsvragen()
        self.r += sectie_einde_portret(FOOTER_STAAND)
        self.bijlage_a()
        self.bijlage_b()
        self.bijlage_c()
        self.bijlage_d()
        self.bijlage_e()
        self.bijlage_f()
        return "\n".join(self.r).rstrip() + "\n"


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genereer de GBO Bronspecificatie (consultatieversie) voor één bron.")
    parser.add_argument("profiel", type=Path, help="bronprofiel (YAML)")
    parser.add_argument("-s", "--schema", type=Path, default=None,
                        help="hoofdschema; overschrijft 'schemabestand' uit het profiel")
    parser.add_argument("--tekst", type=Path, default=None,
                        help="handgeschreven tekstbestand voor deze bron (Markdown met frontmatter)")
    parser.add_argument("--output-dir", type=Path, required=True, help="uitvoermap")
    parser.add_argument("--versie", required=True, help="modelversie, bijvoorbeeld v0.5")
    parser.add_argument("--vorige-versie", default=None, help="vorige modelversie (voor bijlage D)")
    parser.add_argument("--changelog", type=Path, default=None, help="GBO_Changes.md")
    parser.add_argument("--wiki-repo", type=Path, default=None,
                        help="pad naar de wiki-repo (modelstand en herleidingspagina's)")
    parser.add_argument("--pandoc", default="pandoc")
    parser.add_argument("--plantuml", default="plantuml")
    parser.add_argument("--geen-docx", action="store_true", help="alleen Markdown schrijven")
    parser.add_argument("--geen-diagram", action="store_true")
    args = parser.parse_args()

    profiel, index, schema, schemapad = materialiseer(args.profiel, args.schema)
    u = Uitsnede(profiel, index, schema)
    meta, secties = laad_tekst(args.tekst)
    if meta.get("bron") and str(meta["bron"]).lower() != str(profiel["bron"]).lower():
        fout(f"tekstbestand is voor bron {meta['bron']}, profiel voor {profiel['bron']}")
    herleiding = laad_herleiding(args.wiki_repo, meta.get("herleiding") or [])
    namen = set(u.klassen) | set(u.enums) | set(u.typen)
    changelog = laad_changelog(args.changelog, namen)

    nu = dt.datetime.now()
    maanden = ["januari", "februari", "maart", "april", "mei", "juni", "juli",
               "augustus", "september", "oktober", "november", "december"]
    wiki_sha, wiki_vuil = git_stand(args.wiki_repo)
    pub_sha, pub_vuil = git_stand(Path(__file__).resolve().parent.parent)
    vuil = " (werkkopie met niet-vastgelegde wijzigingen)"
    ctx = {
        "versie": args.versie,
        "vorige_versie": args.vorige_versie,
        "datum": nu.strftime("%Y-%m-%d"),
        "datum_tijd": nu.strftime("%Y-%m-%d %H:%M"),
        "datum_lang": f"{nu.day} {maanden[nu.month - 1]} {nu.year}",
        "modelstand": f"commit {wiki_sha}{vuil if wiki_vuil else ''}",
        "stand_publicatie": f"commit {pub_sha}{vuil if pub_vuil else ''}",
        "profielbestand": args.profiel.name,
        "schemabestand": Path(schemapad).name,
        "tekstbestand": args.tekst.name if args.tekst else LEEG,
        "python": f"Python {sys.version.split()[0]}",
        "pandoc": tool_versie([args.pandoc, "--version"]) if not args.geen_docx else "niet gebruikt",
        "plantuml": tool_versie([args.plantuml, "-version"]) if not args.geen_diagram else "niet gebruikt",
    }

    bron = profiel["bron"]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stam = f"GBO-Bronspecificatie-{bron}-{args.versie}"
    diagram_rel = None
    if not args.geen_diagram:
        png = args.output_dir / "assets" / f"{bron.lower()}-overzicht.png"
        if maak_diagram(u, png, args.plantuml):
            diagram_rel = f"assets/{png.name}"

    doc = Document(u, meta, secties, ctx, herleiding, changelog)
    markdown = doc.bouw(diagram_rel)
    md_pad = args.output_dir / f"{stam}.md"
    md_pad.write_text(markdown, encoding="utf-8")
    melding("OK", f"{md_pad}")

    if args.geen_docx:
        return
    identiteit = (f"GBO Bronspecificatie {bron} · {meta.get('status', 'consultatieversie')} · "
                  f"model {args.versie} · {ctx['modelstand']} · {ctx['datum']}")
    ref = args.output_dir / "assets" / f"reference-{bron.lower()}.docx"
    ref.parent.mkdir(parents=True, exist_ok=True)
    bouw_reference_docx(ref, identiteit, args.pandoc)
    docx_pad = args.output_dir / f"{stam}.docx"
    cmd = [args.pandoc, str(md_pad), "-o", str(docx_pad), "--from", "markdown", "--to", "docx",
           "--reference-doc", str(ref), "--toc", "--toc-depth=2",
           "--resource-path", str(args.output_dir), "--metadata", "lang=nl-NL"]
    uit = subprocess.run(cmd, capture_output=True, text=True)
    ref.unlink()
    if uit.returncode != 0:
        fout(f"pandoc mislukt:\n{uit.stderr}")
    if uit.stderr.strip():
        melding("PANDOC", uit.stderr.strip()[:500])
    melding("OK", f"{docx_pad}")


if __name__ == "__main__":
    main()

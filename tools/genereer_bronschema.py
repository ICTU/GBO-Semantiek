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
  supertypen worden niet automatisch meegenomen). Met het veld
  behoudSupertype blijft één voorouder wél als is_a staan, zodat het
  objecttype in de SDL de bijbehorende interface implementeert; die
  voorouder moet zelf in objecttypen staan.
- Relaties met de annotatie gbo:inverseNaam krijgen op het doelobject
  een gematerialiseerde inverse (multivalued), zodat de SDL-navigatie
  ook van doel naar bron kan lopen. Met "inverse: false" in
  relatieAfhandeling blijft die inverse achterwege, voor bronnen die
  het objecttype uitsluitend via een ander pad aanbieden.
- Het profielveld zoeksleutels benoemt per ingang de natuurlijke
  sleutels waarop die ingang bevraagbaar is; ze belanden als annotatie
  gbo:zoeksleutels op het objecttype, waar de GraphQL-generator per
  sleutel een eigen Query-veld van maakt (partijOpBsn,
  partijOpKvkNummer, partijOpRsin). Partij is uitsluitend zo
  bevraagbaar en mag nooit als sleutel-referentie op een technische id
  terugvallen.
- Het profielveld toetsen declareert ja/nee-vragen die de bron
  beantwoordt zonder de onderliggende gegevens te leveren. Ze belanden
  als annotatie gbo:toetsen op het schema; de GraphQL-generator maakt
  er per toets een Query-veld met antwoordtype Indicatie van, met het
  opvraagpad en de uitkomstregel in de docstring.

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

# Objecttypen die nooit tot een sleutel-referentie mogen worden
# herleid. Partij draagt sinds 2026-08-10 geen technische id meer: een
# partij is uitsluitend bevraagbaar op bsn, kvkNummer of rsin. Wijst een
# relatie naar Partij, dan hoort Partij zelf in het profiel te staan.
NOOIT_SLEUTELREFERENTIE = {"Partij"}

BEREIKEN = ("laatstBekend", "overJaar", "alles")

# Het antwoord van een toets: Ja, Nee of Onbekend.
ANTWOORDTYPE_TOETS = "Indicatie"

# Veldscheiders van de querycodering in de annotaties gbo:queries en
# gbo:toetsen; vrije tekst mag ze niet bevatten.
VELDSCHEIDERS = (";", "|", "~", "\n")


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

        # De import-keten wordt recursief afgelopen, elk bestand eenmaal.
        # Nodig omdat een model naast de kern (toestemmingen.yaml,
        # voorzieningen.yaml) gbo.yaml importeert, en gbo.yaml zelf geen
        # klassen draagt maar alleen de deelmodellen bundelt.
        bestanden: list[Path] = []
        inhoud_per_pad: dict[Path, dict] = {}
        gezien: set[Path] = set()

        def verzamel(pad: Path, raw: dict | None = None) -> None:
            sleutel = pad.resolve()
            if sleutel in gezien:
                return
            gezien.add(sleutel)
            deel = raw if raw is not None else laad_yaml(pad)
            bestanden.append(pad)
            inhoud_per_pad[pad] = deel
            for imp in deel.get("imports", []):
                if ":" in imp:  # linkml:types en andere externe imports
                    continue
                verzamel(pad.parent / f"{imp}.yaml")

        verzamel(hoofdschema, self.raw)

        for pad in bestanden:
            deel = inhoud_per_pad[pad]
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

    def is_scalaire_range(self, range_naam: str) -> bool:
        """Kan deze range als sleutel-referentie of query-argument dienen?

        Alleen een type of enum, dus geen klasse. Een gestructureerd
        datatype als KadastraleAanduiding is in LinkML een klasse en
        wordt in de SDL een object-type; dat is geen scalar en kan dus
        niet als sleutel worden doorgegeven."""
        return range_naam not in self.classes

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
        technische id; anders (3) de geërfde identifier.

        Een unique_key op een gestructureerd datatype telt niet mee:
        Perceel.kadastraleAanduiding is sinds 2026-08-28 een klasse en
        kan geen scalar sleutel-referentie dragen. Zo'n verwijzing valt
        terug op de technische identifier."""
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
                    bereik = attr.get("range", "string")
                    if not self.is_scalaire_range(bereik):
                        continue
                    return slots[0], bereik
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


def natuurlijke_sleutels(klasse: str,
                         index: Modelindex) -> list[tuple[str, str]]:
    """Alle natuurlijke sleutels van een klasse, als (naam, range).

    Een eigen identifier eerst, daarna elke enkelvoudige unique_key
    (eigen of geerfd) in declaratievolgorde. NietNatuurlijkPersoon
    levert zo rsin en kvkNummer, IngeschrevenPersoon alleen bsn.

    Een unique_key op een gestructureerd datatype telt niet mee: die
    kan geen scalar query-argument worden."""
    resultaat: list[tuple[str, str]] = []
    for naam, attr in index.eigen_attributen(klasse).items():
        if (attr or {}).get("identifier"):
            resultaat.append((naam, (attr or {}).get("range", "string")))
    induced = index.induced_attributen(klasse)
    for kandidaat in [klasse] + index.voorouders(klasse):
        for uk in ((index.classes.get(kandidaat) or {})
                   .get("unique_keys") or {}).values():
            slots = uk.get("unique_key_slots") or []
            if len(slots) == 1 and slots[0] in induced:
                bereik = (induced[slots[0]] or {}).get("range", "string")
                if not index.is_scalaire_range(bereik):
                    continue
                paar = (slots[0], bereik)
                if paar not in resultaat:
                    resultaat.append(paar)
    return resultaat


def weiger_veldscheiders(naam_query: str, veld: str, tekst: str) -> None:
    """Vrije tekst gaat de querycodering in met ";", "|" en "~" als
    veldscheiders. Die tekens in de tekst zouden de velden stilzwijgend
    verschuiven: de rest van de zin belandt dan als parameternaam in de
    SDL. Daarom hier weigeren."""
    verboden = [t for t in VELDSCHEIDERS if t in tekst]
    if verboden:
        fout(f"{veld} van query '{naam_query}' bevat een veldscheider "
             f"({', '.join(repr(t) for t in verboden)}); herschrijf de "
             f"zin zonder dat teken")


def als_lijst(waarde) -> list:
    if waarde is None:
        return []
    return [waarde] if isinstance(waarde, str) else list(waarde)


def codeer_parameter(par: dict, ptype: str | None) -> str:
    return "~".join([
        par["naam"], ptype or "string",
        "meervoudig" if par.get("meervoudig") else "",
        "" if par.get("verplicht", True) else "optioneel",
        par.get("op") or "",
    ])


def dragers_van_slot(klasse: str, slot: str, profiel: dict,
                     index: Modelindex) -> list[str]:
    """Objecttypen in dit profiel die het genoemde slot dragen.

    Een abstracte ingang als Partij draagt de natuurlijke sleutels niet
    zelf; bsn zit op IngeschrevenPersoon en rsin/kvkNummer op
    NietNatuurlijkPersoon. Gezocht wordt daarom op de klasse zelf plus
    haar afstammelingen, voor zover die in het profiel staan."""
    kandidaten = [klasse] + [k for k in index.afstammelingen(klasse)
                             if k in profiel["objecttypen"]]
    return [k for k in kandidaten
            if slot in index.induced_attributen(k)]


def valideer_profiel(profiel: dict, index: Modelindex) -> None:
    for veld in ("bron", "titel", "schemabestand", "objecttypen"):
        if not profiel.get(veld):
            fout(f"verplicht profielveld '{veld}' ontbreekt of is leeg")
    if not profiel.get("ingangen") and not profiel.get("queries") \
            and not profiel.get("toetsen"):
        fout("profiel heeft geen ingangen, queries of toetsen; minstens "
             "een daarvan is verplicht")
    profiel.setdefault("ingangen", [])

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
        behoud = insluiting.get("behoudSupertype")
        if behoud:
            if behoud not in index.voorouders(klasse):
                fout(f"insluiting '{klasse}': behoudSupertype "
                     f"'{behoud}' is geen voorouder van dit objecttype")
            if behoud not in profiel["objecttypen"]:
                fout(f"insluiting '{klasse}': behoudSupertype "
                     f"'{behoud}' staat niet in objecttypen; een "
                     f"behouden supertype moet zelf geleverd worden")

    namen = set()
    for q in profiel.get("queries") or []:
        naam_query = q.get("naamQuery")
        doel = q.get("levert")
        subjecten = q.get("vanaf") or []
        if isinstance(subjecten, str):
            subjecten = [subjecten]
        if not naam_query:
            fout("query zonder 'naamQuery'; de veldnaam is verplicht")
        if naam_query in namen:
            fout(f"query '{naam_query}' is dubbel gedeclareerd")
        namen.add(naam_query)
        if doel not in profiel["objecttypen"]:
            fout(f"query '{naam_query}': levert '{doel}' dat niet in "
                 f"objecttypen staat")
        if not subjecten:
            fout(f"query '{naam_query}': 'vanaf' ontbreekt")
        for subject in subjecten:
            if subject not in index.classes:
                fout(f"query '{naam_query}': subject '{subject}' bestaat "
                     f"niet in het informatiemodel")
        if q.get("selectie") not in (None, "laatstBekend", "alles"):
            fout(f"query '{naam_query}': onbekende selectie "
                 f"'{q['selectie']}'; kies uit laatstBekend, alles")
        doel_attrs = index.induced_attributen(doel)
        sleutels = {n for s in subjecten
                    for n, _ in natuurlijke_sleutels(s, index)}
        parameters = q.get("parameters") or []
        if not parameters:
            fout(f"query '{naam_query}': 'parameters' ontbreekt")
        for par in parameters:
            par = {"naam": par} if isinstance(par, str) else par
            pnaam = par.get("naam")
            if not pnaam:
                fout(f"query '{naam_query}': parameter zonder naam")
            op = par.get("op")
            if op and op not in doel_attrs:
                fout(f"query '{naam_query}', parameter '{pnaam}': op "
                     f"'{op}' is geen attribuut van {doel}")
            if not par.get("type") and pnaam not in sleutels \
                    and pnaam not in doel_attrs and not op:
                fout(f"query '{naam_query}', parameter '{pnaam}': type "
                     f"niet af te leiden; geef 'type' op, of gebruik een "
                     f"sleutel van het subject, een attribuut van "
                     f"{doel}, of 'op'")
        weiger_veldscheiders(naam_query, "toelichting",
                             q.get("toelichting") or "")
        for stap in als_lijst(q.get("opvraagpad")):
            weiger_veldscheiders(naam_query, "opvraagpad", stap)

    for t in profiel.get("toetsen") or []:
        naam_query = t.get("naamQuery")
        subjecten = als_lijst(t.get("vanaf"))
        if not naam_query:
            fout("toets zonder 'naamQuery'; de veldnaam is verplicht")
        if naam_query in namen:
            fout(f"toets '{naam_query}': de naam is al in gebruik door "
                 f"een andere query of toets")
        namen.add(naam_query)
        if not subjecten:
            fout(f"toets '{naam_query}': 'vanaf' ontbreekt")
        for subject in subjecten:
            if subject not in index.classes:
                fout(f"toets '{naam_query}': subject '{subject}' bestaat "
                     f"niet in het informatiemodel")
        raadpleegt = als_lijst(t.get("raadpleegt"))
        if not raadpleegt:
            fout(f"toets '{naam_query}': 'raadpleegt' ontbreekt")
        for klasse in raadpleegt:
            if klasse not in profiel["objecttypen"]:
                fout(f"toets '{naam_query}': raadpleegt '{klasse}' dat "
                     f"niet in objecttypen staat")
        if not als_lijst(t.get("opvraagpad")):
            fout(f"toets '{naam_query}': 'opvraagpad' ontbreekt")
        if not t.get("uitkomst"):
            fout(f"toets '{naam_query}': 'uitkomst' ontbreekt")
        if t.get("selectie") not in (None, "laatstBekend", "alles"):
            fout(f"toets '{naam_query}': onbekende selectie "
                 f"'{t['selectie']}'; kies uit laatstBekend, alles")
        sleutels = {n for s in subjecten
                    for n, _ in natuurlijke_sleutels(s, index)}
        subject_attrs = {n for s in subjecten
                         for n in index.induced_attributen(s)}
        parameters = t.get("parameters") or []
        if not parameters:
            fout(f"toets '{naam_query}': 'parameters' ontbreekt")
        for par in parameters:
            par = {"naam": par} if isinstance(par, str) else par
            pnaam = par.get("naam")
            if not pnaam:
                fout(f"toets '{naam_query}': parameter zonder naam")
            if par.get("op"):
                fout(f"toets '{naam_query}', parameter '{pnaam}': 'op' "
                     f"is bij een toets niet van toepassing")
            if not par.get("type") and pnaam not in sleutels \
                    and pnaam not in subject_attrs:
                fout(f"toets '{naam_query}', parameter '{pnaam}': type "
                     f"niet af te leiden; geef 'type' op, of gebruik een "
                     f"sleutel of attribuut van een subject")
        for veld in ("toelichting", "uitkomst"):
            weiger_veldscheiders(naam_query, veld, t.get(veld) or "")
        for stap in als_lijst(t.get("opvraagpad")):
            weiger_veldscheiders(naam_query, "opvraagpad", stap)

    for sleutelregel in profiel.get("zoeksleutels") or []:
        klasse = sleutelregel.get("objecttype")
        if klasse not in profiel["ingangen"]:
            fout(f"zoeksleutels verwijst naar objecttype '{klasse}' dat "
                 f"geen ingang is")
        for slot in sleutelregel.get("sleutels") or []:
            if not dragers_van_slot(klasse, slot, profiel, index):
                fout(f"zoeksleutel '{klasse}.{slot}': geen objecttype in "
                     f"dit profiel draagt dit attribuut — noch "
                     f"'{klasse}' zelf, noch een van zijn subtypen")

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
    behoud_supertype = {i["objecttype"]: i["behoudSupertype"]
                        for i in profiel.get("insluitingen") or []
                        if i.get("behoudSupertype")}

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
            behoud = behoud_supertype.get(klasse)
            if behoud:
                # Eén voorouder blijft staan, zodat het objecttype in de
                # SDL de bijbehorende interface implementeert. De
                # attributen van die voorouder komen via overerving en
                # hoeven hier niet gematerialiseerd te worden.
                definitie["is_a"] = behoud
                for naam in index.induced_attributen(behoud):
                    attributen.pop(naam, None)
                melding("INFO", f"insluiting op '{klasse}': supertype "
                                f"'{behoud}' behouden (is_a)")
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
                    if doel in NOOIT_SLEUTELREFERENTIE:
                        fout(f"{klasse}.{naam}: '{doel}' mag geen "
                             f"sleutel-referentie worden. Een partij is "
                             f"uitsluitend bevraagbaar op bsn, kvkNummer "
                             f"of rsin; neem '{doel}' met haar subtypen "
                             f"op in objecttypen, of laat de relatie weg")
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
    geen_inverse = {(r["objecttype"], r["relatie"])
                    for r in profiel.get("relatieAfhandeling") or []
                    if r.get("inverse") is False}
    for klasse in list(resultaat):
        for naam, attr in list(
                (resultaat[klasse].get("attributes") or {}).items()):
            ann = (attr or {}).get("annotations") or {}
            inverse = ann.get("gbo:inverseNaam")
            doel = (attr or {}).get("range")
            if not inverse or doel not in resultaat:
                continue
            if (klasse, naam) in geen_inverse:
                melding("INFO", f"inverse onderdrukt door profiel: "
                                f"{doel}.{inverse} <- {klasse}.{naam}")
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

    # Querydeclaraties als annotatie op het doel-objecttype; de
    # GraphQL-generator maakt er per declaratie een Query-veld van.
    # Codering: declaraties gescheiden door een newline, velden binnen
    # een declaratie door ";", parameters door "|" en parametervelden
    # door "~". Velden: naam, selectie, toelichting, parameters en
    # opvraagpad (stappen gescheiden door "|"). Vrije tekst is in
    # valideer_profiel al op veldscheiders gecontroleerd.
    per_doel: dict[str, list[str]] = {}
    for q in profiel.get("queries") or []:
        doel = q["levert"]
        if doel not in resultaat:
            continue
        subjecten = q["vanaf"]
        if isinstance(subjecten, str):
            subjecten = [subjecten]
        sleutels: dict[str, str] = {}
        for subject in subjecten:
            for n, r in natuurlijke_sleutels(subject, index):
                sleutels.setdefault(n, r)
        doel_attrs = index.induced_attributen(doel)
        stukken = []
        for par in q.get("parameters") or []:
            par = {"naam": par} if isinstance(par, str) else par
            pnaam = par["naam"]
            ptype = par.get("type") or sleutels.get(pnaam)
            if not ptype and pnaam in doel_attrs:
                ptype = (doel_attrs[pnaam] or {}).get("range", "string")
            if not ptype and par.get("op"):
                ptype = (doel_attrs[par["op"]] or {}).get("range",
                                                          "string")
            stukken.append(codeer_parameter(par, ptype))
        per_doel.setdefault(doel, []).append(";".join([
            q["naamQuery"], q.get("selectie") or "",
            q.get("toelichting") or "", "|".join(stukken),
            "|".join(" ".join(str(s).split())
                     for s in als_lijst(q.get("opvraagpad")))]))
        melding("INFO", f"query '{q['naamQuery']}' levert {doel} "
                        f"({len(stukken)} parameter(s))")
    for doel, declaraties in per_doel.items():
        resultaat[doel].setdefault("annotations", {})
        resultaat[doel]["annotations"]["gbo:queries"] = \
            "\n".join(declaraties)

    # Zoeksleutels als annotatie op het objecttype; de GraphQL-generator
    # maakt er alternatieve query-argumenten van.
    for sleutelregel in profiel.get("zoeksleutels") or []:
        klasse = sleutelregel["objecttype"]
        if klasse not in resultaat:
            continue
        sleutels = sleutelregel.get("sleutels") or []
        resultaat[klasse].setdefault("annotations", {})
        resultaat[klasse]["annotations"]["gbo:zoeksleutels"] = \
            ", ".join(sleutels)
        melding("INFO", f"zoeksleutels op '{klasse}': "
                        f"{', '.join(sleutels)}")

    # Abstracte klassen zonder concreet subtype in het profiel.
    for klasse in resultaat:
        if index.classes[klasse].get("abstract"):
            concreet = [s for s in index.afstammelingen(klasse)
                        if s in resultaat
                        and not index.classes[s].get("abstract")]
            if not concreet and klasse in profiel["objecttypen"]:
                melding("INFO",
                        f"abstract objecttype '{klasse}' heeft geen "
                        f"concreet subtype in dit profiel; wordt een "
                        f"gewoon type in de SDL")
    return resultaat


def codeer_toetsen(profiel: dict, index: Modelindex) -> str:
    """Toetsdeclaraties als één annotatie op het schema.

    Een toets levert geen objecttype op, dus er is geen doelklasse om de
    declaratie aan te hangen. Codering als bij gbo:queries: declaraties
    gescheiden door een newline, velden door ";", parameters en
    opvraagstappen door "|" en parametervelden door "~". Velden: naam,
    selectie, toelichting, parameters, opvraagpad, uitkomst en
    raadpleegt (objecttypen gescheiden door ", ")."""
    declaraties = []
    for t in profiel.get("toetsen") or []:
        subjecten = als_lijst(t["vanaf"])
        sleutels: dict[str, str] = {}
        attributen: dict[str, dict] = {}
        for subject in subjecten:
            for n, r in natuurlijke_sleutels(subject, index):
                sleutels.setdefault(n, r)
            for n, a in index.induced_attributen(subject).items():
                attributen.setdefault(n, a or {})
        stukken = []
        for par in t.get("parameters") or []:
            par = {"naam": par} if isinstance(par, str) else par
            pnaam = par["naam"]
            ptype = par.get("type") or sleutels.get(pnaam)
            if not ptype and pnaam in attributen:
                ptype = attributen[pnaam].get("range", "string")
            stukken.append(codeer_parameter(par, ptype))
        declaraties.append(";".join([
            t["naamQuery"], t.get("selectie") or "",
            " ".join(str(t.get("toelichting") or "").split()),
            "|".join(stukken),
            "|".join(" ".join(str(s).split())
                     for s in als_lijst(t["opvraagpad"])),
            " ".join(str(t["uitkomst"]).split()),
            ", ".join(als_lijst(t["raadpleegt"]))]))
        melding("INFO", f"toets '{t['naamQuery']}' "
                        f"({len(stukken)} parameter(s), antwoordtype "
                        f"{ANTWOORDTYPE_TOETS})")
    return "\n".join(declaraties)


def verzamel_enums_en_types(klassen: dict[str, dict],
                            index: Modelindex,
                            toetsen: str = "") -> tuple[dict, dict]:
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
        # Sleuteltypen van benoemde queries: die komen als argument in de
        # SDL terecht zonder dat een attribuut in dit profiel ze gebruikt
        # (de BRV accepteert een bsn maar levert geen persoon).
        rauw = (definitie.get("annotations") or {}).get("gbo:queries")
        for declaratie in str(rauw or "").split("\n"):
            velden = declaratie.split(";")
            if len(velden) < 4:
                continue
            for par in velden[3].split("|"):
                onderdelen = par.split("~")
                if len(onderdelen) > 1 and onderdelen[1] in index.types:
                    voeg_type_toe(onderdelen[1])
    # Toetsen: de argumenttypen en het antwoordtype komen in de SDL,
    # ook als geen attribuut in dit profiel ze gebruikt.
    if toetsen:
        if ANTWOORDTYPE_TOETS not in index.enums:
            fout(f"antwoordtype van toetsen '{ANTWOORDTYPE_TOETS}' "
                 f"ontbreekt in het informatiemodel")
        enums[ANTWOORDTYPE_TOETS] = copy.deepcopy(
            index.enums[ANTWOORDTYPE_TOETS])
        for declaratie in toetsen.split("\n"):
            velden = declaratie.split(";")
            for par in velden[3].split("|"):
                onderdelen = par.split("~")
                if len(onderdelen) < 2:
                    continue
                if onderdelen[1] in index.types:
                    voeg_type_toe(onderdelen[1])
                elif onderdelen[1] in index.enums:
                    enums[onderdelen[1]] = copy.deepcopy(
                        index.enums[onderdelen[1]])
    return enums, typen


def bouw_schema(profiel: dict, index: Modelindex, klassen: dict,
                enums: dict, typen: dict, toetsen: str = "") -> dict:
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
    if toetsen:
        schema["annotations"]["gbo:toetsen"] = toetsen
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
    toetsen = codeer_toetsen(profiel, index)
    enums, typen = verzamel_enums_en_types(klassen, index, toetsen)
    schema = bouw_schema(profiel, index, klassen, enums, typen, toetsen)

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

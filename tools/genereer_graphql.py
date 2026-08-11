#!/usr/bin/env python3
"""Genereer GraphQL SDL uit een gematerialiseerd per-bron LinkML-schema.

Aanvulling op de standaard gen-graphql van LinkML, die de volgende
dingen mist die GBO nodig heeft:
1. een Query-root met velden per ingang (annotatie gbo:ingangen);
   met annotatie gbo:lijstQueries=false blijft alleen de query op de
   natuurlijke sleutel over (geen "...Lijst"-velden); multivalued
   object-velden krijgen filterargumenten voor doel-attributen met de
   annotatie gbo:filterbaar; dat zijn altijd lijstargumenten, met de
   attribuutnaam als argumentnaam;
2. de GBO-primitieven Tekst en Alfanumeriek worden afgebeeld op String,
   Numeriek op Int en Decimaal op Float; overige datatypes (Datum,
   DatumTijd, Geometrie, NEN3610ID, codelijsten, ...) worden benoemde
   scalars;
3. de overervingsketen: abstracte klassen worden interfaces, concrete
   klassen implementeren alle abstracte voorouders (GraphQL staat
   type-implements-type niet toe, dus een concrete superklasse wordt
   alleen plat overgenomen);
4. klassen met de annotatie gbo:graphql=uitsluiten (de patroon-mixins
   Voorkomen en Datakwaliteit) blijven volledig buiten de SDL: geen
   interface, geen implements en hun attributen worden niet uitgevlakt.

Attributen worden per type volledig uitgevlakt (eigen plus geërfde),
zoals GraphQL vereist.

Gebruik:
    python3 tools/genereer_graphql.py /tmp/gbo-bron-brp.yaml \
        -o v0.2/graphql/brp.graphql
"""

import argparse
import re
import sys
import textwrap
from pathlib import Path

import yaml

BUILTIN_SCALARS = {
    "string": "String", "integer": "Int", "float": "Float",
    "double": "Float", "decimal": "Float", "boolean": "Boolean",
    "date": "String", "datetime": "String", "time": "String",
    "uri": "String", "uriorcurie": "String", "curie": "String",
    "ncname": "String", "objectidentifier": "ID",
    "nodeidentifier": "ID",
}

# GBO-primitieven die rechtstreeks op een ingebouwde GraphQL-scalar worden
# afgebeeld in plaats van als benoemde scalar; houdt de SDL eenvoudig.
# Overige datatypes (Datum, DatumTijd, Geometrie, codelijsten, ...) blijven
# benoemde scalars.
PRIMITIEVE_SCALARS = {
    "Tekst": "String", "Alfanumeriek": "String",
    "Numeriek": "Int", "Decimaal": "Float",
}


def melding(soort: str, tekst: str) -> None:
    print(f"{soort}: {tekst}", file=sys.stderr)


def fout(tekst: str) -> None:
    melding("FOUT", tekst)
    sys.exit(1)


def graphql_naam(naam: str) -> str:
    """Maak van een willekeurige naam een geldige GraphQL-naam."""
    schoon = re.sub(r"[^_0-9A-Za-z]", "_", naam)
    if re.match(r"^[0-9]", schoon):
        schoon = "_" + schoon
    return schoon


def docstring(tekst: str | None, inspring: str = "") -> list[str]:
    if not tekst:
        return []
    plat = " ".join(str(tekst).split()).replace('"""', "'''")
    return [f'{inspring}"""{plat}"""']


def lcfirst(naam: str) -> str:
    return naam[0].lower() + naam[1:] if naam else naam


def ucfirst(naam: str) -> str:
    return naam[0].upper() + naam[1:] if naam else naam


class SDLGenerator:
    def __init__(self, schema: dict):
        self.schema = schema
        self.classes: dict[str, dict] = schema.get("classes") or {}
        self.enums: dict[str, dict] = schema.get("enums") or {}
        self.types: dict[str, dict] = schema.get("types") or {}
        self.default_range = schema.get("default_range", "string")
        self.gebruikte_scalars: set[str] = set()
        self.gebruikte_enums: set[str] = set()
        self.query_ingangen: set[str] = set()

    # -- hiërarchie ----------------------------------------------------------

    def voorouders(self, klasse: str) -> list[str]:
        resultaat, stapel = [], [klasse]
        while stapel:
            d = self.classes.get(stapel.pop(0)) or {}
            ouders = ([d["is_a"]] if d.get("is_a") else []) \
                + list(d.get("mixins") or [])
            for o in ouders:
                if o in self.classes and o not in resultaat \
                        and not self.is_uitgesloten(o):
                    resultaat.append(o)
                    stapel.append(o)
        return resultaat

    def is_uitgesloten(self, klasse: str) -> bool:
        """Klasse met annotatie gbo:graphql=uitsluiten blijft buiten de
        SDL — bijvoorbeeld de patroon-mixins Voorkomen en Datakwaliteit:
        wel in het semantische model, geen GraphQL-interface."""
        ann = (self.classes.get(klasse) or {}).get("annotations") or {}
        return ann.get("gbo:graphql") == "uitsluiten"

    def heeft_concrete_afstammeling(self, klasse: str) -> bool:
        return any(
            not (d or {}).get("abstract")
            and klasse in self.voorouders(n)
            for n, d in self.classes.items() if n != klasse)

    def is_interface(self, klasse: str) -> bool:
        d = self.classes.get(klasse) or {}
        if d.get("mixin"):
            return True
        return bool(d.get("abstract")) \
            and self.heeft_concrete_afstammeling(klasse)

    def induced_attributen(self, klasse: str) -> dict[str, dict]:
        """Eigen plus geërfde attributen; eigen definitie wint."""
        resultaat: dict[str, dict] = {}
        for voorouder in reversed(self.voorouders(klasse)):
            resultaat.update(
                (self.classes[voorouder].get("attributes") or {}))
        resultaat.update(
            (self.classes[klasse].get("attributes") or {}))
        return resultaat

    def identifier_van(self, klasse: str) -> tuple[str, str] | None:
        for kandidaat in [klasse] + self.voorouders(klasse):
            for naam, attr in (self.classes[kandidaat].get("attributes")
                               or {}).items():
                if (attr or {}).get("identifier"):
                    return naam, self.veldtype(attr, kaal=True)
        return None

    def zoeksleutel_van(self, klasse: str) -> tuple[str, str] | None:
        """Natuurlijke zoeksleutel voor een query-ingang.

        Voorkeur: (1) een eigen identifier op de klasse zelf; anders
        (2) een enkelvoudige unique_key (eigen of geërfd) als
        natuurlijke sleutel — zo zoekt IngeschrevenPersoon op bsn in
        plaats van op de geërfde technische ID; anders (3) de geërfde
        identifier (de universele technische handle)."""
        eigen = self.classes.get(klasse) or {}
        for naam, attr in (eigen.get("attributes") or {}).items():
            if (attr or {}).get("identifier"):
                return naam, self.veldtype(attr, kaal=True)
        induced = self.induced_attributen(klasse)
        for kandidaat in [klasse] + self.voorouders(klasse):
            for uk in ((self.classes.get(kandidaat) or {})
                       .get("unique_keys") or {}).values():
                slots = uk.get("unique_key_slots") or []
                if len(slots) == 1 and slots[0] in induced:
                    return slots[0], self.veldtype(induced[slots[0]],
                                                   kaal=True)
        return self.identifier_van(klasse)

    @staticmethod
    def annotatie(annotaties: dict, naam: str):
        waarde = (annotaties or {}).get(naam)
        if isinstance(waarde, dict):  # {tag, value}-vorm
            waarde = waarde.get("value")
        return waarde

    def benoemde_queries(self) -> list[str]:
        """Query-velden uit de querydeclaraties op de doel-objecttypen.

        Een bron biedt niet alleen ingangen aan maar ook benoemde
        vragen: de BRI levert een inkomen, geen persoon. Elke declaratie
        (annotatie gbo:queries) levert precies een Query-veld op, met de
        naam en de parameters zoals die in het bron-profiel staan. De
        generator leidt alleen datatypes, het lijstresultaat en de
        docstring af."""
        regels: list[str] = []
        for doel, definitie in self.classes.items():
            rauw = self.annotatie((definitie or {}).get("annotations"),
                                  "gbo:queries")
            if not rauw:
                continue
            for declaratie in str(rauw).split("\n"):
                velden = declaratie.split(";")
                if len(velden) < 4:
                    fout(f"onleesbare querydeclaratie op '{doel}'")
                naam_query, selectie, toelichting, rauwe_pars = velden[:4]
                argumenten, zinnen = [], []
                for par in rauwe_pars.split("|"):
                    onderdelen = (par.split("~") + [""] * 5)[:5]
                    pnaam, ptype, meervoudig, optioneel, op = onderdelen
                    basis = self.veldtype({"range": ptype}, kaal=True)
                    typetekst = f"[{basis}!]" if meervoudig else basis
                    if not optioneel:
                        typetekst += "!"
                    argumenten.append(
                        f"{graphql_naam(pnaam)}: {typetekst}")
                    if op:
                        zinnen.append(f"Het argument {pnaam} selecteert "
                                      f"op {op}.")
                if selectie == "laatstBekend":
                    zinnen.insert(0, "Levert uitsluitend de laatst "
                                     "bekende situatie op het moment van "
                                     "bevragen; de peildatum is "
                                     "leveringsmetadata en staat in de "
                                     "antwoord-envelop van de levering.")
                elif selectie == "alles":
                    zinnen.insert(0, "Levert de volledige historie, niet "
                                     "alleen de laatst bekende situatie.")
                if toelichting:
                    zinnen.insert(0, toelichting)
                regels.extend(docstring(
                    " ".join([f"{doel}."] + zinnen), "  "))
                regels.append(f"  {graphql_naam(naam_query)}"
                              f"({', '.join(argumenten)}): "
                              f"[{graphql_naam(doel)}!]")
            self.query_ingangen.add(doel)
        return regels

    def zoeksleutels_van(self, klasse: str) -> list[tuple[str, str]]:
        """Alternatieve natuurlijke sleutels van een ingang (annotatie
        gbo:zoeksleutels op het objecttype).

        Een abstracte ingang draagt de sleutels zelf niet: bsn zit op
        IngeschrevenPersoon en rsin/kvkNummer op NietNatuurlijkPersoon.
        Er wordt daarom gezocht op de klasse zelf plus alle klassen die
        haar als voorouder hebben."""
        ann = (self.classes.get(klasse) or {}).get("annotations") or {}
        waarde = ann.get("gbo:zoeksleutels")
        if isinstance(waarde, dict):  # {tag, value}-vorm
            waarde = waarde.get("value")
        if not waarde:
            return []
        kandidaten = [klasse] + [n for n in self.classes
                                 if n != klasse
                                 and klasse in self.voorouders(n)]
        resultaat = []
        for naam in [s.strip() for s in str(waarde).split(",") if s.strip()]:
            for kandidaat in kandidaten:
                attr = self.induced_attributen(kandidaat).get(naam)
                if attr:
                    resultaat.append(
                        (naam, self.veldtype(attr, kaal=True)))
                    break
            else:
                fout(f"zoeksleutel '{klasse}.{naam}' komt op geen enkel "
                     f"objecttype in dit schema voor")
        return resultaat

    # -- veldtypen -----------------------------------------------------------

    def veldtype(self, attr: dict, kaal: bool = False) -> str:
        bereik = (attr or {}).get("range") or self.default_range
        if bereik in self.classes:
            basis = bereik
        elif bereik in self.enums:
            basis = bereik
            self.gebruikte_enums.add(bereik)
        elif bereik in PRIMITIEVE_SCALARS:
            basis = PRIMITIEVE_SCALARS[bereik]
        elif bereik in self.types:
            basis = bereik
            self.gebruikte_scalars.add(bereik)
        elif bereik in BUILTIN_SCALARS:
            basis = BUILTIN_SCALARS[bereik]
        else:
            melding("WAARSCHUWING",
                    f"onbekende range '{bereik}'; String gebruikt")
            basis = "String"
        if kaal:
            return basis
        if (attr or {}).get("multivalued"):
            resultaat = f"[{basis}!]"
        else:
            resultaat = basis
        if (attr or {}).get("required"):
            resultaat += "!"
        return resultaat

    # -- bouwstenen ----------------------------------------------------------

    def filterargumenten(self, doelklasse: str) -> str:
        """Argumentenlijst voor een multivalued object-veld: één
        optioneel lijstargument per doel-attribuut met annotatie
        gbo:filterbaar.

        Het argument is altijd een lijst, ook bij één waarde. Daarmee
        hebben enkelvoudige en meervoudige selectie dezelfde vorm en kan
        een policy-beslispunt de gevraagde verzameling rechtstreeks uit
        de operatie aflezen, zonder een filter-inputobject te moeten
        uitpakken.

        Het argument houdt de naam van het attribuut, in enkelvoud: de
        lijstnotatie drukt de meervoudigheid al uit. GraphQL coerceert
        bovendien een losse waarde naar een lijst van één, zodat het
        verbreden van een bestaand enkelvoudig argument geen bestaande
        query met een literale waarde breekt.
        """
        argumenten = []
        for naam, attr in self.induced_attributen(doelklasse).items():
            ann = (attr or {}).get("annotations") or {}
            waarde = ann.get("gbo:filterbaar")
            if isinstance(waarde, dict):  # {tag, value}-vorm
                waarde = waarde.get("value")
            if str(waarde).lower() not in ("true", "ja"):
                continue
            argumenten.append(f"{graphql_naam(naam)}: "
                              f"[{self.veldtype(attr, kaal=True)}!]")
        return "(" + ", ".join(argumenten) + ")" if argumenten else ""

    def velden(self, klasse: str) -> list[str]:
        regels = []
        for naam, attr in self.induced_attributen(klasse).items():
            attr = attr or {}
            beschrijving = attr.get("description")
            sleutelref = (attr.get("annotations") or {}) \
                .get("gbo:sleutelreferentie")
            if sleutelref:
                beschrijving = ((beschrijving + " ") if beschrijving
                                else "") \
                    + f"(Sleutel-referentie naar {sleutelref}.)"
            regels.extend(docstring(beschrijving, "  "))
            argumenten = ""
            if attr.get("multivalued") \
                    and attr.get("range") in self.classes:
                argumenten = self.filterargumenten(attr["range"])
            regels.append(f"  {graphql_naam(naam)}{argumenten}: "
                          f"{self.veldtype(attr)}")
        return regels

    def klasse_blok(self, klasse: str) -> list[str]:
        soort = "interface" if self.is_interface(klasse) else "type"
        implementaties = [v for v in self.voorouders(klasse)
                          if self.is_interface(v)]
        kop = f"{soort} {graphql_naam(klasse)}"
        if implementaties:
            kop += " implements " + " & ".join(
                graphql_naam(i) for i in implementaties)
        d = self.classes.get(klasse) or {}
        regels = docstring(d.get("description"))
        regels += [kop + " {", *self.velden(klasse), "}"]
        return regels

    def enum_blok(self, naam: str) -> list[str]:
        d = self.enums.get(naam) or {}
        regels = docstring(d.get("description"))
        regels.append(f"enum {graphql_naam(naam)} {{")
        for waarde, wd in (d.get("permissible_values") or {}).items():
            regels.extend(docstring((wd or {}).get("description"), "  "))
            regels.append(f"  {graphql_naam(waarde)}")
        regels.append("}")
        return regels

    def query_blok(self) -> list[str]:
        annotaties = self.schema.get("annotations") or {}
        ingangen = [i.strip() for i in
                    (annotaties.get("gbo:ingangen") or "").split(",")
                    if i.strip()]
        benoemd = self.benoemde_queries()
        if not ingangen and not benoemd:
            melding("WAARSCHUWING",
                    "geen ingangen en geen queries; Query-root blijft "
                    "leeg")
            return []
        lijsten = str(annotaties.get("gbo:lijstQueries",
                                     True)).lower() \
            not in ("false", "nee", "uit")
        regels = ['"""Query-ingangen van dit bronprofiel."""',
                  "type Query {", *benoemd]
        for ingang in ingangen:
            if ingang not in self.classes:
                fout(f"ingang '{ingang}' bestaat niet in het schema")
            veld = lcfirst(graphql_naam(ingang))
            sleutels = self.zoeksleutels_van(ingang)
            if sleutels:
                # Meerdere natuurlijke sleutels: één Query-veld per
                # sleutel, elk met precies één verplicht argument. Dat is
                # eenduidiger dan één veld met evenzoveel optionele
                # argumenten waarvan er precies één gevuld moet zijn: die
                # regel is in de SDL niet uit te drukken en zou pas bij
                # uitvoering afgedwongen worden. Nu noemt de operatie de
                # gebruikte sleutel zelf, wat een policy-beslispunt
                # rechtstreeks kan lezen.
                for slotnaam, slottype in sleutels:
                    arg = graphql_naam(slotnaam)
                    regels.extend(docstring(
                        f"Eén {ingang} op {slotnaam}.", "  "))
                    regels.append(f"  {veld}Op{ucfirst(arg)}"
                                  f"({arg}: {slottype}!): "
                                  f"{graphql_naam(ingang)}")
                self.query_ingangen.add(ingang)
                if lijsten:
                    regels.extend(docstring(
                        f"Alle voorkomens van {ingang}.", "  "))
                    regels.append(
                        f"  {veld}Lijst: [{graphql_naam(ingang)}!]")
                continue
            ident = self.zoeksleutel_van(ingang)
            if ident:
                slotnaam, slottype = ident
                regels.extend(docstring(
                    f"Eén {ingang} op {slotnaam}.", "  "))
                regels.append(f"  {veld}({graphql_naam(slotnaam)}: "
                              f"{slottype}!): {graphql_naam(ingang)}")
                self.query_ingangen.add(ingang)
            elif not lijsten:
                melding("WAARSCHUWING",
                        f"ingang '{ingang}' heeft geen zoeksleutel en "
                        f"lijstQueries staat uit: geen Query-veld")
            if lijsten:
                regels.extend(docstring(
                    f"Alle voorkomens van {ingang}.", "  "))
                regels.append(f"  {veld}Lijst: [{graphql_naam(ingang)}!]")
                self.query_ingangen.add(ingang)
        regels.append("}")
        return regels

    def onbereikbare_objecttypen(self,
                                 objecttypen: list[str]) -> list[str]:
        """Objecttypen die vanuit geen enkel Query-veld bereikbaar zijn.

        Bereikbaarheid loopt via velden met een objecttype-range
        (inclusief geërfde en gematerialiseerde inverse velden) en, bij
        interfaces, via fragment-spreads naar de implementerende types.
        Supertypen gelden als opvraagbaar zodra een subtype bereikbaar
        is (hun velden liggen op elk subtype). Sleutel-referenties zijn
        scalars en tellen niet als navigatie."""
        bereikbaar: set[str] = set()
        stapel = list(self.query_ingangen)
        while stapel:
            klasse = stapel.pop()
            if klasse in bereikbaar or klasse not in self.classes \
                    or self.is_uitgesloten(klasse):
                continue
            bereikbaar.add(klasse)
            stapel.extend(self.voorouders(klasse))
            for attr in self.induced_attributen(klasse).values():
                doel = (attr or {}).get("range")
                if doel in self.classes:
                    stapel.append(doel)
            if self.is_interface(klasse):
                for naam in self.classes:
                    if naam != klasse \
                            and klasse in self.voorouders(naam):
                        stapel.append(naam)
        return [o for o in objecttypen if o not in bereikbaar]

    # -- hoofdgenerator ------------------------------------------------------

    def genereer(self, bronbestand: str) -> str:
        blokken: list[list[str]] = []
        # Interfaces eerst, daarna types, in schema-volgorde; uitgesloten
        # klassen (patroon-mixins) blijven buiten de SDL.
        volgorde = sorted(
            (c for c in self.classes if not self.is_uitgesloten(c)),
            key=lambda c: not self.is_interface(c))
        for klasse in volgorde:
            blokken.append(self.klasse_blok(klasse))
        # Alleen enums die door een uitgevlakt veld worden gebruikt.
        for naam in self.enums:
            if naam in self.gebruikte_enums:
                blokken.append(self.enum_blok(naam))
        query = self.query_blok()
        if query:
            blokken.append(query)
        # Regel: elk in het bron-profiel opgesomd objecttype moet
        # opvraagbaar zijn, dus bereikbaar vanuit de Query-root.
        objecttypen = [o.strip() for o in
                       ((self.schema.get("annotations") or {})
                        .get("gbo:objecttypen") or "").split(",")
                       if o.strip()]
        if objecttypen:
            onbereikbaar = self.onbereikbare_objecttypen(objecttypen)
            if onbereikbaar:
                fout(f"objecttypen niet opvraagbaar vanuit de "
                     f"Query-root: {', '.join(onbereikbaar)}; voeg een "
                     f"ingang of een query toe, of maak ze bereikbaar "
                     f"via navigatie (bijvoorbeeld een "
                     f"gbo:inverseNaam-annotatie op de relatie in het "
                     f"informatiemodel)")
        # Scalars pas nu: self.gebruikte_scalars is gevuld. GraphQL-scalars
        # zijn opaak; de formaatrestricties uit het LinkML-datatype
        # (pattern, minimum, maximum) projecteren we als @restrictie-directive
        # zodat ze in de SDL zichtbaar/machine-leesbaar terugkomen.
        scalars = []
        restrictie_gebruikt = False
        for naam in sorted(self.gebruikte_scalars):
            t = self.types.get(naam) or {}
            scalars.extend(docstring(t.get("description")))
            args = []
            if t.get("pattern"):
                pat = str(t["pattern"]).replace("\\", "\\\\").replace(
                    '"', '\\"')
                args.append(f'patroon: "{pat}"')
            if t.get("minimum_value") is not None:
                args.append(f'minimum: {int(t["minimum_value"])}')
            if t.get("maximum_value") is not None:
                args.append(f'maximum: {int(t["maximum_value"])}')
            regel = f"scalar {graphql_naam(naam)}"
            if args:
                regel += " @restrictie(" + ", ".join(args) + ")"
                restrictie_gebruikt = True
            scalars.append(regel)
        if scalars:
            blokken.insert(0, scalars)
        if restrictie_gebruikt:
            blokken.insert(0, [
                '"""Formaatrestrictie op een scalar, afgeleid uit het '
                'LinkML-datatype."""',
                "directive @restrictie(",
                '  """Reguliere expressie waaraan de waarde voldoet."""',
                "  patroon: String",
                '  """Ondergrens (inclusief) voor numerieke waarden."""',
                "  minimum: Int",
                '  """Bovengrens (inclusief) voor numerieke waarden."""',
                "  maximum: Int",
                ") on SCALAR",
            ])

        bron = (self.schema.get("annotations") or {}).get("gbo:bron", "")
        kop = (f"# GEGENEREERD BESTAND — niet handmatig bewerken.\n"
               f"# GraphQL SDL voor bronprofiel {bron}, gegenereerd uit "
               f"{bronbestand}.\n"
               f"# Regenereer met: task generate:graphql\n")
        beschrijving = self.schema.get("description")
        if beschrijving:
            kop += "#\n" + "\n".join(textwrap.wrap(
                " ".join(str(beschrijving).split()), width=72,
                initial_indent="# ", subsequent_indent="# ")) + "\n"
        return kop + "\n" + "\n\n".join("\n".join(b) for b in blokken) \
            + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genereer GraphQL SDL uit een gematerialiseerd "
                    "per-bron LinkML-schema.")
    parser.add_argument("schema", type=Path,
                        help="gematerialiseerd bron-schema (YAML)")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="uitvoerbestand (default: stdout)")
    args = parser.parse_args()

    try:
        schema = yaml.safe_load(args.schema.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fout(f"bestand niet gevonden: {args.schema}")
    except yaml.YAMLError as e:
        fout(f"ongeldige YAML: {e}")

    generator = SDLGenerator(schema)
    sdl = generator.genereer(args.schema.name)

    # Validatie als graphql-core beschikbaar is: zowel syntax als
    # schema-semantiek is blokkerend. Een SDL die build_schema haalt maar
    # validate_schema niet, wordt door consumenten (Apollo, graphql-js,
    # codegenerators) alsnog geweigerd; zo'n schema mag de pipeline dus
    # niet verlaten. Let op interface-covariantie: een implementerend
    # type moet het veldtype van de interface aanhouden, dus een subtype
    # mag een attribuut niet naar een ander type versmallen.
    try:
        from graphql import build_schema, validate_schema
        gebouwd = build_schema(sdl)
        schemafouten = validate_schema(gebouwd)
        if schemafouten:
            for schemafout in schemafouten:
                melding("FOUT", f"schema-semantiek: {schemafout.message}")
            fout(f"gegenereerde SDL is geen geldig GraphQL-schema "
                 f"({len(schemafouten)} fouten)")
        melding("INFO", "SDL gevalideerd met graphql-core")
    except ImportError:
        melding("INFO", "graphql-core niet beschikbaar; "
                        "syntaxvalidatie overgeslagen")
    except Exception as e:
        fout(f"gegenereerde SDL is ongeldig: {e}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(sdl, encoding="utf-8")
    else:
        print(sdl)
    melding("KLAAR", f"{len(generator.classes)} types/interfaces, "
                     f"{len(generator.enums)} enums, "
                     f"{len(generator.gebruikte_scalars)} scalars")


if __name__ == "__main__":
    main()

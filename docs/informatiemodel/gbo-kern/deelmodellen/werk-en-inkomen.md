---
title: "Deelmodel: Werk en Inkomen"
description: "Uitkeringen onder werknemers- en volksverzekeringen, beslissingen, dagloon, arbeidsongeschiktheidspercentage, arbeidsverhouding en arbeidsverleden, ontsloten via het Suwi Gegevensregister."
---

# Deelmodel: Werk en Inkomen

Uitkeringsrelaties, arbeidsverhoudingen en daaraan gekoppelde
besluitvorming op grond van de Wet SUWI en de afzonderlijke
werknemers- en volksverzekeringswetten. Operationele ontsluiting via
het Suwi Gegevensregister, beheerd door BKWI namens UWV; uitvoering
door UWV (werknemersverzekeringen plus Wajong en WIA) of SVB (AOW
en ANW).

Persoonsgegevens van de uitkeringsgerechtigde of werknemer staan in
[Personen](personen.md). De werkgever, uitvoeringsinstelling of
inhoudingsplichtige rechtspersoon staat in
[Bedrijven en instellingen](bedrijven-en-instellingen.md). De
loonaangifteketen-data zelf (Inkomstenverhouding, Inkomstenopgave,
Inkomstenperiode, LoonBestanddeel) staat in
[Belastingen](belastingen.md), omdat de Belastingdienst wettelijk
eigenaar is van die definities. Het `Partij`-supertype staat in het
[hoofdmodel](../hoofdmodel.md).

## Diagram

```plantuml
@startuml
!pragma layout elk

skinparam dpi 140
skinparam classAttributeIconSize 0
skinparam shadowing false
skinparam roundCorner 6
skinparam ClassBackgroundColor #FAFAFA
skinparam ClassBorderColor #555555
skinparam ArrowColor #444444
skinparam ArrowFontColor #333333
skinparam NoteBackgroundColor #FFFCD8
hide empty members
hide circle

skinparam class<<algemeen>> {
  BackgroundColor #f3e5f5
  BorderColor #6a1b9a
  HeaderBackgroundColor #f3e5f5
}
skinparam class<<personen>> {
  BackgroundColor #e8f0fe
  BorderColor #1967d2
  HeaderBackgroundColor #e8f0fe
}
skinparam class<<bedrijven-en-instellingen>> {
  BackgroundColor #fff4e5
  BorderColor #e67e22
  HeaderBackgroundColor #fff4e5
}
skinparam class<<belastingen-loonketen>> {
  BackgroundColor #e3f2fd
  BorderColor #0d47a1
  HeaderBackgroundColor #e3f2fd
}
skinparam class<<werk-en-inkomen>> {
  BackgroundColor #ffe9c2
  BorderColor #b87a00
  HeaderBackgroundColor #ffe9c2
}
skinparam class<<werk-en-inkomen-feit>> {
  BackgroundColor #fff1d8
  BorderColor #c8932d
  HeaderBackgroundColor #fff1d8
}

abstract class Partij <<algemeen>>
abstract class InkomensOndersteuning <<algemeen>>
class NatuurlijkPersoon <<personen>>
class Onderneming <<bedrijven-en-instellingen>>
class Inkomstenverhouding <<belastingen-loonketen>>
class Inkomstenopgave <<belastingen-loonketen>>

abstract class Uitkering <<werk-en-inkomen>>

together {
  class UitkeringWW <<werk-en-inkomen>>
  class UitkeringZW <<werk-en-inkomen>>
  class UitkeringWIA <<werk-en-inkomen>>
  class UitkeringIVA <<werk-en-inkomen>>
  class UitkeringWGA <<werk-en-inkomen>>
  class UitkeringWajong <<werk-en-inkomen>>
  class UitkeringAOW <<werk-en-inkomen>>
}

class Arbeidsverhouding <<werk-en-inkomen>>
class Beslissing <<werk-en-inkomen-feit>>
class Dagloon <<werk-en-inkomen>>
class Arbeidsongeschiktheidspercentage <<werk-en-inkomen-feit>>
class ArbeidsverledenFeit <<werk-en-inkomen-feit>>

Partij <|-- NatuurlijkPersoon
Partij <|-- Onderneming
InkomensOndersteuning <|-- Uitkering
Uitkering <|-- UitkeringWW
Uitkering <|-- UitkeringZW
Uitkering <|-- UitkeringWIA
Uitkering <|-- UitkeringWajong
Uitkering <|-- UitkeringAOW
UitkeringWIA <|-- UitkeringIVA
UitkeringWIA <|-- UitkeringWGA

NatuurlijkPersoon "1" <-- "0..*" Arbeidsverhouding : heeftWerknemer
Onderneming "1" <-- "0..*" Arbeidsverhouding : heeftWerkgever
Arbeidsverhouding "1" --> "0..*" Inkomstenverhouding : komtTotUitingIn
NatuurlijkPersoon "1" <-- "0..*" Uitkering : toegekendAan
Uitkering "n" --> "1" Beslissing : gegrondvestOp
NatuurlijkPersoon "1" <-- "0..*" Beslissing : betreft
Onderneming "1" <-- "0..*" Beslissing : genomenDoor
Inkomstenopgave "1..*" <-- "0..*" Dagloon : berekendOp
Uitkering "0..*" --> "1" Dagloon : basisVoor
Beslissing "1" <-- "0..*" Arbeidsongeschiktheidspercentage : bepaaldDoor
NatuurlijkPersoon "1" <-- "0..*" ArbeidsverledenFeit : betreft

note right of Uitkering
  Concrete varianten:
  WW, ZW, WIA, IVA, WGA,
  Wajong (UWV) en AOW (SVB).
end note

note bottom of Arbeidsverhouding
  Operationeel zichtbaar via
  Inkomstenverhouding-records
  in de loonaangifteketen
  (zie Belastingen).
end note

note right of Dagloon
  Berekend op basis van
  Inkomstenopgave-historie;
  vormt grondslag voor
  uitkeringshoogte.
end note

@enduml
```

## Objecttypen

### Arbeidsongeschiktheidspercentage

**Definitie**: Het door een verzekeringsarts en arbeidsdeskundige
vastgestelde percentage waarmee de verdiencapaciteit van een
werknemer ten opzichte van zijn oude loon is verminderd, op grond
waarvan de WIA-uitkering wordt geclassificeerd in IVA of WGA met hun
fasen.

**Herkomst definitie**: Schattingsbesluit arbeidsongeschiktheidswetten;
Wet werk en inkomen naar arbeidsvermogen.

**Toelichting**: Het percentage bepaalt de uitkeringstak: 80% of meer
duurzaam geeft IVA; 35% tot 80% of 80% of meer niet-duurzaam geeft
WGA; minder dan 35% geeft geen recht op WIA. Een herziening kan
leiden tot een wijziging van uitkeringssoort en hoogte.

| MIM-veld | Waarde |
|---|---|
| Naam | Arbeidsongeschiktheidspercentage |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/Arbeidsongeschiktheidspercentage` |
| Herkomst | SGR cluster Beslissing |
| Datum opname | 2026-05-19 |
| Unieke aanduiding | Combinatie van persoon, beschikkingsdatum en vaststellingsdatum. |
| Populatie | Alle door UWV vastgestelde arbeidsongeschiktheidspercentages die de basis vormen voor classificatie van een WIA-uitkering in IVA of WGA, inclusief herzieningen. |

**Attribuutsoorten**:

| Naam | Type | Kard. | Definitie | Herkomst |
|---|---|---|---|---|
| `percentage` | [Decimaal](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Het AO-percentage. | WIA-beschikking |
| `vaststellingsdatum` | [Datum](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Datum waarop het percentage is vastgesteld. | SGR |
| `duurzaamIndicatie` | [Indicatie](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Bepaalt IVA versus WGA bij volledig AO. | Schattingsbesluit |

### Arbeidsverhouding

**Definitie**: De juridische en feitelijke relatie tussen een
natuurlijk persoon als werknemer en een werkgever op grond waarvan
arbeid wordt verricht tegen beloning, gedurende een bepaalde of
onbepaalde periode.

**Herkomst definitie**: Burgerlijk Wetboek Boek 7 titel 10
(arbeidsovereenkomst); Wet SUWI voor het SUWI-aspect.

**Toelichting**: Arbeidsverhouding ligt boven Inkomstenverhouding
in [Belastingen](belastingen.md): één arbeidsverhouding kan in de
tijd meerdere inkomstenverhoudingen genereren (na contractvernieuwing
of bij wisseling van loonperiode-type). De Arbeidsverhouding-
attributen leggen de afspraak vast; de bijbehorende
inkomstenverhoudingen leggen de uitvoering en de aangifte
loonheffingen vast.

| MIM-veld | Waarde |
|---|---|
| Naam | Arbeidsverhouding |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/Arbeidsverhouding` |
| Herkomst | SGR cluster Arbeidsverhouding |
| Datum opname | 2026-05-19 |
| Unieke aanduiding | Combinatie van werknemer, werkgever en ingangsdatum. |
| Populatie | Alle juridische en feitelijke arbeidsrelaties tussen een natuurlijk persoon als werknemer en een onderneming als werkgever die zichtbaar zijn in het Suwi Gegevensregister. |

**Attribuutsoorten**:

| Naam | Type | Kard. | Definitie | Herkomst |
|---|---|---|---|---|
| `soortDienstverband` | CodeAardArbeidsverhouding | 1 | Aard van de arbeidsverhouding. | SGR + Loonheffingen |
| `ingangsdatum` | [Datum](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Begindatum dienstverband. | SGR |
| `einddatum` | [Datum](../datatypes-en-codelijsten.md#simpele-datatypes) | 0..1 | Einddatum dienstverband. | SGR |
| `proeftijdEinddatum` | [Datum](../datatypes-en-codelijsten.md#simpele-datatypes) | 0..1 | Einde proeftijd. | SGR |
| `beroep` | [Tekst](../datatypes-en-codelijsten.md#simpele-datatypes) | 0..1 | Functie of vakgebied. | SGR |
| `redenEinde` | CodeRedenEindeArbeidsverhouding | 0..1 | Reden van einde. | Loonheffingen bijlage |
| `overnameIndicatie` | [Indicatie](../datatypes-en-codelijsten.md#simpele-datatypes) | 0..1 | Onderneming in overnameproces. | SGR |

### ArbeidsverledenFeit

**Definitie**: Een afzonderlijk feit in het arbeids- of inkomensverleden
van een natuurlijk persoon, zoals een periode in dienst, een periode
met uitkering of een leerwerk-periode, dat relevant is voor de
berekening van werknemersverzekerings-rechten.

**Herkomst definitie**: Werkloosheidswet (refertes 26-uit-36-weken en
4-uit-5-jaren); SGR cluster Arbeidsverhouding.

**Toelichting**: Arbeidsverleden bepaalt onder andere de WW-duur.
ArbeidsverledenFeit dient als bouwsteen waarmee UWV een
arbeidsverleden-overzicht kan opstellen, met feit-typen voor
dienstverband, uitkeringsperiode, leerwerk-periode en periode van
zelfstandig werk.

| MIM-veld | Waarde |
|---|---|
| Naam | ArbeidsverledenFeit |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/ArbeidsverledenFeit` |
| Herkomst | SGR cluster Arbeidsverhouding |
| Datum opname | 2026-05-19 |
| Unieke aanduiding | Combinatie van persoon, soortFeit, begindatum en einddatum. |
| Populatie | Alle afzonderlijke feiten in het arbeids- of inkomensverleden van een natuurlijk persoon (dienstverband, uitkeringsperiode, leerwerk-periode of periode zelfstandig werk) die relevant zijn voor de berekening van werknemersverzekerings-rechten. |

**Attribuutsoorten**:

| Naam | Type | Kard. | Definitie | Herkomst |
|---|---|---|---|---|
| `soortFeit` | [Tekst](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Dienstverband, Uitkering, Leerwerk of ZelfstandigWerk. | SGR |
| `begindatum` | [Datum](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Aanvang van het feit. | SGR |
| `einddatum` | [Datum](../datatypes-en-codelijsten.md#simpele-datatypes) | 0..1 | Einde van het feit. | SGR |
| `sv-loonbedrag` | [Bedrag](../datatypes-en-codelijsten.md#aanvullende-datatypes) | 0..1 | Cumulatief SV-loon over de periode. | Loonaangifteketen |

### Beslissing

**Definitie**: Een door een uitvoerings-instelling in het SUWI-stelsel
genomen besluit over het recht op, de hoogte van of de beeindiging
van een uitkering of een andere voorziening voor een natuurlijk
persoon.

**Herkomst definitie**: Wet SUWI; Algemene wet bestuursrecht (Awb)
hoofdstuk 4 (beschikking); de afzonderlijke werknemers- en
volksverzekeringswetten.

**Toelichting**: Beslissing is de juridische grondslag onder een
uitkering. Een uitkering bestaat alleen als er een geldige
beschikking onder ligt. Wijzigingen (verhoging, verlaging,
beeindiging) zijn elk afzonderlijke beschikkingen.

| MIM-veld | Waarde |
|---|---|
| Naam | Beslissing |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/Beslissing` |
| Herkomst | SGR cluster Beslissing |
| Datum opname | 2026-05-19 |
| Unieke aanduiding | Beschikkingsnummer (UWV of SVB). |
| Populatie | Alle door een SUWI-uitvoeringsinstelling (UWV, SVB) genomen besluiten over het recht op, de hoogte van of de beeindiging van een uitkering of voorziening voor een natuurlijk persoon. |

**Attribuutsoorten**:

| Naam | Type | Kard. | Definitie | Herkomst |
|---|---|---|---|---|
| `beschikkingsnummer` | [Tekst](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Identifier van de beschikking. | SGR |
| `beschikkingsdatum` | [Datum](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Datum van de beschikking. | SGR |
| `beslissingSoort` | [BeslissingSoort](#beslissingsoort) | 1 | Toekenning, herziening of beeindiging. | SGR |
| `betrefftSoortUitkering` | [SoortUitkering](#soortuitkering) | 0..1 | Op welke uitkering de beschikking ziet. | SGR |

### Dagloon

**Definitie**: Het op grond van de Dagloonregels werknemersverzekeringen
voor een specifieke uitkering vastgestelde dagloon, dat dient als
grondslag voor de hoogte van de uitkering en wordt berekend op basis
van de inkomstenopgaven over de referteperiode.

**Herkomst definitie**: Dagloonregels werknemersverzekeringen 2015
(ministeriele regeling); Werkloosheidswet, Ziektewet en Wet WIA.

**Toelichting**: Het dagloon wordt door UWV berekend uit de
loonaangifteketen-data (Inkomstenopgave-records in de
referteperiode, doorgaans een jaar). Het wordt gemaximeerd op het
wettelijk maximumdagloon, jaarlijks door SZW vastgesteld.

| MIM-veld | Waarde |
|---|---|
| Naam | Dagloon |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/Dagloon` |
| Herkomst | SGR cluster Uitkering |
| Datum opname | 2026-05-19 |
| Unieke aanduiding | Combinatie van persoon, uitkering en peildatum. |
| Populatie | Alle door UWV vastgestelde daglonen die als grondslag dienen voor de hoogte van een werknemersverzekerings-uitkering, berekend uit de inkomstenopgaven over de referteperiode. |

**Attribuutsoorten**:

| Naam | Type | Kard. | Definitie | Herkomst |
|---|---|---|---|---|
| `dagloonBedrag` | [Bedrag](../datatypes-en-codelijsten.md#aanvullende-datatypes) | 1 | Het vastgestelde dagloon. | Dagloonregels |
| `peildatum` | [Datum](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Peilmoment voor de berekening. | SGR |
| `referteperiodeStart` | [Datum](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Aanvang van de referteperiode. | Dagloonregels art. 2 |
| `referteperiodeEinde` | [Datum](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Einde van de referteperiode. | Dagloonregels art. 2 |
| `maximumDagloon` | [Bedrag](../datatypes-en-codelijsten.md#aanvullende-datatypes) | 0..1 | Wettelijk maximum-dagloon op de peildatum. | SZW jaartabel |

### InkomensOndersteuning

**Definitie**: Een door of namens de overheid aan een natuurlijk
persoon verstrekte financiele bijdrage met als doel
inkomensondersteuning, in de vorm van een inkomensafhankelijke
regeling of een sociale-zekerheidsuitkering.

**Herkomst definitie**: Algemene wet inkomensafhankelijke regelingen
(Awir) voor toeslagen; Wet SUWI en de afzonderlijke werknemers- en
volksverzekeringswetten voor uitkeringen; GBO-Kern-abstractie.

**Toelichting**: Cross-domein algemene categorie boven Toeslag (in
[Belastingen](belastingen.md)) en Uitkering (in dit deelmodel).
Beide takken delen de basis-eigenschappen rechthebbende natuurlijk
persoon, toekenningsperiode, bedrag en grondslag-beschikking; de
varianten verschillen in juridische basis, uitvoerings-organisatie
en aanvraagprocedure.

| MIM-veld | Waarde |
|---|---|
| Naam | InkomensOndersteuning |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/InkomensOndersteuning` |
| Herkomst | Cross-domein abstractie |
| Datum opname | 2026-05-19 |
| Indicatie abstract object | Ja |
| Populatie | Alle door of namens de overheid aan natuurlijke personen verstrekte financiele bijdragen met als doel inkomensondersteuning, omvattende zowel toeslagen (Awir) als sociale-zekerheidsuitkeringen (werknemers- en volksverzekeringen). |

**Attribuutsoorten**:

| Naam | Type | Kard. | Definitie | Herkomst |
|---|---|---|---|---|
| `identificatie` | [Tekst](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Interne identificatie. | GBO-Kern |
| `ingangsdatum` | [Datum](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Aanvang van de toekenning. | Awir / Wet SUWI |
| `einddatum` | [Datum](../datatypes-en-codelijsten.md#simpele-datatypes) | 0..1 | Einde van de toekenning. | Awir / Wet SUWI |
| `bedragPeriode` | [Bedrag](../datatypes-en-codelijsten.md#aanvullende-datatypes) | 1 | Bedrag per periode. | per regeling |

### Uitkering

**Definitie**: Een door of namens de overheid aan een natuurlijk
persoon toegekende periodieke uitkering op grond van een
werknemersverzekering of volksverzekering, ter vervanging of
aanvulling van loon.

**Herkomst definitie**: Wet SUWI plus de afzonderlijke werknemers-
en volksverzekeringswetten (Werkloosheidswet, Ziektewet, Wet WIA,
Wajong, AOW).

**Toelichting**: Zeven concrete varianten, uitgevoerd door UWV
(WW, ZW, WIA, IVA, WGA, Wajong) of SVB (AOW).

| MIM-veld | Waarde |
|---|---|
| Naam | Uitkering |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/Uitkering` |
| Herkomst | SGR cluster Uitkering |
| Datum opname | 2026-05-19 |
| Indicatie abstract object | Ja |
| Unieke aanduiding | Combinatie van persoon, soortUitkering en toekenningsperiode. |
| Populatie | Alle aan natuurlijke personen toegekende periodieke uitkeringen op grond van een werknemersverzekering (WW, ZW, WIA, IVA, WGA, Wajong) of volksverzekering (AOW), uitgevoerd door UWV of SVB. |

**Attribuutsoorten**:

| Naam | Type | Kard. | Definitie | Herkomst |
|---|---|---|---|---|
| `soortUitkering` | [SoortUitkering](#soortuitkering) | 1 | Welke uitkering. | SGR |
| `ingangsdatum` | [Datum](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Aanvang van de uitkering. | SGR |
| `einddatum` | [Datum](../datatypes-en-codelijsten.md#simpele-datatypes) | 0..1 | Einde van de uitkering. | SGR |
| `bedragMaand` | [Bedrag](../datatypes-en-codelijsten.md#aanvullende-datatypes) | 0..1 | Maandelijks bedrag. | SGR |
| `redenEinde` | [RedenEindeUitkering](#redeneindeuitkering) | 0..1 | Reden van einde van de uitkering. | SGR |

### UitkeringAOW

**Definitie**: Een door SVB op grond van de Algemene Ouderdomswet
toegekende periodieke uitkering aan personen vanaf de AOW-gerechtigde
leeftijd, gebaseerd op de in Nederland opgebouwde verzekerde jaren.

**Herkomst definitie**: Algemene Ouderdomswet (AOW).

**Toelichting**: Anders dan de overige uitkeringen, die UWV uitvoert,
wordt AOW uitgevoerd door SVB. Het Suwi Gegevensregister ontsluit
een deel van de AOW-administratie voor afnemers in het SUWI-stelsel;
voor het volledige beeld is mogelijk een directe SVB-aansluiting
nodig.

| MIM-veld | Waarde |
|---|---|
| Naam | UitkeringAOW |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/UitkeringAOW` |
| Herkomst | SGR (ontsluiting); SVB (uitvoering) |
| Datum opname | 2026-05-19 |
| Notation | AOW |
| Unieke aanduiding | Combinatie van BSN en AOW-toekenningsperiode. |
| Populatie | Alle door SVB op grond van de Algemene Ouderdomswet toegekende periodieke uitkeringen aan natuurlijke personen vanaf de AOW-gerechtigde leeftijd. |

**Attribuutsoorten**:

| Naam | Type | Kard. | Definitie | Herkomst |
|---|---|---|---|---|
| `aowGerechtigdeLeeftijd` | [Geheel](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Ingangsleeftijd voor deze persoon. | AOW |
| `opgebouwdeVerzekerdeJaren` | [Geheel](../datatypes-en-codelijsten.md#simpele-datatypes) | 0..1 | Maximaal 50; bepaalt 100%-opbouw. | SVB |
| `aowHoogteCategorie` | [Tekst](../datatypes-en-codelijsten.md#simpele-datatypes) | 0..1 | Alleenstaande, gehuwd of samenwonend. | SVB |

### UitkeringIVA

**Definitie**: De Inkomensvoorziening Volledig Arbeidsongeschikten op
grond van de WIA, toegekend aan werknemers die duurzaam minder dan
twintig procent van hun oude loon kunnen verdienen.

**Herkomst definitie**: Wet WIA hoofdstuk IV (IVA-regeling).

**Toelichting**: IVA-criterium: minder dan 20% van het oude loon
kunnen verdienen en geen herstel verwacht. De uitkering is hoger en
stabieler dan WGA omdat het duurzaamheids-criterium is gehaald.

| MIM-veld | Waarde |
|---|---|
| Naam | UitkeringIVA |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/UitkeringIVA` |
| Herkomst | SGR cluster Uitkering |
| Datum opname | 2026-05-19 |
| Notation | IVA |
| Unieke aanduiding | Combinatie van BSN en IVA-toekenningsperiode. |
| Populatie | Alle door UWV toegekende IVA-uitkeringen aan werknemers die duurzaam minder dan twintig procent van hun oude loon kunnen verdienen, op grond van hoofdstuk IV van de Wet WIA. |

**Attribuutsoorten**:

| Naam | Type | Kard. | Definitie | Herkomst |
|---|---|---|---|---|
| `dagloonBedrag` | [Bedrag](../datatypes-en-codelijsten.md#aanvullende-datatypes) | 1 | Berekeningsbasis. | SGR |
| `uitkeringspercentage` | [Decimaal](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | 75% van dagloon. | Wet WIA |

### UitkeringWajong

**Definitie**: Een door UWV op grond van de Wet
arbeidsongeschiktheidsvoorziening jonggehandicapten toegekende
periodieke uitkering aan jonggehandicapten die door
arbeidsongeschiktheid niet of beperkt kunnen werken.

**Herkomst definitie**: Wajong (drie generaties: oude Wajong,
Wajong 2010, Wajong 2015).

**Toelichting**: Drie historische generaties met eigen voorwaarden:
oude Wajong (toekenningen voor 2010), Wajong 2010 (instroom
2010-2014, met werkregeling) en Wajong 2015 (vanaf 2015, uitsluitend
voor duurzaam volledig arbeidsongeschikten).

| MIM-veld | Waarde |
|---|---|
| Naam | UitkeringWajong |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/UitkeringWajong` |
| Herkomst | SGR cluster Uitkering |
| Datum opname | 2026-05-19 |
| Notation | Wajong |
| Unieke aanduiding | Combinatie van BSN en Wajong-toekenningsperiode. |
| Populatie | Alle door UWV toegekende Wajong-uitkeringen aan jonggehandicapten, verdeeld over de drie generaties oude Wajong (toekenningen voor 2010), Wajong 2010 en Wajong 2015. |

**Attribuutsoorten**:

| Naam | Type | Kard. | Definitie | Herkomst |
|---|---|---|---|---|
| `wajongGeneratie` | [Tekst](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | OudeWajong, Wajong2010 of Wajong2015. | SGR |
| `arbeidsongeschiktheidspercentage` | [Decimaal](../datatypes-en-codelijsten.md#simpele-datatypes) | 0..1 | Bij relevante generatie. | Wajong-beschikking |

### UitkeringWGA

**Definitie**: De Werkhervatting Gedeeltelijk Arbeidsongeschikten op
grond van de WIA, toegekend aan werknemers die vijfendertig procent
tot tachtig procent arbeidsongeschikt zijn, of volledig
arbeidsongeschikt maar niet duurzaam.

**Herkomst definitie**: Wet WIA hoofdstuk VII (WGA-regeling).

**Toelichting**: Drie fasen: LGU (loongerelateerde uitkering, op
basis van arbeidsverleden), LAU (loonaanvullingsuitkering, wanneer
de uitkering minus resterende verdiencapaciteit boven een drempel
uitkomt) en VVU (vervolguitkering, gerelateerd aan
minimumloon-percentages).

| MIM-veld | Waarde |
|---|---|
| Naam | UitkeringWGA |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/UitkeringWGA` |
| Herkomst | SGR cluster Uitkering |
| Datum opname | 2026-05-19 |
| Notation | WGA |
| Unieke aanduiding | Combinatie van BSN en WGA-toekenningsperiode. |
| Populatie | Alle door UWV toegekende WGA-uitkeringen aan werknemers die 35 tot 80 procent arbeidsongeschikt zijn, of volledig maar niet duurzaam, verdeeld over de fasen LGU, LAU en VVU. |

**Attribuutsoorten**:

| Naam | Type | Kard. | Definitie | Herkomst |
|---|---|---|---|---|
| `dagloonBedrag` | [Bedrag](../datatypes-en-codelijsten.md#aanvullende-datatypes) | 1 | Berekeningsbasis. | SGR |
| `arbeidsongeschiktheidspercentage` | [Decimaal](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Bepaalt fase en hoogte. | WIA-beschikking |
| `wgaFase` | [Tekst](../datatypes-en-codelijsten.md#simpele-datatypes) | 0..1 | LGU, LAU of VVU. | SGR |

### UitkeringWIA

**Definitie**: Een door UWV op grond van de Wet werk en inkomen naar
arbeidsvermogen toegekende periodieke uitkering aan een werknemer
die na een wachttijd van twee jaar van ziekte gedeeltelijk of
volledig arbeidsongeschikt is.

**Herkomst definitie**: Wet WIA.

**Toelichting**: De WIA splitst zich in IVA (volledig duurzaam
arbeidsongeschikt) en WGA (gedeeltelijk of niet-duurzaam
arbeidsongeschikt). UitkeringWIA is in dit deelmodel de
gemeenschappelijke aanwijzing; concrete varianten zijn UitkeringIVA
en UitkeringWGA.

| MIM-veld | Waarde |
|---|---|
| Naam | UitkeringWIA |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/UitkeringWIA` |
| Herkomst | SGR cluster Uitkering |
| Datum opname | 2026-05-19 |
| Notation | WIA |
| Unieke aanduiding | Combinatie van BSN en WIA-toekenningsperiode. |
| Populatie | Alle door UWV toegekende WIA-uitkeringen aan werknemers die na de wachttijd van twee jaar ziekte gedeeltelijk of volledig arbeidsongeschikt zijn; concreet uitgesplitst naar UitkeringIVA en UitkeringWGA. |

**Attribuutsoorten**:

| Naam | Type | Kard. | Definitie | Herkomst |
|---|---|---|---|---|
| `dagloonBedrag` | [Bedrag](../datatypes-en-codelijsten.md#aanvullende-datatypes) | 1 | Berekeningsbasis. | SGR |
| `arbeidsongeschiktheidspercentage` | [Decimaal](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Vastgesteld door UWV. | WIA-beschikking |

### UitkeringWW

**Definitie**: Een door UWV aan een werkloze werknemer toegekende
periodieke uitkering op grond van de Werkloosheidswet, ter
vervanging van het weggevallen loon.

**Herkomst definitie**: Werkloosheidswet hoofdstukken II en III.

**Toelichting**: Hoogte gebaseerd op het dagloon vermenigvuldigd met
een percentage dat in de tijd kan dalen. Duur afhankelijk van
arbeidsverledenjaren (basis-WW plus eventueel verlengde uitkering).

| MIM-veld | Waarde |
|---|---|
| Naam | UitkeringWW |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/UitkeringWW` |
| Herkomst | SGR cluster Uitkering |
| Datum opname | 2026-05-19 |
| Notation | WW |
| Unieke aanduiding | Combinatie van BSN en WW-toekenningsperiode. |
| Populatie | Alle door UWV aan werkloze werknemers toegekende WW-uitkeringen ter vervanging van weggevallen loon, op grond van de Werkloosheidswet. |

**Attribuutsoorten**:

| Naam | Type | Kard. | Definitie | Herkomst |
|---|---|---|---|---|
| `dagloonBedrag` | [Bedrag](../datatypes-en-codelijsten.md#aanvullende-datatypes) | 1 | Berekeningsbasis. | SGR |
| `uitkeringspercentage` | [Decimaal](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Aanvankelijk 75%, daarna 70%. | WW art. 47 |
| `arbeidsverledenJaren` | [Geheel](../datatypes-en-codelijsten.md#simpele-datatypes) | 0..1 | Bepaalt duur uitkering. | SGR |

### UitkeringZW

**Definitie**: Een door UWV aan een zieke werknemer of vangnetter
toegekende periodieke uitkering op grond van de Ziektewet, ter
vervanging van het door ziekte weggevallen loon.

**Herkomst definitie**: Ziektewet.

**Toelichting**: ZW dekt het vangnet-deel van de ziektevoorziening:
uitzendkrachten, oproepkrachten, werklozen en werknemers zonder
doorbetalingsplichtige werkgever. Werknemers met een
doorbetalingsplichtige werkgever krijgen loondoorbetaling van die
werkgever en vallen niet onder ZW.

| MIM-veld | Waarde |
|---|---|
| Naam | UitkeringZW |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/UitkeringZW` |
| Herkomst | SGR cluster Uitkering |
| Datum opname | 2026-05-19 |
| Notation | ZW |
| Unieke aanduiding | Combinatie van BSN en ZW-toekenningsperiode. |
| Populatie | Alle door UWV toegekende ZW-uitkeringen aan zieke werknemers en vangnetters (uitzendkrachten, oproepkrachten, werklozen, werknemers zonder doorbetalingsplichtige werkgever) ter vervanging van weggevallen loon. |

**Attribuutsoorten**:

| Naam | Type | Kard. | Definitie | Herkomst |
|---|---|---|---|---|
| `dagloonBedrag` | [Bedrag](../datatypes-en-codelijsten.md#aanvullende-datatypes) | 1 | Berekeningsbasis. | SGR |
| `uitkeringspercentage` | [Decimaal](../datatypes-en-codelijsten.md#simpele-datatypes) | 1 | Doorgaans 70%. | ZW art. 29 |

## Enumeraties

### BeslissingSoort

**Definitie**: De soorten besluit die in het SUWI-stelsel door UWV
of SVB kunnen worden genomen over uitkeringen en voorzieningen.

**Herkomst definitie**: SGR cluster Beslissing.

**Toelichting**: De waardenset onderscheidt de juridisch relevante
beslissoorten die een uitkering doen ontstaan, wijzigen of laten
eindigen, plus de procedurele soorten afwijzing, beslissing op
bezwaar en sanctie. Per uitkering kan een keten van Beslissingen
bestaan, beginnend bij een Toekenning en eventueel gevolgd door
Herziening of Beeindiging.

| MIM-veld | Waarde |
|---|---|
| Naam | BeslissingSoort |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/BeslissingSoort` |
| Herkomst | SGR |
| Datum opname | 2026-05-19 |

**Gebruikt door**: `Beslissing.beslissingSoort`.

**Waarden**:

| Code | Naam | Definitie | Toelichting |
|---|---|---|---|
| Toekenning | Toekenning uitkering | Besluit waarbij een nieuwe uitkering wordt toegekend. | Eerste beschikking onder een uitkering. |
| Herziening | Herziening uitkering | Besluit waarbij hoogte of grondslag van een lopende uitkering wijzigt. | Bij wijziging van AO-percentage, dagloon of relevante feiten. |
| Beeindiging | Beeindiging uitkering | Besluit waarbij een lopende uitkering eindigt. | Bij werkhervatting, einde wachttijd, AOW-leeftijd of overlijden. |
| Afwijzing | Afwijzing aanvraag | Besluit waarbij een aanvraag voor een uitkering wordt afgewezen. | Geen uitkering ontstaat. |
| Bezwaar | Beslissing op bezwaar | Heroverweging van een eerder besluit na een ingediend bezwaarschrift. | Awb hoofdstuk 7. |
| Sanctie | Sanctie-besluit | Besluit waarbij een korting of maatregel wordt opgelegd wegens niet-nakomen van verplichtingen. | Bijvoorbeeld bij weigering passende arbeid of niet-melden van inkomsten. |

### RedenEindeUitkering

**Definitie**: De redenen waarom een uitkering kan eindigen op grond
van de werknemers- of volksverzekeringswetten.

**Herkomst definitie**: SGR cluster Uitkering.

**Toelichting**: Top 10 weergegeven; volledige set te bevestigen
tegen SGR-publicatie.

| MIM-veld | Waarde |
|---|---|
| Naam | RedenEindeUitkering |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/RedenEindeUitkering` |
| Herkomst | SGR |
| Datum opname | 2026-05-19 |

**Gebruikt door**: `Uitkering.redenEinde`.

**Waarden (top 10)**:

| Code | Naam | Definitie | Toelichting |
|---|---|---|---|
| WerkHervat | Werk hervat | Uitkering eindigt omdat de rechthebbende weer aan het werk is. | Meest voorkomende reden bij WW en ZW. |
| TermijnVerstreken | Maximale uitkeringsduur bereikt | Uitkering eindigt omdat de wettelijke maximumduur is verstreken. | Bij WW gerelateerd aan arbeidsverleden. |
| Herkeuring | Herkeuring leidt tot beeindiging | Uitkering eindigt na een nieuwe medische of arbeidskundige beoordeling. | Bij WIA en Wajong. |
| BereiktAOW | AOW-leeftijd bereikt | Uitkering eindigt omdat de rechthebbende de AOW-gerechtigde leeftijd heeft bereikt. | Overgang naar AOW. |
| Overlijden | Persoon is overleden | Uitkering eindigt door overlijden van de rechthebbende. | Trigger via BRP cat 06. |
| Emigratie | Persoon is gemigreerd | Uitkering eindigt omdat de rechthebbende naar het buitenland is vertrokken. | Tenzij export-recht van toepassing is. |
| Sanctie | Sanctie wegens niet-nakomen verplichtingen | Uitkering eindigt als gevolg van een sanctie-besluit. | Zie BeslissingSoort = Sanctie. |
| Detentie | Persoon zit in detentie | Uitkering eindigt omdat de rechthebbende in detentie verblijft. | Uitsluitingsgrond op grond van de SV-wetgeving. |
| WeigeringMedewerking | Weigering medewerking re-integratie | Uitkering eindigt na vastgestelde weigering om mee te werken aan re-integratie. | Bij WW, ZW en WIA. |
| BeeindigingDoorWerknemer | Vrijwillige beeindiging | Uitkering eindigt op verzoek van de rechthebbende zelf. | Bijvoorbeeld bij start eigen bedrijf. |

### SoortUitkering

**Definitie**: De soorten uitkering die in het deelmodel Werk en
Inkomen worden onderscheiden, gebaseerd op de werknemers- en
volksverzekeringswetten.

**Herkomst definitie**: SGR cluster Uitkering.

**Toelichting**: De waardenset dekt de zeven concrete uitkerings-
takken die binnen het SUWI-stelsel worden uitgevoerd door UWV
(WW, ZW, WIA, IVA, WGA, Wajong) of SVB (AOW). De codes komen
overeen met de gangbare juridische afkortingen van de
onderliggende wetten.

| MIM-veld | Waarde |
|---|---|
| Naam | SoortUitkering |
| Begrip (URI) | `https://begrippen.gbo-semantiek.nl/id/begrip/SoortUitkering` |
| Herkomst | SGR |
| Datum opname | 2026-05-19 |

**Gebruikt door**: `Uitkering.soortUitkering`.

**Waarden**:

| Code | Naam | Wettelijke basis | Definitie | Toelichting |
|---|---|---|---|---|
| WW | Werkloosheidsuitkering | Werkloosheidswet | Uitkering aan werkloze werknemer ter vervanging van weggevallen loon. | Uitgevoerd door UWV. |
| ZW | Ziektewet-uitkering | Ziektewet | Uitkering aan zieke werknemer of vangnetter ter vervanging van door ziekte weggevallen loon. | Uitgevoerd door UWV. |
| WIA | WIA-uitkering | Wet WIA | Uitkering aan werknemer die na wachttijd van twee jaar ziekte arbeidsongeschikt is. | Verzamel-aanduiding; concrete tak IVA of WGA. |
| IVA | IVA-uitkering | Wet WIA hoofdstuk IV | Uitkering aan werknemer die duurzaam minder dan 20% van zijn oude loon kan verdienen. | WIA-subvorm; hoger en stabieler dan WGA. |
| WGA | WGA-uitkering | Wet WIA hoofdstuk VII | Uitkering aan werknemer die 35-80% arbeidsongeschikt is, of volledig maar niet duurzaam. | WIA-subvorm; drie fasen (LGU, LAU, VVU). |
| Wajong | Wajong-uitkering | Wajong | Uitkering aan jonggehandicapte die door arbeidsongeschiktheid niet of beperkt kan werken. | Drie generaties (oude Wajong, Wajong 2010, Wajong 2015). |
| AOW | AOW-uitkering | Algemene Ouderdomswet | Uitkering aan persoon vanaf de AOW-gerechtigde leeftijd op basis van opgebouwde verzekerde jaren. | Uitgevoerd door SVB. |

## Codelijsten

Deelmodel-specifieke codelijsten. Stelselbrede codelijsten staan op
de [Datatypes en codelijsten](../datatypes-en-codelijsten.md).
Loonketen-codelijsten (CodeAardArbeidsverhouding,
CodeSoortInkomstenverhouding, CodeRedenEindeArbeidsverhouding) staan
in [Belastingen](belastingen.md), omdat de Belastingdienst eigenaar
is van de loonketen-definities; ze worden hier alleen gerefereerd.

| Codelijst | Bron / beheerder | GBO-typering | Gebruikt door |
|---|---|---|---|
| [SoortUitkering](#soortuitkering) | SGR cluster Uitkering / BKWI namens UWV | inline-enum | `Uitkering.soortUitkering` |
| [RedenEindeUitkering](#redeneindeuitkering) | SGR cluster Uitkering / BKWI namens UWV | inline-enum | `Uitkering.redenEinde` |
| [BeslissingSoort](#beslissingsoort) | SGR cluster Beslissing / BKWI namens UWV | inline-enum | `Beslissing.beslissingSoort` |

### Onderhoudsritme

| Codelijst | Mutatieritme | Bron |
|---|---|---|
| SoortUitkering | Per wetswijziging | UWV via SGR |
| RedenEindeUitkering | Per wetswijziging | UWV via SGR |
| BeslissingSoort | Per wetswijziging | UWV via SGR |

## Stelselkoppelingen

- Naar [Personen](personen.md): `NatuurlijkPersoon` is de werknemer
  in een arbeidsverhouding, de uitkeringsgerechtigde in een uitkering,
  het subject van een beslissing en de drager van een arbeidsverleden.
- Naar [Bedrijven en instellingen](bedrijven-en-instellingen.md): een
  `Onderneming` is de werkgever in een arbeidsverhouding; UWV en SVB
  zijn `NietNatuurlijkPersoon`-instanties die optreden als
  uitvoerings-instelling bij een beslissing.
- Naar [Belastingen](belastingen.md): de loonketen-objecten zijn
  inhoudelijk eigendom van de Belastingdienst en zitten daar in het
  deelmodel. Werk en Inkomen verwijst:
  `Arbeidsverhouding.komtTotUitingIn` naar `Inkomstenverhouding`;
  `Dagloon.berekendOp` naar `Inkomstenopgave`.

## Bron

Autoritatieve bron voor dit deelmodel: het **Suwi Gegevensregister
(SGR)**, beheerd door BKWI namens UWV. Wettelijke grondslag in de
Wet SUWI en het Besluit SUWI; Bijlage 1 SGR koppelt per attribuut
een wetsartikel.

De afzonderlijke werknemers- en volksverzekeringswetten leveren de
inhoudelijke kaders:

- **Werkloosheidswet (WW)** voor UitkeringWW.
- **Ziektewet (ZW)** voor UitkeringZW.
- **Wet werk en inkomen naar arbeidsvermogen (WIA)** voor
  UitkeringWIA met de subtype-tak naar UitkeringIVA en UitkeringWGA.
- **Wajong** voor UitkeringWajong met drie generaties.
- **Algemene Ouderdomswet (AOW)** voor UitkeringAOW (uitgevoerd door
  SVB).

De loonaangifteketen waarop dit deelmodel operationeel leunt
(Inkomstenverhouding, Inkomstenopgave, Inkomstenperiode,
LoonBestanddeel) is inhoudelijk eigendom van de Belastingdienst
(Wet LB 1964; Besluit SUWI art. 5.1) en staat in
[Belastingen](belastingen.md). SGR is voor die laag een
ontsluitingskanaal, niet de definitie-bron.

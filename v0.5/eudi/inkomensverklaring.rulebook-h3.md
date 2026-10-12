# Inkomensverklaring: attributen en metadata

!!! note "Gegenereerd"
    Gegenereerd uit het attestatieprofiel `inkomensverklaring.yaml` met
    `tools/genereer_attestatie.py`. Dit is hoofdstuk 3 van een
    Attestation Rulebook (ARF-sjabloon): de claims, los van hun
    codering. Codering, gebruik, vertrouwensankers, intrekking en
    compliance staan niet in het profiel.

| Kenmerk | Waarde |
|---|---|
| Attestatietype | `Inkomensverklaring` (https://lod.gbo-semantiek.nl/attestaties/Inkomensverklaring) |
| Type-id en versie | `inkomensverklaring` 3.0 |
| Juridische categorie | PuB-EAA |
| Bron | bronprofiel `via`, query `aangifteOverJaar`, type `AangifteInkomstenbelasting` |
| Subject | `bsn`, uit de PID |
| Aanbiedingen | `jaar` = 2024, 2025 |

## 3.1 Inleiding

Verklaring van het inkomen dat in de aangifte inkomstenbelasting over één belastingjaar is aangegeven, volgens de Belastingdienst.

Bron: de aangifte inkomstenbelasting zoals het VIA-profiel die levert. De status geeft aan in welk stadium de aangifte is: vooringevuld, ingediend of herzien. Een vastgesteld inkomen staat niet in deze verklaring; dat komt uit de aanslag (bri-plus) of, als authentiek gegeven, uit de BRI.

Typeversie 3.0. De demo publiceert 2.3; de Type Metadata van een versie is onveranderlijk, en dit profiel wijkt af: de query volgt het v0.5-model, aangifte_status is verplicht en indieningsdatum en de box-inkomens zijn optioneel.

## 3.2 Verplichte attributen

| Data identifier | Definitie | Datatype | Voorbeeld | Semantisch anker | Bronpad |
|---|---|---|---|---|---|
| `belastingjaar` | Het belastingjaar waarop de aangifte betrekking heeft. | integer (jaar) | 2024 | [`gbo:belastingen/fiscaleopgave/belastingjaar`](https://lod.gbo-semantiek.nl/belastingen/fiscaleopgave/belastingjaar) (exact) | `belastingjaar` |
| `verzamelinkomen` | Het in de aangifte aangegeven verzamelinkomen, in hele euro's. | integer (EUR) | 43000 | [`gbo:belastingen/aangifteinkomstenbelasting/verzamelinkomen`](https://lod.gbo-semantiek.nl/belastingen/aangifteinkomstenbelasting/verzamelinkomen) (close) | `verzamelinkomen.waarde` |
| `aangifte_status` | Het stadium van de aangifte: Voorinvulling, Ingediend of Herzien. | string | Ingediend | [`gbo:belastingen/aangifte/status`](https://lod.gbo-semantiek.nl/belastingen/aangifte/status) (exact) | `status` |

## 3.3 Optionele attributen

| Data identifier | Definitie | Datatype | Voorbeeld | Semantisch anker | Bronpad |
|---|---|---|---|---|---|
| `indieningsdatum` | De datum waarop de aangifte is ingediend. | full-date | 2025-04-15 | [`gbo:belastingen/aangifte/indieningsdatum`](https://lod.gbo-semantiek.nl/belastingen/aangifte/indieningsdatum) (exact) | `indieningsdatum` |
| `inkomen_box1` | Het in de aangifte aangegeven inkomen uit werk en woning, in hele euro's. | integer (EUR) | 41000 | [`gbo:belastingen/aangifteinkomstenbelasting/box1inkomen`](https://lod.gbo-semantiek.nl/belastingen/aangifteinkomstenbelasting/box1inkomen) (close) | `box1Inkomen.waarde` |
| `inkomen_box2` | Het in de aangifte aangegeven inkomen uit aanmerkelijk belang, in hele euro's. | integer (EUR) | 0 | [`gbo:belastingen/aangifteinkomstenbelasting/box2inkomen`](https://lod.gbo-semantiek.nl/belastingen/aangifteinkomstenbelasting/box2inkomen) (close) | `box2Inkomen.waarde` |
| `inkomen_box3` | Het in de aangifte aangegeven inkomen uit sparen en beleggen, in hele euro's. | integer (EUR) | 2000 | [`gbo:belastingen/aangifteinkomstenbelasting/box3inkomen`](https://lod.gbo-semantiek.nl/belastingen/aangifteinkomstenbelasting/box3inkomen) (close) | `box3Inkomen.waarde` |

## 3.4 Conditionele attributen

Niet gespecificeerd.

## 3.5 Verplichte metadata

| Data identifier | Definitie | Datatype | Vaste waarde | Gevuld door |
|---|---|---|---|---|
| `attestation_legal_category` | De juridische categorie waaronder de attestatie is uitgegeven. | string | `PuB-EAA` | uitgever |
| `issuing_authority` | De naam van de instantie die de attestatie uitgeeft. | string | - | uitgever |
| `issuing_country` | Landcode (ISO 3166-1 alpha-2) van de uitgevende instantie. | string | `NL` | uitgever |

## 3.6 Optionele metadata

Niet gespecificeerd.

## 3.7 Conditionele metadata

Niet gespecificeerd.

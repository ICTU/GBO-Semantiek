# Naamgeving

Deze pagina beschrijft de naamgevingsconventies voor modelelementen en URI-paden in GBO-Semantiek. Naamgeving is een concrete uitwerking van het ontwerpprincipe [S-02 FAIR als basisraamwerk](../uitgangspunten/ontwerpprincipes.md#s-02-fair-als-basisraamwerk) en het [informatiemodel-principe](../uitgangspunten/ontwerpprincipes.md#principes-voor-het-informatiemodel) van hergebruik en betekenisvolle definities.

Naamgeving heeft directe invloed op leesbaarheid, herbruikbaarheid en interoperabiliteit. Consistente conventies voorkomen dat hetzelfde begrip onder verschillende namen voorkomt, en maken modellen makkelijker te begrijpen voor domeinexperts.

## Naamgeving conform MIM

Het informatiemodel volgt de naamgevingsconventies van [MIM](https://www.geonovum.nl/geo-standaarden/mim):

| MIM-element | Conventie | Voorbeeld |
|-------------|-----------|-----------|
| Objecttype | UpperCamelCase, enkelvoud, zelfstandig naamwoord | `NatuurlijkPersoon`, `Zaak` |
| Attribuutsoort | lowerCamelCase, zelfstandig naamwoord | `geboortedatum`, `postcode` |
| Relatiesoort | lowerCamelCase, werkwoord of samenstelling | `heeftAlsAdres`, `isVan` |
| Relatierol | lowerCamelCase, zelfstandig naamwoord | `adres`, `eigenaar` |
| Gegevensgroeptype | UpperCamelCase, enkelvoud | `Contactgegevens` |
| Enumeratie | UpperCamelCase, enkelvoud | `Geslachtsaanduiding` |
| Enumeratiewaarde | Zoals in de bron gedefinieerd | `man`, `vrouw`, `onbekend` |

Aanvullend:

- Definities zijn in het **Nederlands** en gekoppeld aan het begrippenkader
- Namen zijn **betekenisvol** en herkenbaar voor domeinexperts, geen afkortingen of technische codes
- Namen zijn **stabiel** na publicatie; wijzigingen worden opgevangen met `owl:sameAs`

## Naamgeving in URI-paden

In URI-paden gelden aanvullende conventies die aansluiten bij de [URI-strategie](uri-strategie.md):

- URI-paden gebruiken **lowercase** voor padsegmenten die het artefacttype aanduiden (bijv. `/ontologie/`, `/begrippen/`, `/id/`)
- Namen van klassen en properties in de URI volgen de MIM-conventies (CamelCase, lowerCamelCase)
- URI's bevatten **geen** bestandsextensies, versie-indicatoren of technische ID's
- URI-paden zijn **leesbaar** en betekenisvol (bijv. `/ontologie/Zaak` in plaats van `/id/a4f2`)

## Meertaligheid

GBO-Semantiek is primair Nederlandstalig. Waar labels en definities in meerdere talen beschikbaar zijn, wordt dit vastgelegd via `@lang`-tagged literals (bijv. `"Zaak"@nl`, `"Case"@en`). De URI zelf blijft taalonafhankelijk en gebruikt de Nederlandse voorkeursterm als basis.

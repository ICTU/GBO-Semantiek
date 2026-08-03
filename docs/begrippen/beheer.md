## Beheer en governance

### Beheerproces

Het begrippenkader wordt beheerd als onderdeel van GBO-Semantiek. Wijzigingen doorlopen het volgende proces:

1. **Voorstel** — een nieuw begrip of wijziging wordt ingediend via een GitHub Issue of Pull Request
2. **Review** — de werkgroep beoordeelt het voorstel op consistentie, volledigheid en aansluiting
3. **Besluit** — bij akkoord wordt het begrip opgenomen of gewijzigd
4. **Publicatie** — het bijgewerkte begrippenkader wordt gepubliceerd in de volgende versie

### Rollen

| Rol | Verantwoordelijkheid |
|-----|---------------------|
| Beheerder | Coördinatie, kwaliteitsbewaking, publicatie |
| Werkgroepleden | Inhoudelijke bijdragen en review |
| Stakeholders | Voorstellen indienen, deelnemen aan consultaties |

### Wijzigingsbeleid

#### Toevoegen van begrippen

Nieuwe begrippen kunnen worden toegevoegd zonder dat dit een breaking change vormt. Dit is een MINOR versiewijziging.

#### Wijzigen van definities

Wijzigingen aan bestaande definities worden als impactvol beschouwd en vereisen:

- Onderbouwing waarom de huidige definitie niet voldoet
- Consultatieperiode van minimaal 4 weken
- Impactanalyse op het informatiemodel en de ontologie

#### Verwijderen van begrippen

Begrippen worden in principe **niet verwijderd**, maar kunnen worden gemarkeerd als `owl:deprecated`. Dit voorkomt dat bestaande verwijzingen breken.

### Communicatie

Alle wijzigingen aan het begrippenkader worden bijgehouden in de [CHANGELOG](https://github.com/ICTU/gbo-semantiek/blob/main/CHANGELOG.md).

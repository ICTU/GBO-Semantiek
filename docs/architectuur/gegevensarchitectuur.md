# Gegevensarchitectuur

De GBO-Semantiek gegevensarchitectuur is opgebouwd uit drie lagen die samen het volledige spectrum van overheidsgegevensbeschrijving afdekken. De middelste laag vormt het fundament: een set gedeelde kerngegevens waar zowel de bovenliggende sector- en clientmodellen als het onderliggende GBO-Voorzieningenmodel op steunen.

![Gegevensarchitectuur](../assets/diagrams/gegevensarchitectuur.svg)

Het diagram toont de drie lagen en hun onderlinge afhankelijkheden. De pijlen geven aan dat zowel de sector- en clientmodellen als GBO-Voorzieningen hun definities ontlenen aan de GBO-Kern-laag. Dit garandeert dat alle lagen dezelfde begrippen en structuren hanteren.

## GBO-Kernmodel (middenlaag)

Het [GBO-Kernmodel](../informatiemodel/gbo-kern/hoofdmodel.md) bevat de kerngegevens die voor alle aangesloten overheidsdomeinen relevant zijn, ongeacht of een afnemer een gemeente, een uitvoeringsorganisatie of een private ketenpartner is. Het gaat om gegevens uit de landelijke basisregistraties en aanvullende bronnen die breed worden hergebruikt: personen (BRP), bedrijven (HR), panden (BAG), locaties (BGT, BRK), belastingen (BRI en overige), voertuigen (BRV, RDW), DUO (onderwijs en studieschuld) en aanverwante registraties. De inhoudelijke definities zijn voor een belangrijk deel afgeleid uit gemeentelijke referentiemodellen zoals het GGM en het RSGB; de scope van GBO zelf is landelijk.

Deze laag is de gemeenschappelijke taal van GBO. Door kernbegrippen zoals "Natuurlijk persoon", "Verblijfsobject" of "Kadastraal perceel" centraal te definiëren, hoeven individuele domeinen deze begrippen niet opnieuw uit te vinden. Elke verwijzing naar een persoon of een adres in een sectormodel of in GBO-Voorzieningen verwijst naar dezelfde, eenduidig gedefinieerde entiteit in de GBO-Kern.

Uitwerking van het GBO-Kernmodel vind je in de sectie [GBO-Kernmodel binnen Informatiemodel](../informatiemodel/gbo-kern/hoofdmodel.md)

## Sector- en clientmodellen (bovenlaag)

Boven de GBO-Kern ligt de bovenlaag met twee soorten afnemende modellen die beide op de kerngegevens steunen: **sectormodellen** (Nederlandse domeinsilo's) en **clientmodellen** (Europese afnemerkaders zoals EDI en OOTS). Beide soorten definiëren of selecteren hun eigen informatieobjecten, maar verwijzen voor gedeelde begrippen zoals "persoon", "adres" of "voertuig" naar de definities in de GBO-Kern. Deze aanpak voorkomt duplicatie en zorgt ervoor dat zowel sectoroverstijgende als grensoverschrijdende uitwisseling mogelijk blijven.

### Sectormodellen

Sectormodellen zijn domeinspecifieke silo's die de kerngegevens verrijken met begrippen en structuren die eigen zijn aan een bepaald beleidsterrein. Op dit moment zijn twee sectormodellen uitgewerkt.

**Zorgeloos Vastgoed** bundelt gegevens rond woningbezit en vastgoedtransacties. Informatieobjecten in dit domein zijn onder meer WOZ-waarde, Eigendomsrecht, Hypotheek, Taxatierapport en Inkomen. Het sectormodel combineert gegevens uit meerdere bronregistraties (WOZ, BRK, BAG) tot een samenhangend beeld per object.

**Gebouwinformatie** richt zich op de fysieke en functionele kenmerken van gebouwen. Dit sectormodel bevat objecten als Verblijfsobject, Gebruiksdoel, Bouwjaar, Oppervlakte en Pandstatus. De gegevens komen primair uit de BAG en worden aangevuld met domeinspecifieke kenmerken.

De architectuur is zo opgezet dat nieuwe domeinen kunnen worden toegevoegd door een sectormodel te definiëren dat de GBO-Kern-definities hergebruikt en GBO-Voorzieningen importeert.

### Clientmodellen: EDI en OOTS

Clientmodellen beschrijven niet een nieuw domein, maar een **afnemerkanaal**: ze leggen vast welke gegevens een specifieke (Europese) afnemer nodig heeft en in welke vorm, uitgedrukt als een selectie en hergebruik van GBO-Kern-gegevens. Waar een sectormodel de kern *verrijkt*, *projecteert* een clientmodel de kern op het formaat van een uitwisselkanaal. Twee clientmodellen zijn opgenomen, passend bij de twee Europese kaders waarvoor GBO als gegevensbron kan optreden.

**EDI — European Digital Identity (EUDI-wallet).** Het EDI-clientmodel beschrijft de *attestaties* (verifiable credentials/attributen) die een burger of organisatie via de [EUDI-wallet](../bijlagen/woordenlijst.md) kan delen. De attributen volgen de Europese *Minimum List of Attributes*. In de plaat staan de attestaties die GBO het meest direct uit zijn kern kan leveren: Adres, Leeftijd, Geslacht, Burgerlijke staat en Nationaliteit (uit Personen/BRP) en Bedrijfsgegevens van rechtspersonen (uit Bedrijven/HR). Elke attestatie is een uitsnede over de kern; de semantiek loopt via credentialtype-metadata (vct) en het rulebook, niet via een runtime-payload (zie [Toepassing](gegevenstoepassing.md), Lane A).

**OOTS — Once-Only Technical System (SDG).** Het OOTS-clientmodel beschrijft de *bewijsstukken* (evidence) die GBO grensoverschrijdend en eenmalig kan aanleveren onder de [Single Digital Gateway](../bijlagen/woordenlijst.md). In de plaat staan enkele voor de hand liggende evidencemodellen: Bewijs van woonplaats (Personen/BRP), Uittreksel handelsregister (Bedrijven/HR), Kentekenbewijs (Voertuigen/BRV) en WOZ-waardebewijs (WOZ). Het Kentekenbewijs koppelt direct aan het nieuwe deelmodel [Voertuigen](../informatiemodel/gbo-kern/deelmodellen/voertuigen.md). De levering loopt via de SDG-OOTS Adapter als zelf-beschrijvende JSON-LD/RDF (zie [Toepassing](gegevenstoepassing.md), Lane B).

Beide clientmodellen ontlenen hun gegevens aan dezelfde GBO-Kern. Onderstaande tabel toont de herkomst per model-element.

| Clientmodel | Model-element | GBO-Kern-herkomst |
|---|---|---|
| EDI (attestatie) | Adres | Personen (BRP), Adressen en gebouwen (BAG) |
| EDI (attestatie) | Leeftijd | Personen (BRP) — geboortedatum |
| EDI (attestatie) | Geslacht | Personen (BRP) |
| EDI (attestatie) | Burgerlijke staat | Personen (BRP) |
| EDI (attestatie) | Nationaliteit | Personen (BRP) |
| EDI (attestatie) | Bedrijfsgegevens | Bedrijven en instellingen (HR) |
| OOTS (evidence) | Bewijs van woonplaats | Personen (BRP) |
| OOTS (evidence) | Uittreksel handelsregister | Bedrijven en instellingen (HR) |
| OOTS (evidence) | Kentekenbewijs | Voertuigen (BRV) |
| OOTS (evidence) | WOZ-waardebewijs | Waarde onroerende zaken (WOZ) |

## GBO-Voorzieningenmodel (onderlaag)

De onderlaag beschrijft het [GBO-Voorzieningenmodel](../informatiemodel/gbo-voorzieningen.md) voor de Gemeenschappelijke Bronontsluiting. Dit model definieert in één samenhangend geheel hoe gegevens uit de GBO-Kern-laag gestructureerd, ontsloten en uitgewisseld worden: welke gegevens er zijn, wie erbij betrokken is en onder welke voorwaarden gegevens mogen worden gedeeld.

Het model bevat objecttypen voor de structuur van gegevensdeling (zoals Gegevenselement, Bron, Dienst en Scope), voor de betrokken rollen (zoals Burger, Bronhouder en Dienstverlener) en voor het transactieproces (zoals Toestemming, Gegevensverzoek en Grondslag). De volledige uitwerking van deze objecttypen staat in het [GBO-Voorzieningenmodel](../informatiemodel/gbo-voorzieningen.md).

Het GBO-Voorzieningenmodel wordt per domein uitgebreid met specifieke gegevenselementen, bronnen en diensten. Een domeinextensie importeert het generieke model en voegt alleen toe wat domeinspecifiek is. Voorbeelden van domeinen zijn hypotheekadvies, zorgeloos vastgoed en gebouwinformatie.

## Samenhang tussen de lagen

De kracht van deze drielaagse opzet zit in de gedeelde kern. Sectormodellen, clientmodellen en GBO-Voorzieningen worden onafhankelijk van elkaar ontwikkeld en beheerd, maar delen dezelfde fundamentele definities uit de GBO-Kern. GBO-Voorzieningen beschrijft *hoe* gegevens worden gedeeld: met welke scope, op welke grondslag en met wiens toestemming.

Dit levert drie concrete voordelen op. Ten eerste **interoperabiliteit**: gegevens uit verschillende bronregistraties zijn via GBO-Voorzieningen uniform opvraagbaar — ook richting Europese kanalen, omdat de clientmodellen (EDI, OOTS) dezelfde kernbegrippen hergebruiken. Ten tweede **dataminimalisatie**: het scope-mechanisme garandeert dat alleen de strikt noodzakelijke gegevens worden gedeeld. En ten derde **schaalbaarheid**: nieuwe domeinen én nieuwe afnemerkanalen kunnen worden toegevoegd door een sector- of clientmodel te maken dat de GBO-Kern hergebruikt, zonder de bestaande lagen te verstoren.

# GBO-Core v0.5

Deze werkversie maakt het mogelijk om vanaf een adres de eigenaar van een onroerende zaak te vinden, ook als het adres in een heel pand ligt en niet in een appartement. Tot nu toe kwam een afnemer vanaf een adres alleen bij een appartementsrecht uit; een eengezinswoning of een niet gesplitst bedrijfspand was vanaf het adres onvindbaar. Daarnaast introduceert v0.5 een nieuw soort bevraging, de *toets*: een ja/nee-vraag die de bron beantwoordt zonder de onderliggende gegevens te leveren. De eerste twee toetsen beantwoorden de vraag of een persoon eigenaar is van de onroerende zaak op een adres.

## In het kort

- De adreskoppeling `betreft` verhuist van `Appartementsrecht` naar het supertype `OnroerendeZaak`, met kardinaliteit `* → *`. Een adres leidt nu naar het appartementsrecht óf naar het perceel.
- De BRK-query `AppartementsrechtOpBAGID` heet `onroerendeZaakOpBAGID` en levert percelen en appartementsrechten.
- Twee nieuwe toetsen in het BRK-profiel: `isEigenaarOpBAGID` en `isEigenaarOpAdres`, met antwoord `Indicatie` (`Ja`, `Nee` of `Onbekend`).
- Het bronprofiel-meta-schema krijgt `toetsen` (klasse `Brontoets`), een `opvraagpad` bij queries en toetsen, en invoertypen: een parameter mag een objecttype als type hebben, zoals `Binnenlandsadres`.
- Het opvraagpad staat als genummerde stappen in de docstring van het Query-veld, zodat afnemer en bronhouder in de SDL zelf lezen hoe een antwoord tot stand komt.
- `v0.4/` blijft ongewijzigd; v0.5 is de nieuwe werkversie (`VERSION=v0.5`, `PREVIOUS_VERSION=v0.4`).

## Model en semantiek

In v0.4 stond de relatie naar het adresseerbaar object alleen op `Appartementsrecht` (`0..1 → 0..1`). Dat weerspiegelde de BRK niet: het Kadaster koppelt adressen aan de onroerende zaak, aan een perceel even goed als aan een appartementsrecht. HC-BRK zoekt `kadastraalonroerendezaken` op postcode, huisnummer, huisletter, huisnummertoevoeging en `nummeraanduidingIdentificatie`, voor beide soorten. Het gevolg in v0.4 was dat de eigenaar van een woning in een niet gesplitst pand niet vanaf het adres te bepalen was.

In v0.5 staat `betreft` op `OnroerendeZaak` en is de relatie meervoudig in beide richtingen. Een perceel met een pand met meerdere verblijfsobjecten draagt meerdere adresseerbare objecten, en een verblijfsobject dat over twee percelen ligt, hoort bij beide. De relatie blijft een basisgegeven met materiële en formele historie. `Perceel` en `Appartementsrecht` erven haar; de `datumWijziging` van `OnroerendeZaak` en `Appartementsrecht` staat op 2026-09-28.

De geometrische koppeling `Pand staat op Perceel(en)` blijft daarnaast bestaan, maar is voor eigendom ongeschikt: het is een projectie, m:n, en een pand kan over percelen van verschillende eigenaren liggen. De administratieve adreskoppeling uit de BRK is de route voor eigendomsvragen.

## Bronprofielen en bevraging

### Adresingang van de BRK

`onroerendeZaakOpBAGID(identificatie: BAGID!): [OnroerendeZaak!]` vervangt `AppartementsrechtOpBAGID`. Het resultaat is de interface `OnroerendeZaak`; de afnemer onderscheidt perceel en appartementsrecht met een fragment. De identificatie is die van het adresseerbaar object (verblijfsobject, standplaats of ligplaats), zoals in de oude query.

### Toetsen

Een toets is een ja/nee-vraag. Het antwoordtype is altijd `Indicatie!`, en `Onbekend` betekent iets anders dan `Nee`: de vraag is met de gegevens van de bron niet te beantwoorden. De bron levert bij een toets geen tenaamstellingen, aandelen of rechten; alleen de uitkomst.

```graphql
isEigenaarOpBAGID(bsn: BSN!, identificatie: BAGID!): Indicatie!
isEigenaarOpAdres(bsn: BSN!, adres: BinnenlandsadresInvoer!): Indicatie!
```

Eigenaar is wie een lopende tenaamstelling heeft op een lopend zakelijk recht van de aard `Eigendom` of `Opstal`, op een onroerende zaak die aan het adres is gekoppeld. Opstal telt mee omdat de opstaller eigenaar is van het gebouw op andermans grond. De grootte van het aandeel doet er niet toe: een mede-eigenaar is eigenaar. Erfpacht, vruchtgebruik en de overige beperkte rechten tellen niet mee.

De uitkomst is `Ja` als zo'n tenaamstelling van de persoon bestaat, `Nee` als het adres wel aan onroerende zaken is gekoppeld maar de persoon daarop geen eigendom of opstal heeft, en `Onbekend` als het adres niet bestaat of aan geen enkele onroerende zaak is gekoppeld. Beide toetsen gaan uit van de laatst bekende situatie op het moment van bevragen.

Bij `isEigenaarOpAdres` legt het adres zich vast met postcode en huisnummer. Een weggelaten huisletter of huisnummertoevoeging betekent dat het adres er geen heeft; het is een exacte match, geen jokerteken.

### Opvraagpad

Omdat de generator de betekenis van een toets niet kan afleiden, zijn het opvraagpad en de uitkomstregel verplichte onderdelen van de declaratie. Beide komen letterlijk in de docstring, met de geraadpleegde objecttypen erbij. Voor `isEigenaarOpBAGID` luidt het opvraagpad:

1. Zoek de onroerende zaken waarvan `betreft` het adresseerbaar object met deze identificatie bevat.
2. Neem van die zaken de zakelijke rechten (`heeftZakelijkRecht`) met `aardZakelijkRecht` `Eigendom` of `Opstal` en zonder `datumEinde`.
3. Neem van die rechten de tenaamstellingen (`heeftTenaamstelling`) zonder `datumEinde`.
4. Kijk of een van die tenaamstellingen via `tenNameVan` naar de ingeschreven persoon met dit bsn wijst.

`isEigenaarOpAdres` gaat daaraan vooraf met de nummeraanduiding die het adres vormt (`Binnenlandsadres.wordtGevormdDoor`) en het adresseerbaar object waartoe die behoort. Ook een gewone benoemde query kan een opvraagpad krijgen; `onroerendeZaakOpBAGID` heeft er een.

### Invoertypen

GraphQL staat geen objecttype als argument toe. Een parameter met een objecttype als type wordt daarom een input-type met de naam van het objecttype plus `Invoer`. Het profiel kiest in `velden` welke attributen het invoertype draagt en welke verplicht zijn:

```graphql
input BinnenlandsadresInvoer {
  postcode: Postcode!
  huisnummer: Int!
  huisletter: String
  huisnummertoevoeging: String
}
```

De verplichting staat in het profiel en niet in het model, omdat een zoekvraag andere eisen heeft dan een registratie. In het model zijn bij `Binnenlandsadres` straatnaam en woonplaatsnaam verplicht en is de postcode optioneel; voor een toets ligt een adres vast met postcode en huisnummer.

### Meta-schema

Het bronprofiel-meta-schema is op drie punten uitgebreid:

- `toetsen` op `Bronprofiel`, met de klasse `Brontoets`: `naamQuery`, `vanaf`, `parameters`, `raadpleegt`, `opvraagpad`, `uitkomst`, `selectie` en `toelichting`. `raadpleegt` noemt de objecttypen waarop de toets draait; ze moeten in `objecttypen` staan, ook al levert de toets ze niet.
- `opvraagpad` op `Bronquery`, optioneel.
- `velden` op `Queryparameter`, met de klasse `Invoerveld`, voor parameters met een objecttype als type.

Een profiel moet nu minstens één ingang, query of toets hebben. Querynamen en toetsnamen delen één naamruimte, omdat ze allebei een veld van dezelfde Query-root worden.

## Build en generatoren

`tools/genereer_bronschema.py` valideert en codeert toetsen, opvraagpaden en invoertypen. Het weigert een profiel met een dubbele veldnaam, een toets die een objecttype raadpleegt dat niet in het profiel staat, een invoerveld dat geen attribuut is of naar een ander objecttype wijst, en vrije tekst met een van de veldscheiders `;`, `|` of `~`. Die laatste controle gold al voor de toelichting van een query en geldt nu ook voor het opvraagpad en de uitkomstregel.

`tools/genereer_graphql.py` schrijft toetsen als Query-velden met antwoordtype `Indicatie!` en invoertypen als `input`. De Query-root wordt nu opgebouwd vóór de enumeraties, zodat een enumeratie die alleen als argument- of antwoordtype voorkomt ook in de SDL komt.

Voor de twaalf andere bron-profielen is de gegenereerde SDL byte-identiek aan v0.4.

## Documentatie

Het deelmodel Onroerende zaken en het hoofdmodel zijn meegegaan: de relatie `betreft` staat in de diagrammen en de relatietabel van `OnroerendeZaak`, de stelselkoppeling naar Adressen en gebouwen noemt de administratieve adreskoppeling naast de geometrische, en de toelichting bij onroerend goed in het hoofdmodel is herschreven. De README van de bron-profielen beschrijft het opvraagpad, de toetsen en de invoertypen.

Versieverwijzingen op de site en de versielabels in de diagrammen staan op v0.5.

## Breaking changes en migratie

Voor afnemers van de GraphQL-SDL van de BRK:

- **`AppartementsrechtOpBAGID` heet `onroerendeZaakOpBAGID`** en levert `[OnroerendeZaak!]` in plaats van `[Appartementsrecht!]`. Wie alleen appartementsrechten verwacht, selecteert met `... on Appartementsrecht`.
- **`Appartementsrecht.betreft` is meervoudig geworden**: `[BAGID!]` in plaats van `BAGID`, en het veld staat nu ook op `Perceel` en op de interface `OnroerendeZaak`.

Voor wie bron-profielen schrijft:

- **Een parameter met een objecttype als type vereist `velden`.** Zonder die selectie faalt de snoei-tool.

## Cijfers

- Kernmodel plus deelmodellen: aantal klassen en enumeraties ongewijzigd ten opzichte van v0.4. Eén relatie verhuisd (`betreft`).
- SKOS-begrippen in `GBO-Begrippenkader.ttl`: 119 (ongewijzigd).
- Bron-profielen: 13. GraphQL-SDL-bestanden: 13, waarvan alleen `brk.graphql` gewijzigd.
- Benoemde queries over alle profielen: 46 (ongewijzigd; één hernoemd). Toetsen: 2 (nieuw).
- Invoertypen: 1 (`BinnenlandsadresInvoer`, nieuw).

## Vooruitblik

Eén punt ligt bij het Kadaster: koppelt de BRK bij een gesplitst gebouw het adres alleen aan de appartementsrechten, of ook aan het grondperceel? Het model gaat ervan uit dat bij een gesplitst gebouw het appartementsrecht de rechthebbende bepaalt. Dit staat als openstaand punt bij de relatie `betreft` en hoort op de agenda van het overleg met het Kadaster in oktober 2026.

Daarnaast verdient het twee-tijdlijnenvraagstuk een besluit. `Tenaamstelling` en `ZakelijkRecht` hebben elk een eigen `datumIngang` en `datumEinde` en via de `Voorkomen`-mixin nog `beginGeldigheid` en `eindGeldigheid`. De toetsen gebruiken `datumEinde`, omdat alleen die in de SDL staat; het model zegt nog niet welke van de twee de geldigheid bepaalt.

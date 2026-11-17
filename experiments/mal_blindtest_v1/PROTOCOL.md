# MAL Blindtest v1 – förregistrerat protokoll

**Status:** Testpaket fryst 17 november 2026. **Prognoser ännu inte producerade.** Testet mäter prognosförmåga, inte hur övertygande förklaringar kan skrivas efter att betygen har avslöjats.

## Material och avgränsning

- 529 betygsatta completed-verk från en fryst snapshot av `anime.json`; 424 träningsfall och **105 blindfall**.
- 97 dropped-verk är inte poängsatta observationer. De 19 uttryckliga dropped-svaren ingår i träningsfilen med användarutsagor, inte som negativa betyg.
- Varje träningstitel har ett känt användarbetyg och MAL-metadata plus objektiv faktabrief. Varje blindfall har samma metadata och faktabrief men **INGA användarbetyg, personliga datum eller modellerade residualer**.
- 62 besvarade frågor och sju sparade kvalitativa uttalanden finns i `qualitative_evidence.json`. Alla är hänförliga till träningsmaterial eller ej poängsatta dropped-verk.
- `manifest.json` anger exakt vilka Git-blob-SHA som låg till grund för datamängden. Ändra aldrig urval, träning eller testfall efter att experimentet startat.

## Urval

Testfall väljs deterministiskt: FNV-1a 32-bit på `mal-blindtest-v1-2026-11-17|<family_key>`, sortering stigande, sedan kompletta grupper till minst 105 testposter. Gruppering sker efter definierade franchiseord eller normaliserade tre första titelord, plus sammanslagning av titlar där den ena är ett fullständigt prefix till den andra (exempelvis en serie och dess namngivna uppföljare). Grupper skapas från alla 778 poster med en union-find-beräkning och hålls intakta. En förhandskontroll reparerade nio sådana korsande uppföljare **innan några prognoser hade producerats**. Från testet utesluts grupper med redan besvarade frågor, användarens tidigare explicita verksspecifika omdömen, kända tidigare samtalsexempel eller ofullständiga faktabriefar. Urvalet har **inte** efterjusterats med betyg för att se fördelaktigt ut.

**Begränsning:** Titelnormalisering och prefixkontroll är inte ett fullständigt franchise-register. En uppföljare med väsentligt annorlunda titel kan hamna på andra sidan. Detta är en känd risk, inte ett påstående om perfekt franchisespärr. Alla 105 testfall ska besvaras; man får inte plocka bort svåra fall i efterhand.

**Ytterligare metodrisk:** Originalbriefarna skapades i ett system där MAL-betygen fanns tillgängliga, trots instruktion om neutral faktaskrivning. Därför kan viss omedveten betygsbetingad vinkling i briefarna inte uteslutas. Betrakta resultaten som ett explorativt test, inte som ett helt oberoende externt prov.

## Förhindrad facitläcka

1. Kör själva prognosarbetet i en **separat, isolerad session** med enbart `training.json`, `blind_cases.json`, `qualitative_evidence.json`, protokollet och gissningsformatet. Inte i samma chatt som kände till individuella betyg.
2. Modellens körning får **inte** tillgång till originalrepo, GitHub, webbsökning, MyAnimeList-användarprofil, historiska chattsammanfattningar eller sparade personliga smakminnen. Även ett oavsiktligt återhämtat användarbetyg gör berört testfall otillåtet för en strikt blind jämförelse.
3. Ge inte modellen `anime.json`, `anime_backup.json`, `anime_preference_learning.json`, `anime_profiles.json` eller tidigare resultat. De innehåller facit eller statistik där blindfallens facit redan ingår.
4. `mal_mean_score` är en tillåten **allmän konsensusuppgift** och tillhör testets förklarande variabler, inte användarens dolda betyg.
5. Lås exakt en prediktionsfil innan facit hämtas. Inga omtag, redigeringar eller nya prompts efter poängsättning. Testfall, träningsunderlag och facit får inte ändras under körningen.
6. Användarsvarens valda alternativ är uttrycklig evidens för de angivna titlarna, inte automatiska generella preferenssanningar.

## Förregistrerade jämförelser

- **B0:** konstant median av de 424 träningsbetygen.
- **B1 (primär jämförelse):** `clamp(MAL-medelbetyg + median(train_user_score - train_MAL_mean), 1, 10)`. Global kalibrering beräknas **enbart från träningen**.
- **B2 (genrebänkmärke):** B1 plus genomsnittet av krympta träningsresidualer för respektive exakt MAL-tagg. För varje tagg `correction = sum(train_residuals_for_tag)/(n_tag + 20)`; genomsnitt av tillgängliga taggkorrektioner, begränsat till intervallet [-0,75; +0,75]. Saknade taggar ger noll. Ingen träning på blindfall.
- **M1:** AI-modell med fakta och användarens kvalitativa träningsuppgifter enligt en i förväg fixerad instruktion; en numerisk poäng (1–10, decimal tillåten), säkerhetsklass (low/medium/high) och en konkret motivering per blindfall.

**Primärt utfall:** Medelabsolutfel (MAE) för M1 jämfört med B1, på samtliga 105 blindfall, utan avrundning av prognoser. Vinst = B1_MAE − M1_MAE. 95-procentigt parat bootstrapintervall (2 000 omsamplingar med fast seed). Förbättring ska inte beskrivas som säker om intervallet inkluderar noll.

**Sekundärt:** MAE jämfört med B0 och B2, RMSE, andel inom ±1 betygssteg, precision/recall/F1 för 8–10 respektive 1–6, MAE för efterhand identifierade starka konsensusavvikelser, MAE per deklarerad säkerhetsklass. Små undergrupper får bara indikativa slutsatser. Utfallet på 7:or ska inte få dölja systematiska fel på 9–10 eller 4–5.

**Separat kvalitativ utvärdering:** Motiveringar granskas utan att skriva om prognosen: (a) pekar de ut faktiska egenskaper i verket, (b) skiljer de mellan användarens belagda preferens och modellens hypotes, (c) förklarar de rimligt något som enbart genre/MAL-konsensus inte förklarar? En plausibel efterhandsförklaring räknas **inte** som en träff.

## Prediktionsfil

Skapa en separat lokal `predictions.json` med formen:

```json
{
  "experiment_id": "mal_blindtest_v1",
  "model_id": "ange vald modell och eventuell promptversion",
  "predictions": [
    {
      "mal_id": 12345,
      "predicted_score": 7.2,
      "confidence": "medium",
      "reason": "Konkret, före facit, baserad på tillåtet underlag"
    }
  ]
}
```

Listan ska innehålla **exakt ett objekt för vart och ett av de 105 test-ID:na**. Inga extra ID och inga saknade fall. Numerisk gissning krävs även vid låg säkerhet. Spara förutsägelsen oförändrad innan poängsättningen.

## Poängsättning (separat session)

Hämta `anime.json` från den **exakta Git-blob som anges i manifestet** (inte nyaste main). I en klon med tillgång till Git-objektet kan man exempelvis använda `git cat-file blob <sha-från-manifest> > frozen_anime.json`. Verifiera därefter SHA och kör:

```bash
python score.py predictions.json frozen_anime.json
```

Poängsättningsskriptet återläser då facit och redovisar utfallen. Det får inte användas eller visas i prediktionssessionen förrän samtliga gissningar är låsta. Fel eller läckage dokumenteras utan att tysta misslyckanden räknas bort.

## Tolkning

Om modellen inte slår B1/B2 visar det att denna version ännu inte ger bevisad prognosnytta. Om den slår dem är nästa steg en **ny fryst extern testomgång** med nytillkomna verk eller en oberoende tidsperiod, inte att trimma modellen mot samma 105 facit och kalla nästa försök blindtest.

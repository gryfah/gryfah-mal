# MAL – överlämning till ChatGPT Work
*Upprättad 2026-11-17. Utgångsläge: `main` i `gryfah/gryfah-mal`. Detta är en beständig projektbrief, inte en bekräftelse på att en Work-körning har startat.*

## Uppdrag och övergripande mål

Projektet har två skilda nivåer:

1. **Datainsamlingen, nu till största delen avslutad:** synkroniserad MyAnimeList-historik, källförankrade verkbriefar samt explicit användarevidens om varför enskilda titlar fungerade eller inte fungerade.
2. **Smakmodellering, huvudarbetet från och med nu:** pröva om fakta om verkens dramaturgi, relationer, ton, premiss och upplösning tillsammans med uttalade användarmotiv förbättrar personliga prognoser och rekommendationer jämfört med enkla MAL-/genremodeller.

Bygg inte en modell som blott återger genre/favoritfranchise eller som konstruerar trovärdiga motiveringar efter att ha sett betygen. Skilj **intresse för en premiss**, **kvalitet på genomförandet**, **komponenter som faktiskt drev betyget**, **tolererade brister**, **avbrott utan betyg** och **resonemangens osäkerhet**. Användaren vill ha genreöverskridande rekommendationer och användbara negativa prognoser, inte bara självbekräftelse.

Arbetsspråk med användaren: svenska, naturligt och sakligt; rutinrapporter och omotiverade följdfrågor är inte önskade. Databasfiler och modellskript kan använda engelska fältnamn. Kalla inte heuristiska efterhandsförklaringar för verifierade användaråsikter.

## Verifierat bestånd 2026-11-17

- `anime.json`: **778** poster – **529 completed**, **97 dropped**, **152 plan_to_watch**. Filen är dynamisk; behandla den som enda källa för aktuell status och användarbetyg. Senast verifierad git-blob i överlämningskontrollen: `c8a39c53c2e39d6107cdcdbf8f45c01c59490520`. Synk körs separat och skriver även `anime_backup.json` och `results.json`.
- `anime_profiles.json`: **778** verkbriefar; **770 complete**, **8 partial** (fem PTW, tre completed). De åtta partial är avsiktligt märkta där verifiering inte räcker eller anime ännu inte kan bedömas. Senast verifierad git-blob: `65ee46c5d708cb696fa1378977d4c15f02258f55`. Faktabriefen är källbaserat underlag, **inte** ett smakfacit.
- `anime_preference_learning.json`: **529/529** completed-observationer och **529/529** retrospektiva reassessments; **62/62** frågor besvarade i omgångarna 200 (16), 220 (3), 400 (24), final_inventory (19); **7** uttryckliga kvalitativa omdömen granskade; **endast en** formellt etablerad hypotes, `narrative_pacing_and_progression`, med `confidence=tentative`. Senast verifierad git-blob: `d0b985ddf369313b6cc1fe110caf89a32db957f5`. De många observations- och reassessment-posterna innebär **inte** att ett flerdimensionellt preferenssystem redan är tränat.
- `results.json` innehåller senaste MAL-statushändelser med `event_id`, `mal_id`, `signals` och `detected_at`. Detta är integration för Next-up och Post-watch, inte facit för smak.

**Viktigt:** dropped har `score=0` som avsaknad av betyg, inte 0/10. Tillämpa inte vanlig betygsregression på dropped. De besvarade dropped-frågorna innehåller användarens explicit valda skäl; ett avbrott kan bero på avbrott i livet, ointresse, problem i verket eller annat. Generalisera inte utan stöd.

## Användarens viktigaste explicita smakevidens

Fullständiga ordagranna formuleringar och separata försiktiga tolkningar finns under `insights.explicit_user_qualitative_evidence` i `anime_preference_learning.json`. Följ respektive `evidence_id` och `mal_ids`, inte lösa minnesassociationer:

- `premise_execution_20261115`: väl genomförd, ägd premiss kan motivera högt betyg oavsett genre. Användaren uttrycker respekt för tittarens tid, undvikande av mjölkning och att verket når en meningsfull slutsats. **Inte** samma sak som en generell preferens för korta verk.
- `franxx_relationships_20261115`: *Darling in the FranXX* 10/10 på grund av starka relationer; mecha-delarna bedöms som undermåliga. Genrekomponent i en favorit är **inte** belagt positivt betygsmotiv.
- `happy_sugar_life_motivation_20261115`: *Happy Sugar Life* 8/10 uppskattas för framgångsrik gestaltning av två människors subjektivt upplevda lycka/gemenskap i en nattsvart värld, **inte** för yandere-arketypen. Förståelse för deras perspektiv är inte moraliskt godkännande.
- `koi_kaze_execution_20261115`: *Koi Kaze* 8/10 – realism, förankring, konsekvent ton, premissens obekväma implikationer och upplösning. Inte belägg för en allmän dragning till tabun.
- `yosuga_koi_kaze_comparison_20261115`: *Yosuga no Sora* 6/10 jämfördes med `Koi Kaze` och bedömdes som sämre utförd; **vilken specifik brist** som avgjorde har användaren inte bekräftat.
- `twgok_arc_format_20261115`: *The World God Only Knows* säsongerna 7/7/8 trots blockberättande; annan IP med liknande format fungerade inte. **Anta inte** att den andra serien var *Amagami SS* enbart för att den föreslogs som gissning i ett samtal. *Seiren* fick också 7/10, så sammanblanda inte format med kvalitet.
- `anti_genre_determinism_20261115`: användaren avvisar extrapoleringen ”högt på FranXX/Gundam/Macross → vilken Gundam-serie som helst passar”.
  
Följ fråga–svar-historiken också. Tidigare explicit svar inkluderar exempelvis kritik av *Witch Hunter Robin* för mycket svag progression, *Clannad: After Story* för upplevd retcon som neutraliserar sorgens konsekvenser och uppskattning av dynamiken mellan karaktärer i flera verk. Betrakta alla sådana formuleringar som **verksspecifika tills mer generell evidens finns**. Pröva hypoteser mot både höga och låga betyg, inklusive lika genrer med olika utfall.

## Blindtest v1 – genomfört, men begränsat

Alla tillhörande filer finns under [`experiments/mal_blindtest_v1/`](experiments/mal_blindtest_v1/):

- `manifest.json`: frysta Git-blob-SHA och urval; **529** betygsatta completed = **424 träning** och **105 test**.
- `training.json`, `blind_cases.json`, `qualitative_evidence.json`, `PREDICTION_PROMPT.md`, `PROTOCOL.md`: data, facitisolering och förregistrerat test.
- `predictions.json`: **105 prognoser låsta** i commit `9d02f9448c36837f641d3a1eceb4665adf637542` före testbetygen lästes i utvärderingen.
- `model_diagnostics.json`: femfaldig gruppbaserad korsvalidering på träning.
- `results_v1.json` och `REPORT.md`: resultat. `score.py` finns som återkörningsbart scorer-skript; resultatsammanställningen producerades med separat poängsättningskod. Work ska verifiera att skriptet reproducerar utfall och dokumentera eventuella avvikelser. **Ändra inte de låsta prognoserna.**

| Metod | MAE på 105 |
| --- | ---: |
| B0 konstant median | 0,7238 |
| B1 MAL-genomsnitt kalibrerat med träningens medianoffset | 0,7015 |
| B2 B1 + krympt genrejustering | 0,6846 |
| Lexikal TF-IDF/kNN med fakta-briefar | **0,6817** |

Förbättringen mot B2 är endast **0,0029**, parad bootstrap 95 % KI **[−0,0306; 0,0377]**; **ingen säkerställd förbättring**. B2 hade något bättre RMSE (0,8444 mot 0,8539). Betydande missar var *Blue Reflection Ray* (8 → 5,572), *Sousou no Frieren* (7 → 8,787), *Boku no Tsuma wa Kanjou ga Nai* (8 → 6,4) och *Shinigami Bocchan to Kuro Maid 3rd Season* (6 → 7,988).

**Metodologisk varning:** Den här M1-implementationen var en **lexikal rekommendationsmodell**, inte ett resonemang med de 62 frågesvaren och de 7 djupare omdömena; dessa fanns som tillgängligt material men användes **inte direkt i estimatorn**. Detta säger därför ännu inte om den semantiska smakmodellen fungerar. Dessutom kan originalbriefarna ha färgats av betyg synliga vid ursprunglig tillkomst, och titelbaserad franchisegruppering är inte en perfekt franchisegraf.

**Återanvänd INTE de avslöjade 105 testbetygen som nytt strikt blindtest.** De är redan utvärderade och ingår i nuvarande historik och tidigare chatt. Vill man testa en ny modell utan läckage krävs *nytt, osett* prospektivt material efter fryspunkten, med en verkligt isolerad prognoskontext. Retrospektiva out-of-fold-studier får göras, men ska ärligt märkas som sådana. Undvik att kalla återtest på samma 105 för en ny blind prestation.

## Föreslagen arbetsplan för Work

### 0. Läs och etablera körbar miljö
- Läs detta dokument, `experiments/mal_blindtest_v1/PROTOCOL.md`, `REPORT.md` och respektive manifest.
- Validera hela 778-postersbeståndet, enum för status, 8 partial, 62 explicita svar, 7 evidensnoteringar och aktuell SHA; JSON-filer kan ha ändrats av pågående synk och automationer sedan överlämningen.
- Kör `score.py` på de låsta prognoserna och exakt frysta `anime.json` (Git-blob-SHA i manifest). Notera om script och rapport skiljer sig.
- Gör ändringar helst i separat feature branch/PR med test och spårbarhet. Samordna GitHub-skrivningar; skriv inte `anime.json` eller till synkproducerade filer.

### 1. Spåra evidens innan preferensmodeller
- Normalisera en läsande modell över fråga–svar, raw/free-text och explicita uttalanden. Varje hypotes behöver stöd, motexempel, osäkerhet och spårbara käll-ID. Uttryckliga verksskäl har högre bevisvärde än härledd genreassociation.
- Skilj **verksegenskaper** (faktakällor), **användarreaktion** (uttryckligt belagd), **observerad rating** och **modellhypotes**. Modellens prediktion får inte omvandlas till verifierad mänsklig åsikt.
- Undvik cirkelresonemang såsom ”användaren gillar välskrivna serier, alltså var högt betyg en följd av välskriven serie”. Operationalisera premisskonsekvens, förväntansuppfyllelse, tonal stabilitet, relationsutveckling och avslut där faktaunderlaget räcker. Mät osäkerheten i att inferera subjektiv kvalitet från en spoilerfri brief.

### 2. Bygg förklarande och testbar modell
- Behåll B0/B1/B2 som baslinjer. Utred explicita preferensdimensioner snarare än att först öka antalet språkmodellstexter.
- Hantera franchise-/uppföljarkorrektioner utan kunskapsläckage. Skilj **prognos för ett helt nytt verk** från **prognos för säsong 2 när säsong 1 har betyg**: det är olika uppgifter.
- Gör jämförelser där identiska genrer ger motsatta utfall, och jämför genremärkta serier där den uppskattade komponenten INTE är genren. Kontinuitet, dramaturgisk progression och hur verk uppfyller sin premiss kan väga mer.
- Skilj sannolikhet att avsluta/avbryta från förväntat betyg GIVET completed (selection bias). Dropped saknar numerisk rating.
- Använd kalibrering och sannolikhetsfördelning över 1–10, inte bara ett punktbetyg. Utvärdera särfallen 9–10, 4–6 och oväntade konsensusavvikelser.

### 3. Seriös evaluering
- Pröva enklare observerbara steg först: train-only gruppvis CV, ablationer (genre; premissbriefar; explicit smak; franchise; MAL), väl definierade mått och öppen felanalys.
- Strikt nya prospektiva blindtestfall ska utses *innan* de poängsätts och förutsägas i en isolerad process utan läsrätt till facit, tidigare personliga konversationer/minne eller aktuella MAL-statusar. För nya PTW-verk kan man låsa förutsägelser före tittning; utvärdera först när avslut och betyg faktiskt finns. Detta kan ta tid och ska inte döljas som om testet redan vore slutfört.
- Om vägen via ett språkmodellstest inte kan garantera verklig isolering, kalla det ett **icke-blint explorativt test**. Värdera faktisk träffsäkerhet före verbal övertygelse.

### 4. Bygg en användbar rekommendationsprodukt
- Rekommendationerna ska i första hand förankras i aktuella PTW-verk, verifierade fakta och användarens motiv, men kunna upptäcka oväntade verk utanför listan med källkontroll.
- Visa 2–3 konkreta *orsaksfaktorer* samt en risk/motfaktor när den är verkligt relevant. Låg säkerhet ska framgå.
- Bevara befintliga Next-up och Post-watch som separata användarflöden om de fortfarande önskas. Ändra inte automationsprompter som del av modellträningen utan egen granskad ändring.

## Automationer – granskade 2026-11-17

Samtliga fem befintliga ChatGPT-automationer var **aktiverade**, ingen pausad. Ingen av dem har ändrats som följd av denna överlämning.

| Uppgift | ID | Läge/tid | Rekommendation |
| --- | --- | --- | --- |
| MAL – bygg animeprofiler | `6aedb8d829008191a8ed1c6e7af69375` | `exact_schedule`, varje timme :15 | **Pausa eller konvertera till lågfrekevent underhåll när Work äger modellen.** Alla 778 täcks; 529 observationer, 62 svar och 7 evidensposter är färdiga. Den 39 362 tecken långa timinstruktionen är en tidigare produktionspipeline; risk för dubbel analys och skrivkonflikter mot Work. Behåll separat, lättviktig kontroll av NYA saknade PTW/completed/dropped och verifierbar förbättring av partial när fakta tillkommer. Utan ersättare skulle helt avstängd profilbyggare innebära att nya PTW saknar automatisk research. |
| MAL – synka GitHub | `6ae9709753a88191955f53590c364bc6` | `exact_schedule`, varje timme :05 | **Behåll.** Den är uppströmskälla för event, synk och aktuella betyg. Timkadens kan sänkas först om användaren accepterar längre eftersläpning i Next-up/Post-watch. |
| MAL – Post-watch och eftersnack | `6ae9c46fa140819198a4c3eaa3809e2e` | `condition_watch`, nominellt :20 | **Behåll, men justera.** Kontrollera faktisk `scheduled_for`/start-tid och byt vid behov till exakt schema; nuvarande strikt en-timmesfönster utan beständig eventkvittens riskerar missad leverans vid försenad eller utebliven körning. Bevara lågbruspolicy och självständig eftersnackstext. |
| MAL – Next-up och tittförslag | `6ae9c3895b588191bab3b267c29a447e` | `condition_watch`, nominellt :25 | **Behåll, men justera** tidsfönster/idempotens i samspel med Post-watch. Nuvarande löfte är exakt tre korta PTW-förslag vid faktisk relevant statusövergång. Uppdaterad smakmodell kan senare integreras genom en explicit godkänd revision; nuvarande prompt använder INTE `anime_preference_learning.json`. |
| Hitta jobb som matchar min kompetens | `6ae84d61ee14819192d8060e1a3b5bf4` | `condition_watch`, dagligen 08 | **Behåll oförändrad** som separat, pågående användarprojekt. Inte del av MAL-överlämningen. |

Före eventuella automationändringar: ta backup av prompt och schema, verifiera konsumtionskedjan från GitHub Actions till `results.json`, definiera regler för idempotent eventhantering och konsekvenser av att dra ned synkfrekvensen. Rekommenderad ordning vid ändringar är **(1)** byt ägare för smakmodell/säkra skrivning, **(2)** pausa/renodla produktionsbyggaren, **(3)** säkra eventleveranserna, **(4)** optimera frekvensen vid behov. Schemaläggningsläge `condition_watch` har historiskt gett körningar som avviker från nominell minut. Att bara ändra till `exact_schedule` löser inte utebliven körning eller dubbelleverans. En beständig event-ID-cursor/processed-uppsättning kräver uttryckligt beslutad placering (gärna separat fil, **inte** ändring av källfilerna).

## Säkerhets- och ändringsgränser

- Behandla `main` som levande; GitHub Actions och profilautomationer kan fortfarande skriva till sina filer. Använd aktuell blob-SHA och sekventiella commits, gör aldrig blind overwrite.
- Behåll alla råa frågesvar, `questions.rounds.final_inventory`, redan besvarade dropped-val och äldre observationsfält. Be inte om samma slutfrågor igen och skapa ingen femte omgång utan uttrycklig beställning.
- Ändra inte `anime.json`, `anime_backup.json`, `results.json`, `sync_mal.py`, workflows, befintliga automationer eller användarens jobbuppgift på grundval av denna överlämning utan separat beslut.
- Arbeta reproducerbart: testfiler, versionsnummer, mätetal, felanalys och osäkerheter. **Det finns ännu inget belägg för att den djupare semantiska smakmodellen slår B2.**
- Detta dokument bygger på verifierad data vid 2026-11-17; om nuläget ändras ska Work uppdatera avsnittet med datum och faktiska skillnader, inte förlita sig på statiska räknetal.

## Första körningen i Work – konkret uppdrag

> Ta över projektet `gryfah/gryfah-mal`. Börja med `WORK_HANDOFF_MAL.md` och `experiments/mal_blindtest_v1/REPORT.md`, verifiera huvuddatabasernas aktuella status och auditera blindtestets reproducerbarhet. Förbered därefter en spårbar, mångdimensionell smakmodell som direkt använder de 62 användarsvaren och 7 kvalitativa evidensposterna, med motexempel, separata fakta/slutsatser, kvantitativa baslinjer och läckageskydd. Utvärdera med träningsbaserad CV men hävda inte nytt strikt blindtest på redan avslöjade 105 testfall. Fortsätt i separat gren/PR och låt synk, Next-up, Post-watch och daglig jobbsökning vara oförändrade tills migrationsplan för profilbyggare och säker eventleverans är godkänd. Leverera konkreta kod-/dataändringar, validering och rapport med länkar.

# Smakmotor v2 — första retrospektiva försök

Körd mot MAL-snapshoten `anime.json` från 2026-11-18 (Git blob `ec68ba8db62df4d1275e020988f8cdb0f6bf06d3`) och verkbriefarna i `anime_profiles.json` (Git blob `65ee46c5d708cb696fa1378977d4c15f02258f55`). Försöket ändrar inte animehistoriken, synken eller bevakningarna.

## Resultat

| Uppgift | Enkel baslinje | Textmodell | Utfall |
|---|---:|---:|---|
| Poäng, MAE på 526 betygssatta titlar | Egen median: **0,7605** | Brieftext: **0,7484** | Förbättring **0,0121** poäng |
| Drop/completed, ROC-AUC på 623 titlar | Slumpnivå: **0,50** | **0,5088** | I praktiken ingen urskiljning |
| Drop/completed, Brier | Basfrekvens: **0,1318** | **0,1315** | Försumbar skillnad |

Poängskillnaden är liten. Ett bootstrapintervall grupperat per serie för MAE-förbättring är **−0,014 till +0,057**, alltså förenligt med att textmodellen inte hjälper alls. Den tillför ännu inte ett trovärdigt prognoslyft. Drop-modellen klarar inte att urskilja vilka startade titlar som avslutades respektive droppades. Det bekräftar att drop måste behandlas med egna skäl och visad mängd, inte som ett lågt betyg.

Textmodellens säsongsresultat varierar: vinter förbättras mot medianbaslinjen (0,748 mot 0,798 MAE), vår försämras (0,708 mot 0,673), sommar förbättras svagt (0,763 mot 0,795) och höst förbättras svagt (0,781 mot 0,795). Mönstret är för litet och ojämnt för att dra slutsatser om säsongssmak.

## Vad misstagen visar

Modellen dras mot ett generiskt sjubetyg och missar specifika skäl. Den undervärderar exempelvis `5-toubun no Hanayome Movie` med 3,19 poäng, `Boku dake ga Inai Machi` med 3,01 och `86` med 2,88. Den överskattar bland annat `Kyokou Suiri` med 2,83, `Myself; Yourself` med 2,62 och `Hotaru no Haka` med 2,15.

Detta är diagnostiska fel, inte nya preferenspåståenden. I samtalet har flera av dem fått konkreta förklaringar: tidigare investering i relationer och deras upplösning kan ge stark utdelning; en premiss som inte granskas eller en relation som loopar kan sänka ett i övrigt lovande verk; och välgjort lidande kan ändå vara något Fredrik inte vill ha i sitt liv. Brieftexten beskriver ofta ämnena men saknar sådana bedömningsskillnader.

## Avgränsning och metod

- 778 MAL-titlar har profilposter; 770 verkbriefar har status `complete`. Åtta ofärdiga briefar ingår inte. 526 titlar med både komplett brief och eget betyg ingår i poängutvärderingen. De 244 poängförslagen gäller titlar utan betyg (147 `plan_to_watch` och 97 `dropped`); ett förslag för en drop är uttryckligen bara en hypotetisk poäng om verket hade setts färdigt.
- Poängmodellen använder bara synopsis, teman, ton, tempo/struktur, karaktärsdynamik och särdrag i briefen. Den använder inte MAL-medel, genrer, studio, titel, användarbetyg eller status som prediktor. `comparison_cues` är uteslutna eftersom de kan spegla rekommendationslogik.
- Femdelad korsvalidering håller titlar med gemensam titelstart i samma fold. Regularisering väljs inuti träningsfolden; slutmodellens alpha är 0,5. Baslinjen är medianen av träningsfoldens egna poäng. Det 80:e percentilet för absolut out-of-fold-fel är 1,2 poäng; det är en felstorlek, inte ett kalibrerat konfidensintervall.
- Drop-modellen är separat och predicerar observerad `dropped` kontra `completed`; den säger inte om användaren ogillade ett verk.
- Detta är retrospektiv korsvalidering, inte ett nytt blint test. Beskrivningarna är redaktionellt skrivna och kan ha urvalsbias. MAL:s medelbetyg har inte använts.

## Slutsats

Det är vettigt att bygga vidare, men inte att kalla den här textmodellen för smakmotorn. Nästa motor bör först representera verkens egenskaper och användarens reaktion som separata, flervärda observationer. Hypoteserna att pröva är bland annat:

1. **Progression och minne:** går relationer, världen och konsekvenser framåt över tid, eller återställs samma situation?
2. **Premissens logik:** etableras reglerna, reagerar världen på dem och används de konsekvent?
3. **Relationers agens:** förändras relationerna genom egna initiativ och ömsesidig sårbarhet?
4. **Känslomässig förtjänst:** växer känslan ur berättelsen, eller instruerar verket tittaren hur den ska reagera?
5. **Ton och livskänsla:** hur balanseras humor, nyfikenhet, melankoli och lidande?
6. **Upprepning kontra form:** fungerar återkomst tack vare dynamik och ackumulerade save states, eller känns den som slotfyllnad?
7. **Hantverk och avsikt:** kan tydlig kreativ kontroll eller ett väl utfört experiment väga upp brister?
8. **Innehållskostnad:** är till exempel fanservice, angst eller grafiskt lidande något användaren uppskattar, tolererar eller helst undviker?

Varje observation ska dessutom märkas som direkt uttalad, försiktig tolkning, modellhypotes eller okänd. Färska samtalsfall som valts för att de var intressanta avvikelser ska användas för kvalitativ granskning, inte för att lära in generella vikter utan kontroll.

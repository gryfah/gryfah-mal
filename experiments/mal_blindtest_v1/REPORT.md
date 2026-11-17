# MAL-blindtest v1 – resultat (17 november 2026)

**Status: slutfört för den textbaserade innehållsmodellen.** Alla 105 numeriska prognoser för de 105 blindfallen låstes i GitHub-commit `9d02f9448c36837f641d3a1eceb4665adf637542` **innan** det frysta facit (Git-blob `ecc337aad25a821141b98f7708b2ad800925c19f`) lästes för poängsättning. Inga prognoser justerades efter utvärderingen.

## Resultat

| Modell | MAE | RMSE | Andel inom ±1 betygssteg |
| --- | ---: | ---: | ---: |
| B0: konstant träningsmedian (7) | 0,7238 | 0,9462 | 91,4 % |
| B1: MAL + medianavvikelse i träning | 0,7015 | 0,8617 | 73,3 % |
| B2: MAL + krympt genrekorrektion | 0,6846 | **0,8444** | 73,3 % |
| Textbaserad TF–IDF/kNN-modell | **0,6817** | 0,8539 | 70,5 % |

Modellen använder träningsbetyg, allmänt MAL-medelbetyg, taggar och texten i verkbriefarna. Grannarnas betygsresidualer viktades efter genre- och beskrivningslikhet; hyperparametrar valdes i femfaldig träningskorsvalidering. Av 424 träningstitlar och 105 blindfall fick testmodellen aldrig läsa blindfallens användarbetyg före commit. Testfallens saknade poäng som 0 för dropped ingår inte alls: här bedöms bara 105 completed-fall.

Parade MAE-förbättringar för textmodellen (positiva värden betyder lägre fel):
- Mot B0: +0,0421, bootstrap 95 % KI [−0,0771; +0,1596].
- Mot B1: +0,0198, bootstrap 95 % KI [−0,0203; +0,0603].
- Mot B2: +0,0029, bootstrap 95 % KI [−0,0306; +0,0377].

**Ingen förbättring är säkerställd.** Mot B2 är skillnaden praktiskt taget noll. Dessutom har B2 lägre RMSE, vilket innebär en liten fördel för B2 vad gäller större fel. Att konstant gissa 7 gav mycket hög andel inom ±1 beror på klassobalansen och visar varför detta hjälpmått inte får användas ensamt.

## Svåra avvikelser

Exempel på stora missar från textmodellen (verkligt betyg → prognos):
- Blue Reflection Ray: 8 → 5,572.
- Shinigami Bocchan to Kuro Maid 3rd Season: 6 → 7,988.
- Sousou no Frieren: 7 → 8,787.
- Ore wo Suki nano wa Omae dake ka yo: 6 → 7,640.
- Boku no Tsuma wa Kanjou ga Nai: 8 → 6,400.

På de sex testfall som låg minst 1,5 steg från den MAL-kalibrerade förväntningen nådde textmodellen MAE 1,760 mot B1:s 1,795. Modellen löser alltså ännu inte de särskilt personliga smakavvikelserna.

## Begränsningar

1. **Detta var inte det ursprungligt planerade fristående språkmodellstestet.** Utvärderingen testar en lexikal maskininlärningsmodell med text- och genregrannar. De 62 explicita frågesvaren och 7 kvalitativa omdömena var tillgängliga i träningspaketet men **användes inte direkt i estimatorn**. Den djupare smakmodellens värde är därmed fortfarande oprövat.
2. Faktaprofilerna skapades i ett system där användarbetygen kunde vara synliga. Eventuell omedveten vinkling i texterna kan inte uteslutas.
3. Titelnormalisering hindrar många, men inte garanterat alla, franchiseöverlapp. Detta är ett explorativt hållout-test, inte en definitiv extern validering.
4. De 105 testbetygen har nu avslöjats vid poängsättningen. **De får inte återanvändas som ett nytt blindtest** efter modelljustering. En utökad kvalitativ/semantisk smakmodell behöver en ny orörd provmängd för ett rättvisande resultat.

## Verifierbara filer

- [Manifest och urval](manifest.json)
- [Träningsdata](training.json)
- [Blinda testfall](blind_cases.json)
- [Kvalitativt träningsunderlag](qualitative_evidence.json)
- [Låsta prognoser](predictions.json)
- [Träningsdiagnostik](model_diagnostics.json)
- [Fullständigt maskinläsbart resultat](results_v1.json)
- [Förregistrerat testprotokoll](PROTOCOL.md)

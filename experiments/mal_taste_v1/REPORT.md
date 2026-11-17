# Personlig MAL-modell · första utvärderingen i Work

## Nuläge och audit av blindtest v1

Kontrollen av `main` den 17 november 2026 matchade överlämningen. MAL-listan hade 778 unika ID:n, fördelade på 529 completed, 97 dropped och 152 plan_to_watch. Alla ID:n hade verkbriefar. Åtta var partial, varav tre completed och fem plan_to_watch. Smakfilen hade 529 observationer, 529 reassessments, 62 besvarade frågor och sju kvalitativa evidensposter.

Blindtestets export har 62 frågeposter. För Kennel Tokorozawa, Kamisama Hajimemashita OVA och Tamako Love Story saknas själva svarstexten i exporten. Alla tre svar finns i huvudfilen och ingår i den nya kartläggningen. Två andra svar är ”Minns inte” och bidrar med noll modellvikt.

Jag körde det befintliga [poängskriptet](../mal_blindtest_v1/score.py) mot blobben `ecc337aad25a821141b98f7708b2ad800925c19f` från manifestet. Prognosfilens Git-blob matchade låscommitten. Dess SHA-256 var `7695bf6111e391f666b4e8d90b5a23a6d4210dc4d0db63d2adc51303fef8cc55`.

- MAE, RMSE och andel inom ett betygssteg matchade de publicerade fyra modellraderna på sex decimaler. M1:s MAE var 0,681714 och B2:s 0,684614.
- MAE-vinsten mot B2 var 0,002899. Skriptets 95-procentiga bootstrapintervall var [−0,030146, +0,033479], medan den publicerade sammanställningen anger [−0,030571, +0,037721]. Intervallen för B0 och B1 skiljer sig också. Båda beräkningarna lämnar slutsatsen öppen.
- Skriptet fick fem konsensusavvikelser där rapporten fick sex. Det sjätte fallet, Rock wa Lady no Tashinami deshite, ligger exakt på gränsen 1,5 med decimalaritmetik men blir 1,4999999999999996 med skriptets flyttalsuttryck. På de fem fallen fick M1 MAE 1,8802 och B1 1,8540. Med gränsfallet inkluderat matchar urvalet rapportens sex fall. Detta spelar roll när man tolkar vilken modell som låg närmast i den lilla delgruppen.

## Modell och läckageskydd

[Evidenskartan](evidence_map.json) länkar samtliga 62 frågesvar och sju kvalitativa uttalanden till åtta prövbara dimensioner. Varje dimension har stöd, motexempel och ett villkor för tolkning. Råtexten läses från den låsta huvudfilen. Gruppningen av svaren är en manuell bedömning. Vid exempelvis ett svar om stil eller tempo kan faktorn vara känd samtidigt som riktningen är osäker. Betygsresidualen är en observerad avvikelse och används för att skatta en viktad association.

[Utvärderaren](evaluate.py) använder en avsiktligt enkel första representation. Ordmönster i verkbriefarna markerar när en dimension nämns. Därefter skattas krympta residualkorrektioner ovanpå B2. En relevant användarobservation fördubblar vikten för ett träningsverk i dimensionen och ett direkt kvalitativt uttalande kan ge tredubbel vikt. Ett verk får högst en vikt per dimension. Den försiktiga jämförelsen Koi Kaze/Yosuga no Sora och TWGOK:s oidentifierade jämförelseverk ger kvalitativ kontext. Kritiken mot genreextrapolering bidrar till tolkningen. Dessa tre poster saknar numerisk vikt. De 19 dropped-svaren redovisas separat som möjliga avbrottsorsaker, inklusive uttryckta omständigheter utanför verket. Det finns ännu ingen kalibrerad sannolikhetsmodell för avbrott.

Fem yttre foldar grupperar titlar efter titelprefix. Modellen använder enbart träningsfoldens betyg. Ett uttalande med flera refererade MAL-ID:n kan viktas först när alla finns på träningssidan. På samma sätt uppskattas sannolikheter över 1–10 från residualer i inre träningsfoldar. De 105 gamla blindfallen utesluts genom manifestet. Detta är retrospektiv korsvalidering. Kodningen togs fram med kännedom om projekthistoriken. Titelgrupperna kan missa förklädda uppföljare och briefarna kan ha påverkats av att betygen var synliga när de skrevs.

## Träningsbaserade resultat

| Modell | MAE | RMSE |
| --- | ---: | ---: |
| B0 · träningsmedian | 0,7712 | 1,0695 |
| B1 · kalibrerat MAL-betyg | 0,7438 | 0,9462 |
| B2 · kalibrerat MAL-betyg och genrekorrektion | **0,7323** | 0,9353 |
| B2 och åtta dimensioner från verkbriefarna | 0,7334 | 0,9343 |
| B2, dimensionerna och viktning från uttrycklig evidens | 0,7339 | **0,9336** |

På 424 titlar gav evidensmodellen en parad MAE-vinst mot B2 på −0,00154 med ett gruppbootstrappat 95-procentigt intervall [−0,00789, +0,00489]. Den isolerade evidensviktningen gav −0,00048 [−0,00279, +0,00196] mot versionen med briefar. Ordinalt sannolikhetsfel (RPS, lägre är bättre) var 0,05547 mot 0,05567 för B2. Det finns inget tillskott i genomsnittlig prognosprecision att använda för rangordning utifrån detta test.

I de 40 fallen med faktiskt 9–10 sjönk MAE från 1,459 till 1,408, medan det steg från 0,920 till 0,944 för de 109 fallen med betyg 1–6. Bland 53 stora konsensusavvikelser sjönk MAE från 1,859 till 1,847. Det är indikativa delgrupper. Modellen underskattade exempelvis Darling in the FranXX med tre betygssteg och överskattade Hotaru no Haka med över tre. Breda omnämnanden av relationer och utsatthet ger svaga signaler om hur gestaltningen faktiskt landar. Ett stringent nästa test behöver koda mer prövbara egenskaper, till exempel om ett relationsval förändrar senare handlingsmöjligheter, och registrera osäkerhet när briefen saknar belägg. En ny prospektiv omgång kräver prognoser frysta innan användarbetygen finns.

## Bedömning av bevakningar

| Bevakning | Bedömning |
| --- | --- |
| Synka GitHub | Behåll. Skriptet producerar gemensamma event i `results.json`; ett nytt completed får både `next_up` och `post_watch`. Vid kontrollen hade synkningen registrerat båda signalerna på det senaste completed-eventet. |
| Bygg animeprofiler | Renodla till glesare underhåll av nya ID:n och uppdateringsbara partial. Hela den aktuella listan täcks, så den tunga timkörningen har liten marginalnytta. En ersättare behöver kunna upptäcka nya ID:n i listan och skriva briefar före ett eventuellt stopp. |
| Post-watch | Behåll med separat leveranskvittens per event-ID. I den kontrollerade körningen startade den 22.05.38 Stockholmstid men var schemalagd 22.20. Ett event publicerat efter läsningen men före 22.20 kan hamna mellan två läsningar eftersom nästa fönster börjar 22.20. Kontrollen visar ett möjligt glapp i mekanismen. Ingen förlorad leverans har verifierats. |
| Next-up | Behåll exakt tre förslag per relevant händelse. Inför samma princip för leveranskvittens med egen nyckel per mottagare och event-ID. Den nuvarande synklogiken signalerar destinationerna completed, dropped och removed. Den äldre regeln om första PTW-utgång via watching/on_hold kräver en separat ändring i eventproducenten om de statusarna åter används. |
| Hitta jobb | Behåll som separat uppgift. |

Synkens eventhistorik är begränsad till sju dagar och högst 200 poster. En senare migration behöver därför kunna läsa ikapp inom den horisonten och rapportera om en utebliven körning gjort att historik saknas. Hantera återförsök per kombination av bevakning och event-ID. Next-up och Post-watch kan då båda reagera på samma completed-event och samtidigt kontrollera sina egna dubbelleveranser.

## Kör om

Från en full Git-klon där de låsta blobbarna finns. Kommandona nedan använder Bash för att bevara råa filbyten vid omdirigering.

```bash
git cat-file blob ecc337aad25a821141b98f7708b2ad800925c19f > frozen_anime.json
git cat-file blob d0b985ddf369313b6cc1fe110caf89a32db957f5 > frozen_preferences.json
python experiments/mal_blindtest_v1/score.py \
  experiments/mal_blindtest_v1/predictions.json frozen_anime.json \
  --expected-predictions-sha256 7695bf6111e391f666b4e8d90b5a23a6d4210dc4d0db63d2adc51303fef8cc55
python experiments/mal_taste_v1/evaluate.py --evidence frozen_preferences.json
```

Maskinläsbara resultat finns i [cv_results.json](cv_results.json).

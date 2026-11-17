# Smakfunktionen · betyg, avbrott och textbelägg

Den här iterationen är en körbar experimentfunktion för ett MAL-ID som ligger i PTW. Den ger en sannolikhetsfördelning för betyget givet att verket avslutas och en separat uppskattning av avslut givet att tittningen påbörjas. Utdata innehåller styckena som gav utslag i analysen. Betygsprognosen lämnas tom när verkets MAL-snitt saknas.

## Utvärdering

| Utfall | Referens | Textbaserad modell |
| --- | ---: | ---: |
| MAE, 424 betyg | 0,73232 (MAL + genre) | 0,73286 |
| MAE på 40 betyg 9–10 | 1,45874 | 1,43728 |
| MAE på 109 betyg 1–6 | 0,91982 | 0,93060 |
| Brier, 496 avslut eller avbrott | 0,11810 (format och antal avsnitt) | 0,11819 |

Resultatet bygger på fem titelgrupperade foldar. De 105 tidigare blindfallen används inte. Betygsmodellen skattar sju krympta koefficienter utifrån specifika textmönster och ger högre vikt åt en träningsobservation om dess uttryckliga evidens pekar på samma dimension. Återstående osäkerhet skattas med inre korsvalidering. Den parade MAE-vinsten mot MAL + genre var −0,00054 med 95-procentigt gruppbootstrapintervall [−0,00703, +0,00550]. Den nya modellen gav ingen visad prognosvinst. De frysta träningsfilerna och approximationen för titelgrupper innebär att detta fortfarande är ett retrospektivt resultat.

Avbrottsdelen använder 72 verk som faktiskt påbörjats enligt registrerade avsnitt. Fall med uttrycklig osäker start eller blandade externa skäl undantas. Avbrutna verk ingår som avbrottsutfall och får inget konstruerat betyg. Avslutsuppskattningen gäller jämförbara, redan avgjorda fall i listan. Den tar inte hänsyn till öppna tittningar eller ändrade förhållanden i tittarens liv och säger inget om orsakssamband.

## Vad textkontrollen visade

- Textreglerna hittade avsnitt som bygger vidare på varandra i 84 av 424 briefar. Val med följder hittades i sju och berättelsemässig återställning i två. De siffrorna beskriver ordmönstrens täckning, inte hur vanliga mekanismerna är i verken.
- PTW-provet för *Liz to Aoi Tori* gav inga textträffar. Briefen beskriver hur duetten uttrycker flickornas samspel, vilket den automatiska kontrollen missade. Punktprognosen blev därför precis densamma som genrebänkmärket.
- PTW-provet för *Hone Dragon no Mana Musume* saknade MAL-snitt och gav följdriktigt inget betyg. Samma prov avslöjade ett falskt utslag. Formuleringen om relationen mellan liv och död hade registrerats som en mellanmänsklig relation.
- En textträff är ett förslag på relevant passage. Tolkningen kan vara fel även när bägge orden förekommer i samma mening. Utebliven träff säger bara att regeln saknade textbelägg.

Nästa mätbara förbättring är en liten genomgång av verkens faktiska berättelseförlopp, med dold tittarhistorik under kodningen. Börja med tre bedömningar där texten visade svag täckning.

| Fråga om verket | Belägg som krävs |
| --- | --- |
| Förändrar ett relationsval vad karaktärerna kan eller vill göra senare? | Beskriv valet och dess följd som två skilda händelser. |
| Bär fristående avsnitt vidare något? | Beskriv en relation, ett beslut eller ett villkor som finns kvar i ett senare avsnitt. |
| Vad blir kvar när ett övernaturligt grepp återställer något? | Ange vad som återställs och vilka följder som kvarstår. |

En framtida annotation behöver MAL-ID, mekanism, bedömning, text- eller episodbelägg och källa. Använd utfallen `evidenced`, `counterevidenced` och `unknown`. `Counterevidenced` kräver ett konkret belägg för motsatsen. Registrera tolkningen av tittarens gamla svar i ett eget steg efter kodning av verket. Börja med att mäta hur ofta två oberoende bedömningar av samma verk överensstämmer innan ytterligare vikter läggs på betyget.

## Kör funktionen

Från en full Git-klon. Nedan används Bash så att de låsta blobbarna kan skrivas byte för byte.

```bash
git cat-file blob c8a39c53c2e39d6107cdcdbf8f45c01c59490520 > frozen_anime_current.json
git cat-file blob 65ee46c5d708cb696fa1378977d4c15f02258f55 > frozen_profiles.json
git cat-file blob d0b985ddf369313b6cc1fe110caf89a32db957f5 > frozen_preferences.json

python experiments/mal_taste_v1/taste_profile.py \
  --anime frozen_anime_current.json \
  --profiles frozen_profiles.json \
  --evidence frozen_preferences.json
```

Lägg till `--target-id 35677` för resultat på ett enskilt PTW-verk. Med `--current-anime` och `--current-profiles` tillsammans kan aktuella PTW-titlar analyseras med träningskohorten fortsatt fryst. [Fullständiga utvärderingsresultat](profile_cv.json).

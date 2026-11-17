# Instruktion till den isolerade prognosmodellen – MAL Blindtest v1

Du ska förutsäga EN användares betyg för 105 redan sedda animeverk utan att se deras verkliga betyg.

**Tillåten indata:** endast bifogade `training.json`, `blind_cases.json`, `qualitative_evidence.json`, `manifest.json` och `PROTOCOL.md`.

**Förbjuden indata:** hela originalrepositoryt, originalfilen `anime.json`, MAL-användarprofilen, GitHub/webbsökning, minne från tidigare användarkonversationer, modellens gamla betygsresidualer, global statistik eller facit. Har du redan fått tillgång till sådana källor är försöket inte blindt: redovisa problemet och avstå från att hävda blindtest.

Metod:
1. Bygg en bedömning av användarens smak från de 424 kända betygen och de faktiska svaren i kvalitativa träningsdata. Var uppmärksam på motexempel och på skillnaden mellan förekomst av en genre och vad användaren faktiskt värdesätter.
2. Använd bara träningsdata för eventuell kalibrering, modellval, regressionsanpassning och validering. Intern korsvalidering är tillåten, men avslöja aldrig blindfacit.
3. För varje av de 105 fallen använd MAL:s allmänna betyg, genrer, produktionsmetadata och verkets objektiva faktabrief. Uppskatta ett **numeriskt användarbetyg 1–10**. Decimaler är tillåtna; låg säkerhet kräver fortfarande en prognos.
4. Ge en säkerhetsklass `low`, `medium` eller `high`, och 1–3 meningar med **konkreta iakttagbara faktorer**. Ange osäkerhet där du inte har underlag för orsakssamband. Påstå inte att två verk måste gillas lika bara för att de delar taggar, franchise eller berättelseformat.
5. Skriv ett enda giltigt `predictions.json` som innehåller exakt alla `mal_id` i `blind_cases.json`, utan dubbletter eller extrafall. Följ formatet i protokollet. Lägg inte facit eller uppskattade användarbetyg för träningsfallen i detta dokument.
6. Lås filens innehåll innan en separat bedömare hämtar originalbetygen. Gör **inga efterhandsändringar**. Inga extra frågeomgångar till användaren ska ställas.

Målet är inte att skriva en övertygande analys i efterhand. Målet är att se om beskrivningen av smaken tillför prognosvärde jämfört med en enkel MAL-kalibrerad modell.

Håll analys och generering av prognoser helt åtskilda från poängsättningen.

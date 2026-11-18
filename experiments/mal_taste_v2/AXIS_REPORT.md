# Smakaxlar v2 — evidens- och säsongsgranskning

Det här steget gör modellen flerdimensionell, men lämnar tydligt öppet vad som är känt och vad som ännu bara är en hypotes. Körningen använder `anime.json` från 2026-11-18, verkbriefarna och dåvarande `anime_preference_learning.json`. MAL-medelbetyg används inte.

## Datat som granskats

- 778 titlar i MAL-listan, varav 529 `completed`, 97 `dropped` och 152 `plan_to_watch`.
- 770 briefar är färdiga. Poänganalysen omfattar 526 titlar där brief och eget betyg finns.
- Säsongsgranskningen omfattar samtliga **626 completed- och dropped-titlar**, grupperade efter releaseår och release-säsong.
- 140 svar och användaranteckningar pekar på 112 titlar. 514 granskade titlar saknar ännu direkt smakkommentar: 445 completed och 69 dropped. De är **okända**, inte neutrala.

## Axlar som nu hålls isär

| Axel | Frågan den skiljer på |
|---|---|
| Progression och minne | Byggs relationer, värld och konsekvenser upp, eller börjar berättelsen om? |
| Premisslogik | Följer berättelsen sina regler och låter världen reagera på premissen? |
| Relationers agens | Tar personer initiativ och förändras ömsesidigt, eller fastnar de i en loop? |
| Känslomässig inramning | Väljer tittaren själv sin reaktion, eller pressar berättelsen fram den? |
| Ton och textur | Hur samspelar humor, nyfikenhet, melankoli, värme och ångest? |
| Form och ackumulation | Fungerar episodisk form genom bestående utveckling, eller upprepas samma slot? |
| Hantverk och avsikt | Håller genomförandet ihop och känns det som att kreatörerna äger sitt grepp? |
| Innehållskostnad | Vad gör fanservice, angst, våld eller detaljerat lidande med upplevelsen? |

Verksbriefens signaler och dina reaktioner lagras var för sig. Ett omnämnande av en relation betyder alltså inte automatiskt att relationen uppskattades. Direkta blandade omdömen kan också förbli blandade.

Den första axeltaggningen är lexikonbaserad. En tagg visar att formuleringen matchar en axel, inte att tolkningen är verifierad; vissa taggar behöver manuell granskning innan de kan påverka rekommendationsvikter.

## Första mätningen

Den automatiska axelavläsningen av brieftext gav MAE **0,7958**, sämre än medianbaslinjens **0,7605**. Den enkla textmodellen från första försöket gav 0,7484, men dess lilla förbättring var osäker. De här automatiska signalerna är därför inte tillräckliga för att rangordna titlar som om de vore säkra smakprognoser.

Det finns också en tydlig informationslucka: nuvarande briefar ger nästan ingen direkt signal om **hur en premiss granskas och följs**, och mycket lite om **episodisk form kontra återställning**. De axlarna finns starkt i dina omdömen, men arbetsbeskrivningarna säger sällan tillräckligt för att tillämpa dem på osedda titlar. De behöver källförankrade, strukturerade verkanteckningar.

## Mönster som redan är tydliga i dina egna exempel

- **Episodisk betyder inte automatiskt stillastående.** Azumanga Daioh bevarar en hel skolbåge och tidigare händelser mellan avsnitten. Strike Witches upprepar däremot samma slot; Eureka Seven har canon men drar ut utvecklingen så långt att den tappar kraft.
- **Relationer behöver rörelse.** Initiativ och ömsesidig sårbarhet bar Nagatoro S2, medan Kamisama-OVA:n kändes som ännu en “ska de, ska de inte”-loop. I Horimiya Piece fick redan älskade personer mer tid, vilket är en annan sorts värde än att vänta på en relation som stannat.
- **Kvalitet och personlig vilja att återvända är skilda saker.** Hotaru no Haka kan vara mycket välgjord och realistisk, men ändå vara en film du inte vill se igen eftersom den går så nära barns död av svält.
- **Konsekvenser kan ge berättelsen tyngd.** Du lyfte hur världen, ansvar och risk faktiskt förändras i Attack on Titan Final Season, och hur relationernas förskjutning bar Evangelion Q.
- **En stark final kan betala av en specifik relationshistoria.** 5-toubun-filmen fungerade genom spänningen i att vara systrar, extramamma och rivaler, följd av en förlösande kärleksförklaring och ett bokstavligt bröllop. Det är ett exempel på payoff efter investering, inte stöd för att bröllopsslut i sig räcker.
- **86 Part 2 samlade flera saker samtidigt.** Action och drama, starka personer, meningssökande i dystopin, relationer, återföreningen och musiken byggde tillsammans upp tian.
- **Formatetiketter behöver precisering.** Saki föll inte på majong i sig, utan blev för inrökt i sitt majongtie-in. Amagami SS korrigerar i sin tur hypotesen att omnibus generellt är din grej: efter tre berättelser insåg du att det specifikt var The World God Only Knows som fungerade.

Detta är än så länge fallförankrade exempel, inte generella vikter. Urvalet av kommenterade verk är skevt mot intressanta avvikelser. Räkna därför inte antalet negativa omnämnanden som hur ofta en egenskap stör dig i hela katalogen.

## Konkreta modellmissar

Axelmodellen dras mot 7/10 och visar varför separata dimensioner behövs. Prognosen nedan är bara ett diagnostiskt jämförelsetal, inte ett nytt betygsförslag.

| Titel | Ditt betyg | Axelmodell | Vad den missar enligt dina kommentarer |
|---|---:|---:|---|
| Myself; Yourself | 5 | 7,19 | Relationskonflikterna räckte inte för att bära en medioker premiss; bi-karaktärerna blev pastischer. |
| Hotaru no Haka | 5 | 7,21 | Hantverk och realism kan vara höga medan den detaljerade skildringen av barns svältdöd gör filmen ovälkommen att återse. |
| Strike Witches | 5 | 6,85 | Premiss och gruppdynamik hade värde, men återkomsten av samma episodupplägg och kostymer tröttade ut. |
| Kamisama Hajimemashita OVA | 6 | 7,01 | Redan uttalad trötthet på parets fram-och-tillbaka-loop; OVA:n blev ännu en loop. |
| Azumanga Daioh | 7 | 7,19 | Episodisk form uppskattades för att den ändå bevarade en hel skolbåge och tidigare händelser. Det gav inte automatiskt ett toppbetyg. |

Eureka Seven hör till en annan etikett: dropped efter 17 registrerade avsnitt, med en kommentar om att canon drogs ut tills den tappade kraft. Det ska inte jämställas med ett numeriskt lågbetyg.

## Vad filerna innehåller

- `seasonal_audit.csv`: alla completed- och dropped-titlar, sorterade kronologiskt. Visar betyg eller drop, antal sedda avsnitt, briefsignaler, direkt kommenterade axlar och källnära skäl.
- `axis_evidence.csv`: varje enskilt svar eller uttalande med MAL-ID, källa, axlar och riktning (`positive`, `negative`, `mixed`, `unclear` eller icke-värderande). Riktning tilldelas bara när formuleringen stödjer den.
- `axis_results.json`: fullständiga axeldefinitioner, mätresultat, säsongsutfall, evidensposter och en separat, lågkonfidens scoreprognos för titlar utan eget betyg.
- `axis_model_v2.py`: körbar implementation.

Scoreprognosen för en drop betyder endast “om den hade setts färdigt”; den omvandlar aldrig en drop till ogillande. Än så länge bör vi använda filerna som en granskningsyta: hitta titlar där din egen kommentar förklarar varför textmodellen missar, och fyll först därefter de verkaxlar som saknas.

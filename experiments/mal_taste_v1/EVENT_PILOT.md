# Pilot med händelsebelägg och frågeomgång

## Resultat

Åtta färdigsedda verk valdes deterministiskt på MAL-ID, fyra TV-serier och fyra filmer. Urvalet kom ur den tidigare träningsmängden. Tidigare frågor och kända exempel uteslöts. Verkbeskrivningarna visades utan tittarbetyg. En bedömare kodade tre egenskaper med källstöd och låste anteckningarna och poängregeln i commit `dbdb01ae0fef64770d3ef1bec3342fdf590164a7` före visning av testbetygen. De åtta titlarna och deras titelgrupper uteslöts tillsammans ur anpassningen av jämförelsemodellen. De 105 tidigare blindfallen användes aldrig.

MAL + genre gav medelabsolutfel **0,569**. Samma prognos med den låsta händelsejusteringen gav **0,619**. Tre verk fick lägre fel, fyra högre och ett samma. Sju verk hade belägg för att något byggdes vidare, tre för val med följder och inget för att en återställning suddade ut följderna. Piloten säger därför inget om effekten av den sistnämnda regeln. Den testar en fast poängjustering på åtta verk och visar inte om en större, oberoende verifierad annotering skulle ge bättre prognoser.

Det konkreta problemet är att regeln behandlade olika sorters progression som likvärdiga. Lärlingsspåret i *Flying Witch* kunde beläggas, men prognosen låg redan över 6:an. *Nagatoro 2nd Attack* fick däremot 8 trots en lägre grundprognos. I *Inugami-san to Nekoyama-san* fanns för lite underlag för att belägga en genomgående utveckling, medan det faktiska betyget ändå var 7 och låg över grundprognosen. För nästa modell behöver vi veta vilken roll utvecklingen spelade i upplevelsen.

Kör om med `python experiments/mal_taste_v1/score_event_pilot.py`. [Låsta anteckningar](event_pilot_annotations.json) och [resultat per titel](event_pilot_results.json).

## Sex frågor om tidigare betyg

Välj en huvudorsak per titel. Lägg till en bokstav om två saker vägde ungefär lika tungt. Svara **e** och skriv fritt om alternativen missar, eller **f** om du inte minns. Fråga 6 gäller en titel utanför pilotens åtta verk. Samtliga sex är nya i frågedatabasen. Alternativen är hypoteser om vad som spelade roll.

1. **Flying Witch (31376), 6/10. Vad satte taket?**  
   a) För lite förändrades mellan avsnitten.  
   b) Serien fick gärna vara episodisk, men de enskilda upptäckterna och mötena gav för lite.  
   c) Personerna eller deras samspel engagerade inte tillräckligt.  
   d) Det lågmälda utförandet var det jag ville ha. 6 var ett okej betyg för upplevelsen.

2. **Inugami-san to Nekoyama-san (22123), 7/10. Vad bar kortformatet?**  
   a) Skämten och rollkontrasterna fungerade i sig.  
   b) Samspelet mellan huvudpersonerna var det roliga, även när situationerna liknade varandra.  
   c) Avsnitten slutade innan upplägget hann bli tjatigt.  
   d) Jag fick ändå ut tillräckligt av hur relationen utvecklades.

3. **Nagatoro 2nd Attack (50197), 8/10. Vad bar andra säsongen?**  
   a) Senpai tar egna initiativ och förändrar relationen.  
   b) Retandet i sig var huvudbehållningen.  
   c) Båda visar mer sårbarhet och det förändrar hur deras tidigare dynamik känns.  
   d) Betyget bygger främst på att jag redan var engagerad i paret efter första säsongen.

4. **Kimi wa Houkago Insomnia (50796), 8/10. Vad betydde mest?**  
   a) De hittar en kravlös närhet kring ett problem de båda delar.  
   b) Fotograferingen och resan gör att relationen faktiskt tar steg framåt.  
   c) Nattmiljöerna och rytmen bar en stor del av upplevelsen.  
   d) Det avgörande var hur slutet tog hand om det som byggts upp.

5. **Made in Abyss: Dawn of the Deep Soul (36862), 7/10. Vad avgjorde helheten?**  
   a) Prushka och Riko gav filmen dess känslomässiga tyngd.  
   b) Bondrewd och de moraliska frågorna var filmens styrka.  
   c) Filmen gjorde avgrundens regler och nedstigningen mer intressanta.  
   d) Filmen tog steg framåt, men sättet den skildrade lidandet eller följderna höll nere betyget.

6. **Busu ni Hanataba wo. (53512), 5/10. Vad drog ned betyget?**  
   a) Jag trodde inte på hur relationen mellan Hana och Ueno utvecklades.  
   b) Hanas självbild användes för att upprepa samma konflikt för länge.  
   c) Jag köpte relationen, men väntan på att den skulle förändras tog för mycket plats.  
   d) Humorn, berättarrösten eller tonen gjorde att jag tappade intresset.

Källor för verksdetaljer finns i pilotanteckningarna. [Källa för *Busu ni Hanataba wo.*](https://us.oricon-group.com/news/5204/)

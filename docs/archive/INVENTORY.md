# Inventory of places to fix

Generated from the current `master` of `zpevnik` (733 songs). Format: `song` followed by what was found, `L<n>` = line number.

> Snapshot of 3 Nov 2026; line numbers and counts are stale. Since then: R6–R12 consumed sections C and D, H1–H4 (session 8) removed the final `\newpage`, the per-song `\hyt` and the accent macros, and fixed the five source quirks. Re-derive lists with grep before use.


## A. Horizontal spacing

Totals: `\nc` 712, `\mm` 319, `\sm` 254, `\bc` 0 uses; 303 songs affected.

*Session 9:* every run of these macros is classified in docs/C1-review-lists.md:
- 681 runs between chords
- 288 gaps before a chord
- 157 pauses after a chord
- 69 gaps inside lyrics

There are also ≈ 96 chords written as `\textbf`. The C3 batch plan will be docs/C3-batches.md (D-123).

### A1. Songs using `\nc` `\mm` `\sm` `\bc` (all must be reviewed once the chord spacing is automatic)
```
aintnograve: mm=11 nc=3
alberta: nc=6
alisongross: sm=1
allihavetodoisdream: nc=2
allmyloving: nc=4
allyouneedislove: nc=6
alwayslookonthebrightsideoflife: nc=4
amazonka: nc=2
andel: mm=1 nc=1
andelska: mm=2 nc=8 sm=3
anickadusickanekasli: sm=1
apak: mm=1 nc=1
azseknampravovrati: sm=1
azvzletnouptaci: mm=2 nc=1
babickamary: mm=1
batalion: sm=10
bigbangtheorytheme: sm=1
blackbird: mm=2 nc=2 sm=8
bluesnacestuposledni: nc=9
bratrickuzavirejvratka: mm=7 nc=1 sm=8
brnojezlatalod: mm=1 sm=1
ceresnicky: sm=1
cerneocijdetespat: mm=1
cervenareka: mm=6 nc=3 sm=8
cervenarekatucny: sm=2
ceskapisnicka: nc=1
changetheworld: mm=1 nc=3
chattanoogachoochoo: mm=1 nc=3
chcibytpritom: mm=14 nc=2 sm=1
chirpychirpycheepcheep: mm=2
cizesutokone: sm=2
cmelak: nc=3
conselho: mm=4 nc=1
dajana: nc=2
dancingqueen: mm=5 nc=9
darmodej: mm=1 nc=4
davidagolias: mm=1 sm=2
dejmivicsvelasky: sm=1
delani: mm=2
depese: mm=1 nc=9 sm=1
dezo: mm=2 sm=1
digadigadoplihal: mm=1
digadigadospiritual: mm=1 nc=2
dobrouzpravuhlasej: mm=2 sm=2
dokudsezpiva: nc=10
dontstopmenow: mm=2 sm=3
duhovavila: mm=1 nc=5 sm=3
dumuvychazejicihoslunce: nc=1
dvakrat: nc=1
eduvzalikfotografovi: nc=1
ejbozemuj: nc=1 sm=1
elektrickyvalcik: mm=1 sm=2
farao: mm=1
flymetothemoon: mm=2 nc=2
fornoone: nc=1 sm=1
fotky: mm=1 nc=9
frantisek: nc=3
frydekmistek: nc=1 sm=4
gilotina: mm=1 sm=3
girl: nc=3
goodriddance: mm=4 nc=6
guadalcanal: sm=1
hadejkdomipise: sm=4
hajnyjelesapan: nc=1
harmonikarska: nc=2 sm=1
haubilouplani: mm=2 sm=2
hejnovran: nc=4
hejpanekrali: nc=2 sm=1
hejteto: nc=6
hittheroadjack: mm=1 nc=2
hledamdevcenanedeli: nc=6
hlidackrav: nc=2
hlupakunajdute: sm=1
holubidum: mm=1 sm=2
hornicka: sm=2
hudsonskysify: mm=2
huslicky: mm=1
hvezdanavrbe: nc=7 sm=5
hvezdyjsoujaksedmikraskynadbrnem: nc=2
icantstoplovingyou: nc=1 sm=1
idzepostaridze: nc=2
ififell: nc=2 sm=1
illfollowthesun: nc=3
inthesummertime: mm=4
ionlywanttobewithyou: mm=1
jachcipoezii: nc=2
jasetesimdonebe: sm=1
jasnazprava: nc=5
jastebouzitnebudu: nc=11
jednohodnesevratis: mm=4 nc=7
jednoubudemdal: sm=1
jednourano: mm=4 nc=8 sm=6
jestlitonebudelaska: nc=4
jinetonebude: mm=4 nc=2
jozinzbazin: mm=2
karavanamraku: mm=2
katce: mm=1 nc=5 sm=1
kdejsou: nc=1
kdonaplninebe: sm=1
kdyzjsembylchlapecmalej: nc=5
kdyzsezamilujekun: mm=1
kloboukvekrovi: mm=3 nc=5
kluziste: mm=2 sm=10
kockanaokne: mm=2 nc=1 sm=1
kocourseschoulilnatvujklin: mm=1 nc=2
kolobezka: mm=1 nc=1
koukamjakcelazemevstava: nc=2
krajinaposedlatmou: nc=3 sm=6
kralaklaun: mm=8 nc=1
kratkypopisleta: nc=2
krutavalka: sm=1
labamba: nc=4
lachtani: nc=3
lacinyvino: mm=2 nc=1 sm=1
ladycarneval: mm=1
laughingontheoutside: nc=3
layallyourloveonme: mm=2 sm=1
layla: mm=1 nc=4
leavingonajetplane: nc=1
letadozravani: mm=1 sm=2
letitbe: nc=4
letniukolebavka: mm=5 nc=6 sm=7
linda: nc=2
litaliano: nc=1 sm=2
lizatko: nc=1
loddeti: mm=1
lonelystranger: mm=8 nc=6 sm=6
magdalena: nc=7
majak: mm=4 nc=5
malujzaseobrazky: sm=1
mamjizvunartu: nc=3 sm=1
maschutmajoranky: nc=3
mecvrucemam: nc=3
medicinman: mm=1
medvedinevedi: mm=1 sm=1
metroprokrtky: nc=5
mezinarodni: mm=2
mikymauz: nc=1
mladickabasnirka: mm=2 nc=2
mlyny: sm=1
mnisijsoutisi: mm=1
mobilizace: nc=3
mojiprvnimuze: mm=1 nc=3
montgomery: nc=2
moskevskavirtualka: nc=2
mosty: mm=3
motyl: mm=2
mravencivkredenci: mm=2 sm=9
muzika: mm=2 nc=1
mys: sm=2
nacopojdemdomov: nc=1 sm=1
nadejeatouhy: nc=4 sm=2
nadejilaskouavirou: mm=1 sm=1
nadstademkoni: nc=6
nagasakihirosima: nc=4
nahoteluvolomouci: mm=2
namornicka: nc=4
namsestalonecoprekrasneho: mm=1 nc=1
navode: nc=4
nebenazemi: mm=1
nechtezvonyznit: mm=1
necoolasce: nc=1
nejlipjimbylo: nc=15
nekdopijelih: nc=2
neninutno: mm=1
nepijjanonepijvodu: mm=1 sm=1
nevadi: sm=1
nictolikneboli: nc=3
nobodyknowsyouwhenyouredownandout: nc=14
noe: nc=1
nomoreauctionblockforme: mm=2
obladioblada: nc=3
ohfreedom: mm=1 nc=1
oldtimereligion: mm=1
oneofus: nc=12
orlice: mm=2
otazky: nc=44
ourlastsummer: mm=1 nc=6 sm=1
padalyhvezdy: sm=1
paradaI: mm=2 nc=7 sm=3
paradaII: mm=2 nc=7 sm=3
pata: mm=2 nc=12
pepita: sm=1
pianoman: mm=2 nc=7
pisencomeucillistopad: mm=2
pisenokoni: nc=1
pisenorose: nc=1
pisenzhrzenehotrampa: nc=1
piskajicicikan: nc=1 sm=1
pisnickaprotebe: nc=4
pocestny: mm=1
podzim: nc=1
podzimnispiritual: sm=1
pohoda: mm=2 nc=2 sm=2
pojdmespat: mm=3 sm=2
porekadla: mm=1 nc=5 sm=5
potopa: nc=5
poutnikadivka: mm=1 nc=1
prachovskeskaly: mm=1
prehlidkaztracenyhocasu: nc=1
prejelijsmeslepici: nc=2 sm=1
priznavam: mm=2
proklatejvuz: mm=1 sm=1
prolabute: mm=1 sm=1
prsi: mm=1 nc=4
radsebrouzdamrosou: sm=2
ranavtrave: nc=4
reddwarftheme: mm=1
redrivervalley: mm=3 nc=3 sm=1
rekalasky: mm=4 nc=13 sm=1
reklamanaticho: mm=1
reknikdetykytkyjsou: mm=1
ringoffire: nc=19
rockyraccoon: nc=3
rosanakolejich: mm=2 nc=2 sm=4
ryljencelejdenryl: mm=1
salome: mm=5 nc=1 sm=1
sanfranciscobayblues: nc=4
satydelajcloveka: mm=2 nc=1 sm=4
sbohemgalanecko: sm=1
scarboroughfaircarthy: mm=1
sirokyhluboky: sm=1
siryproud: mm=1 sm=1
skupinovefoto: mm=2
slapejdalspiritual: mm=1
slunecnyhrob: mm=8 nc=1
slunicko: mm=2 sm=1
snebyvalouochotou: mm=1
soske: mm=2 nc=16 sm=1
soudnyden: mm=3 nc=1 sm=1
spanembohemidemodvas: mm=2
spravnyslovo: nc=3
sprostyadmindusan: mm=1
sroubyamatice: nc=3
sss: nc=2
starypribeh: mm=4
stinkatedral: nc=4
summertime: mm=1 nc=5 sm=5
svagrmabagr: nc=2 sm=1
svatekmazofie: mm=1
takbytjednoubouri: mm=1 sm=1
takjenpojd: mm=1 nc=1 sm=1
takjsmevandrovali: nc=1 sm=1
tamunebeskychbran: nc=3
tasidele: mm=2 nc=1
tata: mm=2
tearsinheaven: mm=2 nc=10 sm=2
tenkdoneduma: mm=1
tesinska: nc=11
thepassenger: nc=4
thewateriswide: mm=1 sm=2
tiamo: mm=1
timeinabottle: mm=1 nc=2 sm=2
tocozbyvalasko: nc=4
tophatbarandgrill: nc=3
totenkratvctyricatompatom: nc=2
touha: nc=1
tresnezraly: sm=1
tresnicky: mm=2
trezor: mm=1
trhvescarborough: mm=1 sm=1
trochuvhlavemam: mm=3
trpaslicisvatba: mm=1
trubadurska: mm=1 nc=1 sm=2
tvojesnidane: mm=1 nc=2 sm=2
twistandshout: mm=2 nc=6
ukolebavkaprokubualenku: mm=1
unasnaseveru: nc=4
valcicek: nc=1 sm=1
vandrovani: mm=3 nc=4 sm=3
vandrovni: nc=1
variacenarenesancnitema: nc=2
vbufetu: sm=1
vcelkamaja: nc=2
vcera: nc=1 sm=2
vdobrymizlym: mm=1
vienna: mm=2 nc=2
vineckobile: sm=2
vlak: nc=1
vlastovkolet: nc=2
vodacomadrzinadvodou: mm=3 nc=5 sm=5
vodavodenka: mm=2
vor: mm=1
vranaplihal: mm=2
vyletelaholubicka: mm=1
walkingbacktohappiness: mm=1 nc=1
waterlooabba: mm=2 nc=2
wearethechampions: nc=8
wewillrockyou: nc=3
yesterday: mm=1 nc=1 sm=2
zafukane: mm=1 nc=9
zasvoupravdoustat: mm=1
zatimcosekoupes: mm=2 nc=4 sm=2
zeleneplane: sm=1
zelva: nc=5
zelviblues: mm=1
zitraranovpet: mm=1 nc=3 sm=1
zivotjejennahoda: mm=2 sm=1
zizen: sm=2
zkratky: mm=1 sm=4
ztracenabackorka: nc=2 sm=1
zustan: mm=1 nc=1
zvednetekotvy: mm=1 sm=2
```

### A2. Chord directly followed by another chord (the case `\nc` was invented for; most likely to be 'too narrow')
```
aintnograve: L6,7,9
alberta: L7
allihavetodoisdream: L24
allmyloving: L25
allyouneedislove: L9,10,16
alwayslookonthebrightsideoflife: L12,13
amazonka: L5,6
andelska: L8,22
blackbird: L11,23,24,25
bluesnacestuposledni: L6
bratrickuzavirejvratka: L14
cervenareka: L9,23,37
ceskapisnicka: L10
chattanoogachoochoo: L6,25
chcibytpritom: L6,7,9
cmelak: L8,21
dajana: L7
dancingqueen: L5,10,17
darmodej: L22
depese: L5,10,15,17,21,26,28
dokudsezpiva: L4,5,7
duhovavila: L10,11
dvakrat: L36
eduvzalikfotografovi: L6
ejbozemuj: L33
flymetothemoon: L14,21
fotky: L5,6,7,8,19
frantisek: L18,19,20
frydekmistek: L11
girl: L14
goodriddance: L5,6
hajnyjelesapan: L6
harmonikarska: L13
hejnovran: L4,12,19
hejpanekrali: L6,31
hejteto: L19
hittheroadjack: L6
hledamdevcenanedeli: L6,13,15,23
hlidackrav: L14
holubidum: L13
hvezdanavrbe: L5,6,7,15
hvezdyjsoujaksedmikraskynadbrnem: L5
icantstoplovingyou: L17
ififell: L13,42
illfollowthesun: L11,32
jachcipoezii: L16
jasnazprava: L4
jastebouzitnebudu: L4,7,8,15,38
jednohodnesevratis: L14,19,24,34
jednourano: L7,8,9,10
jestlitonebudelaska: L8,9
katce: L9,18
kdejsou: L12
kdyzjsembylchlapecmalej: L7
kloboukvekrovi: L5,9
kocourseschoulilnatvujklin: L18
kolobezka: L40
koukamjakcelazemevstava: L6
krajinaposedlatmou: L4,7
kralaklaun: L7,8,9,10
kratkypopisleta: L9,16
labamba: L6,7,8,10
lachtani: L5
laughingontheoutside: L20,35
layla: L18
letitbe: L6,13
letniukolebavka: L7,8,9,10
linda: L5,11
lizatko: L18
lonelystranger: L8,17,18
magdalena: L39
majak: L7,9,12
mamjizvunartu: L19
maschutmajoranky: L17,19
mecvrucemam: L6,12
medicinman: L30
metroprokrtky: L5,6,8
mezinarodni: L11
mikymauz: L22
mladickabasnirka: L10
mobilizace: L5,6,8
mojiprvnimuze: L8,9
montgomery: L4,5
moskevskavirtualka: L26,27
muzika: L8
nacopojdemdomov: L5
nadejeatouhy: L7,8,17
nadstademkoni: L37,44
nagasakihirosima: L6,9
namornicka: L15
namsestalonecoprekrasneho: L7
navode: L6
necoolasce: L13
nejlipjimbylo: L6,10,11,23
nekdopijelih: L13
nictolikneboli: L6,13,16
nobodyknowsyouwhenyouredownandout: L4,18,26
obladioblada: L26
ohfreedom: L5
oneofus: L9,15,16,27,28,34,35
otazky: L6,22,38,47
ourlastsummer: L8,13,17,33,50
paradaI: L6,7,13,25,26,32,34
paradaII: L6,7,13,25,26,32,34
pata: L16,36
pianoman: L19
pisenokoni: L15
pisenorose: L20
pisenzhrzenehotrampa: L18
piskajicicikan: L5
pisnickaprotebe: L4,8
podzim: L9
pohoda: L36
porekadla: L8,14,44,45
potopa: L19,22
poutnikadivka: L33
prehlidkaztracenyhocasu: L21
prejelijsmeslepici: L14,15
proklatejvuz: L7
prsi: L27
redrivervalley: L9,23,37
rekalasky: L6,28
ringoffire: L4,7,8,9,10,22,23
rockyraccoon: L26
rosanakolejich: L7
salome: L12,16
sanfranciscobayblues: L25
soske: L23,31
soudnyden: L31
spravnyslovo: L15
sroubyamatice: L15
sss: L8
stinkatedral: L32
summertime: L7,8,10
svagrmabagr: L5,6
tamunebeskychbran: L26
tearsinheaven: L31
tesinska: L5,6,8
thepassenger: L5,19
timeinabottle: L23
tocozbyvalasko: L14
tophatbarandgrill: L20
totenkratvctyricatompatom: L20
tresnicky: L6
tvojesnidane: L25
twistandshout: L49
unasnaseveru: L17
valcicek: L10
vandrovani: L8,19
vandrovni: L9
variacenarenesancnitema: L7,8
vcelkamaja: L7,9
vcera: L6
vlak: L13
vlastovkolet: L8
vodacomadrzinadvodou: L6
waterlooabba: L7,12
wearethechampions: L14,17
wewillrockyou: L33
yesterday: L6
zafukane: L8,16,17
zatimcosekoupes: L24,35
zelva: L5,6,8,20
zitraranovpet: L8
zkratky: L7
ztracenabackorka: L15
zustan: L36
```

324 lines in total.

### A3. Spacing macro placed *inside* a chord argument, e.g. `\chord{D\sm}` (a nudge, not a gap)
```
pepita: L6
```

### A4. Raw `\hspace` in songs
```
acrosstheuniverse:L9 20pt
deepriverblues:L7 20pt
dvakrat:L7 20pt
eldorado:L25 4pt
herecomesthesun:L14 9mm
herecomesthesun:L37 1cm
heyhey:L7 20pt
illbethereforyou:L8 20pt
morseovka:L14 21pt
morseovka:L27 21pt
pohadka:L10 20pt
pohadka:L44 20pt
promeny:L71 -0.5em
reddwarftheme:L8 20pt
reddwarftheme:L27 20pt
ringoffire:L22 28pt
scarboroughfaircarthy:L6 9mm
slunecnyhrob:L7 21pt
slunecnyhrob:L23 21pt
tearsinheaven:L7 20pt
tickettoride:L7 21pt
triandele:L7 20pt
variacenarenesancnitema:L16 20pt
velicenstvokat:L28 -7pt
velicenstvokat:L28 -5pt
velicenstvokat:L28 -10pt
```

`\nv` (28 pt, aligns unlabelled text under verse text) is used in 39 songs; it stays but should be renamed/defined from the label width (see plan).


## B. Vertical spacing

Totals: `\ns` 300, `\cns` 4, `\vnv` 30, `\vinv` 92, `\lsp` 59, `\newpage` 708.

### B1. Songs using custom vertical macros `\ns` `\cns` `\vnv` `\vinv` `\lsp` (`\newpage` omitted: see plan)
```
acrosstheuniverse: ns=4
alisongross: ns=4
andelska: ns=5
aztosemnusekne: ns=1
babickamary: ns=4
barbarskepobrezi: ns=1
barborapiseztabora: ns=1
batalion: vinv=2
bigbangtheorytheme: vinv=1
botyprotilasce: vnv=1
bratrickuzavirejvratka: vinv=2
buchetjespousta: ns=1
carodejnicezamesbury: ns=2
cernaostrava: ns=26
cernymuz: ns=2
cervenarekatucny: ns=1
cestadom: ns=2
coztebebude: vinv=2
dablovynamluvy: ns=1
dance: ns=8
darmodej: ns=1
digadigadospiritual: ns=1
dobreminenarada: vnv=2
donebes: ns=2
dontstopmenow: ns=6
duhovavila: vinv=3
dvakrat: ns=4
ejhorahora: ns=20
farao: ns=7
feleenazelpasa: ns=7
hajnyjelesapan: vinv=2
herecomesthesun: ns=3
hittheroadjack: vinv=1
hladiny: ns=5
hodiljsemflintudozita: vinv=2
holkyznasiskolky: ns=5
holubidum: vinv=2
idzepostaridze: ns=4 vnv=1
illbethereforyou: ns=3
jaro: vinv=3
jdoupomnejdou: ns=1
jednoubudemdal: vnv=1
jenamteplo: lsp=7 ns=3
jez: vinv=2
jinetonebude: vinv=3 vnv=1
jozinzbazin: ns=1
katce: ns=1 vinv=2
kloboukvekrovi: vnv=3
koberecek: ns=1 vinv=1
kockanaokne: vnv=1
kolobezka: vinv=3
kometa: lsp=7 ns=1
laughingontheoutside: ns=1
letosmonikou: ns=2
livingnextdoortoalice: ns=1
maleceskeblues: vinv=1
malekote: vinv=4
malujzaseobrazky: ns=11
mamdomakocku: lsp=7 ns=1
mamjizvunartu: ns=4
mammalystan: vinv=1
melanaocichbryle: ns=2
milionar: ns=12
mladickabasnirka: ns=2
morseovka: ns=4
nadejeatouhy: ns=1
nancymulligan: ns=1
natusvatukaterinu: vinv=1
nebenazemi: vnv=2
necoolasce: ns=7
nemusibejt: ns=1 vinv=2
nepijjanonepijvodu: cns=1 lsp=17
noe: ns=9
nowhereman: ns=1 vinv=3
obladioblada: ns=1
orlice: ns=1
osmichu: ns=1
ourlastsummer: ns=4
outsiderwaltz: ns=6
pata: ns=1
pennylane: ns=1
pianoman: ns=1
pochodamerickychnamorniku: vinv=3
pohadka: vinv=7
pohoda: vinv=3
porekadla: ns=2
potopa: ns=3
povestehovejs: ns=3
prazce: ns=3
prejelijsmeslepici: vnv=4
prodavac: ns=2
ridictentvrdejchlebama: ns=2
salome: vinv=2
satydelajcloveka: vnv=2
scarboroughfaircarthy: ns=1
skrhola: vinv=3
skupinovefoto: ns=7
slunecnyhrob: ns=3
slunicko: vnv=3
soudnyden: ns=1
spimvobili: vnv=1
sprostyadmindusan: ns=1
summernights: cns=3 ns=12
svatekmazofie: ns=3
swingmodrezdi: vinv=4
tasidele: ns=3
tearsinheaven: ns=3
tesar: lsp=16 ns=1
thetimestheyareachangin: ns=1
tiamo: ns=1
tophatbarandgrill: ns=4
totenkratvctyricatompatom: vinv=2
totenkratvsedesatomosmom: vinv=1
tramvajacka: vinv=3
tresnicky: ns=1
trhvescarborough: ns=1
trikrize: ns=1
trpaslicisvatba: vinv=2
vadinevadi: vnv=2
vcelkamaja: vnv=1
velrybarskavyprava: vinv=5
vienna: ns=5
vjednymdumku: vinv=4
vlese: vinv=3
vodauzjesvarena: vinv=3
vranabuty: vinv=1
vreledikyzpupku: ns=1
walkingbacktohappiness: ns=1
www.idnes: ns=2
zapomenutytrumf: ns=4
zivotjejennahoda: vnv=4
zizniva: vnv=1
zlatestrevicky: vinv=3
zpatkydotrenek: lsp=5 ns=2
zumzumII: ns=11
```

### B2. Raw `\vspace` in songs (each must be justified or deleted after the block spacing is fixed)
```
acrosstheuniverse: L8 -45pt; L13 -10pt
allyouneedislove: L5 5mm; L30 5mm; L32 5mm
aztosemnusekne: L5 -3mm
azvzletnouptaci: L26 3mm
babickamary: L3 -9mm
barbarskepobrezi: L4 -10pt
barborapiseztabora: L41 10pt; L44 -10pt
bellaciao: L36 100pt
carodejnicezamesbury: L10 -10pt
cernymuz: L50 5mm
dance: L23 -18pt; L38 -18pt
darmodej: L19 -6mm; L52 -4mm
deepriverblues: L6 -55pt; L10 -35pt
digadigadoplihal: L5 15pt
dobrodruzstvisbohempanem: L6 15pt
dvakrat: L6 -25pt; L54 -4mm; L60 -4mm
eldorado: L24 10pt
elektrickyvalcik: L17 15pt; L33 15pt
greensleeves: L6 3mm
haubilouplani: L30 5mm
herecomesthesun: L7 10mm; L13 -10mm; L17 7mm; L23 -5mm; L25 5mm; L32 -5mm; L34 5mm; L39 5mm; L41 5mm; L48 5mm; L53 -5mm; L55 5mm; L61 5mm
heyhey: L6 -58pt
hodiljsemflintudozita: L28 10pt
hvezdyjsoujaksedmikraskynadbrnem: L6 15pt; L10 15pt; L14 15pt
idzepostaridze: L11 5mm
illbethereforyou: L7 -25pt; L11 -35pt
jaktosnamalaskobude: L6 5mm
jdoupomnejdou: L46 -4mm
jednourano: L4 20pt
jestemichvilkuzpivej: L17 5mm
ladovskazima: L4 15pt; L18 5mm; L22 2mm; L26 2mm; L30 2mm; L34 5mm; L39 2mm; L43 2mm; L49 2mm
lasko: L33 15pt
lizatko: L6 20pt; L10 20pt; L14 20pt
malekote: L24 5mm
malujzaseobrazky: L4 -5pt
mamdomakocku: L22 5pt; L68 5pt
marieklus: L4 10mm
mikymauz: L5 -8pt; L11 -8pt; L17 -8pt; L24 -8pt; L30 -8pt; L36 -8pt; L43 -8pt; L49 -8pt; L55 -8pt; L62 -8pt; L68 -8pt; L74 -8pt; L81 -8pt
milionar: L116 -10mm
morseovka: L13 -30pt; L17 -30pt; L26 -30pt; L29 -20pt
motyl: L8 5mm; L14 5mm
nebenazemi: L4 10pt
noe: L75 5mm
paneprezidente: L38 5mm
pianoman: L5 -30pt
pisenokoni: L18 20pt
podzimniplihal: L35 20pt
pohadka: L5 10pt; L9 -25pt; L14 10pt; L37 -15pt; L43 0pt
prejelijsmeslepici: L17 5mm; L20 5mm
promeny: L41 2cm
pterodaktylus: L11 15pt; L20 15pt; L29 15pt; L38 15pt
reddwarftheme: L7 -25pt; L16 20pt; L26 -25pt
redrivervalley: L39 15pt
ringoffire: L20 -15pt
romance16leta: L6 5mm
slunecnyhrob: L6 -30pt; L22 -30pt; L55 2mm
snebyvalouochotou: L5 20pt
svazceskychbohemu: L5 8mm
tearsinheaven: L6 -45pt
tickettoride: L6 -30pt; L10 -10pt
touha: L15 10pt; L18 -10 pt
triandele: L6 -53pt
variacenarenesancnitema: L12 25pt; L15 -52pt
vcelkamaja: L5 10mm
vodavodenka: L35 175pt
vosa: L33 20pt
```

133 raw `\vspace` uses in total.


## C. Artists

48 artist anchors used by 550 songs; **183 songs have no `\interpret`**.

### C1. Anchors that are not the slug of their name -> proposed rename (slug = name as listed in the index, lowercase ASCII, no spaces, no leading article)
```
klus                   -> tomasklus              (4 songs; name 'Tomáš Klus'; index shows 'Klus')
kryl                   -> karelkryl              (8 songs; name 'Karel Kryl'; index shows 'Kryl')
kubisova               -> martakubisova          (6 songs; name 'Marta Kubišová'; index shows 'Kubišová')
lenk                   -> jaroslavsamsonlenk     (11 songs; name 'Jaroslav Samson Lenk'; index shows 'Lenk')
nohavica               -> jaromirnohavica        (48 songs; name 'Jaromír Nohavica'; index shows 'Nohavica')
plihal                 -> karelplihal            (42 songs; name 'Karel Plíhal'; index shows 'Plíhal')
redl                   -> vlastaredl             (8 songs; name 'Vlasta Redl'; index shows 'Redl')
rottrova               -> marierottrova          (1 songs; name 'Marie Rottrová'; index shows 'Rottrová')
spinarova              -> veraspinarova          (3 songs; name 'Věra Špinarová'; index shows 'Špinarová')
trikyapovery           -> (keep, but DECIDE) two different artists share it: 'Triky a pověry' x4 (index name) and 'Ricchi e Poveri' x4 (Italian originals: felicita, litaliano, saraperchetiamo, tiamo) -> probably two registry entries - yes, each should get its own entry, Ricchi e Poveri are the Italian originals, Triky a pověry are the Czech covers
zalman                 -> zalmanspol             (3 songs; name 'Žalman \& spol.'; index shows 'Žalman')
zich                   -> karelzich              (9 songs; name 'Karel Zich'; index shows 'Zich')
```

### C2. Same anchor, different display names (decide canonical name; per-song override only where intentional)
```
beatles: 'The Beatles' x21  e.g. acrosstheuniverse, allmyloving, allyouneedislove, blackbird - correct
beatles: 'Beatles' x1  e.g. acrosstheuniverse, allmyloving, allyouneedislove, blackbird - wrong
kubisova: 'Marta Kubišová' x5  e.g. depese, dobrodruzstvisbohempanem, nechtezvonyznit, reknikdetykytkyjsou - correct
kubisova: 'Marie Kubišová' x1  e.g. casysemeni - wrong
lenk: 'Jaroslav Samson Lenk' x9  e.g. katce, kdovicobudepak, nictolikneboli, pohoda - correct
lenk: 'J. S. Lenk' x2  e.g. lacinyvino, mojiprvnimuze - wrong
michaltucny: 'Michal Tučný' x21  e.g. abychtuzil, bajecnazenska, botyzkuzetoulavejchpsu, cervenarekatucny - becomes "Michal Tučný & Greenhorns"
michaltucny: 'Greenhorns' x5  e.g. bluesfolsomskeveznice, caseyjones, jajedudal, navanocerano - becomes "Michal Tučný & Greenhorns"
nohavica: 'Jaromír Nohavica' x46  e.g. aztosemnusekne, cernaostrava, darmodej, dezo - correct
nohavica: 'Jaromír Nohvica' x1  e.g. mamjizvunartu - wrong
nohavica: 'Nohavica' x1  e.g. aztosemnusekne, cernaostrava, darmodej, dezo - wrong
plihal: 'Karel Plíhal' x41  e.g. basniktenmapravoveta, brejden, cernadira, digadigadoplihal - correct
plihal: 'Plíhal' x1  e.g. basniktenmapravoveta, brejden, cernadira, digadigadoplihal - wrong
trikyapovery: 'Ricchi e Poveri' x4  e.g. felicita, litaliano, saraperchetiamo, tiamo - see C1
trikyapovery: 'Triky a pověry' x4  e.g. hejholazpivejsisam, italneznatenzazrak, odecita, tyjamo - see C1
```

### C3. Songs with two artists (`\interpretdva`) - the registry/template must support two
```
mikymauz:L2 plihal
mojiprvnimuze:L2 lenk
```
Yes, some songs can have two artists. These listed here are correctly attributed to both authors.

### C4. Artist sections currently below 3 songs (kept, as agreed) - yes, keep the sections
```
nezmari: 1 (mamutikrik)
rottrova: 1 (rekalasky)
bobdylan: 1 (thetimestheyareachangin)
johnnycash: 2 (folsomprisonblues, ringoffire)
raycharles: 2 (hittheroadjack, icantstoplovingyou)
mnagaazdorp: 2 (nejlipjimbylo, pisnickaprotebe)
billyjoel: 2 (pianoman, vienna)
```

### C5. Artist index in `obsah.tex` vs `\interpret` tags in the songs (this is the duplication the registry removes)

49 names in the index block, 49 artist sections, 48 anchors used by songs.

Index/sections/songs that disagree:
```
section but no song has \interpret for it: filmy (48 songs listed)
kryl: song has \interpret but is missing in obsah section: bratrickuzavirejvratka - add to obsah section
olympic: listed in obsah but song lacks \interpret: bonsoirmademoiselleparis, hvezdanavrbe - add author to songs
plihal: song has \interpret but is missing in obsah section: mikymauz - add to obsah, song has two authors
redl: listed in obsah but song lacks \interpret: huslicky, sbohemgalanecko - add author to songs
spiritualkvintet: listed in obsah but song lacks \interpret: dvebaby, sirokyhluboky - add author to songs
```

### C6. Songs whose `\song{}` title contains a `\footnote` - we can move the footnote somewhere else, but it's a footnote about the whole song so bear that in mind
```
bellaciao, conselho, johnnybgoode, pasopanori, tasidele, thepassenger
```

## D. `obsah.tex` vs song files (to be generated)

Letter sections: 793 entries for 732 songs; songs missing from letter sections: 1: `nadstademkoni` (Buty) has no alphabetical entry; the entry 'Nad stádem koní' (obsah.tex:826) points to `nadejeatouhy` (Redl), so two different songs share that title; 28 italic alternative titles (-> `\alttitle{}` in the song file); 35 songs whose plain obsah title differs from `\song{}`.

### D1. Italic alternative titles -> move into song files
```
anickadusickanekasli: \emph{Kdo si tu pěsničku zazpívá?
azvzletnouptaci: \emph{Na předměstí stával dům
dobreminenarada: \emph{Běž domů, Ivane!
zabilizabili: \emph{Bylo tu, není tu
carminaamorosa: \textit{More festi querimus
kedsomisiel: \emph{Čerešně
proklatejvuz: \textit{Čtyři bytelný kola
jednohodnesevratis: \emph{Den se v růži skryl
jednohodnesevratis: \emph{Tenkrát na Západě
jednourano: \textit{Dlaždič
dobrouzpravuhlasej: \textit{Mou dobrou zprávu hlásej
maleceskeblues: \textit{Doprdelepráce
drunkensailor: \emph{What Shall We Do with a Drunken Sailor
illbethereforyou: \textit{Friends Theme
hohowatanay: \emph{Indiánská ukolébavka
honkytonkyblues: \emph{Každý ráno na piáno
idzepostaridze: \emph{O poštaris avel
jedesohajzvidna: \emph{Teče voda, teče, ryby po ní skáčú
jednoumifotrpovida: \textit{Rock'n'roll for you
kovbojuvnarek: \emph{V Laredu tenkrát
zvednetekotvy: \emph{Loď John B.
vitrtovi: \textit{Míle
starypribeh: \textit{Mojžíš
veronika: \emph{Ó, Vero Veroniko
vodavodenka: \emph{Petře, Petříčku
vosa: \emph{Plavala vosa v kofole
rezrezrez: \emph{Po potoce chodila
zapomnetliva: \emph{Takovej ten s takovou tou
```
### D2. Plain obsah title differs from `\song{}` (typo on one side, or a disambiguation such as '(Hegerová)'; decide per row)
```
alwayslookonthebrightsideoflife: obsah=['Always Look on the Brigh Side of Life'] | song='Always Look on the Bright Side of Life' - song
autobusyprijizdeji: obsah=['Autobusy přijíždějí'] | song='Autobusy přijížději' - toc
cestanaisland: obsah=['Cesta na Island'] | song='Cesta na island' - toc
ceresne: obsah=['Čerešně (Hegerová)'] | song='Čerešně' - keep
cernaostrava: obsah=['Černá, Ostrava'] | song='Černá Ostrava' - song
cervenarekatucny: obsah=['Červená řeka (Michal Tučný)'] | song='Červená řeka' - keep
digadigadoplihal: obsah=['Diga diga do (Plíhal)'] | song='Diga diga do' - keep
digadigadospiritual: obsah=['Diga diga do (Spirituál kvintet)'] | song='Diga diga do' - keep
maleceskeblues: obsah=['Malé české blues aneb Doprdelepráce'] | song='Malé české blues' - song
escesomsaneozenil: obsah=['Eščě som sa neoženil'] | song='Eště som sa neoženil' - toc
felicita: obsah=['Felicit\\`{a'] | song='Felicit\`{a}' - song
oldtimereligion: obsah=["Gimme Dat Ol' Time Religion", 'Old Time Religion'] | song='Old Time Religion' - song
hejpanekrali: obsah=['Hej, pane králi!'] | song='Hej, pane králi' - toc
hittheroadjack: obsah=['Hit The Road Jack'] | song='Hit the Road Jack' - song
jenamteplo: obsah=['Je nám teplo'] | song='Je nám teplo!' - song
kdejsou: obsah=['Kde jsou?'] | song='Kde jsou' - toc
marieklus: obsah=['Marie (Klus)'] | song='Marie' - keep
marienavarova: obsah=['Marie (Navarová)'] | song='Marie' - keep
mlyny: obsah=['Mlýny (Mlýnský kámen)'] | song='Mlýny' - song
nadejeatouhy: obsah=['Naděje a touhy', 'Nad stádem koní'] | song='Naděje a touhy' - song
nomoreauctionblockforme: obsah=['No More Auction Block For Me'] | song='No More Auction Block For me' - toc
outsiderwaltz: obsah=['Outsider Waltz'] | song='Outsider waltz' - song
podzimniplihal: obsah=['Podzimní (Karel Plíhal)'] | song='Podzimní' - keep
podzimnispiritual: obsah=['Podzimní (Spirituál kvintet)'] | song='Podzimní' - keep
saraperchetiamo: obsah=['Sarà perché ti amo'] | song='Sar\`{a} perché ti amo' - toc
scarboroughfaircarthy: obsah=['Scarborough Fair (Martin Carthy)'] | song='Scarborough Fair' - keep
summernights: obsah=['Summer Night'] | song='Summer Nights' - song
slapejdalspiritual: obsah=['Šlapej dál (Spirituál kvintet)'] | song='Šlapej dál' - keep
slapejdaltucny: obsah=['Šlapej dál (Michal Tučný)'] | song='Šlapej dál' - keep
timeinabottle: obsah=['Time In a Bottle'] | song='Time in a Bottle' - toc
vranabuty: obsah=['Vrána (Buty)'] | song='Vrána' - keep
vranaplihal: obsah=['Vrána (Plíhal)'] | song='Vrána' - keep
waterlooabba: obsah=['Waterloo (ABBA)'] | song='Waterloo' - keep
waterlootucny: obsah=['Waterloo (Michal Tučný)'] | song='Waterloo' - keep
whenthesaintsgomarchingin: obsah=['When the Saints Go Marching In'] | song='When the saints go marching in' = toc
```

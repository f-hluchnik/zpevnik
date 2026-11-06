# C3 · Migration batches

Written by C3a (session 10a, 4 Nov 2026), regenerated the same night for the parallel run. The songs C3b migrates to the automatic chord spacing, alphabetically (D-123).

## Why 449 and not 733

The other 284 songs need nothing: no manual spacing to remove, no chord list to convert, and their page does not change with the spacing on. They get `\autochords` for free in C4.

## How the list was made

1. `tools/strip_chord_spacing.py` was run on every song as a dry run. A song is listed when it would change (spacing, textbf chords, chord lines) or when its page changes with the spacing on for everyone (scratch build, compared with `tools/pdfdiff.py`).
2. Songs the owner must decide on went to **batch 11**; the other 434 form batches 1–10 (43–44 songs each, 38 in the last).
3. Each batch 1–10 has its own branch `refactor/c3b-batch-N` from master and its own PR; none is merged. Per batch, the local build (TeX Live 2023): 757 pages, `check_pages` 0 problems, `chord_gaps` 0 errors, `lint` 0 errors, `pdfdiff` changed songs = exactly the batch songs. CI of the PRs: see the PR checks.
4. The batch PDF `C3-batches/batch-NN.pdf` holds only the pages of its songs, **alternating: odd pages = master, even pages = the batch** (batch 11 and 12 too).

Chord lists with a line break are now `\chords` rows, one per line (tool change in PR #44; the batches were generated with it).

## Batches

| Batch | Songs | From | To | PR | PDF |
|---|---|---|---|---|---|
| 1 | 44 | `ahorsewithnoname` | `chattanoogachoochoo` | #47 | `C3-batches/batch-01.pdf` |
| 2 | 44 | `chcibytpritom` | `frankiedlouhan` | #48 | `C3-batches/batch-02.pdf` |
| 3 | 44 | `frantisek` | `jastebouzitnebudu` | #49 | `C3-batches/batch-03.pdf` |
| 4 | 43 | `jdemzpatkydolesu` | `letniromance` | #50 | `C3-batches/batch-04.pdf` |
| 5 | 43 | `letniukolebavka` | `nadejeatouhy` | #51 | `C3-batches/batch-05.pdf` |
| 6 | 44 | `nadejilaskouavirou` | `pisenzhrzenehotrampa` | #52 | `C3-batches/batch-06.pdf` |
| 7 | 44 | `piskajicicikan` | `satydelajcloveka` | #53 | `C3-batches/batch-07.pdf` |
| 8 | 44 | `sbohemgalanecko` | `tetkajulka` | #54 | `C3-batches/batch-08.pdf` |
| 9 | 44 | `thepassenger` | `virginie` | #55 | `C3-batches/batch-09.pdf` |
| 10 | 38 | `vitrtovi` | `zvednetekotvy` | #56 | `C3-batches/batch-10.pdf` |
| 11 | 15 | `azvzletnouptaci` | `vranabuty` | #58 (needs #57) | `C3-batches/batch-11.pdf` |
| 12 | 2 | `jenamteplo` | `malujzaseobrazky` | #60 (stacked on #59) | `C3-batches/batch-12.pdf` |

Batches 1–10 are reviewed and merged independently, in any order: they touch different files. Merging one makes the other PRs' base older, which the CI diff handles (it compares each PR with its own base).

## Batch 11 and 12: the songs that needed the owner's decision (decided 4–5 Nov; see DECISIONS)

Fix all the glued chords, for the songs that now take two pages I will need a graphic representation to make a decision.
| Song | Why |
|---|---|
| `azvzletnouptaci` | glued chords in a `\textbf` list (4 places): TeX swallows the space after a control word, so `Dm Dm\maj Dm\7` prints "Dm△Dm7" on master. Fixing it inserts `{}` and changes the printed chords. |
| `blackbird` | glued chords in a `\textbf` list (2 places): TeX swallows the space after a control word, so `Dm Dm\maj Dm\7` prints "Dm△Dm7" on master. Fixing it inserts `{}` and changes the printed chords. |
| `conselho` | CHECK pause (entregar|a): one word or two? | - two words
| `imagine` | glued chords in a `\textbf` list (1 place): TeX swallows the space after a control word, so `Dm Dm\maj Dm\7` prints "Dm△Dm7" on master. Fixing it inserts `{}` and changes the printed chords. |
| `jasetesimdonebe` | CHECK pause (le|luja): one word or two? | - one word
| `jenamteplo` | with `\autochords` the song takes a second page; the owner decides how to shorten it (smaller text, shorter line, cut a gap) |
| `kluziste` | glued chords in a `\textbf` list (4 places): TeX swallows the space after a control word, so `Dm Dm\maj Dm\7` prints "Dm△Dm7" on master. Fixing it inserts `{}` and changes the printed chords. |
| `malujzaseobrazky` | with `\autochords` the song takes a second page; the owner decides how to shorten it (smaller text, shorter line, cut a gap) |
| `nekdopijelih` | glued chords in a `\textbf` list (1 place): TeX swallows the space after a control word, so `Dm Dm\maj Dm\7` prints "Dm△Dm7" on master. Fixing it inserts `{}` and changes the printed chords. |
| `nemusibejt` | glued chords in a `\textbf` list (1 place): TeX swallows the space after a control word, so `Dm Dm\maj Dm\7` prints "Dm△Dm7" on master. Fixing it inserts `{}` and changes the printed chords. |
| `pisenokoni` | glued chords in a `\textbf` list (2 places): TeX swallows the space after a control word, so `Dm Dm\maj Dm\7` prints "Dm△Dm7" on master. Fixing it inserts `{}` and changes the printed chords. |
| `prosimteholka` | glued chords in a `\textbf` list (2 places): TeX swallows the space after a control word, so `Dm Dm\maj Dm\7` prints "Dm△Dm7" on master. Fixing it inserts `{}` and changes the printed chords. |
| `rosanakolejich` | line 16 edited by H5 (PR #45); migrate after it merges |
| `timeinabottle` | glued chords in a `\textbf` list (1 place): TeX swallows the space after a control word, so `Dm Dm\maj Dm\7` prints "Dm△Dm7" on master. Fixing it inserts `{}` and changes the printed chords. |
| `tvojesnidane` | glued chords in a `\textbf` list (1 place): TeX swallows the space after a control word, so `Dm Dm\maj Dm\7` prints "Dm△Dm7" on master. Fixing it inserts `{}` and changes the printed chords. |
| `uznechcisevdat` | glued chords in a `\textbf` list (1 place): TeX swallows the space after a control word, so `Dm Dm\maj Dm\7` prints "Dm△Dm7" on master. Fixing it inserts `{}` and changes the printed chords. |
| `vranabuty` | glued chords in a `\textbf` list (2 places): TeX swallows the space after a control word, so `Dm Dm\maj Dm\7` prints "Dm△Dm7" on master. Fixing it inserts `{}` and changes the printed chords. |

What I need per song: for glued chords, `glue` (keep the printed glue) or `fix` (insert `{}`); for the two pauses, `one word` or `two words`; for the two overflows, how to fit the page. Then batch 11 is generated like the others.

## Batch song lists

### Batch 1 (PR #47)

```
ahorsewithnoname aintnograve ajatakadzivocka alberta alisongross allihavetodoisdream allmyloving allyouneedislove alwayslookonthebrightsideoflife amazonka andel andelska anickadusickanekasli apak auldlangsyne autobusyprijizdeji autumnleaves aznamprijdoumirubrat azseknampravovrati babickamary barborapiseztabora basniktenmapravoveta batalion bigbangtheorytheme bluesnacestuposledni bonsoirmademoiselleparis bratrickuzavirejvratka breclavskakasarna brnojezlatalod buchetjespousta bytstalemlad casysemeni ceresne ceresnicky cernadira cernaostrava cernejpasazer cerneocijdetespat cervenareka cervenarekatucny ceskapisnicka chajdamala changetheworld chattanoogachoochoo
```

### Batch 2 (PR #48)

```
chcibytpritom chirpychirpycheepcheep cizesutokone cmelak dajana daltouvodou dameklukoviskoly dance dancingqueen darmodej davidagolias dejmivicsvelasky delani depese dezo digadigadoo digadigadoplihal digadigadospiritual dobreminenarada dobrouzpravuhlasej dokudsezpiva donebes dontstopmenow dorajenevedemost drakodbileskaly dreamalittledreamofme duhovavila dumuvychazejicihoslunce dvahavrani dvakrat eduvzalikfotografovi ejbozemuj ejhorahora ejtahuckahospoda eldorado elektrickyvalcik escesijapoharvinazaplatim fallingslowly farao fiveshortminutes flymetothemoon fornoone fotky frankiedlouhan
```

### Batch 3 (PR #49)

```
frantisek frydekmistek gilotina girl goodriddance greensleeves gronskapisnicka guadalcanal hadejkdomipise hajnyjelesapan harmonikarska haubilouplani hejnovran hejpanekrali hejteto herecomesthesun hittheroadjack hladiny hledamdevcenanedeli hlidackrav hlupakunajdute hodiljsemflintudozita hojahoj holkyznasiskolky holubidum hornicka houseoftherisingsun hudsonskysify huslicky hvezdanavrbe hvezdyjsoujaksedmikraskynadbrnem icantstoplovingyou idzepostaridze ififell illbethereforyou illfollowthesun inthesummertime ionlywanttobewithyou isielmacekdomalacek islamarina jachcipoezii jaktosnamalaskobude jasnazprava jastebouzitnebudu
```

### Batch 4 (PR #50)

```
jdemzpatkydolesu jdoupomnejdou jedesohajzvidna jednohodnesevratis jednoubudemdal jednourano jestemichvilkuzpivej jestlitonebudelaska jez jinetonebude jozinzbazin karavanamraku katce kdejsou kdonaplninebe kdovicobudepak kdybybylamorava kdybychbylavlastovkou kdyzjsembylchlapecmalej kdyzmebralizavojaka kdyznapavoukasedneblues kdyzsezamilujekun klada kloboukvekrovi kockanaokne kocourseschoulilnatvujklin kolobezka koukamjakcelazemevstava krajinaposedlatmou kralaklaun kratkypopisleta krutavalka labamba lachtani lacinyvino ladycarneval laughingontheoutside layallyourloveonme layla leavingonajetplane letadozravani letitbe letniromance
```

### Batch 5 (PR #51)

```
letniukolebavka letochovahospudecka linda litaliano lizatko lochlomond loddeti lojzaaliza lonelystranger magdalena majak malekote mamjizvunartu mammalystan mammamia marieklus marnivasestrenice maschutmajoranky masirujunafrancuza mecvrucemam medicinman medvedinevedi metroprokrtky mezihorami mezinarodni mikymauz milencivtexaskach mladickabasnirka mlyny mnisijsoutisi mobilizace mojiprvnimuze montgomery morseovka moskevskavirtualka mosty motyl mravenciukolebavka mravencivkredenci muzika mys nacopojdemdomov nadejeatouhy
```

### Batch 6 (PR #52)

```
nadejilaskouavirou nadstademkoni nagasakihirosima nahorachstudenky nahoteluvolomouci namornicka namsestalonecoprekrasneho nancymulligan navode nebenazemi nechtezvonyznit necoolasce nejdelsivlak nejlipjimbylo neninutno nepijjanonepijvodu nevadi nictolikneboli nobodyknowsyouwhenyouredownandout noe nomoreauctionblockforme norwegianwood obladioblada ohfreedom oldtimereligion olivertwist olomouc oneofus orlice otazky ourlastsummer padalyhvezdy paneprezidente panubohudooken paradaI paradaII parhavranichcopanku pata pepita perinamastyryrozky pianoman pisencomeucillistopad pisenorose pisenzhrzenehotrampa
```

### Batch 7 (PR #53)

```
piskajicicikan pisnickaprotebe pocestny pochodmarodu poddubemzadubem podzim podzimnispiritual pohoda pojdmespat porekadla potopa potrikratsomnaokenkotukal poutnikadivka povestehovejs povidej prachovskeskaly prahaprcice prehlidkaztracenyhocasu prejelijsmeslepici pridijanoknam priznavam proklatejvuz prolabute promeny prsi pulnocni radasemiluje radsebrouzdamrosou ranavtrave reddwarftheme redrivervalley rekalasky reklamanaticho reknikdetykytkyjsou ridictentvrdejchlebama ringoffire rockyraccoon rubikovakostka ruzicka ryljencelejdenryl salome samsnohaminastole sanfranciscobayblues satydelajcloveka
```

### Batch 8 (PR #54)

```
sbohemgalanecko scarboroughfair scarboroughfaircarthy senzaunperche sirokyhluboky siryproud sklenickotysklenena skodalasky skupinovefoto slapejdalspiritual slavicizmadridu slunecnyhrob slunicko snebyvalouochotou soske soudnyden spanembohemidemodvas spimvobili spravnyslovo sprostyadmindusan sroubyamatice sss starypribeh stinkatedral summernights summertime svagrmabagr svatebnikosile svatekmazofie svatoborskesirepole takabystetovedela takbytjednoubouri takdavnojiz takjenpojd takjsmevandrovali takuzmimaholkamava tamunebeskychbran tasidele tata tearsinheaven tecevodatece tenkdoneduma tesinska tetkajulka
```

### Batch 9 (PR #55)

```
thepassenger thewateriswide tiamo tickettoride tocozbyvalasko tophatbarandgrill totahelpa totenkratvctyricatompatom touha tresnezraly tresnicky trezor trhvescarborough tribratri tricitronky tricunici trochuvhlavemam trpaslicisvatba trubadurska twistandshout ukolebavkaprokubualenku unasnaseveru uzsenamcaskrati uztypilkydorezaly valcicek valkaruzi vandrovani vandrovni variacenarenesancnitema vbufetu vcelkamaja vcera vdobrymizlym vecernicek vedmedalcestoma velicenstvokat velkyvuz veronika veskrini vienna vila vineckobile vinnetou virginie
```

### Batch 10 (PR #56)

```
vitrtovi vlak vlastovkolet vlese vodacomadrzinadvodou vodavodenka vor vosa vranaplihal vsinidolinecka vyletelaholubicka vysokyjalovec wadeinthewater walkingbacktohappiness waterlooabba wearethechampions wewillrockyou whenthesaintsgomarchingin workinatthecarwashblues yesterday zafukane zasvoupravdoustat zatimcosekoupes zavolejtestraze zelenefrancouzskeplane zeleneplane zelva zelviblues zitraranovpet zivotjejennahoda zizen zkratky zlataklec zpivatatajan ztracenabackorka zumzumII zustan zvednetekotvy
```

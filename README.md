# O zpěvníku
Tento zpěvník se jmenuje "Ještě mi chvilku zpívej" a obsahuje různé písničky podle vůle mé a postupem času i dalších lidí, kteří z něj zpívali.

## Filosofie zpěvníku
Filosofie tohoto zpěvníku je taková, že by se z něj mělo dobře zpívat a hrát. To znamená několik principů, které se během tvorby snažím dodržovat.

1. Každá písnička na jednu stránku.
    - Raději písničku trochu namačkat na jednu stranu než ji roztahovat na dvě strany, protože se pak při hraní musí stránky posouvat nebo otáčet. Zatím se mi dařilo tento princip dodržovat, avšak mohou nastat situace, kdy bude nevyhnutelně nutné zapsat písničku na dvě strany. V takovém případě je potřeba zajistit, aby nebylo potřeba v průběhu hraní otáčet na předchozí stranu. To znamená například znovu zapsat akordy ve sloce a znovu přepsat refrain.

2. Akordy sedí.
    - Při přepisování písničky dbám na to, aby akordy seděly a dalo se podle nich spolehlivě hrát. Tedy určitě písničku vyzkouším zahrát a zkontroluji, zda jsou akordy správné a na správných místech.
    - Volím tóninu, ve které se písnička dobře zpívá, nebo originální tóninu. Je jasné, že tento parametr se může měnit s postupem času či vypitého alkoholu. Tónina pravděpodobně nikdy nebude ve všech případech ideální. Mělo by se v ní ale dobře zpívat při přepisování písničky.
    
3. Hraní > zpívání > vzhled.
    - Písnička musí být zapsaná tak, aby se hlavně dobře hrála. Na druhém místě se musí dobře zpívat, na třetím místě je vzhled. Tyto tři charakteristiky spolu samozřejmě úzce souvisí. V tomto bodě mám ale na mysli hlavně případy, kdy je například potřeba zvolit nestandardní odsazení či zalomení, a to z důvodu, aby hraní písničky bylo přirozené a hladké. Toto je samozřejmě velmi subjektivní.

## Nastavení lokální kopie
Zpěvník (celý i jednotlivá vydání) se dá sestavit na vlastním počítači. Postup platí pro macOS a Linux, příkazy jsou pro Homebrew a apt. Hotovo je, když projde `make check`.

1. Stáhnu repozitář:
   ```
   git clone git@github.com:f-hluchnik/zpevnik.git
   cd zpevnik
   ```
2. Python 3.11 nebo novější. Nástroje v `tools/` potřebují `tomllib`, který je ve standardní knihovně od verze 3.11; na starší verzi skončí `make` chybou `No module named 'tomllib'`. Jiné balíčky se neinstalují, nástroje používají jen standardní knihovnu. Na macOS stačí `brew install python`, na Linuxu balík `python3` v dost nové verzi. Aby `make` nespouštěl starší Python, který je v systému dřív v `PATH`, vytvořím si virtuální prostředí (složka `.venv` se necommituje) a aktivuji ho:
   ```
   python3.12 -m venv .venv      # příkaz Pythonu 3.11 nebo novějšího
   source .venv/bin/activate
   python3 --version             # musí být 3.11 nebo novější
   ```
   Aktivaci (`source .venv/bin/activate`) opakuji v každém novém terminálu, ve kterém spouštím `make`. `make` si verzi Pythonu zkontroluje a u starší skončí srozumitelnou chybou; jiný Python mu mohu zadat i napřímo: `make PYTHON=python3.12`.
3. TeX Live s češtinou, `latexmk` a několik balíků (`csquotes`, `dashrule`, `eso-pic`, `pgf`, `geometry`, `xcolor`, `hyperref`, `cm-super`, `musixtex-fonts` pro křížky a béčka v akordech). GitHub Actions kompiluje s TeX Live 2023; novější verze funguje také, výsledek se jen může mírně lišit, rozhodující je vždy GitHub Actions.
   - **Linux (Debian, Ubuntu):** `sudo apt-get install texlive-lang-czechslovak texlive-latex-extra texlive-fonts-extra texlive-music latexmk poppler-utils`. `poppler-utils` je na kontrolu stran a porovnání PDF (`tools/check_pages.py`, `tools/pdfdiff.py`).
   - **macOS:** buď celý MacTeX (`brew install --cask mactex-no-gui`), nebo menší BasicTeX (`brew install --cask basictex`) a po něm `sudo tlmgr update --self` a `sudo tlmgr install collection-langczechslovak babel-czech hyphen-czech csquotes dashrule eso-pic pgf geometry xcolor hyperref cm-super musixtex-fonts latexmk`.
4. Noty se exportují z MuseScoru (viz [Noty](#noty)), takže `make` potřebuje ještě tři věci:
   - **MuseScore 4.6.5.** Stejnou verzi používá GitHub Actions; jiná verze může změnit rozvržení not, a tím i to, jestli se písnička vejde na jednu stranu. Stáhnu ji ze [stránky vydání 4.6.5](https://github.com/musescore/MuseScore/releases/tag/v4.6.5). Na macOS nainstalovanou aplikaci v `/Applications` najde `make` sám; leží-li jinde nebo je nainstalováno víc verzí, dám cestu k programu `mscore` do proměnné `MSCORE`, například `export MSCORE="/Applications/MuseScore 4.app/Contents/MacOS/mscore"`. Na Linuxu je to AppImage (cestu k němu dám do `MSCORE`; na stroji bez displeje se spouští přes `xvfb-run`).
   - **`rsvg-convert`** (převod SVG na PDF): `brew install librsvg` nebo `sudo apt-get install librsvg2-bin`.
   - **Písmo CMU Serif** (všechny texty v notách): `brew install --cask font-computer-modern` nebo `sudo apt-get install fonts-cmu`. Zkontroluji `fc-list | grep "CMU Serif"`; bez písma MuseScore tiše použije jiné a obrázky not se budou lišit od zpěvníku.
5. Ověřím, že všechno funguje: `make check`. Poprvé to trvá déle, protože se exportují všechny noty. Každý krok má nadpis (`==> Unit tests`, `==> Lint`, …) a úspěšný běh končí řádkem `==> All checks passed. The PDF:` s úplnou cestou k hotovému PDF.

Nejčastější chyby:
- `the tools need Python 3.11 or newer` (nebo při přímém spuštění nástroje `No module named 'tomllib'`): Python je starší než 3.11, nebo není aktivní `.venv`.
- `MuseScore 4 not found`: MuseScore je jinde, než ho `make` hledá; nastavím `MSCORE`.
- `rsvg-convert not found`: nainstaluji `librsvg` (krok 4).

## Nová písnička
Písnička je jediný soubor ve složce `songs`. Seznam písniček, obsah (podle písmen i podle interpretů) a verzi zpěvníku generuje `make`, takže `zpevnik.tex` ani `shared-pages/contents.tex` ručně neupravuji. Písnička se sama zařadí podle názvu v `\song{}`, do obsahu podle písmen i do sekce svého interpreta.

1. Ve složce `songs` vytvořím soubor s názvem podle názvu písničky. Název souboru se tvoří odebráním diakritiky a mezer z názvu písničky a zapsáním tohoto názvu malými písmeny. Je-li potřeba odlišit dvě písničky se stejným názvem od různých interpretů, učiní se tak přidáním jména interpreta (pokud možno jednoslovně, tedy příjmení nebo název skupiny) za jméno písničky, opět bez mezer a diakritiky, malými písmeny. Název souboru bez `.tex` je `id` písničky. Je možné použít šablonu `song-template.tex` v kořenovém adresáři zpěvníku.
2. Na řádek s příkazem `\song{}` doplním `\artist{<kotva>}`. Pokud interpret ještě v registru není, přidám ho do `data/artists.toml` (viz [Interpreti a registr interpretů](#interpreti-a-registr-interpretů)).
3. Přepíšu písničku podle konvencí v části [Přepisování písniček](#přepisování-písniček). Průběžně si ji sestavuji samotnou: `make song SONG=<id>` (například `make song SONG=lonelystranger`) ji za pár sekund zkompiluje do `build/songs/<id>.pdf`, bez obsahu a bez jména interpreta.
4. Spustím `make check`: unit testy, kontrola písniček a registru interpretů, sestavení celého zpěvníku (selže při odkazu, který vede nikam), jedna stránka na písničku a překryv akordů. Nezávažné nálezy (varování) jen vypíše. Celý zpěvník je pak v `build/editions/full/zpevnik.pdf`, kde písničku zkontroluji na jejím místě.
5. Zkontroluji přepsanou písničku nejlépe tím, že si ji přehraji.
6. Změnu zveřejním přes pull request (viz [Publikování](#publikování)).

Písničku jde psát i na Overleafu, protože kompilace celého zpěvníku v běžných IDE pro LaTeX trvá kvůli počtu souborů příliš dlouho: do projektu nahraji `zpevnik.sty` a jednoduchý hlavní soubor, který importuje jedinou přepisovanou písničku (vzor je v `tests/single-song.tex`). Obsah ani registr interpretů tam nejsou, proto se jméno interpreta nevysází a místo not je rámeček s názvem; písnička se ale zkompiluje bez chyby. Hotový text pak zkopíruji do `songs/<id>.tex` a pokračuji krokem 2.

## Přepisování písniček
V této sekci popíšu postup a konvence přepisování písniček. Písnička začíná příkazem `\song{název}`, který vysází název písničky jako odkaz na obsah; na stejný řádek patří `\artist{}` s interpretem (viz [Interpreti a registr interpretů](#interpreti-a-registr-interpretů)). Na konec písničky žádný příkaz pro novou stranu nepatří: každá písnička sama začíná na nové straně. Cíl odkazu z obsahu je `id` písničky a do písničky se nepíše.

Následuje přehled příkazů, které se v písničce používají. Příkazy pro akordy jsou v sekci „Psaní akordů“ níže.

#### Hlavička

| Příkaz | Co dělá | Příklad |
|---|---|---|
| `\song{}` | název písničky, odkaz do obsahu | `\song{Hotel California} \artist{eagles}` |
| `\subtitle{}` | podnázev pod názvem | `\subtitle{(Pomalu)}` |
| `\seealso{id}{}` | řádek s odkazem na jinou písničku | `\seealso{folsomprisonblues}{Folsom Prison Blues}` |

#### Název písničky v obsahu
Písnička se v obsahu řadí a vypisuje podle názvu v `\song{}`. Tyto řádky na začátku řádku za `\song{}` na stránce nic nevysází, jen řídí obsah:
- `\alttitle{<jiný název>}` - jiný název, pod kterým se písnička zpívá (třeba první řádek textu). V obsahu má vlastní kurzívou psanou položku pod svým písmenem. Je možné jich uvést víc.
- `\toctitle{<název v obsahu>}` - název pro obsah a řazení, když se musí lišit od `\song`, například `Marie (Klus)`, když existují dvě písničky se stejným názvem. Kontrola `make check` na stejné názvy upozorní.
- `\collection{<kotva>}` - zařadí písničku do sbírky, třeba `\collection{filmy}` do sekce "z pohádek, filmů, muzikálů, her a seriálů".

#### Bloky

Každý blok je odstavec se štítkem v levém okraji a s mezerou nad sebou. Text bloku se píše do složených závorek a smí obsahovat prázdné řádky. Číslo je volitelný parametr v hranatých závorkách; prázdný nebo vynechaný parametr znamená bez čísla.

| Příkaz | Štítek | Příklad |
|---|---|---|
| `\vers{}` | bez štítku (sloka bez čísla, poznámka) | `\vers{\emph{Mluvené.}}` |
| `\vers[n]{}` | `n.` | `\vers[2]{\chord{C}Text}` |
| `\chorus{}` | `R.` | `\chorus{\chord{G}Text}` |
| `\chorus[n]{}` | `Rn.` | `\chorus[2]{\chord{G}Text}` |
| `\prechorus{}`, `\prechorus[n]{}` | `P.`, `Pn.` | `\prechorus{\chord{F}Text}` |
| `\bridge{}`, `\bridge[n]{}` | `B.`, `Bn.` | `\bridge{\chord{Am}Text}` |
| `\solo{}`, `\solo[n]{}` | `S.`, `Sn.` | `\solo[1]{\chords{C G Am F}}` |
| `\intro{}` | `I.` | `\intro{\chords{Am F G}}` |
| `\coda{}` | `C.` | `\coda{\chords{C G C}}` |
| `\speaker{jméno}{}` | kurzívní jméno s dvojtečkou ve sloupci štítků, zarovnané doprava | `\speaker{On}{Text}` |

Všechny štítky (`1.`, `R.`, `I.`, `S.`, ...) končí tečkou a jsou zarovnané doprava, takže tečky jsou pod sebou (`9.` nad `10.`) a krátký štítek jako `R.` stojí těsně u textu. Štítek má pevnou šířku `\labelw` (25 pt) a za ním pevnou mezeru, takže text bloku vždy začíná na levém okraji, stejně jako řádky pod ním; na tom, jestli text ve složených závorkách začíná na novém řádku, nezáleží. Řádky bez štítku, které nejsou blok (`\seealso`, čárkovaná čára `\blockrule`), se odsadí o šířku štítku i s mezerou, takže jejich text začíná tam, kde text označeného bloku.

#### Značky opakování a poznámky

| Příkaz | Co dělá | Příklad |
|---|---|---|
| `\cue{}` | tučné označení místa, kde se znovu zpívá část napsaná dříve; vysází štítek a tečku | `\cue{R}` → **R.**, `\cue{R2}`, `\cue{B}`, `\cue{S1}`, `\cue{1}` |
| `\note{}` | poznámka (capo, tempo) patřící k následujícímu bloku | `\note{capo 2}` |
| `\rep{}` | označení repetice v textu (znaky `\:` a `:\` nepiš ručně) | `\rep{\chord{C}Text}` |
| `\ntimes{}` | kolikrát se část hraje nebo zpívá | `\cue{R} \ntimes{2}` → **R.** ×2 |
| `\echo{}` | ozvěna nebo vokály v pozadí: kurzívou, zvednuté, ve velikosti okolního textu | `srdce \echo{(že na)} svírá` |
| `\rec{}` | označení recitativu v textu | `\rec{Text}` |

`\cue` se chová podle místa: po prázdném řádku je to samostatný blok s mezerou nad sebou a se štítkem zarovnaným jako ostatní štítky, za blokem nebo uvnitř něj se připojí na konec řádku (`\vers[1]{...} \cue{R}`).

#### Řádky a oddělovače

| Příkaz | Co dělá | Příklad |
|---|---|---|
| `\groupbreak` | mezera mezi skupinami řádků uvnitř sloky | `řádek\\ řádek \groupbreak řádek` |
| `\blockrule{cm}` | čárkovaná čára mezi těsnými bloky | `\blockrule{10}` |
| `\partrule` | plná čára mezi částmi písničky | `\partrule` |
| `\gap{n}` | záměrná pauza mezi akordem a textem | `\chord{G}\gap{4}text` |


### Svislé mezery a velikost písma
Svislé mezery se v písničce nepíšou ručně, stará se o ně sazba:

- Mezi bloky (sloka, refrain, intro, ...) je jedna mezera `\blocksep` (20 pt), která se smrští až na nulu, když by se písnička jinak nevešla na stranu. Blok bez štítku je `\vers{...}`.
- Střídání zpěváků (`On:`, `Ona:`) je `\speaker{On}{text}`: kurzívní jméno ve sloupci štítků (zarovnané doprava jako štítky; delší jméno přečnívá doleva) a normální mezera nad blokem. Jméno se nepíše přes `\vers`, protože je kurzívou a s dvojtečkou. Uvnitř bloku (v sloce s číslem, kde je sloupec štítků obsazený) se jméno vysází kurzívou před řádek, bez mezery nad ním: `\vers[1]{\speaker{A}{Text}\\ \speaker{B}{Text}}`.
- Skupiny řádků uvnitř sloky odděluje `\groupbreak`.
- Čárkovaná čára mezi těsnými slokami je `\blockrule{délka v cm}`, plná čára mezi částmi písničky `\partrule`. Obě nahrazují mezeru před dalším blokem.
- `\note{}` (capo apod.) patří k následujícímu bloku: mezeru pod sebou nemá, nad sebou ji má (kromě začátku písničky a místa za `\subtitle`/`\seealso`). Samostatná poznámka k písničce má normální mezery `\vspace{\blocksep}` na obou stranách (s komentářem).
- Celý zpěvník je v `\Large`. Když se písnička nevejde na stranu ani s mezerami smrštěnými na nulu, přidá se za hlavičku `\large` a komentář proč. Velikost písma se do dalších písniček nepřenáší (každá písnička běží ve skupině).
- Ruční `\vspace` do písniček nepiš: mezery mezi bloky jsou automatické a noty se zarovnají samy (viz [Noty](#noty)).

`make check` hlásí každou písničku, která zabere víc než jednu stranu. Když se písnička opravdu musí zapsat na dvě strany (viz [Filosofie zpěvníku](#filosofie-zpěvníku), bod 1), zapíšu její `id` do `tools/multipage-allowlist.txt` s komentářem proč; kontrola ji pak pustí.

### Noty
Každý obrázek s notami je jeden soubor `scores/<název>.mscz` z MuseScoru 4 a v písničce ho vysází `\score{<název>}`. Na začátku bloku stojí vedle štítku (`\intro{` + `\score{pohadka}` + `}`), jinde na vlastním řádku. Do písničky se nepíše žádné odsazení, posun ani šířka: obrázek začíná tam, kde text bloku, štítek stojí uprostřed první osnovy a všechny noty mají stejné měřítko (celý systém přesně vyplní řádek).

- Před úpravou noty načti v MuseScoru sdílený styl `scores/zpevnik.mss` (Formát → Styl → Načíst styl). Sestavení ho stejně použije na každý soubor, takže jen tak uvidíš rozdělení do systémů, jaké bude ve zpěvníku.
- Nota je vždy na jedné stránce. Víc obrázků v jedné písničce znamená víc souborů (`morseovka_1.mscz`, `morseovka_2.mscz`).
- Noty z MuseScoru ručně neexportuj: `make` (nebo `make scores`) je vyexportuje do `build/scores/` sám a přeskočí ty, které se nezměnily. Akordy dostanou stejnou červenou jako ve zpěvníku.
- Písnička otevřená samostatně (Overleaf) místo not ukáže rámeček s názvem.
- `make check` hlásí `\score` bez souboru `.mscz` a soubor, který žádná písnička nepoužívá.

### Psaní akordů
V této sekci popíšu psaní akordů a příkazy potřebné k vysázení různých akordových značek. Základním příkazem pro psaní akordů je příkaz `\chord{}`. Tento příkaz vysází akord nad bezprostředně následující text. Do složených závorek uvádím název akordu velkým písmenem. Charakteristiku akordu uvádím za akord příkazem podle následujícího seznamu. Výjimkou je mollový akord, který označím jednoduše písmenem "m".
- `\add{}` - manuální horní index, například pro akord typu C<sup>4/6</sup>.
- `\bas{}` - dolní index pro postupky v basu
- `\sus{}` - sus akord
- `\maj` - maj7 akord
- `\dm` - zmenšený akord (dim)
- `\hdm` - malý zmenšený akord (m7/5-)
- `\+` - zvětšený akord
- `\bb` - béčko
- `\kk` - křížek
- `\2-9` - 2-9 akord, patřičně podle čísla

Mezery mezi akordy a texty se nepíšou ručně, o rozestup se stará sazba: akord a jeho text zabírají aspoň šířku akordu plus půl em (mezi dvěma akordy bez textu je to šířka akordu plus 1 em), takže se akordy nikdy nepřekryjí a text se hýbe jen tam, kde by se akord srazil s dalším. Uvnitř slova se v takovém místě vysází vystředěný spojovník. Starší příkazy `\nc`, `\mm`, `\sm` a `\bc` už neexistují a `make check` je v písničce nahlásí jako chybu.
- `\gap{n}` - záměrná pauza (akord zazní a zpívá se až za chvíli), `n` je počet znaků po půl em, například `\chord{G}\gap{4}text`. Uvnitř slova pauzu nepíšu.
- `\chords{}` - řádek samých akordů bez slov (intro, konec řádku, `\intro{\chords{Am F G}}`), akordy se píšou oddělené mezerou a vysázejí se červeně. Jeden řádek lze zúžit nebo rozšířit volitelným parametrem, např. `\chords[0.55em]{Am F G}`.

Písničku bez akordů `make check` ohlásí jako varování. Je-li bez akordů správně (například obsahuje jen noty), zapíšu její `id` do `tools/no-chords-allowlist.txt` s komentářem proč; kontrola ji pak nehlásí a ohlásí naopak `id`, které není písnička.

### Interpreti a registr interpretů
Každá písnička má na řádku s `\song{}` příkaz `\artist{<kotva>}`, například `\artist{ericclapton}` pro Erica Claptona. Kotva je záznam v souboru `data/artists.toml`; odtud se bere i jméno interpreta, které se vysází vpravo nahoře jako odkaz na jeho sekci v obsahu. Jméno lze u jedné písničky přepsat: `\artist[Jiné jméno]{ericclapton}`. Má-li písnička dva interprety, napíšu `\artist{prvni}\artist{druhy}` (první je vpravo, třetí se nevysází). Písnička bez známého interpreta má `\artist{}`; prázdná nebo neznámá kotva nevysází nic (`make check` ale neznámou kotvu nahlásí jako chybu).

Záznam v `data/artists.toml` potřebuje jen dvě položky, ostatní píšu, jen když výchozí hodnota nesedí (celý popis je na začátku souboru):
- `slug` - kotva: jméno malými písmeny bez diakritiky a mezer, bez úvodního členu (`beatles`, ne `thebeatles`).
- `name` - nadpis sekce a jméno v rejstříku, u osob ve tvaru "Příjmení, Jméno". Podle něj (přesněji podle `sort`) se interpreti řadí.
- `label` - jméno vysázené u písničky (výchozí je "Jméno Příjmení"), `link_label` - kratší jméno u písničky, `sort` - jiný klíč řazení, `kind = "collection"` - sbírka místo interpreta, `section = false` - interpret bez vlastní sekce.

Každý záznam se sekcí (výchozí) musí mít aspoň jednu písničku. U interpreta bez sekce (`section = false`) se jeho jméno u písničky nevysází (odkaz by nikam nevedl) a v rejstříku není; až bude mít tři písničky, `make check` upozorní, že by si sekci zasloužil.

## Vydání zpěvníku
Vydání je výběr písniček s vlastními úvodními stranami, sestavený ze stejných souborů jako celý zpěvník. Celý zpěvník je také vydání (`editions/full/`); další je například `lidovky` (lidové písničky, dřív samostatný repozitář). Vydání je složka `editions/<název>/` se souborem `edition.toml` a PDF vznikne příkazem `make EDITION=<název>` do `build/editions/<název>/zpevnik.pdf`.

### Jak vytvořit vydání
1. Vytvořím složku `editions/<název>/` (název z malých písmen, číslic a pomlček) a v ní soubor `edition.toml`. Nejkratší vydání vybere písničky podle interpreta:
   ```toml
   artists = ["lidove"]
   cover_image = "../../images/cover_image.jpg"

   [pages]
   cover = "shared"
   halftitle = "shared"
   titlepage = "shared"
   ```
   `cover_image` je obrázek, který sdílená obálka (`cover = "shared"`) roztáhne přes celou stranu; cesta je od složky vydání. U sdílené obálky je povinný, u vlastní obálky (`cover = "own"`) se neuvádí, protože obrázek patří do jejího `cover.tex`.
2. Výběr písniček je `all = true` (všechny), `artists = ["<kotva>", ...]` (všechny písničky interpretů z registru) nebo `songs = ["<id>", ...]` (jednotlivé písničky podle názvu souboru bez `.tex`). `songs` a `artists` lze spojit. Neznámé `id` nebo kotvu ohlásí `make` i `make check` jako chybu. Pořadí písniček je vždy jako v celém zpěvníku (abecední).
3. Volitelně doplním `title`, `subtitle` (podtitul pod názvem na titulní straně), `editors` (seznam jmen), `imprint` (soubor s texty nad tiráží, např. poděkování) a stránky před písničkami (`before_songs`) a po obsahu (`after_contents`). Obálku, předtitul a titulní stranu lze nahradit vlastní: v `[pages]` je pak `"own"` a vedle `edition.toml` leží soubor `cover.tex`, `halftitle.tex` nebo `titlepage.tex` (příklad je vydání `lidovky` s vlastní obálkou). Soubor `.tex` ve složce vydání, na který se nic neodkazuje, je chyba. Všechny klíče a chyby popisuje `tools/edition.py`.
4. Spustím `make check EDITION=<název>`: stejné kontroly jako u celého zpěvníku, navíc kontrola definic vydání.

### Jak přidat písničku do vydání
Vydání podle interpreta se doplní samo: stačí, aby písnička měla `\artist{<kotva>}` z jeho seznamu. U vydání podle `songs` přidám `id` písničky do seznamu. Odkaz `\seealso` na písničku, která ve vydání není, se ve vydání nevytiskne.

### Soukromé vydání
Složka vydání, kterou necommituji, je soukromé vydání: sestaví se jen lokálně (`make EDITION=<název>`) a GitHub Actions o ní neví. Co je v repozitáři, se vydává.

### Formát pro tisk
Vydání se dá sestavit i pro papír: `make EDITION=<název> FORMAT=print` (akordy barevně) nebo `FORMAT=print-black` (akordy černě, pro tisk jednou barvou). PDF je v `build/editions/<název>/<formát>/zpevnik.pdf`, vedle PDF pro obrazovku, které se nemění. Na papíře nejdou odkazy kliknout, proto z PDF zmizí: odkazy „→ obsah“ za názvem písničky, šipky před jménem interpreta, řádek písmen nad obsahem, odkaz „řazení podle interpretů“ a věta o hypertextových odkazech. Obsah, rejstřík interpretů a řádky „→ viz také“ mají místo odkazů čísla stran. Rozložení stránek písniček je stejné jako na obrazovce, takže se písničky vejdou na jednu stranu; ověří to `make check EDITION=<název> FORMAT=print`. Formáty jsou v `tools/formats.py`.

PDF pro tiskárnu v A5: `make print EDITION=<název>` (formát `print`, nebo `FORMAT=print-black`) sestaví vydání pro papír a zmenší ho na A5 do `build/editions/<název>/<formát>/zpevnik-a5.pdf`. A4 na A5 je přesně 1/√2, takže se každá písnička pořád vejde na jednu stranu. Volby se předávají přes `PRINT_ARGS`, například `make print EDITION=<název> PRINT_ARGS="--spine-shift-mm 3 --skip-first 2"`: `--spine-shift-mm` odsune obsah každé strany od hřbetu (u kroužkové vazby je u hřbetu potřeba místo; inkoust je na A5 7,1 mm od obou okrajů, takže 3 mm dá 10,1 mm u hřbetu a 4,1 mm na vnější straně), `--skip-first` vynechá první strany, sudý počet (obálku, která se odevzdává zvlášť). Lichý počet stran se doplní prázdnou stranou na konec.

## Publikování
Do větve `master` se nepushuje přímo: každá změna jde přes vlastní větev a pull request.

1. **Pull request.** GitHub Actions (`.github/workflows/build-and-publish.yml`) spustí stejné kontroly jako `make check` pro každé vydání (každou složku `editions/`), takže nové vydání se kontroluje samo, bez úpravy workflow. Navíc porovná PDF každého vydání po jednotlivých písničkách i stranách s PDF před změnou (nové vydání nemá s čím); výsledek je v souhrnu běhu. Rozdíly build neshodí, ale před sloučením je projdu.
2. **Sloučení do `master`.** Workflow znovu sestaví každé vydání, vytvoří GitHub Release `v<verze>` s PDF každého vydání (`zpevnik-<vydání>-<verze>.pdf`, celý zpěvník jako `zpevnik-full-<verze>.pdf`) a zapíše verzi do repozitáře webu ([zpevnik-web](https://github.com/f-hluchnik/zpevnik-web)). Ten si PDF z Release stáhne a nasadí web https://zpevnik.hluchnikovi.cz. Celý zpěvník je navíc stále na pevné adrese https://zpevnik.hluchnikovi.cz/static/files/zpevnik_last.pdf, na kterou míří vytištěné QR kódy. Která vydání web nabízí a v jakém pořadí, se nastavuje v repozitáři webu (`EDITION_DOWNLOADS` v `build.py`).

Verze zpěvníku má tři čísla `major.minor.patch` a vypíše ji `python3 tools/generate.py --version`:
- `major.minor` je počet písniček ve složce `songs` + 100 (738 písniček dává 8.38),
- `patch` je počet commitů v `master` (first-parent) od posledního commitu, který změnil počet písniček. Přidání písničky tedy začíná znovu od 0 a každá další změna číslo zvýší o 1. Počítá se z historie Gitu; bez ní (např. `git clone --depth 1`) vyjde `8.38.?`.

Existující tag se nikdy nepřepisuje: pokud tag už existuje (jen když se po smazání písniček vrátí počet na dřívější hodnotu), workflow skončí chybou dřív, než cokoli zveřejní. Podrobnosti jsou v komentářích workflow a v `docs/DECISIONS.md` (D-133, D-150).

## Příkazy
Všechno, co `make` vytvoří, je ve složce `build` (necommituje se, `make clean` ji smaže). Cíle `make` vypisují jen výsledek a končí cestou k PDF; když kompilace selže, vypíšou první chybu TeXu a cestu k úplnému logu (`build/editions/<vydání>/zpevnik.log`, u jedné písničky `build/songs/<id>.log`).

- `make` - vygeneruje seznam písniček, obsah a verzi (do `build/editions/full/generated/`), vyexportuje noty a zkompiluje celý zpěvník do `build/editions/full/zpevnik.pdf`
- `make check` - všechny kontroly najednou: unit testy, kontrola písniček, registru interpretů a definic vydání, sestavení s kontrolou odkazů, jedna stránka na písničku, překryv akordů
- `make song SONG=<id>` - jen jedna písnička do `build/songs/<id>.pdf` (bez obsahu a bez jména interpreta, jako na Overleafu)
- `make EDITION=<název>`, `make check EDITION=<název>` - jiné vydání (složka `editions/<název>/`, výsledek `build/editions/<název>/zpevnik.pdf`)
- `make EDITION=<název> FORMAT=print` (nebo `print-black`, černé akordy) - vydání pro papír; `make print EDITION=<název>` - PDF zmenšené na A5 pro tiskárnu (viz [Formát pro tisk](#formát-pro-tisk))
- `make generate` - jen generování, `make scores` - jen export not
- `make PYTHON=python3.12` - jiný Python než `python3`
- jednotlivé kroky `make check`: `python3 -m unittest discover -s tools` (unit testy nástrojů), `python3 tools/lint.py` (kontrola písniček, registru interpretů a definic vydání), `python3 tools/check_pages.py` (jedna stránka na písničku, po `make`) a `python3 tools/chord_gaps.py` (překryv akordů, po `make`); u jiného vydání s `--edition <název>`
- verze zpěvníku `python3 tools/generate.py --version`
- vyhledání souboru písničky `ls songs | grep <nazevpisnicky>`
- vyhledání souboru obsahujícího daný text `grep -lr <text> ./ -s`
- počet písniček `ls songs/*.tex | wc -l`

## Licence a autorská práva
Zpěvník je nekomerční a šíří se zdarma. Autorská práva k textům, hudbě a akordům písní (`songs/`), k notám (`scores/`) a k PDF z nich sestaveným patří autorům písní; licence tohoto repozitáře se na ně nevztahuje. Totéž platí pro úvodní strany (`shared-pages/` kromě `contents.tex` a strany vydání v `editions/`, úvod celého zpěvníku cituje text Vlasty Redla) a obálku (`images/`, nakreslila Ivana Vlčková). Licence Apache 2.0 (soubor `LICENSE`) platí jen pro mou vlastní práci: skripty, styl a strukturu dokumentu, registr interpretů a dokumentaci. Držitelé práv, kteří si nepřejí, aby zde jejich píseň byla, mi mohou napsat na frantahluchnik@gmail.com a píseň odstraním.

Písničku skryji tak, že její `id` zapíšu do `data/hidden.txt` s komentářem proč. Zmizí ze všech vydání i s položkami v obsahu a v rejstříku interpretů a odkazy `\seealso` na ni se nevytisknou; soubor písničky ale v repozitáři zůstává (a verze ho dál počítá), natrvalo ji odstraní až smazání souboru. Skrytí se zveřejní jako každá jiná změna, přes pull request; `make check` ohlásí `id`, které není písnička.

Stejné upozornění je v tiráži zpěvníku (`shared-pages/notice.tex`) a v patičce webu; když se mění, mění se na obou místech.

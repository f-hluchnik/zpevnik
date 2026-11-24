# Ještě mi chvilku zpívej
Zpěvník „Ještě mi chvilku zpívej“ obsahuje písničky, které jsem vybral já a postupem času i další lidé, kteří z něj zpívali. Ke stažení je na https://zpevnik.hluchnikovi.cz. V tomto repozitáři jsou zdrojové texty písniček v LaTeXu a nástroje, které z nich sestaví PDF.

Návod je seřazený tak, jak budeš postupovat: nejdřív si připravíš počítač, pak napíšeš první písničku a sestavíš zpěvník. Podrobná pravidla zápisu najdeš v části [Přepisování písniček](#přepisování-písniček), vydání a zveřejnění až na konci.

## Filosofie zpěvníku
Z tohoto zpěvníku se má dobře zpívat a hrát. Proto se při jeho tvorbě držím několika zásad.

1. **Každá písnička na jedné stránce.**
    - Radši písničku trochu namačkám na jednu stránku, než abych ji roztáhl na dvě: při hraní by se pak muselo listovat. Zatím se mi to daří, ale může se stát, že se písnička na jednu stránku opravdu nevejde. Pak ji zapíšu tak, aby se během hraní nemuselo listovat zpátky, například znovu vypíšu akordy ve sloce nebo zopakuji refrén.

2. **Akordy sedí.**
    - Při přepisování dbám na to, aby akordy byly správné, stály na správných místech a dalo se podle nich spolehlivě hrát. Každou písničku si proto zahraji.
    - Tóninu volím buď původní, nebo takovou, ve které se písnička dobře zpívá. Ta se samozřejmě mění s časem i s množstvím vypitého alkoholu, takže nikdy nebude ideální pro všechny. V době přepisu by se v ní ale mělo zpívat dobře.

3. **Hraní > zpívání > vzhled.**
    - Písnička musí být zapsaná hlavně tak, aby se dobře hrála. Na druhém místě je, aby se dobře zpívala, a teprve na třetím vzhled. Tyto tři věci spolu úzce souvisí; mám tu na mysli hlavně případy, kdy je potřeba zvolit nezvyklé odsazení nebo zalomení, aby hraní bylo přirozené a plynulé. Je to samozřejmě velmi subjektivní.

## Nastavení lokální kopie
Zpěvník (celý i jednotlivá vydání) si můžeš sestavit na svém počítači. Návod platí pro macOS (Homebrew) a Linux (Debian, Ubuntu). Instalace je hotová, když projde `make check`.

1. **Stáhni repozitář.**
   ```
   git clone git@github.com:f-hluchnik/zpevnik.git
   cd zpevnik
   ```
2. **Připrav Python 3.11 nebo novější.** Nástroje ve složce `tools/` potřebují modul `tomllib`, který je ve standardní knihovně až od verze 3.11. Jinak jim standardní knihovna stačí. Další balíky z `requirements-dev.txt` potřebují testy a kontrola `songs.json` pro web (`jsonschema`) a tisk v CMYK (`Pillow`). Python nainstaluješ na macOS příkazem `brew install python`, na Linuxu je to balík `python3` (v dostatečně nové verzi). Vytvoř si virtuální prostředí, aby `make` nespustil starší Python, který může být v `PATH` dřív:
   ```
   python3.12 -m venv .venv      # libovolný Python 3.11 nebo novější
   source .venv/bin/activate
   python3 --version             # musí ukázat 3.11 nebo novější
   pip install -r requirements-dev.txt
   ```
   Složka `.venv` se necommituje. Prostředí aktivuj (`source .venv/bin/activate`) v každém novém terminálu, ve kterém spouštíš `make`. `make` verzi Pythonu kontroluje a se starší skončí srozumitelnou chybou. Jiný Python mu můžeš zadat i přímo: `make PYTHON=python3.12`.
3. **Nainstaluj TeX Live, poppler a Ghostscript.** Zpěvník potřebuje TeX Live s češtinou, `latexmk` a několik balíků: `csquotes`, `dashrule`, `eso-pic`, `pgf`, `geometry`, `xcolor`, `hyperref`, `qrcode`, `cm-super` a `musixtex-fonts` (křížky a béčka v akordech); PDF pro tiskárnu ještě `pdfpages`, `crop` (ořezové značky) a `colorprofiles` (barevný profil pro CMYK). Poppler (programy `pdfinfo`, `pdftoppm`, `pdftotext`, `pdffonts` a `pdfimages`) potřebuje PDF pro tiskárnu (viz [Tisk](#tisk)) a porovnání PDF (`tools/pdfdiff.py`). Ghostscript (program `gs`) potřebuje tisk černou barvou a v CMYK: převádí noty do černé a kontroluje, že PDF pro tiskárnu černou barvou nepotřebuje jinou.
   - **macOS:** buď celý MacTeX (`brew install --cask mactex-no-gui`), nebo menší BasicTeX (`brew install --cask basictex`) a k němu balíky:
     ```
     sudo tlmgr update --self
     sudo tlmgr install collection-langczechslovak babel-czech hyphen-czech csquotes dashrule eso-pic pgf geometry xcolor hyperref qrcode cm-super musixtex-fonts latexmk pdfpages crop colorprofiles
     ```
     V obou případech pak ještě `brew install poppler ghostscript` (MacTeX Ghostscript obvykle přináší sám; `gs --version` ukáže, jestli ho máš).
   - **Linux:** `sudo apt-get install texlive-lang-czechslovak texlive-latex-extra texlive-fonts-extra texlive-music latexmk poppler-utils ghostscript`

   GitHub Actions sestavuje zpěvník s TeX Live 2023. Novější verze funguje také, výsledek se ale může mírně lišit. Rozhoduje vždy sestavení na GitHub Actions.
4. **Nainstaluj nástroje na noty.** Noty se exportují z MuseScoru (viz [Noty](#noty)), proto `make` potřebuje ještě tři věci:
   - **MuseScore 4.6.5**, stejnou verzi, jakou používá GitHub Actions. Jiná verze může noty rozvrhnout jinak, a tím změnit, jestli se písnička vejde na jednu stránku. Stáhni ho ze [stránky vydání 4.6.5](https://github.com/musescore/MuseScore/releases/tag/v4.6.5). Na macOS najde `make` aplikaci ve složce `/Applications` sám. Pokud je jinde nebo máš nainstalovaných víc verzí, ulož cestu k programu `mscore` do proměnné `MSCORE`, například `export MSCORE="/Applications/MuseScore 4.app/Contents/MacOS/mscore"`. Na Linuxu je MuseScore AppImage: cestu k němu ulož do `MSCORE`. Na počítači bez displeje ho spouštěj přes `xvfb-run`.
   - **`rsvg-convert`** (převádí SVG na PDF): `brew install librsvg`, nebo `sudo apt-get install librsvg2-bin`.
   - **Písmo CMU Serif** (všechny texty v notách): `brew install --cask font-computer-modern`, nebo `sudo apt-get install fonts-cmu`. Zda je nainstalované, ověříš příkazem `fc-list | grep "CMU Serif"`. Bez něj MuseScore bez varování použije jiné písmo a noty se budou od zpěvníku lišit.
5. **Ověř, že všechno funguje:** `make check`. Poprvé to trvá déle, protože se exportují všechny noty. Každý krok vypíše nadpis (`==> Unit tests`, `==> Lint`, …) a úspěšný běh končí řádkem `==> All checks passed. The PDF:` s úplnou cestou k hotovému PDF.

### Když něco nefunguje
- `the tools need Python 3.11 or newer` (nebo `No module named 'tomllib'`, když nástroj spouštíš přímo): Python je starší než 3.11, nebo není aktivní `.venv`.
- `the tests and the check of songs.json need the packages of requirements-dev.txt`: ve virtuálním prostředí chybí `jsonschema` nebo `Pillow`. S aktivním `.venv` spusť `pip install -r requirements-dev.txt`.
- `MuseScore 4 not found`: MuseScore je jinde, než ho `make` hledá. Nastav `MSCORE` (krok 4).
- `rsvg-convert not found`: nainstaluj `librsvg` (krok 4).
- `pdfinfo not found`, `pdftoppm not found`, `pdftotext not found`, `pdffonts not found` nebo `pdfimages not found`: nainstaluj poppler (krok 3).
- `gs not found: install Ghostscript`: nainstaluj Ghostscript (krok 3).

## Nová písnička
Každá písnička je jeden soubor ve složce `songs`. Seznam písniček, obsah (podle písmen i podle interpretů) a verzi zpěvníku vygeneruje `make`, takže `zpevnik.tex` ani `shared-pages/contents.tex` ručně neupravuješ. Písnička se podle názvu v `\song{}` sama zařadí do obsahu podle písmen i do sekce svého interpreta.

1. **Založ soubor.** Ve složce `songs` vytvoř soubor pojmenovaný podle názvu písničky: bez diakritiky, bez mezer a malými písmeny (`Lonely Stranger` → `lonelystranger.tex`). Mají-li dvě písničky od různých interpretů stejný název, připoj za název interpreta, pokud možno jedním slovem, tedy příjmení nebo název skupiny (`marieklus.tex`). Název souboru bez `.tex` je `id` písničky. Jako základ můžeš použít šablonu `song-template.tex` z kořene repozitáře.
2. **Doplň interpreta.** Na řádek s `\song{}` napiš `\artist{<kotva>}`. Pokud interpret ještě v registru není, přidej ho do `data/artists.toml` (viz [Interpreti a registr interpretů](#interpreti-a-registr-interpretů)).
3. **Přepiš písničku** podle pravidel v části [Přepisování písniček](#přepisování-písniček). Průběžně si ji sestavuj samotnou: `make song SONG=<id>` (třeba `make song SONG=lonelystranger`) ji za pár sekund zkompiluje do `build/songs/<id>.pdf`, bez obsahu a bez jména interpreta.
4. **Spusť `make check`.** Projde všechny kontroly (seznam je u [příkazů](#příkazy)) a sestaví celý zpěvník do `build/editions/full/zpevnik.pdf`. Tam písničku zkontroluj na jejím místě.
5. **Zahraj si ji.** To je nejlepší kontrola přepsané písničky.
6. **Zveřejni ji** přes pull request (viz [Publikování](#publikování)).

### Psaní na Overleafu
Celý zpěvník se v běžných editorech LaTeXu kompiluje kvůli počtu souborů příliš dlouho. Písničku proto můžeš psát i na Overleafu: do projektu nahraj `zpevnik.sty` a jednoduchý hlavní soubor, který vloží jen tuto písničku (vzor je v `tests/single-song.tex`). Obsah ani registr interpretů tam nejsou, takže se nevysází jméno interpreta a místo not se ukáže rámeček s názvem. Písnička se ale zkompiluje bez chyby. Hotový text pak zkopíruj do `songs/<id>.tex` a pokračuj krokem 2.

## Přepisování písniček
Tato část je příručka k zápisu písničky. Písnička začíná příkazem `\song{název}`, který vysází název jako odkaz na obsah. Na stejný řádek patří `\artist{}` s interpretem (viz [Interpreti a registr interpretů](#interpreti-a-registr-interpretů)). Na konec písničky nepiš žádný příkaz pro novou stránku: každá písnička sama začíná na nové stránce. Cílem odkazu z obsahu je `id` písničky, do písničky ho nepiš.

Následují příkazy, které se v písničce používají. Příkazy pro akordy popisuje část [Psaní akordů](#psaní-akordů).

### Hlavička

| Příkaz | Co dělá | Příklad |
|---|---|---|
| `\song{}` | název písničky, odkaz do obsahu | `\song{Hotel California} \artist{eagles}` |
| `\subtitle{}` | podnázev pod názvem | `\subtitle{(Pomalu)}` |
| `\seealso{id}{}` | řádek s odkazem na jinou písničku | `\seealso{folsomprisonblues}{Folsom Prison Blues}` |

### Název písničky v obsahu
Písnička se v obsahu řadí a vypisuje podle názvu v `\song{}`. Následující příkazy piš na samostatné řádky za `\song{}`. Na stránce nic nevysázejí, jen řídí obsah:
- `\alttitle{<jiný název>}` – jiný název, pod kterým se písnička zpívá (třeba první řádek textu). V obsahu má vlastní položku kurzívou pod svým písmenem. Může jich být víc.
- `\toctitle{<název v obsahu>}` – název pro obsah a řazení, když se musí lišit od `\song`, například `Marie (Klus)`, když existují dvě písničky stejného jména. Na stejné názvy upozorní `make check`.
- `\collection{<kotva>}` – zařadí písničku do sbírky, třeba `\collection{filmy}` do sekce „z pohádek, filmů, muzikálů, her a seriálů“.

### Bloky
Každý blok je odstavec se štítkem v levém okraji a s mezerou nad sebou. Text bloku patří do složených závorek. Řádky odděluj `\\`, skupiny řádků `\groupbreak`. Uvnitř bloku nesmí být prázdný řádek a text nekončí `\\` (to by vysázelo prázdný řádek navíc). Číslo bloku je volitelný parametr v hranatých závorkách; prázdný nebo vynechaný znamená blok bez čísla.

Každý řádek zdroje je v PDF právě jeden řádek, nic se nezalamuje. Řádek o trochu delší než šířka textu sazba stáhne zúžením mezer mezi slovy. Když ani to nestačí, `make check` selže s hlášením `<id>: N line(s) of the source printed as M on p. P`. Řádek pak rozděl pomocí `\\` tam, kde to dává smysl (u čárky, u rýmu). Totéž platí pro akord na konci řádku: celý se musí vejít do šířky textu, jinak `make check` hlásí `a chord runs X pt into the margin`. Výjimkou je recitativ `\rec{}`: je to próza, takže se jeho řádky zalamovat smějí. Bloky napsané za sebou bez prázdného řádku (`\intro{...} \solo{...}`) zůstanou na jednom řádku. Písmena se nezužují; kdyby to někdy bylo potřeba, postup popisuje [docs/architecture.md](docs/architecture.md) (*Songs*).

| Příkaz | Štítek | Příklad |
|---|---|---|
| `\vers{}` | bez štítku (sloka bez čísla) | `\vers{\chord{C}Text}` |
| `\vers[n]{}` | `n.` | `\vers[2]{\chord{C}Text}` |
| `\chorus{}` | `R.` | `\chorus{\chord{G}Text}` |
| `\chorus[n]{}` | `Rn.` | `\chorus[2]{\chord{G}Text}` |
| `\prechorus{}`, `\prechorus[n]{}` | `P.`, `Pn.` | `\prechorus{\chord{F}Text}` |
| `\bridge{}`, `\bridge[n]{}` | `B.`, `Bn.` | `\bridge{\chord{Am}Text}` |
| `\solo{}`, `\solo[n]{}` | `S.`, `Sn.` | `\solo[1]{\chords{C G Am F}}` |
| `\intro{}` | `I.` | `\intro{\chords{Am F G}}` |
| `\coda{}` | `C.` | `\coda{\chords{C G C}}` |
| `\remark{}` | bez štítku, kurzívou: text, který se nezpívá (ladění, stavba sloky). Stojí samostatně mezi bloky, řádky odděluje `\\`. Vyhledávání na webu ho nezahrnuje. | `\remark{Ladění D-E-d-g-h-d.}` |
| `\speaker{jméno}{}` | jméno kurzívou s dvojtečkou ve sloupci štítků, zarovnané doprava | `\speaker{On}{Text}` |

Všechny štítky (`1.`, `R.`, `I.`, `S.`, …) končí tečkou a jsou zarovnané doprava. Tečky tak stojí pod sebou (`9.` nad `10.`) a krátký štítek jako `R.` stojí těsně u textu. Štítek má pevnou šířku `\labelw` (25 pt) a za ním je pevná mezera, takže text bloku vždy začíná na stejném místě jako řádky pod ním. Nezáleží přitom na tom, jestli text ve složených závorkách začíná na novém řádku. Řádky bez štítku, které nejsou blok (`\seealso`, čárkovaná čára `\blockrule`), se odsadí o šířku štítku i s mezerou, takže jejich text začíná tam, kde text bloku se štítkem.

### Značky opakování a poznámky

| Příkaz | Co dělá | Příklad |
|---|---|---|
| `\cue{}` | tučně označí místo, kde se znovu zpívá dříve zapsaná část; vysází štítek s tečkou | `\cue{R}` → **R.**, `\cue{R2}`, `\cue{B}`, `\cue{S1}`, `\cue{1}` |
| `\note{}` | krátká poznámka (capo, tempo) k následujícímu bloku; samostatný nezpívaný text je `\remark{}` | `\note{capo 2}` |
| `\rep{}` | repetice v textu (znaky `\:` a `:\` nepiš ručně) | `\rep{\chord{C}Text}` |
| `\ntimes{}` | kolikrát se část hraje nebo zpívá | `\cue{R} \ntimes{2}` → **R.** ×2 |
| `\echo{}` | ozvěna nebo vokály v pozadí: kurzívou, zvednuté, ve velikosti okolního textu | `srdce \echo{(že na)} svírá` |
| `\rec{}` | recitativ v textu; je to próza, jeho řádky se smějí zalomit | `\rec{Text}` |

`\cue` se chová podle toho, kde stojí. Po prázdném řádku je to samostatný blok s mezerou nad sebou a se štítkem zarovnaným jako ostatní štítky. Za blokem nebo uvnitř něj se připojí na konec řádku (`\vers[1]{...} \cue{R}`). Odkazuje vždy na poslední dříve zapsanou část se stejným štítkem: když jsou refrény číslované (`\chorus[1]`, `\chorus[2]`), piš `\cue{R1}`, ne `\cue{R}`.

### Řádky a oddělovače

| Příkaz | Co dělá | Příklad |
|---|---|---|
| `\groupbreak` | mezera mezi skupinami řádků uvnitř sloky | `řádek\\ řádek \groupbreak řádek` |
| `\blockrule{cm}` | čárkovaná čára mezi těsnými bloky | `\blockrule{10}` |
| `\partrule` | plná čára mezi částmi písničky | `\partrule` |
| `\gap{n}` | záměrná pauza mezi akordem a textem | `\chord{G}\gap{4}text` |

### Svislé mezery a velikost písma
Svislé mezery v písničce nepiš ručně, stará se o ně sazba:

- Mezi bloky (sloka, refrén, intro, …) je jedna mezera `\blocksep` (20 pt). Když by se písnička jinak nevešla na stránku, mezera se smrští až na nulu. Blok bez štítku je `\vers{...}`.
- Střídání zpěváků (`On:`, `Ona:`) zapiš jako `\speaker{On}{text}`: jméno se vysází kurzívou ve sloupci štítků (zarovnané doprava jako štítky, delší jméno přečnívá doleva) a nad blokem bude normální mezera. Jméno nepiš přes `\vers`, protože má být kurzívou a s dvojtečkou. Uvnitř bloku (ve sloce s číslem, kde je sloupec štítků obsazený) se jméno vysází kurzívou před řádek, bez mezery nad ním: `\vers[1]{\speaker{A}{Text}\\ \speaker{B}{Text}}`.
- Skupiny řádků uvnitř sloky odděluje `\groupbreak`.
- Čárkovanou čáru mezi těsnými slokami udělá `\blockrule{délka v cm}`, plnou čáru mezi částmi písničky `\partrule`. Obě nahrazují mezeru před dalším blokem. Písnička z více částí (číslování slok začíná znovu) má mezi částmi vždy `\partrule`.
- `\note{}` (capo apod.) patří k následujícímu bloku: pod sebou mezeru nemá, nad sebou ano (kromě začátku písničky a místa za `\subtitle` nebo `\seealso`). Samostatná poznámka k písničce je `\remark{}` (viz [Bloky](#bloky)).
- Celý zpěvník je vysázený v `\Large`. Když se písnička nevejde na stránku ani s mezerami smrštěnými na nulu, přidej za hlavičku `\large` a komentář proč. Velikost písma se do dalších písniček nepřenáší (každá písnička je ve vlastní skupině).
- Ruční `\vspace` do písniček nepiš: mezery mezi bloky jsou automatické a noty se zarovnají samy (viz [Noty](#noty)).

`make check` hlásí každou písničku delší než jedna stránka. Když se písnička opravdu musí zapsat na dvě stránky (viz [Filosofie zpěvníku](#filosofie-zpěvníku), bod 1), zapiš její `id` do `data/multipage-allowlist.txt` s komentářem proč. Kontrola ji pak pustí.

### Noty
Každý obrázek s notami je jeden soubor `scores/<název>.mscz` z MuseScoru 4 a v písničce ho vysází `\score{<název>}`. Noty stojí vždy uvnitř bloku: na jeho začátku vedle štítku (`\intro{\score{pohadka}}`), jinde na vlastním řádku za `\\`. Odsazení, posun ani šířku do písničky nepiš: obrázek začíná tam, kde text bloku, štítek stojí uprostřed první osnovy a všechny noty mají stejné měřítko (celý systém přesně vyplní řádek).

- Než začneš noty upravovat, načti v MuseScoru sdílený styl `scores/zpevnik.mss` (Formát → Styl → Načíst styl). Sestavení ho stejně použije na každý soubor, takže jen tak uvidíš rozdělení do systémů, jaké bude ve zpěvníku.
- Akordy v notách piš v německém značení, jako ve zpěvníku: `B` (anglicky B♭) a `H` (anglicky B). Se sdíleným stylem je MuseScore ukáže jako „B♭“ a „H“, zpěvník vysází „B“ a „H“.
- Soubor s notami má vždy jen jednu stránku. Víc obrázků v jedné písničce znamená víc souborů (`morseovka_1.mscz`, `morseovka_2.mscz`).
- Noty z MuseScoru ručně neexportuj: `make` (nebo `make scores`) je vyexportuje do `build/scores/` sám a přeskočí ty, které se nezměnily. Akordy dostanou stejnou červenou jako ve zpěvníku.
- Písnička otevřená samostatně (Overleaf) ukáže místo not rámeček s názvem.
- `make check` hlásí `\score` bez souboru `.mscz` i soubor, který žádná písnička nepoužívá.

### Psaní akordů
Akord zapiš příkazem `\chord{}`: vysází akord nad text, který bezprostředně následuje. Do závorek napiš název akordu s velkým písmenem. Mollový akord označ jen písmenem „m“, ostatní vlastnosti akordu přidej za název těmito příkazy:
- `\add{}` – horní index zadaný ručně, například pro akord C<sup>4/6</sup>
- `\bas{}` – dolní index pro postupy v basu
- `\sus{}` – sus akord
- `\maj` – maj7 akord
- `\dm` – zmenšený akord (dim)
- `\hdm` – malý zmenšený akord (m7/5-)
- `\+` – zvětšený akord
- `\bb` – béčko
- `\kk` – křížek
- `\2`, `\4`, `\5`, `\6`, `\7`, `\9` – číslo v horním indexu, například `\7` pro septakord

TeX spolkne mezeru za značkou, jejíž jméno je z písmen (`\kk`, `\bb`, `\maj`, `\dm`, `\hdm`). Uvnitř názvu akordu je to správně: `F\kk m` je F♯m. Má-li se mezera vysázet, napiš za značku `{}`: mezi tóny v basu `\bas{C\kk{} F\kk{} C\kk}`, mezi akordy `\chords{Dm\maj{} Dm}`, v textu `C\kk{} dur`. `make check` hlásí spolknutou mezeru všude kromě místa před `m` nebo před další značkou.

Mezery mezi akordy a textem nepiš ručně, o rozestupy se stará sazba. Akord a jeho text zabírají vždy aspoň šířku akordu plus půl em (dva akordy bez textu mezi sebou šířku akordu plus 1 em). Akordy se tak nikdy nepřekryjí a text se posune jen tam, kde by se akord srazil s dalším. Je-li takové místo uvnitř slova, vysází se v něm vystředěný spojovník. Starší příkazy `\nc`, `\mm`, `\sm` a `\bc` už neexistují a `make check` je v písničce nahlásí jako chybu.
- `\gap{n}` – záměrná pauza (akord zazní a zpívá se až za chvíli); `n` je počet znaků po půl em, například `\chord{G}\gap{4}text`. Uvnitř slova pauzu nepiš.
- `\chords{}` – řádek samých akordů bez slov (intro, konec řádku: `\intro{\chords{Am F G}}`). Akordy odděluj mezerou, vysázejí se červeně. Rozestup jednoho řádku zúžíš nebo rozšíříš volitelným parametrem, například `\chords[0.55em]{Am F G}`.

Písničku bez akordů ohlásí `make check` jako varování. Pokud má být bez akordů (například obsahuje jen noty), zapiš její `id` do `data/no-chords-allowlist.txt` s komentářem proč. Kontrola ji pak nehlásí a naopak ohlásí `id`, které nepatří žádné písničce.

### Interpreti a registr interpretů
Každá písnička má na řádku s `\song{}` příkaz `\artist{<kotva>}`, například `\artist{ericclapton}` pro Erica Claptona. Kotva odkazuje na záznam v souboru `data/artists.toml`. Odtud se bere i jméno interpreta, které se vysází vpravo nahoře jako odkaz na jeho sekci v obsahu. U jedné písničky můžeš jméno přepsat: `\artist[Jiné jméno]{ericclapton}`. Má-li písnička dva interprety, napiš `\artist{prvni}\artist{druhy}` (první stojí vpravo, třetí se už nevysází). Písnička bez známého interpreta má `\artist{}`. Prázdná nebo neznámá kotva nevysází nic, `make check` ale neznámou kotvu ohlásí jako chybu.

Záznam v `data/artists.toml` potřebuje jen dvě položky. Ostatní uváděj, jen když výchozí hodnota nesedí (všechny popisuje začátek souboru):
- `slug` – kotva: jméno malými písmeny bez diakritiky a mezer, bez úvodního členu (`beatles`, ne `thebeatles`).
- `name` – nadpis sekce a jméno v rejstříku, u osob ve tvaru „Příjmení, Jméno“. Podle něj (přesněji podle `sort`) se interpreti řadí.
- volitelně `label` – jméno vysázené u písničky (výchozí je „Jméno Příjmení“), `link_label` – kratší jméno u písničky, `sort` – jiný klíč řazení, `kind = "collection"` – sbírka místo interpreta, `section = false` – interpret bez vlastní sekce.

Každý interpret s vlastní sekcí (to je výchozí stav) musí mít aspoň jednu písničku. U interpreta bez sekce (`section = false`) se jméno u písničky nevysází (odkaz by nikam nevedl) a v rejstříku chybí. Až bude mít tři písničky, `make check` upozorní, že by si sekci zasloužil.

## Sestavení zpěvníku
Všechno, co `make` vytvoří, ukládá do složky `build` (necommituje se, `make clean` ji smaže). Cíle `make` vypisují jen výsledek a končí cestou k PDF. Když kompilace selže, vypíšou první chybu TeXu a cestu k úplnému logu (`build/editions/<vydání>/zpevnik.log`, u jedné písničky `build/songs/<id>.log`). Co dělá který nástroj ve složce `tools/` a kdo ho spouští (`make`, nebo jen GitHub Actions), popisuje [tools/README.md](tools/README.md).

### Příkazy
- `make` – vygeneruje seznam písniček, obsah a verzi (do `build/editions/full/generated/`), vyexportuje noty a zkompiluje celý zpěvník do `build/editions/full/zpevnik.pdf`.
- `make check` – všechny kontroly najednou: unit testy; kontrola písniček, registru interpretů a definic vydání; převod písniček pro web (hlásí, čemu nerozumí, i s číslem řádku); sestavení s kontrolou odkazů (selže na odkazu, který nikam nevede); jedna stránka na písničku; překrývání akordů; řádky v šířce textu. Chyby kontrolu zastaví, varování jen vypíše.
- `make song SONG=<id>` – jen jedna písnička do `build/songs/<id>.pdf` (bez obsahu a bez jména interpreta, jako na Overleafu).
- `make EDITION=<název>`, `make check EDITION=<název>` – jiné vydání (složka `editions/<název>/`, výsledek v `build/editions/<název>/zpevnik.pdf`, viz [Vydání zpěvníku](#vydání-zpěvníku)).
- `make print EDITION=<název>` – PDF pro tiskárnu, jak ho popisuje `edition.toml` vydání, do `build/print/<název>/` (viz [Tisk](#tisk)).
- `make generate` – jen generování, `make scores` – jen export not, `make clean` – smaže složku `build`.
- `make PYTHON=python3.12` – jiný Python než `python3`.
- Jednotlivé kroky `make check`: `python3 -m unittest discover -s tools` (unit testy nástrojů), `python3 tools/lint.py` (kontrola písniček, registru interpretů a definic vydání), a po `make` ještě `python3 tools/check_pages.py` (jedna stránka na písničku), `python3 tools/chord_gaps.py` (překrývání akordů a akordy v okraji) a `python3 tools/song_lines.py` (zalomené řádky a řádky v okraji). U jiného vydání přidej `--edition <název>`.
- `python3 tools/generate.py --version` – verze zpěvníku.
- `ls songs | grep <nazevpisnicky>` – najde soubor písničky.
- `grep -lr <text> ./ -s` – najde soubory, které obsahují daný text.
- `ls songs/*.tex | wc -l` – počet písniček.

### Tisk
PDF pro tiskárnu sestavíš jedním příkazem, u kteréhokoli vydání:
```
make print EDITION=skaut-kravare
```
Výsledek je ve složce `build/print/<vydání>/`: knižní blok `zpevnik-<vydání>-<verze>-blok.pdf` a u vydání s obálkou tištěnou zvlášť ještě obálka (`-obalka.pdf`) a náhled celé knihy s obálkou bez ořezových značek (`-nahled.pdf`, jen na prohlížení). Co tiskárna chce (formát papíru, okraje, černá barva nebo CMYK, ořezové značky, spadávka), patří do tabulky `[print.block]` v `edition.toml` vydání, obálka tištěná zvlášť do tabulky `[print.cover]` s vlastním návrhem (příkladem je `editions/skaut-kravare/print-cover/`). Všechny klíče, kontroly a otázky pro novou tiskárnu popisuje [docs/printing.md](docs/printing.md) (anglicky). Bez tabulky se vydání vytiskne na A4, barevně a s obálkou.

Na papíře nejde na odkazy kliknout, proto se pro tisk zpěvník sází trochu jinak: zmizí odkazy „→ obsah“ za názvem písničky, šipky před jménem interpreta, řádek písmen nad obsahem, odkaz „řazení podle interpretů“ a věta o hypertextových odkazech. Obsah podle písmen, písničky v sekcích interpretů a řádky „→ viz také“ mají místo odkazů čísla stran. Stránky písniček vypadají stejně jako na obrazovce, takže se každá písnička vejde na jednu stránku; `make print` to zkontroluje stejně jako `make check`.

## Vydání zpěvníku
Vydání je výběr písniček s vlastními úvodními stránkami, sestavený ze stejných souborů jako celý zpěvník. I celý zpěvník je vydání (`editions/full/`); další je třeba `lidovky` (lidové písničky, dřív samostatný repozitář). Každé vydání je složka `editions/<název>/` se souborem `edition.toml` a PDF z něj sestaví `make EDITION=<název>` do `build/editions/<název>/zpevnik.pdf`.

### Jak vytvořit vydání
1. **Založ složku** `editions/<název>/` (název z malých písmen, číslic a pomlček) a v ní soubor `edition.toml`. Nejkratší vydání vybírá písničky podle interpreta:
   ```toml
   artists = ["lidove"]
   cover_image = "../../images/cover_image.jpg"

   [pages]
   cover = "shared"
   halftitle = "shared"
   titlepage = "shared"
   ```
   `cover_image` je obrázek, který sdílená obálka (`cover = "shared"`) roztáhne přes celou stránku; cesta vede od složky vydání. U sdílené obálky je povinný. U vlastní obálky (`cover = "own"`) se neuvádí, protože obrázek patří do jejího `cover.tex`.
2. **Vyber písničky:** `all = true` (všechny), `artists = ["<kotva>", ...]` (všechny písničky daných interpretů z registru) nebo `songs = ["<id>", ...]` (jednotlivé písničky podle názvu souboru bez `.tex`). `songs` a `artists` můžeš kombinovat. Neznámé `id` nebo kotvu ohlásí `make` i `make check` jako chybu. Písničky jsou vždy seřazené jako v celém zpěvníku, tedy abecedně.
3. **Doplň, co potřebuješ.** Volitelně `title`, `subtitle` (podtitul pod názvem na titulní straně), `editors` (seznam jmen), `imprint` (soubor s texty nad tiráží, např. poděkování), stránky před písničkami (`before_songs`) a za obsahem (`after_contents`) a tabulku `[print]`, když vydání půjde do tiskárny (viz [Tisk](#tisk)). Obálku, předtitul a titulní stranu můžeš nahradit vlastní: v `[pages]` pak napiš `"own"` a vedle `edition.toml` přidej soubor `cover.tex`, `halftitle.tex` nebo `titlepage.tex` (příkladem je vydání `lidovky` s vlastní obálkou). Soubor `.tex` ve složce vydání, na který nic neodkazuje, je chyba. Všechny klíče a chyby popisuje `tools/edition.py`.
4. **Spusť `make check EDITION=<název>`:** stejné kontroly jako u celého zpěvníku a navíc kontrola definice vydání.

### Jak přidat písničku do vydání
Vydání vybrané podle interpretů se doplňuje samo: stačí, aby písnička měla `\artist{<kotva>}` některého z nich. U vydání se seznamem `songs` přidej `id` písničky do seznamu. Odkaz `\seealso` na písničku, která ve vydání není, se ve vydání nevytiskne.

### Soukromé vydání
Složka vydání, kterou necommitneš, je soukromé vydání: sestavíš ho jen u sebe (`make EDITION=<název>`) a GitHub Actions o něm neví. Co je v repozitáři, to se vydává.

## Publikování
Do větve `master` se nepushuje přímo: každá změna jde přes vlastní větev a pull request.

1. **Pull request.** GitHub Actions (`.github/workflows/build-and-publish.yml`) spustí pro každé vydání (každou složku v `editions/`) stejné kontroly jako `make check`, takže nové vydání se kontroluje samo, bez úpravy workflow. Navíc porovná PDF každého vydání po písničkách i po stránkách s PDF před změnou (nové vydání nemá s čím) a výsledek zapíše do souhrnu běhu. Rozdíly build neshodí, ale před sloučením je projdi.
2. **Sloučení do `master`.** Workflow znovu sestaví každé vydání, vytvoří GitHub Release `v<verze>` s PDF každého vydání (`zpevnik-<vydání>-<verze>.pdf`, celý zpěvník jako `zpevnik-full-<verze>.pdf`) a zapíše verzi do repozitáře webu ([zpevnik-web](https://github.com/f-hluchnik/zpevnik-web)). Ten si PDF z Release stáhne a nasadí web https://zpevnik.hluchnikovi.cz. Celý zpěvník je navíc vždy na pevné adrese https://zpevnik.hluchnikovi.cz/static/files/zpevnik_last.pdf, na kterou vedou vytištěné QR kódy. Která vydání web nabízí a v jakém pořadí, se nastavuje v repozitáři webu (`EDITION_DOWNLOADS` v `build.py`).

### Verze
Verze zpěvníku má tři čísla `major.minor.patch` a vypíše ji `python3 tools/generate.py --version`:
- `major.minor` je počet písniček ve složce `songs` plus 100 (738 písniček dává 8.38).
- `patch` je počet commitů v `master` (first-parent) od posledního commitu, který změnil počet písniček. Nová písnička tedy začíná znovu od 0 a každá další změna číslo zvýší o 1. Počítá se z historie Gitu; bez ní (např. po `git clone --depth 1`) vyjde `8.38.?`.

Odkaz „Jaké písničky přibyly?“ na webu vede na porovnání aktuální verze s poslední verzí před poslední změnou počtu písniček (např. `v8.38.46...v8.47.8`). Tu vypíše `python3 tools/generate.py --previous-version` a workflow ji zapíše do webu spolu s verzí.

Existující tag se nikdy nepřepisuje. Pokud už tag existuje (stane se to jen tehdy, když se po smazání písniček počet vrátí na dřívější hodnotu), workflow skončí chybou dřív, než cokoli zveřejní. Podrobnosti jsou v komentářích workflow a v [docs/architecture.md](docs/architecture.md).

## Licence a autorská práva
Zpěvník je nekomerční a šíří se zdarma. Autorská práva k textům, hudbě a akordům písní (`songs/`), k notám (`scores/`) a k PDF z nich sestaveným patří autorům písní; licence tohoto repozitáře se na ně nevztahuje. Totéž platí pro úvodní strany (`shared-pages/` kromě `contents.tex` a strany vydání v `editions/`; úvod celého zpěvníku cituje text Vlasty Redla) a pro obálku (`images/`, nakreslila Ivana Vlčková). Licence Apache 2.0 (soubor `LICENSE`) platí jen pro mou vlastní práci: skripty, styl a strukturu dokumentu, registr interpretů a dokumentaci. Pokud si držitel práv nepřeje, aby tu jeho píseň byla, může mi napsat na frantahluchnik@gmail.com a píseň odstraním.

Písničku skryješ tak, že její `id` zapíšeš do `data/hidden.txt` s komentářem proč. Zmizí ze všech vydání i s položkami v obsahu a v rejstříku interpretů a odkazy `\seealso` na ni se nevytisknou. Soubor písničky ale v repozitáři zůstane (a verze ho dál počítá); natrvalo ji odstraní až smazání souboru. Skrytí se zveřejní jako každá jiná změna, přes pull request. `make check` ohlásí `id`, které nepatří žádné písničce.

Stejné upozornění je v tiráži zpěvníku (`shared-pages/notice.tex`) a v patičce webu. Když se mění, změň ho na všech třech místech.

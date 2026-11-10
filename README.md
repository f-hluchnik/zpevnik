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
    
## Postup přidávání nové písničky
V této části popíšu postup přidání nové písničky do Zpěvníku, jak jsem si to navykl dělat. Písnička je jediný soubor; seznam písniček, obsah (podle písmen i podle interpretů) i verzi zpěvníku generuje skript `tools/generate.py`, takže `zpevnik.tex` ani `obsah.tex` ručně neupravuji.

1. Ve složce `pisnicky` vytvořím soubor s názvem podle názvu písničky. Název souboru se tvoří odebráním diakritiky a mezer z názvu písničky a zapsáním tohoto názvu malými písmeny. Je-li potřeba odlišit dvě písničky se stejným názvem od různých interpretů, učiní se tak přidáním jména interpreta (pokud možno jednoslovně, tedy příjmení nebo název skupiny) za jméno písničky, opět bez mezer a diakritiky, malými písmeny. Je možné použít šablonu `sablona.tex`, která je umístěna v kořenovém adresáři zpěvníku.
2. Na řádek s příkazem `\song{}` doplním `\artist{<kotva>}` (více v části o interpretech níže). Pokud interpret ještě v registru není, přidám do souboru `data/artists.toml` nový záznam `[[entry]]` s kotvou (`slug`) a jménem (`name`, ve tvaru "Příjmení, Jméno").
3. Otevřu si soubor s písničkou a začnu přepisovat. Více o přepisování písniček dále.
4. Spustím `make`. Skript nejdřív vygeneruje seznam písniček seřazený podle abecedy, obsah a verzi (do složky `generated`, která se necommituje) a pak zkompiluje `zpevnik.pdf`. Písnička se sama zařadí podle názvu v `\song{}`, do obsahu podle písmen i do sekce svého interpreta.
5. Spustím `python3 tools/lint.py`. Zkontroluje, že každá písnička má `\song` a právě jeden řádek s `\artist`, že všechny kotvy jsou v registru a že každá sekce interpreta má písničky. Stejnou kontrolu spouští i GitHub Actions. Nezávažné nálezy (varování) jen vypíše.
6. Zkontroluji přepsanou písničku nejlépe tím, že si ji přehraji.

Na kompilaci potřebuji Python 3.11 a novější, `latexmk` a TeX Live 2023 s češtinou (ve stejné verzi kompiluje zpěvník i GitHub Actions).

### Lokální sestavení
Na kompilaci potřebuji Python 3.11 a novější a TeX Live s češtinou, `latexmk` a několik balíků (`csquotes`, `dashrule`, `eso-pic`, `pgf`, `geometry`, `xcolor`, `hyperref`, `cm-super`, `musixtex-fonts` pro křížky a béčka v akordech).

- **Linux (Debian, Ubuntu):** `sudo apt-get install texlive-lang-czechslovak texlive-latex-extra texlive-fonts-extra texlive-music latexmk`. Na kontrolu stran a porovnání PDF (`tools/check_pages.py`, `tools/pdfdiff.py`) navíc `poppler-utils`.
- **macOS:** buď celý MacTeX (`brew install --cask mactex-no-gui`), nebo menší BasicTeX (`brew install --cask basictex`) a po něm `sudo tlmgr update --self` a `sudo tlmgr install collection-langczechslovak babel-czech hyphen-czech csquotes dashrule eso-pic pgf geometry xcolor hyperref cm-super musixtex-fonts latexmk`. Python 3.11 a novější je například z Homebrew (`brew install python`).

Noty (viz [Noty](#noty)) se exportují z MuseScoru, takže `make` potřebuje ještě MuseScore 4.6.5, `rsvg-convert` a písmo CMU Serif: na Linuxu `sudo apt-get install librsvg2-bin fonts-cmu` a MuseScore jako AppImage (cestu k němu dej do proměnné `MSCORE`), na macOS MuseScore 4 z musescore.org, `brew install librsvg` a písmo CMU Serif.

`make` zkompiluje celý zpěvník, `make song SONG=<id>` jen jednu písničku. `<id>` je název souboru bez `.tex`, například `make song SONG=lonelystranger`. Hotové PDF je v `build/<id>.pdf` (složka `build` se necommituje) a trvá to pár sekund. Je to stejné nastavení jako na Overleafu: bez obsahu a bez odkazů na interprety. Lokální sestavení s novější verzí TeX Live se může od GitHub Actions mírně lišit; rozhodující je vždy GitHub Actions.

### Název písničky v obsahu
Písnička se v obsahu řadí a vypisuje podle názvu v `\song{}`. Tyto řádky na začátku řádku za `\song{}` na stránce nic nevysází, jen řídí obsah:
- `\alttitle{<jiný název>}` - jiný název, pod kterým se písnička zpívá (třeba první řádek textu). V obsahu má vlastní kurzívou psanou položku pod svým písmenem. Je možné jich uvést víc.
- `\toctitle{<název v obsahu>}` - název pro obsah a řazení, když se musí lišit od `\song`, například `Marie (Klus)`, když existují dvě písničky se stejným názvem. Skript `tools/lint.py` na stejné názvy upozorní.
- `\collection{<kotva>}` - zařadí písničku do sbírky, třeba `\collection{filmy}` do sekce "z pohádek, filmů, muzikálů, her a seriálů".

## Automatické publikování

Zpěvník se po každém pushi do větve `master` automaticky zkompiluje a nová verze PDF se zveřejní na webu (https://zpevnik.hluchnikovi.cz), aniž by bylo potřeba cokoliv dělat ručně. Zajišťuje to GitHub Actions workflow (`.github/workflows/build-and-publish.yml`), který provede tyto kroky:

1. Spustí unit testy a kontroly (`tools/lint.py`, počet stran jednotlivých písniček), vygeneruje odvozené soubory a zkompiluje `zpevnik.tex` do PDF. U pull requestů navíc porovná PDF po jednotlivých písničkách s PDF před změnou.
2. Spočítá aktuální verzi zpěvníku, která má tři čísla `major.minor.patch` (např. `8.33.67`; počítá to `tools/generate.py`, stejně jako verzi v tiráži, a `python3 tools/generate.py --version` ji vypíše):
   - `major.minor` je počet písniček ve složce `pisnicky` + 100 (733 písniček dává 8.33),
   - `patch` je počet commitů v hlavní větvi (first-parent) od posledního commitu, který změnil počet písniček. Přidání písničky tedy začíná znovu od 0 a každá další změna (oprava textu, nástrojů, vzhledu) číslo zvýší o 1. Verze tak určuje jedno konkrétní sestavení PDF. Počítá se z historie Gitu, takže stejný výsledek dá CI i lokální sestavení s celou historií; bez ní (např. `git clone --depth 1`) vyjde `8.33.?`.
3. Vytvoří GitHub Release s tagem `v<verze>` (např. `v8.33.67`) a názvem `Zpěvník v8.33.67` a přiloží k němu zkompilované PDF ke stažení. Existující tag se nikdy nepřepisuje ani nepřesouvá: pokud tag už existuje (stává se to jen tehdy, když se po smazání písniček vrátí počet na dřívější hodnotu), workflow skončí chybou dřív, než cokoli zveřejní. Starý tag `v8.33` zůstává.
4. Zapíše aktuální verzi a zkompilované PDF do repozitáře webu ([zpevnik-web](https://github.com/f-hluchnik/zpevnik-web)) a tuto změnu tam commitne a pushne.

Push do repozitáře webu následně spustí jeho vlastní publikační workflow, který web přebuilduje (mimo jiné vypíše aktuální verzi na hlavní stránku) a nasadí přes GitHub Pages. Odkaz ke stažení na webu tedy vždy směřuje na nejnovější verzi zpěvníku, a stažený soubor má ve svém názvu i příslušné číslo verze.

Díky tomu stačí přidat písničku a pushnout — o zbytek (kompilace, publikace, aktualizace webu) se postará automatizace.

## Přepisování písniček
V této sekci popíšu postup a konvence přepisování písniček. Nejprve uvedu povinné součásti písničky:

1. název a interpret
    - Na začátku písničky je příkaz `\song`, který vytváří název písničky. Tento příkaz udělá z názvu automaticky odkaz na obsah. Na stejný řádek patří `\artist{}` s interpretem (viz níže).
Na konec písničky žádný příkaz pro novou stranu nepatří: každá písnička se vkládá příkazem `\songinclude{id}` (generuje se do `generated/include.tex`, `id` je název souboru bez `.tex`), který sám začíná novou stranu. Stejné `id` použije `\song` jako cíl odkazu z obsahu, takže cíl odkazu se do písničky nepíše.

Následuje přehled příkazů, které se v písničce používají. Příkazy pro akordy jsou v sekci „Psaní akordů“ níže, metadata (`\alttitle`, `\toctitle`, `\collection`) a `\artist` výše.

#### Hlavička

| Příkaz | Co dělá | Příklad |
|---|---|---|
| `\song{}` | název písničky, odkaz do obsahu | `\song{Hotel California} \artist{eagles}` |
| `\subtitle{}` | podnázev pod názvem | `\subtitle{(Pomalu)}` |
| `\seealso{id}{}` | řádek s odkazem na jinou písničku | `\seealso{folsomprisonblues}{Folsom Prison Blues}` |

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

### Noty
Každý obrázek s notami je jeden soubor `scores/<název>.mscz` z MuseScoru 4 a v písničce ho vysází `\score{<název>}`. Na začátku bloku stojí vedle štítku (`\intro{` + `\score{pohadka}` + `}`), jinde na vlastním řádku. Do písničky se nepíše žádné odsazení, posun ani šířka: obrázek začíná tam, kde text bloku, štítek stojí uprostřed první osnovy a všechny noty mají stejné měřítko (celý systém přesně vyplní řádek).

- Před úpravou noty načti v MuseScoru sdílený styl `scores/zpevnik.mss` (Formát → Styl → Načíst styl). Sestavení ho stejně použije na každý soubor, takže jen tak uvidíš rozdělení do systémů, jaké bude ve zpěvníku.
- Nota je vždy na jedné stránce. Víc obrázků v jedné písničce znamená víc souborů (`morseovka_1.mscz`, `morseovka_2.mscz`).
- Noty z MuseScoru ručně neexportuj: `make` (nebo `make scores`) je vyexportuje do `generated/scores/` sám a přeskočí ty, které se nezměnily. Akordy dostanou stejnou červenou jako ve zpěvníku.
- Písnička otevřená samostatně (Overleaf) místo not ukáže rámeček s názvem.
- `tools/lint.py` hlásí `\score` bez souboru `.mscz` a soubor, který žádná písnička nepoužívá.

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

Mezery mezi akordy a texty se nepíšou ručně, o rozestup se stará sazba: akord a jeho text zabírají aspoň šířku akordu plus půl em (mezi dvěma akordy bez textu je to šířka akordu plus 1 em), takže se akordy nikdy nepřekryjí a text se hýbe jen tam, kde by se akord srazil s dalším. Uvnitř slova se v takovém místě vysází vystředěný spojovník. Starší příkazy `\nc`, `\mm`, `\sm` a `\bc` už neexistují a `tools/lint.py` je v písničce nahlásí jako chybu.
- `\gap{n}` - záměrná pauza (akord zazní a zpívá se až za chvíli), `n` je počet znaků po půl em, například `\chord{G}\gap{4}text`. Uvnitř slova pauzu nepíšu.
- `\chords{}` - řádek samých akordů bez slov (intro, konec řádku, `\intro{\chords{Am F G}}`), akordy se píšou oddělené mezerou a vysázejí se červeně. Jeden řádek lze zúžit nebo rozšířit volitelným parametrem, např. `\chords[0.55em]{Am F G}`.

### Interpreti a registr interpretů
Každá písnička má na řádku s `\song{}` příkaz `\artist{<kotva>}`, například `\artist{ericclapton}` pro Erica Claptona. Kotva je záznam v souboru `data/artists.toml`; odtud se bere i jméno interpreta, které se vysází vpravo nahoře jako odkaz na jeho sekci v obsahu. Jméno lze u jedné písničky přepsat: `\artist[Jiné jméno]{ericclapton}`. Má-li písnička dva interprety, napíšu `\artist{prvni}\artist{druhy}` (první je vpravo, třetí se nevysází). Písnička bez známého interpreta má `\artist{}`; prázdná nebo neznámá kotva nevysází nic (kontrola `tools/lint.py` ale neznámou kotvu nahlásí jako chybu).

Záznam v `data/artists.toml` potřebuje jen dvě položky, ostatní píšu, jen když výchozí hodnota nesedí (celý popis je na začátku souboru):
- `slug` - kotva: jméno malými písmeny bez diakritiky a mezer, bez úvodního členu (`beatles`, ne `thebeatles`).
- `name` - nadpis sekce a jméno v rejstříku, u osob ve tvaru "Příjmení, Jméno". Podle něj (přesněji podle `sort`) se interpreti řadí.
- `label` - jméno vysázené u písničky (výchozí je "Jméno Příjmení"), `link_label` - kratší jméno u písničky, `sort` - jiný klíč řazení, `kind = "collection"` - sbírka místo interpreta, `section = false` - interpret bez vlastní sekce.

Každý záznam se sekcí (výchozí) musí mít aspoň jednu písničku. U interpreta bez sekce (`section = false`) se jeho jméno u písničky nevysází (odkaz by nikam nevedl) a v rejstříku není; až bude mít tři písničky, `tools/lint.py` upozorní, že by si sekci zasloužil.

### Doporučení pro psaní písniček
Kompilace celého zpěvníku v běžných IDE pro LaTeX probíhá kvůli počtu souborů příliš dlouho. Navykl jsem si proto používat k psaní písničky pouze zjednodušený projekt na Overleafu. Stačí do něj nahrát soubor `zpevnik.sty` a jednoduchý hlavní soubor, který importuje jedinou přepisovanou písničku (vzor je v `tests/single-song.tex`). Obsah ani registr interpretů tam nejsou, proto se jméno interpreta nevysází; písnička se ale zkompiluje bez chyby. Jakmile mám písničku přepsanou, provedu následující kroky. Používám editor vim, je však možné použít kterýkoli jiný textový editor.

1. Vytvořím nový soubor písničky `vim pisnicky/<nazevpisnicky>.tex`.
2. Překopíruju zdrojový text z Overleafu do tohoto souboru a uložím.
3. Doplním `\artist{}` a případně přidám interpreta do `data/artists.toml`.
4. Spustím `make` a zkontroluji písničku v celém zpěvníku. Import do `zpevnik.tex` ani odkazy do obsahu nepřidávám, vše se vygeneruje.

### Šikovné příkazy
- vyhledání souboru písničky `ls pisnicky | grep <nazevpisnicky>`
- vyhledání souboru obsahujícího daný text `grep -lr <text> ./ -s`
- kontrola počtu písniček `ls pisnicky/*.tex | wc -l`
- vygenerování obsahu a kompilace zpěvníku `make` (jen generování: `make generate`)
- kompilace jedné písničky `make song SONG=<id>` (výsledek `build/<id>.pdf`)
- kontrola písniček a registru interpretů `python3 tools/lint.py`
- unit testy nástrojů `python3 -m unittest discover -s tools`
- kontrola, že každá písnička je na jedné stránce `python3 tools/check_pages.py` (po `make`)
- kontrola, že se akordy na jednom řádku nepřekrývají `python3 tools/chord_gaps.py` (po `make`; překryv akordů kdekoli v knize je chyba)

## Licence a autorská práva
Zpěvník je nekomerční a šíří se zdarma. Autorská práva k textům, hudbě a akordům písní (`pisnicky/`), k notám (`scores/`) a k PDF z nich sestaveným patří autorům písní; licence tohoto repozitáře se na ně nevztahuje. Totéž platí pro úvodní strany (`preamble/`, úvod cituje text Vlasty Redla) a obálku (`obrazky/`, nakreslila Ivana Vlčková). Licence Apache 2.0 (soubor `LICENSE`) platí jen pro mou vlastní práci: skripty, styl a strukturu dokumentu, registr interpretů a dokumentaci. Držitelé práv, kteří si nepřejí, aby zde jejich píseň byla, mi mohou napsat na frantahluchnik@gmail.com a píseň odstraním.

Stejné upozornění je v tiráži zpěvníku (`preamble/upozorneni.tex`) a v patičce webu; když se mění, mění se na obou místech.

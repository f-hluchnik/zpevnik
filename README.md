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

### Název písničky v obsahu
Písnička se v obsahu řadí a vypisuje podle názvu v `\song{}`. Tyto řádky na začátku řádku za `\song{}` na stránce nic nevysází, jen řídí obsah:
- `\alttitle{<jiný název>}` - jiný název, pod kterým se písnička zpívá (třeba první řádek textu). V obsahu má vlastní kurzívou psanou položku pod svým písmenem. Je možné jich uvést víc.
- `\toctitle{<název v obsahu>}` - název pro obsah a řazení, když se musí lišit od `\song`, například `Marie (Klus)`, když existují dvě písničky se stejným názvem. Skript `tools/lint.py` na stejné názvy upozorní.
- `\collection{<kotva>}` - zařadí písničku do sbírky, třeba `\collection{filmy}` do sekce "z pohádek, filmů, muzikálů, her a seriálů".

## Automatické publikování

Zpěvník se po každém pushi do větve `master` automaticky zkompiluje a nová verze PDF se zveřejní na webu (https://zpevnik.hluchnikovi.cz), aniž by bylo potřeba cokoliv dělat ručně. Zajišťuje to GitHub Actions workflow (`.github/workflows/build-and-publish.yml`), který provede tyto kroky:

1. Spustí unit testy a kontroly (`tools/lint.py`, počet stran jednotlivých písniček), vygeneruje odvozené soubory a zkompiluje `zpevnik.tex` do PDF. U pull requestů navíc porovná PDF po jednotlivých písničkách s PDF před změnou.
2. Spočítá aktuální verzi zpěvníku podle počtu souborů ve složce `pisnicky` (počet písniček + 100, tedy 733 písniček dává verzi 8.33; počítá to `tools/generate.py`, stejně jako verzi v tiráži).
3. Vytvoří GitHub Release s tagem odpovídajícím verzi (např. `v8.19`) a přiloží k němu zkompilované PDF ke stažení.
4. Zapíše aktuální verzi a zkompilované PDF do repozitáře webu ([zpevnik-web](https://github.com/f-hluchnik/zpevnik-web)) a tuto změnu tam commitne a pushne.

Push do repozitáře webu následně spustí jeho vlastní publikační workflow, který web přebuilduje (mimo jiné vypíše aktuální verzi na hlavní stránku) a nasadí přes GitHub Pages. Odkaz ke stažení na webu tedy vždy směřuje na nejnovější verzi zpěvníku, a stažený soubor má ve svém názvu i příslušné číslo verze.

Díky tomu stačí přidat písničku a pushnout — o zbytek (kompilace, publikace, aktualizace webu) se postará automatizace.

## Přepisování písniček
V této sekci popíšu postup a konvence přepisování písniček. Nejprve uvedu povinné součásti písničky:

1. cíl odkazu
    - Na začátku každé písničky musí být příkaz `\hyt{}`, který označuje cíl pro odkaz z obsahu.
2. název a interpret
    - Následuje příkaz `\song`, který vytváří název písničky. Tento příkaz udělá z názvu automaticky odkaz na obsah. Na stejný řádek patří `\artist{}` s interpretem (viz níže).
Na konec písničky žádný příkaz pro novou stranu nepatří: každá písnička se vkládá příkazem `\include`, který sám začíná novou stranu.

Následuje popis důležitých součástí písničky.

1. sloka
    - Příkaz `\vers{}{}` vysází číslo sloky s tečkou a sloku. Používá s pro sloku. V prvních složených závorkách je číslo sloky, ve druhých složených závorkách je text sloky.
2. refrain
    - Příkaz `\refrain{}`vysází R s tečkou. Používá se pro refrain.
    - Příkaz `\refrainn{}{}` vysází R s tečkou a číslem. Používá se pro číslovaný refrain. V první závorce je číslo refrainu a ve druhé samotný refrain.
3. ostatní části písničky
    - Přkaz `\intro{}` vysází I s tečkou. Používá se pro úvodní část písničky.
    - Příkaz `\bridge{}` vysází B s tečkou. Používá se pro bridge.
    - Příkaz `\solo{}` vysází S s tečkou. Používá se pro označení sóla.
    - Příkaz `\solon{}{}` vysází S s tečkou. Používá se pro označení číslovaného sóla. V první závorce je číslo sóla, ve druhé samotné sólo.
    - Příkaz `\cod{}` vysází C s tečkou. Používá se pro označení cody.
    - Příkaz `\refsm{}` vysází R s tečkou. Používá se pro označení místa, kde se začíná zpívat refrain, který už byl uveden dříve. Pokud je refrain nečíslovaný, jsou složené závorky prázdné. Pokud je refrain číslovaný, vepíšeme číslo refrainu do složených závorek.
    - Příkaz `\solsm{}` vysází S s tečkou. Používá se pro označení místa, kde začíná sólo, které už bylo uvedeno dříve. Pokud je sólo nečíslované, jsou složené závorky prázdné. Pokud je sólo číslované, vepíšeme číslo sóla do složených závorek.
    - Příkaz `\sub{}` vysází podnázev písničky.
    - Příkaz `\rep{}` vysází označení repetice v textu.
    - Příkaz `\rec{}` vysází označení recitativu v textu.
    
### Psaní akordů
V této sekci popíšu psaní akordů a příkazy potřebné k vysázení různých akordových značek. Základním příkazem pro psaní akordů je příkaz `\chord{}`. Tento příkaz vysází akord nad bezprostředně následující text. Do složených závorek uvádím název akordu velkým písmenem. Charakteristiku akordu uvádím za akord příkazem podle následujícího seznamu. Výjimkou je mollový akord, který označím jednoduše písmenem "m".
- `\add{}` - manuální horní index, například pro akord typu C<sup>4/6</sup>.
- `\bas{}` - dolní index pro postupky v basu
- `\sus{}` - sus akord
- `\maj` - maj7 akord
- `\dm` - zmenšený akord (dim)
- `\hdm` - malý zmenšený akord (m7/5-)
- `+` - zvětšený akord
- `\bb` - béčko
- `\kk` - křížek
- `\2-9` - 2-9 akord, patřičně podle čísla

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
- kontrola písniček a registru interpretů `python3 tools/lint.py`
- unit testy nástrojů `python3 -m unittest discover -s tools`
- kontrola, že každá písnička je na jedné stránce `python3 tools/check_pages.py` (po `make`)

# O zpěvníku
Tento zpěvník se jmenuje "Ještě mi chvilku zpívej" a obsahuje různé písničky podle vůle mé a postupem času i dalších lidí, kteří z něj zpívali.
Odkaz na Trello nástěnku s frontou písniček k přepsání: [nastenka-fronta-pinicek](https://trello.com/b/sJi9Cjii/ještě-mi-chvilku-zpívej).
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
V této části popíšu postup přidání nové písničky do Zpěvníku, jak jsem si to navykl dělat.

1. Ve složce `pisnicky` vytvořím soubor s názvem podle názvu písničky. Název souboru se tvoří odebráním diakritiky a mezer z názvu písničky a zapsáním tohoto názvu malými písmeny. Je-li potřeba odlišit dvě písničky se stejným názvem od různých interpretů, učiní se tak přidáním jména interpreta (pokud možno jednoslovně, tedy příjmení nebo název skupiny) za jméno písničky, opět bez mezer a diakritiky, malými písmeny. Je možné použít šablonu, která je umístěna v kořenovém adresáři zpěvníku.
2. V souboru `zpevnik.tex` přidám řádek `\include{pisnicky/<nazevpisnicky>}` do patřičné sekce. Je potřeba písničku správně zařadit, aby se ve zpěvníku dodrželo řazení podle abecedy.
3. V souboru `obsah.tex` přidám do patřičné sekce řádek `\hylo{<nazevsouborupisnicky>}{<název písničky>}` a vytvořím tak v obsahu odkaz na danou písničku. Pokud má písnička známého interpreta, je potřeba přidat tento odkaz i do části obsahu řazené podle interpretů. Opět dbám na správné abecední zařazení.
4. Otevřu si soubor s písničkou a začnu přepisovat. Více o přepisování písniček dále.
5. Zkontroluji přepsanou písničku nejlépe tím, že si ji přehraji.
6. Upravím číslo verze zvýšením o setinku.

## Přepisování písniček
V této sekci popíšu postup a konvence přepisování písniček. Nejprve uvedu povinné součásti písničky:

1. cíl odkazu
    - Na začátku každé písničky musí být příkaz `\hyt{}`, který označuje cíl pro odkaz z obsahu.
2. název
    - Následuje příkaz `\song`, který vytváří název písničky. Tento příkaz udělá z názvu automaticky odkaz na obsah.
3. \newpage
    - Aby každá písnička byla na nové stránce, je potřeba na konec každé písničky přidat příkaz pro novou stranu.    

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

### Další poznámky pro psaní písniček
V případě, že má písnička známého interpreta, je potřeba uvést odkaz na sekci obsahu řazenou podle interpretů. To se vysází příkazem například `\interpret{clapton}{Eric Clapton}` pro Erica Claptona. V první závorce je uvedena kotva odkazu v obsahu, ve druhé závorce je jméno interpreta.

### Doporučení pro psaní písniček
Kompilace celého zpěvníku v běžných IDE pro LaTeX probíhá kvůli počtu souborů příliš dlouho. Navykl jsem si proto používat k psaní písničky pouze zjednodušený soubor zpevnik.tex. Zjednodušení spočívá v tom, že namísto importování všech souborů s písničkami importuji pouze přepisovanou písničku. V praxi to funguje tak, že mám zjednodušený soubor zpevnik.tex na Overleafu a přepisuji písničky tam. Jakmile mám písničku přepsanou, provedu následující kroky. Používám editor vim, je však možné použít kterýkoli jiný textový editor.

1. Vytvořím nový soubor písničky `vim pisnicky/<nazevpisnicky>.tex`.
2. Překopíruju zdrojový text z Overleafu do tohoto souboru a uložím.
3. Přidám import písničky do souboru zpevnik.tex.
4. Přidám odkaz(y) na písničku do obsahu.
5. Zvýším verzi zpěvníku ve vydavatelské poznámce o setinku.
6. Zkompiluji zpěvník v terminálu `pdflatex zpevnik.tex`.

### Šikovné příkazy
- vyhledání souboru písničky `ls pisnicky | grep <nazevpisnicky>`
- vyhledání souboru obsahujícího daný text `grep -lr <text> ./ -s`

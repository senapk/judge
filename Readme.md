## @qxcode
-|-|-
-|-|-
[Categorias](categorias.md#qxcode) | [Foto Board](view.md#qxcode) |  [Sumário](summary.md#qxcode)

Esse projeto implementa um indexador de arquivos do tipo markdown. 

- Funcionalidades:
    - Organizar por tags, categorias, data, autor ou título.
    - Alterar os títulos dos arquivos através de um único lugar.
    - Gerar a pasta _posts do jekyll.
    - Gerar links para fácil localização dos arquivos utilizando `Control P` da sua `ide`.
    - Gerar as thumbnails das para montar um Photo Board.

## Instalação Linux

```
sh -c "$(wget -O- https://raw.githubusercontent.com/senapk/th/master/tools/linux_install.sh)"
```

## Instalação

Baixe o arquivo indexer.py para o path da sua distro onde ele possa ser encontrado.


## Arquivos MD
Nos arquivos indexados, a primeira linha é utilizada para inserir os dados como categoria, tags, data, etc. Um caractere de marcação define cada informação. Os caracteres utilizados podem ser escolhidos no arquivo de configuração.

Exemplo:
```
## Aqui é o título ©categoria #tag1 #tag2 ð2019-10-29 æautor ß Após isso tudo é subtítulo.
```

- Nesse exemplo acima:
    - `Alt Gr + c` para categoria: ©
    - `Alt Gr + s` para subtítulo: ß
    - `Alt Gr + d` para data: ð
    - `Alt Gr + a` para autor: æ

## A capa
- A capa será o primeiro arquivo de imagem adicionado ao seu markdown através do `![description](path)`.

## Uso
No diretório root onde deseja indexar seus arquivos execute `indexer.py --init` para criar o arquivo de configuração `.indexer.json`.

## Significado das chaves
- base: onde estão localizados seus arquivos
- board: o arquivo que poderá utilizar para editar o título dos seus arquivos.
- links: se for diferente de nulo, será a pasta onde os links serão gerados.
- thumbs: se for diferente de nulo, será onde os thubms serão gerados.
- symbols: quais símbolos serão utilizados para identificar os elementos no título do seu arquivo.
- generate: os arquivos que serão gerados.
    - Toda entrada do generate precisa ter um modo.
    - Os modos são : [index, view, summary, posts]
    - index, view and summary
        - precisam de uma entrada `path` onde o arquivo será gerado.
        - precisam de uma entrada `sorting` informando como será a organização dos dados.
        - podem receber opcionalmente uma entrada `intro` com um arquivo cujo conteúdo será utilizado no início.
    - posts é utilizado para gerar o folder posts utilizado no jekyll

```json
{
    "base": "base",
    "config": ".indexer",
    "board" : ".indexer/board.md",
    "links" : ".indexer/links",
    "thumbs": ".indexer/thumbs",
    "symbols": {
        "tag": "#",
        "category": "$",
        "date": "ð",
        "author": "æ",
        "subtitle": "ß"
    },
    "generate":[
        {
            "mode": "index", 
            "path": "categorias.md",
            "intro" :"intro.md",
            "sorting":{
                "orphan": "Sem categoria",
                "group_by"  : "category",
                "sort_by" : "fulltitle",
                "reverse_sort": false
            }
        }, 
        {            
            "mode": "view", 
            "path": "view.md",
            "sorting":{
                "orphan": "sem tag",
                "group_by": "tag",
                "sort_by" : "fulltitle",
                "reverse_sort": false
            },
            "viewing":{ 
                "empty_fig" : null, 
                "posts_per_row"   : 4
            }
        }, 
        {
            "mode": "summary", 
            "path": "summary.md", 
            "intro": "intro.md",
            "sorting":{
                "orphan": "Sem tag",
                "group_by": "category",
                "sort_by" : "fulltitle",
                "reverse_sort": false
            }
        }, 
        {
            "mode": "posts",
            "dir": "_posts",
            "github_id": "youid",
            "repository": "repository"
        }
    ]
}
```

## O board
O arquivo board reune todos os títulos de todos os arquivos encontrados. Se esse arquivo for editado, um `indexer.py -s` irá alterar o conteúdo dos arquivo nas pastas.
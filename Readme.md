# Ferramentas para construção de banco de questões para juiz online integrado no moodle

[](toc)
- [mdpp](#mdpp)
- [filter](#filter)
- [make_thumbs](#make_thumbs)
- [md2html](#md2html)
- [rep_run_all](#rep_run_all)
- [rep_push_all](#rep_push_all)
- [rep_full_push_to_moodle](#rep_full_push_to_moodle)
- [rep_mirror](#rep_mirror)
- [configurações mais comuns para o problema](#configurações-mais-comuns-para-o-problema)
    - [local.sh](#localsh)
    - [Opção 1 - tudo no Makefile, deixando os links para o student.cpp](#opção-1---tudo-no-makefile-deixando-os-links-para-o-studentcpp)
    - [Opção 2 - arquivo simples sem makefile, deixando o solver sem respostas no moodle](#opção-2---arquivo-simples-sem-makefile-deixando-o-solver-sem-respostas-no-moodle)
    - [Opção 3 - opção sem makefile, gerando o student manualmente no arcade](#opção-3---opção-sem-makefile-gerando-o-student-manualmente-no-arcade)
- [mapi_default](#mapi_default)
- [mapi_build](#mapi_build)
[](toc)


## mdpp

- Gera o toc em arquivos md. 

<!--add teste.h cpp-->

<!--filter teste.h cpp-->


## filter
- Filter code using tags in code to include, exclude
filter solver.cpp -o solver.cpp

## make_thumbs
generate thumbs in all base folders where cover exists and thub is is missing and warning if cover is missing

## md2html
uses pandoc and default css style to generate .html file from .md Readme

## rep_run_all
- used to run problems and test solvers in batch
- if hook has Makefile, just run the makefile
- if hook dont have Makefile, just run tk run -p .
- `rep_run_all 00` runs all hooks starting with 00

## rep_push_all
- commit and push arcade and moodle reps

## rep_full_push_to_moodle
- send all arcade problems do a moodle repository using `mapi`.

## rep_mirror
Mirror arcade to moodle rep using the following rules
- for each hook in arcade
    - if timestamp is newer then moodle hook, rebuild all
    - remove moodle hook folder
    - copy the entire arcade hook folder
    - update Readme.md making all local links becoming remote links to moodle github rep
    - if exists, run `hook/local.sh`
    - if `mapi_default.sh` exists, run it, otherwise run `mapi_default.hs` from mapi repository

## configurações mais comuns para o problema
- o arquivo de descrição deve ser Readme.md, e a primeira linha será utilizada como título da questão.
- o nome da pasta da questão será o label dela no moodle.
- arquivos como main*, data* e lib* vão ser enviados como arquivos auxiliares do problema.
- se houver arquivo student*, o primeiro será utilizado como required.
- arquivos vpl_* serão subir como scripts do vpl tal qual vpl_execution.sh.
- se houver Makefile na pasta, o vpl run -p folder vai rodar o Makefile ao invés do comportamento default

### local.sh
Esse arquivo pode ser criado dentro da pasta do problema e pode ter as seguintes configuração
```sh
required=student.cpp #se existir, defino o nome do arquivo que será utilizado como arquivo requerido
rename=solver.cpp #se existir, define para qual nome o arquivo required será renomeado no moodle
problem="file1 file2 file3" # se existir, define quais arquivo vão subir como arquivos extras do problema

comando1 # se existirem, serão executados antes do script padrão
comando2
```

### Opção 1 - tudo no Makefile, deixando os links para o student.cpp
- o Makefile pode ser algo como
- Os arquivos podem estar organizados para utilizar o student.cpp nos includes

```
all:
    cp solver.cpp student.cpp
    g++ student.cpp main.cpp lib.cpp -o solver.out
    tk run solver.out Readme.md
    filter solver.cpp -o student.cpp
```
- Assim ele usa o solver.cpp para "guardar" a resposta, faz a execução usando o student.cpp.
    - Não precisa de configuração do local.sh, fica tudo já "pronto" no arcade.

### Opção 2 - arquivo simples sem makefile, deixando o solver sem respostas no moodle
```sh
# local.sh
required=solver.cpp
filter solver.cpp -o solver.cpp
```

No rep moodle, ele filtra o solver.cpp para a versão sem as respostas e utiliza como required


### Opção 3 - opção sem makefile, gerando o student manualmente no arcade
```sh
required=student.cpp
rename=solver.cpp
```
Faz o filter manualmente na pasta arcade e sobe ele com o nome de solver.cpp


## mapi_default
- roda em cada pasta moodle/hook para gerar o arquivo json .mapi
- se existir na pasta um arquivo mapi_default.sh, ele será utilizado ao invés do script padrão.

- por default tem o seguinte comportamento:
    - pega como nome da questão a primeira linha do Readme.md
    - gera o html de descrição a partir do Readme.md
    - se não houver arquivo `q.tio`, utiliza o `tk build` para gerar o `q.tio` a partir de todos os arquivos .tio e .vpl na pasta
    - pega todos os arquivos `vpl_*` para subir como scripts do vpl. Exemplo: `vpl_execution.sh`.
    - pega todos os arquivos iniciados por `main`, `data` e `lib` como arquivos de questão, case insensitive.
    - invoca o mapi_build passando os arquivos encontrados e gerados para gerar o mapi.json.


## mapi_build
- utilizado pelo mapi_default para gerar o arquivo json que vai conter todos os dados da questão.
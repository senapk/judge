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

- Gera o toc em arquivos md dentro dessas tags.

```
[](toc)

[](toc)
```


## filter
- Filtra o arquivo de solução utilizando as seguintes tags

```
//++1
corta tudo com mais de uma tabulação
//==
inclui tudo
//--
remove tudo

```

```
# invocação é feita assim
filter solver.cpp -o solver.cpp
```

## make_thumbs
generate thumbs in all base folders where cover exists and thub is is missing and warning if cover is missing

## make_html
Uses pandoc and default css style to generate .html file from .md Readme

## make_remote
Converte os links locais para links remotos

## make_hook_remote
Adiciona o hook no nome da questão e muda os links para o modo remoto

## rep_run_all
- used to run problems and test solvers in batch
- if hook has Makefile, just run the makefile
- if hook dont have Makefile, just run tk run -p .

- `rep_run_all 00` runs all hooks starting with 00

## rep_push_all
- commit and push arcade and moodle reps

## rep_full_push_to_moodle
- send all arcade problems do a moodle repository using `mapi`.

## mapi_def.sh
- roda em cada pasta base/hook para gerar o arquivo json `.cache/mapi.json`.
- antes, ele executa o local.sh se existir

- por default tem o seguinte comportamento:
    - pega como nome da questão a primeira linha do Readme.md
    - gera o html de descrição a partir do Readme.md
    - se não houver arquivo `cases.tio`, utiliza o `tk build` para gerar o `cases.tio` a partir de todos os arquivos .tio e .vpl na pasta
    - pega todos os arquivos `vpl_*` para subir como scripts do vpl. Exemplo: `vpl_execution.sh`.
    - invoca o mapi_build passando os arquivos encontrados e gerados para gerar o `.cache/mapi.json`.

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


### Opção 3 - opção sem makefile, gerando o student manualmente no arcade
```sh
#local.sh
required=student.cpp
rename=solver.cpp

filter solver.cpp -o student.cpp
```

Faz o filter manualmente na pasta arcade e sobe ele com o nome de solver.cpp

## mapi_build
- utilizado pelo mapi_default para gerar o arquivo json que vai conter todos os dados da questão.

## chech_build
verifica se houve modificação na pasta atual desde a última geração do mapi.json
#!/bin/bash

# this variables could be replaced in local_script
required="" #if defined in
rename=""   #if defined, the required file will be renamed in moodle
readme=./Readme.md

# running local scripts
local_script=./local.sh
[[ -f "$local_script" ]] && source "$local_script"

# load title
title=`head -1 "$readme" | sed 's/[#^ ]* *//'`

# building description
description=./q.html
md2html $readme -o "$description"

# building tests if not found
sources=`find . -name "*.tio" -o -name "*.vpl"`
cases=./q.tio
[[ ! -f $cases ]] && tk build "$cases" $readme $sources

# procurando por arquivos de funcionamento do vpl
vpl_scripts=`find . -type f -maxdepth 1 -iname "vpl_*"`

# procurando por arquivos de definição do problema
keep=`find . -type f -maxdepth 1 -iname "data*" -o -iname "main*" -o -iname "lib*"`

# gerando o arquivo final
output=./mapi.json
mapi_build  "$title" "$description"\
            --tests     "$cases"\
            --upload    $vpl_scripts\
            --keep      $keep\
            --required  "$required" "$rename"\
            --output    "$output"

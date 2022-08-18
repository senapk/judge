#!/bin/bash

# this variables could be replaced in local_script
required="" #if defined in
rename=""   #if defined, the required file will be renamed in moodle
readme=./.cache/Readme.md
description=./.cache/q.html
cases=./.cache/q.tio
output=./.cache/mapi.json

# running local scripts
local_script=./local.sh
[[ -f "$local_script" ]] && source "$local_script"

# load title
title=`head -1 "$readme" | sed 's/[#^ ]* *//'`

# building description
md2html $readme -o "$description"

# building tests if not found
sources=`find . -name "*.tio" -o -name "*.vpl"`
[[ ! -f $cases ]] && tk build "$cases" $readme $sources

# procurando por arquivos de funcionamento do vpl
vpl_scripts=`find . -maxdepth 1 -iname "vpl_*"`

# procurando por arquivos de definição do problema
keep=`find . -maxdepth 1 -iname "data*" -o -iname "main*" -o -iname "lib*"`

# gerando o arquivo final
mapi_build  "$title" "$description"\
            --tests     "$cases"\
            --upload    $vpl_scripts\
            --keep      $keep\
            --required  "$required" "$rename"\
            --output    "$output"

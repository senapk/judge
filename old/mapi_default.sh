#!/bin/bash

# this variables could be replaced in local_script
required="" #if defined in
rename=""   #if defined, the required file will be renamed in moodle
upload=""   #vpl scripts like vpl_evaluate.cpp
keep=""     #problem files like main.cpp lib.hpp

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

# gerando o arquivo final
mapi_build  "$title" "$description"\
            --tests     "$cases"\
            --upload    $upload\
            --keep      $keep\
            --required  "$required" "$rename"\
            --output    "$output"


# erasing temporary files
# rm -f "$readme" "$cases" "$description"
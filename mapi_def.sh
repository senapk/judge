#!/bin/bash

# this variables could be replaced in local_script
required="" #if defined in
rename=""   #if defined, the required file will be renamed in moodle
upload=""   #vpl scripts like vpl_evaluate.cpp
keep=""     #problem files like main.cpp lib.hpp

user=$1
repo=$2

# create dir if not found
[[ ! -d .cache ]] &&  mkdir .cache


check_rebuild || exit 0

rm -rf .cache
mkdir .cache

# running local scripts
local_script=local.sh
[[ -f "$local_script" ]] && source "$local_script"

# creating remote readme
rm_readme=.cache/Readme.md
make_hook_remote -i "Readme.md" -o "$rm_readme"

# building description
description=.cache/q.html
make_html $rm_readme -o "$description"

# load title
title=`head -1 "$rm_readme" | sed 's/[#^ ]* *//'`

# building tests if not found
cases=.cache/q.tio
sources=`find . -name "*.tio" -o -name "*.vpl"`
[[ ! -f $cases ]] && tko build "$cases" $rm_readme $sources

# build filelist for tk down
# remove .cache .vscode, solver.* Solver.* _*
filelist=.cache/filelist.txt
du -ah | cut -f2 | sed '/\.cache/d;/\.vscode/d;/solver\./d;/Solver\./d;/\/_/d;/\./!d' | cut -c 3- > "$filelist"

# gerando o arquivo final
output=./.cache/mapi.json
make_mapi  "$title" "$description"\
            --tests     "$cases"\
            --upload    $upload\
            --keep      $keep\
            --required  "$required" "$rename"\
            --output    "$output"


# erasing temporary files
rm -f "$cases" "$description"
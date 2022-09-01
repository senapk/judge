#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# cria o readme, cria as thumbs e roda o mapi default

import os
import sys
from typing import List
from os.path import join, getmtime
import glob

# return the last update for the most recent file in the directory
def last_update(path):
    value = 0
    if os.path.isfile(path):
        value = getmtime(path)
    else:
        file_list = list(glob.iglob(path + '/**', recursive=True))
        file_list = [f for f in file_list if os.path.isfile(f)]
        # juntos = [(f, getmtime(f)) for f in file_list]
        # print(juntos)
        if len(file_list) == 0:
            value = getmtime(path)
        else:
            value = max([getmtime(f) for f in file_list])
    # print (value)
    return value

def check_rebuild(source: str, target: str) -> bool:
    if not os.path.exists(target):
        return True
    # source tem novas alterações
    return last_update(source) > last_update(target)

def main():
    dir1 = sys.argv[1]
    dir2 = sys.argv[2]
    if check_rebuild(dir1, dir2):
        exit(0) # sucesso
    else:
        exit(1) # falha

main()

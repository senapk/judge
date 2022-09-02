#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# cria o readme, cria as thumbs e roda o mapi default

import os
import sys
from typing import List, Tuple
from os.path import join, getmtime
import glob

# return the last update for the most recent file in the directory
def last_update(path) -> Tuple[str, float]:
    value = 0
    if os.path.isfile(path):
        value = (path, getmtime(path))
    else:
        file_list = list(glob.iglob(path + '/**', recursive=True))
        file_list = [f for f in file_list if os.path.isfile(f)]
        # juntos = [(f, getmtime(f)) for f in file_list]
        # print(juntos)
        if len(file_list) == 0:
            value = (path, getmtime(path))
        else:
            juntos = [(f, getmtime(f)) for f in file_list]
            value = max(juntos, key=lambda x: x[1])
    # print (value)
    return value

# retorna se tem atualização e o arquivo mais recente
def check_rebuild(source: str, target: str) -> Tuple[str, bool]:
    if not os.path.exists(target):
        return True
    [source_path, source_time] = last_update(source)
    [target_path, target_time] = last_update(target)
    # source tem novas alterações
    return (source_path, source_time > target_time)

def main():
    dir1 = "."
    dir2 = ".cache/mapi.json"
    [path, result] = check_rebuild(dir1, dir2)
    if result:
        print("changes found in", path)
        exit(0) # sucesso
    else:
        exit(1) # falha

main()

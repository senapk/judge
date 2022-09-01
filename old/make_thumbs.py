#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# receive the folder as parameter

import sys
import os
import subprocess
from os.path import join, isdir, isfile, getmtime

args = sys.argv[1:]
for arg in args:
    if not isdir(arg):
        continue
    cache = join(arg, ".cache")
    if not isdir(cache):
        os.mkdir(cache)
    capa = join(arg, "cover.jpg")
    thumb = join(cache, "thumb.jpg")
    if not isfile(capa):
        print("warning: {} não tem capa".format(arg))
        continue
    # if modification time of thumb is less than capa, rebuild
    if not isfile(thumb) or getmtime(thumb) < getmtime(capa):
        print("gerando {}".format(arg))
        cmd = ["convert", capa, "-resize", "142x80^", "-gravity", "center", "-extent", "142x80", thumb]
        subprocess.run(cmd)

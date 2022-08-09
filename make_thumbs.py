#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess

args = sys.argv[1:]
for arg in args:
    if not os.path.isdir(arg):
        continue
    capa = os.path.join(arg, "__cover.jpg")
    thumb = os.path.join(arg, ".thumb.jpg")
    if not os.path.isfile(capa):
        print("{} não tem capa".format(arg))
        continue
    # if modification time of thumb is less than capa, rebuild
    if not os.path.isfile(thumb) or os.path.getmtime(thumb) < os.path.getmtime(capa):
        print("gerando {}".format(arg))
        cmd = ["convert", capa, "-resize", "142x80^", "-gravity", "center", "-extent", "142x80", thumb]
        subprocess.run(cmd)

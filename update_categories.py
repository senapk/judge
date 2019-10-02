#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from shutil import rmtree
from io import StringIO
from os import mkdir
import json
import re

repository = "qxcodefup.github.io"
header = "site/_includes/header.html"
category_board = "arcade/categories.txt"
category_dir = "site/category"


lines = []
with open(category_board, "r") as f:
    lines = f.readlines()

alive = []
for line in lines:
    if line == "\n":
        continue
    if line[-1] == '\n':
        line = line[:-1]
    data = line.split(":")
    data = [x.strip() for x in data]
    if data[0] != "0":
        alive.append(data)

rmtree(category_dir, ignore_errors= True)
mkdir(category_dir)

buttons = StringIO()
alive.reverse()
for data in alive:
    cat = data[1]
    print(cat, end = " ")
    label = data[2]
    description = data[3]
    with open(category_dir + "/" + cat + ".md", "w") as f:
        f.write("---\n")
        f.write("layout: category\n")
        f.write("title: " + label + "\n")
        f.write("slug: " + cat + "\n")
        f.write("description: " + description + "\n")
        f.write("---\n")

    buttons.write('<a href="https://' + repository + '/category/' + cat + '/" class="get-theme" role="button">\n')
    buttons.write("    " + cat + "\n")
    buttons.write("</a>\n")

print("")

with open(header, "r") as f:
    text = f.read()

with open(header, "w") as f:
    regex = r"<!--BEGIN-->\n(.*?)<!--END-->"
    subst = "<!--BEGIN-->\\n" + buttons.getvalue() + "\\n    <!--END-->"
    result = re.sub(regex, subst, text, 0, re.MULTILINE | re.DOTALL)
    f.write(result)

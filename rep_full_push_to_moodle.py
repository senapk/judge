#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess

def push(section = "", questions = []):
    executable = "/home/tiger/Dropbox/gits/0_tools/mapi/links/mapi"
    cmd = [executable, "-c", "/home/tiger/mapirc/pooisfun"]
    cmd += ["add", "-s", str(section)]
    cmd += questions

    # print(" ".join(cmd))
    subprocess.run(cmd)

with open("Readme.md") as f:
    count = 0
    questions = []
    for line in f:
        if line.startswith("## "):
            if count > 0:
                push(count, questions)
            count += 1
            questions = []
        elif "@" in line:
            label = line.split("@")[1].split(" ")[0]
            questions.append(label)
    push(count, questions)
    
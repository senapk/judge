#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def get_label(line):
    return line.split("@")[1].split(" ")[0].split("]")[0]

output = []
with open("Readme.md") as f:
    count = 0
    lines = f.read().split("\n")
    for line in lines:
        if line.startswith("## "):
            count += 1
        elif "base/" in line and "/Readme.md" in line and "@" in line:
            label = get_label(line)
            output.append(str(count) + ":" + label)

print(" ".join(output))
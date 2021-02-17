#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
from typing import Optional, List, Dict
import json


# Format used to send additional files to VPL
class JsonFile:
    def __init__(self, name: str, contents: str):
        self.name: str = name
        self.contents: str = contents
        self.encoding: int = 0

    def __str__(self):
        return self.name + ":" + self.contents + ":" + str(self.encoding)


class JsonVPL:
    def __init__(self, title: str, description: str, tests: str = ""):
        self.title: str = title
        self.description: str = description
        self.executionFiles: List[JsonFile] = [JsonFile("vpl_evaluate.cases", tests)]
        self.requiredFile: Optional[JsonFile] = None

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def __str__(self):
        return self.to_json()



def load_from_folder(path) -> JsonVPL:
    folder = os.path.normpath(path).split(os.sep)[-1]
    with open(path + os.sep + "Readme.md") as f:
        title = f.read().split("\n")[0]
        words = title.split(" ")
        if words[0].count("#") == len(words[0]):  # only #
            del words[0]
        words = [word for word in words if not word.startswith("#")] #removendo as tags
        title = "@" + folder + " " + " ".join(words)
    with open(path + os.sep + "q.html") as f:
        description = f.read()
    with open(path + os.sep + "q.vpl") as f:
        tests = f.read()
    return JsonVPL(title, description, tests)

def generate(input_folder, output_file: str):
    with open(output_file, "w") as f:
        jvpl = load_from_folder(input_folder)
        f.write(str(jvpl) + "\n")
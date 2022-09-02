#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import argparse
import enum
from typing import Tuple


class Mode(enum.Enum):
    ADD = 1
    RAW = 2
    DEL = 3

class Filter:
    def __init__(self):
        self.mode = Mode.ADD
        self.level = 1

    def evaluate(self, line: str):
        if self.mode == Mode.DEL:
            return False
        if self.mode == Mode.RAW:
            return True
        # mode add
        tab = "    "
        for token in [(self.level + 1) * tab, self.level * tab + "}"]:
            if line.startswith(token):
                return False
        return True

    def transform(self, line: str):
        if self.mode == Mode.RAW:
            return line
        if line == "//":
            return ""
        return line.replace("){", ") {")\
                    .replace("):",   ") :")\
                    .replace(") :",   ") {")\
                    .replace(") const {", ") const; // todo ")\
                    .replace(") {", "); // todo ")

    def process(self, content: str) -> str:
        lines = content.split("\n")
        output = []
        for line in lines:
            if line[-3:-1] == "!+":
                self.mode = Mode.ADD
                self.level = int(line[-1])
            elif line.endswith("!="):
                self.mode = Mode.RAW
            elif line.endswith("!-"):
                self.mode = Mode.DEL
            elif self.evaluate(line):
                line = self.transform(line)
                output.append(line)
        return "\n".join(output)


class Main:
    @staticmethod
    def open_file(path: str) -> Tuple[bool, str]:  
        if os.path.isfile(path):
            with open(path) as f:
                file_content = f.read()
                return True, file_content
        print("Warning: File", path, "not found")
        return False, "" 

def open_file(path): 
        if os.path.isfile(path):
            with open(path) as f:
                file_content = f.read()
                return True, file_content
        print("Warning: File", path, "not found")
        return False, "" 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='file to process')
    parser.add_argument('-u', '--update', action="store_true", help='update source file')
    parser.add_argument('-o', '--output', type=str, help='output file')
    args = parser.parse_args()

    success, content = open_file(args.file)
    if success:
        content = Filter().process(content)
        if args.output:
            if os.path.isfile(args.output):
                old = open(args.output).read()
                if old != content:
                    open(args.output, "w").write(content)
            else:                
                open(args.output, "w").write(content)
        elif args.update:
            with open(args.file, "w") as f:
                f.write(content)
        else:
            print(content)

if __name__ == '__main__':
    main()

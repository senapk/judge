#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from curses.ascii import isupper
import os
import argparse
import enum
from typing import Tuple


class Mode(enum.Enum):
    ADD = 1
    RAW = 2
    DEL = 3

class Filter:
    def __init__(self, cpp_mode: bool):
        self.mode = Mode.RAW
        self.level = 1
        self.cpp_mode = cpp_mode

    # decide se a linha deve entrar no texto
    def evaluate(self, line: str):
        if self.mode == Mode.DEL:
            return False
        if self.mode == Mode.RAW:
            return True
        # mode add
        if line == "":
            return True
        margin = (self.level + 1) * "    "
        if line.startswith(margin):
                return False
        return True

    def transform(self, line: str):
        if self.mode == Mode.RAW:
            return line
        if line == "//":
            return ""
        if self.cpp_mode:
            aux = line;
            while aux.startswith("    "):
                aux = aux[4:]
            if not (aux == "" or aux[0].isupper() or 
                    aux.startswith("void") or 
                    aux.startswith("~")):
                # adding default return
                comp = "{\n" + (self.level + 1) * "    " + "return {}; // todo"
                line = line.replace(") const {", ") const " + comp)\
                                    .replace(") {", ") " + comp)
                return line
        return line.replace(" {", " { //todo");

    def process(self, content: str) -> str:
        lines = content.split("\n")
        output = []
        for line in lines:
            alone = len(line.split(" ")) == 1
            if alone and line[-3:-1] == "++":
                    self.mode = Mode.ADD
                    self.level = int(line[-1])
            elif alone and line.endswith("=="):
                    self.mode = Mode.RAW
            elif alone and line.endswith("--"):
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
        content = Filter(args.file.endswith(".cpp")).process(content)
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

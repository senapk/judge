#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from curses.ascii import isupper
import os
import argparse
import enum
from typing import Tuple

class Mode(enum.Enum):
    ADD = 1 # inserir cortando por degrau
    RAW = 2 # inserir tudo
    DEL = 3 # apagar tudo
    COM = 4 # inserir código removendo comentários

class Filter:
    def __init__(self, filename):
        self.mode = Mode.RAW
        self.backup_mode = Mode.RAW
        self.level = 1
        self.com = "//"
        if filename.endswith(".py"):
            self.com = "#"
    
    def init_raw(self):
        self.mode = Mode.RAW
        return self

    def init_del(self):
        self.mode = Mode.DEL
        return self

    # decide se a linha deve entrar no texto
    def evaluate_insert(self, line: str):
        if self.mode == Mode.DEL:
            return False
        if self.mode == Mode.RAW:
            return True
        if self.mode == Mode.COM:
            return True
        if line == "":
            return True
        margin = (self.level + 1) * "    "
        if line.startswith(margin):
            return False

        return True

    def process(self, content: str) -> str:
        lines = content.split("\n")
        output = []
        for line in lines:
            alone = len(line.split(" ")) == 1
            two_words = len(line.strip().split(" ")) == 2
            if self.mode == Mode.COM:
                if not line.strip().startswith(self.com):
                    self.mode = self.backup_mode
            if two_words and line.endswith("$$") and self.mode == Mode.ADD:
                self.backup_mode = self.mode
                self.mode = Mode.COM
            elif alone and line[-3:-1] == "++":
                self.mode = Mode.ADD
                self.level = int(line[-1])
            elif alone and line.endswith("=="):
                self.mode = Mode.RAW
            elif alone and line.endswith("--"):
                self.mode = Mode.DEL
            elif self.evaluate_insert(line):
                if self.mode == Mode.COM:
                    line = line.replace(self.com + " ", "", 1)
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
        content = Filter(args.file).process(content)
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

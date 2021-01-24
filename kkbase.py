#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
from typing import List, Dict

class Item:
    def __init__(self, base: str, hook: str, header: str):
        self.base = base
        self.hook = hook
        self.header = header

    def hook_path(self):
        return os.path.normpath(os.path.join(self.base, self.hook))

    def readme_path(self):
        return os.path.normpath(os.path.join(self.hook_path(), "Readme.md"))


    def __str__(self):
        return "[" + self.hook + ":" + self.header + "]"

class Base:
    def __init__(self, base: str):
        self.path = base
        self.itens: Dict[str, Item] = {}
        for hook in os.listdir(self.path):
            readme = base + os.sep + hook + os.sep + "Readme.md"
            if os.path.isdir(base + os.sep + hook) and os.path.isfile(readme):
                self.itens[hook] = Item(base, hook, open(readme).read().split("\n")[0])

    def __str__(self):
        return "\n".join([str(item) for item in self.itens.values()])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('base', type=str, help='base folder')
    args = parser.parse_args()

    base = Base(args.base)
    print(base)

if __name__ == '__main__':
    main()
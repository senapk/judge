#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations


from typing import List, Tuple
import os
import shutil
import argparse
from util import Util, Base


class Links:
    @staticmethod
    def generate(hook_header_base: List[Tuple[str, str]], links_dir: str, base: str):
        shutil.rmtree(links_dir, ignore_errors=True)
        os.mkdir(links_dir)
        for hook, header in hook_header_base:
            title = " ".join([word for word in header.split(" ") if not word.startswith("#")])
            path = os.path.join(links_dir, title + ".md")
            with open(path, "w") as f:
                link = Util.get_directions(path, Util.join([base, hook, 'Readme.md']))
                f.write("[LINK](" + link + ")\n")


class Main:
    @staticmethod
    def main():
        parser = argparse.ArgumentParser(prog='links.py')
        parser.add_argument('--base', '-b', type=str, default="base", help="path to dir with the questions")
        parser.add_argument('--dir', type=str, default='.links', help="dir to store md links")
        
        args = parser.parse_args()
        try:
            hook_header_base = Base.load_hook_header_from_base(args.base)
            Links.generate(hook_header_base, args.dir, args.base)
        except ValueError as e:
            print(str(e))


if __name__ == '__main__':
    Main.main()

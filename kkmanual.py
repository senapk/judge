#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
from kkbase import Base
from typing import Optional, List

class Entry:
    def __init__(self, line: str, base: Base):
        self.line = line
        self.hook: Optional[str] = self.search_hook()
        self.new_header: Optional[str] = None

        if self.hook is not None: #
            if self.hook in base.itens:
                self.new_header = base.itens[self.hook].header

    def prefix(self) -> str:
        cont = 0
        for c in self.line:
            if c == ' ':
                cont += 1
            else:
                break
        return ' ' * cont

    def search_hook(self) -> Optional[str]:
        parts = self.line.split("@")
        return None if len(parts) == 1 else parts[1].split("]")[0].split(" ")[0].split(")")[0]

class LineFormatter:
    def __init__(self, base_path, hide_hook, root_target):
        self.base_path = base_path
        self.hide_hook = hide_hook
        self.root_target = root_target

    def format_entry(self, entry: Entry):
        if entry.hook is None or entry.new_header is None:
            return entry.line
        return self.format(entry.prefix(), entry.hook, entry.new_header)

    def format(self, prefix, hook, header):
        words = header.split(" ")
        tags = [word for word in words if word.startswith("#") and len(word) != word.count('#')]
        title = " ".join([word for word in words if not word.startswith("#")])
        line = prefix + '- ['
        if not self.hide_hook:
            line += '@' + hook + ' '
        line += title
        if self.root_target:
            line += '](' + Manual.join([self.base_path, hook]) + ') '
        else:
            line += '](' + Manual.join([self.base_path, hook, 'Readme.md']) + ') '
        extra = []
        if self.hide_hook:
            extra.append('@' + hook)
        if len(tags) > 0:
            extra += tags
        if len(extra) > 0:
            line += " [](" + " ".join(extra) + ")"
        return line

class Manual:
    def __init__(self, base: Base, path, hide_hook, root_target):
        self.base: Base = base
        self.path = path

        self.formatter = LineFormatter(base.path, hide_hook, root_target)

        self.line_list = self.load_lines()
        self.entries = [Entry(line, base) for line in self.line_list]
        self.new_line_list = [self.formatter.format_entry(e) for e in self.entries]


    def load_lines(self) -> List[str]:
        if os.path.isfile(self.path):
            with open(self.path) as f:
                return f.read().split("\n")
        else:
            with open(self.path, "w"):
                pass
        print("Warning: File", self.path, "not found, creating empty file")
        return []

    def update_readme(self):
        if self.line_list != self.new_line_list:
            print("Updating", self.path)
            with open(self.path, "w") as f:
                f.write("\n".join(self.new_line_list))

    @staticmethod
    def join(path_list: List[str]) -> str:
        path_list = [os.path.normpath(x) for x in path_list]
        path = ""
        for x in path_list:
            path = os.path.join(path, x)
        return os.path.normpath(path)

    def find_unmatched(self):
        not_found = [entry for entry in self.entries if entry.new_header is None]
        if len(not_found) > 0:
            print('Warning: There are entries not found on base:')
            for entry in not_found:
                print(self.formatter.format_entry(entry))

        used_hooks = [entry.hook for entry in self.entries]
        unused_hooks = [hook for hook in self.base.itens.keys() if hook not in used_hooks]
        if len(unused_hooks) > 0:
            print('Warning: There are entries not used on base:')
            for hook in unused_hooks:
                print(self.formatter.format("", hook, self.base.itens[hook].header))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, help="source file do load and rewrite")
    parser.add_argument('--base', '-b', type=str, default='base')
    parser.add_argument('--dindex', action='store_true', help="disable index key")
    parser.add_argument('--root', action='store_true', help="link sending to folder instead to file")

    args = parser.parse_args()
    base = Base(args.base)
    manual = Manual(base, args.path, args.dindex, args.root)
    manual.update_readme()
    manual.find_unmatched()

if __name__ == '__main__':
    main()
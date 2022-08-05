#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import argparse
from typing import Optional, List, Dict

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
        regex = r"@\d\d\d" #@ com 3 dígitos
        matches = re.findall(regex, self.line)
        return matches[0][1:] if len(matches) > 0 else None

class LineFormatter:
    def __init__(self, base_path: str, unlabel: bool, root_target: bool, tab_mode: Optional[str], description: bool):
        self.base_path = base_path
        self.unlabel = unlabel
        self.root_target = root_target
        self.tab_mode = tab_mode
        self.description = description

    def format_entry(self, entry: Entry):
        if entry.hook is None or entry.new_header is None:
            return entry.line
        if self.tab_mode is not None:
            return self.format_tab(entry.hook, entry.new_header)
        return self.format(entry.hook, entry.new_header)

    def format(self, hook, header):
        words = header.split(" ")
        tags = [word for word in words if word.startswith("#") and len(word) != word.count('#')]
        title = " ".join([word for word in words if not word.startswith("#")])
        line = '- ['
        if not self.unlabel:
            line += '@' + hook + ' '
        line += title
        if self.root_target:
            line += '](' + Manual.join([self.base_path, hook]) + ') '
        else:
            line += '](' + Manual.join([self.base_path, hook, 'Readme.md']) + ') '
        extra = []
        if self.unlabel:
            extra.append('@' + hook)
        if len(tags) > 0:
            extra += tags
        if len(extra) > 0:
            line += " [](" + " ".join(extra) + ")"
        return line

    def format_tab(self, hook, header):
        words = header.split(" ")
        tags = [word for word in words if word.startswith("#") and len(word) != word.count('#')]
        title = " ".join([word for word in words if not word.startswith("#")])
        title, description = title.split("&", 1) if "&" in title else (title, "")
        
        figura = Manual.join([self.base_path, hook, self.tab_mode])
        readme = Manual.join([self.base_path, hook, 'Readme.md'])
        line = "![](" + figura + ")" + " | " + "[@" + hook + " " + title + "](" + readme + ")"
        if self.description:
            line += " | " + description
        return line

class Manual:
    def __init__(self, base: Base, path, formatter):
        self.base: Base = base
        self.path = path
        self.formatter = formatter

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
        not_found = [entry for entry in self.entries if entry.new_header is None and entry.hook is not None]
        if len(not_found) > 0:
            print('Warning: There are entries not found on base:')
            for entry in not_found:
                print(self.formatter.format_entry(entry))

        used_hooks = [entry.hook for entry in self.entries]
        unused_hooks = [hook for hook in self.base.itens.keys() if hook not in used_hooks]
        if len(unused_hooks) > 0:
            print('Warning: There are entries not used on base:')
            for hook in unused_hooks:
                print(self.formatter.format(hook, self.base.itens[hook].header))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, help="source file do load and rewrite")
    parser.add_argument('--base', '-b', type=str, default='base')
    parser.add_argument('--table', '-t', type=str, help="table mode, parametre is cover filename")
    parser.add_argument('--unlabel', '-u', action='store_true', help="unlabel")
    parser.add_argument('--description', '-d', action='store_true', help="insert description")
    parser.add_argument('--root', '-r', action='store_true', help="link sending to folder instead to file")
    parser.add_argument("--quiet", '-q', action='store_true', help="dont show missing or wrong entries")
    args = parser.parse_args()
    base = Base(args.base)
    formatter = LineFormatter(base.path, args.unlabel, args.root, args.table, args.description)
    manual = Manual(base, args.path, formatter)
    manual.update_readme()
    if not args.quiet:
        manual.find_unmatched()

if __name__ == '__main__':
    main()
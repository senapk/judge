#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import List, Tuple, Optional
import os
import argparse
from util import Util, Base


class Manual:
    @staticmethod
    def load_lines(path) -> List[str]:
        if os.path.isfile(path):
            with open(path) as f:
                return f.read().split("\n")
        return []

    @staticmethod
    def search_hook(line: str) -> Optional[str]:
        parts = line.split("@")
        if len(parts) == 1:
            return None
        return parts[1].split("]")[0].split(" ")[0].split(")")[0]   # extracting token
        
    @staticmethod
    def calc_prefix(line: str):
        cont = 0
        for c in line:
            if c == ' ':
                cont += 1
            else:
                break
        return cont
    
    @staticmethod
    def refactor_line(line: str, hook: str, header: str, base: str, hide: bool):
        prefix = Manual.calc_prefix(line)
        words = header.split(" ")
        tags = [word for word in words if word.startswith("#") and len(word) != word.count('#')]
        title = " ".join([word for word in words if not word.startswith("#")])
        line = ' ' * prefix + '- ['
        if not hide:
            line += '@' + hook + ' '
        line += title
        line += '](' + Util.join([base, hook, 'Readme.md']) + '#' + Util.get_md_link(header) + ') ' 
        
        extra = []
        if hide:
            extra.append('@' + hook)
        if len(tags) > 0:
            extra += tags
        if len(extra) > 0:
            line += " [](" + " ".join(extra) + ")"
        return line

    @staticmethod
    def find_header(hook_header_list: List[Tuple[Optional[str], Optional[str]]], hook: Optional[str]) -> Optional[str]:
        header = []
        if hook:
            header = [header for _hook, header in hook_header_list if _hook == hook]
        if len(header) == 0:
            return None
        else:
            return header[0]

    @staticmethod
    def load_line_hook_header_from_readme(line_list: List[str],
                                          hook_header_base: List[Tuple[Optional[str], Optional[str]]]) -> \
            List[Tuple[str, Optional[str], Optional[str]]]:
        hook_list = [Manual.search_hook(line) for line in line_list]
        header_list = [Manual.find_header(hook_header_base, hook) for hook in hook_list]
        return list(zip(line_list, hook_list, header_list))

    @staticmethod
    def generate_new_list(line_hook_header_readme, base, hide) -> List[str]:
        new_line_list = []
        for line, hook, header in line_hook_header_readme:
            if hook is None or header is None:
                new_line_list.append(line)
            else:
                new_line_list.append(Manual.refactor_line(line, hook, header, base, hide))
        return new_line_list

    @staticmethod
    def update_readme(line_list, new_line_list, path):
        if line_list != new_line_list:
            print("Updating", path)
            with open(path, "w") as f:
                f.write("\n".join(new_line_list))

    @staticmethod
    def find_not_used_hooks(line_hook_header_readme, hook_header_base, base, hide):
        hooks_readme = [item[1] for item in line_hook_header_readme]
        missing_hook_header = [pair for pair in hook_header_base if pair[0] not in hooks_readme]
        if len(missing_hook_header) > 0:
            print('Warning: There are hooks not used:')
            for hook, header in missing_hook_header:
                print(Manual.refactor_line("", hook, header, base, hide))
    
    @staticmethod
    def find_not_found_hooks(line_hook_header_readme):
        line_list = [line for line, hook, _header in line_hook_header_readme if hook is not None and _header is None]
        if len(line_list) > 0:
            print("Warning: There are hooks not found:")
            for line in line_list:
                print(line)

    @staticmethod
    def indexer(hook_header_base, base, path, hide):
        line_list = Manual.load_lines(path)
        line_hook_header_readme = list(Manual.load_line_hook_header_from_readme(line_list, hook_header_base))
        new_line_list = Manual.generate_new_list(line_hook_header_readme, base, hide)
        Manual.update_readme(line_list, new_line_list, path)
        Manual.find_not_used_hooks(line_hook_header_readme, hook_header_base, base, hide)
        Manual.find_not_found_hooks(line_hook_header_readme)


class Main:
    @staticmethod
    def main():
        parser = argparse.ArgumentParser()
        parser.add_argument('--base', '-b', type=str, default="base", help="path to dir with the questions")
        parser.add_argument('--file', '-f', type=str, default='Readme.md', help="source file do load and rewrite")
        parser.add_argument('--key', '-k', action='store_true', help="disable index key")
        
        args = parser.parse_args()
        try:
            hook_header_base = Base.load_hook_header_from_base(args.base)
            Manual.indexer(hook_header_base, args.base, args.file, args.key)
        except ValueError as e:
            print(str(e))


if __name__ == '__main__':
    Main.main()

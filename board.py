#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations


from typing import List, Tuple
import argparse
import io
from util import Util, Base

class Board:
    @staticmethod
    def make_entry(base, hook,  board_file: str) -> str:
        return "[](" + Util.get_directions(board_file, Util.join([base, hook, "Readme.md"])) + ')'

    @staticmethod
    def extract_path_and_header(line: str, board_path: str):
        parts = line.split(":")
        file_path = parts[0].strip()[3:-1]  # removing []( )
        fulltitle = ":".join(parts[1:]).strip()

        # change path relative to board to a path relative to base
        board_dir = Util.split_path(board_path)[0]
        path = Util.join([board_dir, file_path])
        return path, fulltitle

    @staticmethod
    def update_itens(hook_header_list, base):
        for hook, header in hook_header_list:
            with open(item.path_full, "w") as f:
                f.write(item.fulltitle.strip() + "\n")
                f.write(item.payload)
            FileItem.write_from_item(item)

    @staticmethod
    def check_itens_for_update(board_content: str, board_path: str, base: str, hook_header_base: List[Tuple[str, str]]):
        names_list = [x for x in board_content.split("\n") if x != ""]  # cleaning the empty lines
        itens_for_update = []
        for line in names_list:
            path, header = Board.extract_path_and_header(line, board_path)
            hook = Base.extract_hook_from_path(path, base)
            search = [pair for pair in hook_header_base if pair[0] == hook]
            if len(search) == 0:
                print("  warning: file", path, "not found!")
            else:
                if search[0][1] != header:
                    itens_for_update.append((hook, header))
        return itens_for_update

    @staticmethod
    def generate(hook_header_base: List[Tuple[str, str]], board_file: str, base: str) -> str:
        output = io.StringIO()
        pair_list: List[Tuple[str, str]] = []
        for hook, header in hook_header_base:
            pair_list.append((Board.make_entry(base, hook, board_file), header))

        max_len_path = max([len(x[0]) for x in pair_list])

        for path, fulltitle in pair_list:
            output.write(path.ljust(max_len_path) + " : " + fulltitle + "\n")

        return output.getvalue()


class Main:
    @staticmethod
    def main():
        parser = argparse.ArgumentParser(prog='links.py')
        parser.add_argument('--base', '-b', type=str, default="base", help="path to dir with the questions")
        parser.add_argument('--file', '-f', type=str, default='board.md', help="source file do write ou read")
        parser.add_argument('--set', '-f', action='store_true', help="set file headers using board")
        
        args = parser.parse_args()
        try:
            hook_header_base = Base.load_hook_header_from_base(args.base)
            if args.set:
                print("Updating headers using board")
                with open(args.file) as f:
                    marked = Board.check_itens_for_update(f.read(), args.file, hook_header_base)
                    Board.update_itens(marked)
                hook_header_base = Base.load_hook_header_from_base(args.base)

            print("Generating board")
            board = Board.generate(hook_header_base, args.file)
            with open(args.file, "w") as f:
                f.write(board)
        except ValueError as e:
            print(str(e))


if __name__ == '__main__':
    Main.main()

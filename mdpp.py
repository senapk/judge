#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import argparse
import enum
from typing import Optional, List, Tuple
import subprocess

class Action(enum.Enum):
    RUN = 1
    CLEAN = 2

class TocMaker:
    @staticmethod
    def __only_hashtags(x: str) -> bool:
        return len(x) == x.count("#") and len(x) > 0

    # generate md link for the text
    @staticmethod
    def __get_md_link(title: Optional[str]) -> str:
        if title is None:
            return ""
        title = title.lstrip(" #").rstrip()
        title = title.lower()
        out = ''
        for c in title:
            if c == ' ' or c == '-':
                out += '-'
            elif c == '_':
                out += '_'
            elif c.isalnum():
                out += c
        return out

    @staticmethod
    def __get_level(line: str) -> int:
        return len(line.split(" ")[0])

    @staticmethod
    def __get_content(line: str) -> str:
        return " ".join(line.split(" ")[1:])

    @staticmethod
    def __remove_code_fences(content: str) -> str:
        regex = r"^```.*?```\n"
        return re.sub(regex, "", content, 0, re.MULTILINE | re.DOTALL)

    # return List[level, "[text](link)"]
    @staticmethod
    def __extract_entries(content: str) -> List[Tuple[int, str]]:
        content = TocMaker.__remove_code_fences(content)

        lines = content.split("\n")
        disable_tag = "[]()"
        lines = [line for line in lines if TocMaker.__only_hashtags(line.split(" ")[0]) and line.find(disable_tag) == -1]

        entries: List[Tuple[int, str]] = []
        for line in lines:
            level = TocMaker.__get_level(line)
            text = "[" + TocMaker.__get_content(line) + "](#" + TocMaker.__get_md_link(line) + ")"
            entries.append((level, text))
        return entries

    
    @staticmethod
    def execute_toch(content: str) -> str:
        entries = TocMaker.__extract_entries(content)
        links = [b for (a, b) in entries if a == 2]
        table = ["--" for _ in links]
        return " | ".join(links) + "\n" + " | ".join(table)
        

    @staticmethod
    def execute_toc(content: str) -> str:
        entries = TocMaker.__extract_entries(content)
        toc_lines = ["  " * (level - 2) + "- " + link for (level, link) in entries if level > 1]
        toc_text = "\n".join(toc_lines)
        return toc_text

class Toc:
    @staticmethod
    def execute(content: str, action: Action = Action.RUN) -> str:
        regex = r"<!-- toc -->\n" + r"(.*?)"+ r"<!-- toc -->"
        if action == Action.RUN:
            new_toc = TocMaker.execute_toc(content)
            subst = r"<!-- toc -->\n" + new_toc + r"\n<!-- toc -->"
        else:
            subst = r"<!-- toc -->\n<!-- toc -->"
        return re.sub(regex, subst, content, 0, re.MULTILINE | re.DOTALL)

class Toch:
    @staticmethod
    def execute(content: str, action: Action = Action.RUN) -> str:
        regex = r"<!-- toch -->\n" + r"(.*?)"+ r"<!-- toch -->"
        if action == Action.RUN:
            new_toc = TocMaker.execute_toch(content)
            subst = r"<!-- toch -->\n" + new_toc + r"\n<!-- toch -->"
        else:
            subst = r"<!-- toch -->\n<!-- toch -->"
        return re.sub(regex, subst, content, 0, re.MULTILINE | re.DOTALL)

class Drafts:

    @staticmethod
    def load_drafts(readme_path):
        folder = os.path.dirname(readme_path)
        origin = os.path.join(folder, "src")
        output = ""
        if os.path.isdir(origin):
            # create a markdown list os links with all files under .cache/src
            entries = sorted(os.listdir(origin))
            for lang in entries:
                output += "- " + lang + "\n"
                for file in sorted(os.listdir(os.path.join(origin, lang))):
                    output += "  - [" + file + "](.cache/lang/" + lang + "/" + file + ")\n"

        return output


    @staticmethod
    def execute(path, content: str, action: Action = Action.RUN) -> str:
        regex = r"<!-- draft -->\n(.*?)<!-- draft -->"
        if action == Action.RUN:
            new_draft = Drafts.load_drafts(path)
            subst = r"<!-- draft -->\n" + new_draft + r"\n<!-- draft -->"
        else:
            subst = r"<!-- draft -->\n<!-- draft -->"
        return re.sub(regex, subst, content, 0, re.MULTILINE | re.DOTALL)

class Load:

    @staticmethod
    def extract_between_tags(content, tag):
        regex = r"\[\[" + tag + r"\]\].*?^(.*)^[\S ]*\[\[" + tag + r"\]\]"
        matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            return match.group(1)
        return ""

    @staticmethod
    def execute(content: str, action: Action = Action.RUN) -> str:
        new_content = ""
        last = 0

        regex = r"<!-- load (\S*?) (\S*?) -->\n(.*?)<!-- load -->"
        matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            path = match.group(1)
            tags = match.group(2)
            words: List[str] = tags.split(":")

            fenced: List[str] = [tag for tag in words if tag.startswith("fenced")]
            words = [tag for tag in words if not tag.startswith("fenced")]

            filter: List[str] = [tag for tag in words if tag.startswith("filter")]
            words = [tag for tag in words if not tag.startswith("filter")]

            extract: List[str] = [tag for tag in words if tag.startswith("extract")]
            words = [tag for tag in words if not tag.startswith("extract")]


            ext = os.path.splitext(path)[1][1:]
            if len(words) > 0:
                ext = words[0]
            if len(fenced) == 1:
                parts = fenced[0].split("=")
                if len(parts) == 2:
                    ext = parts[1]


            new_content += content[last:match.start()] # inserindo texto entre matches
            last = match.end()
            # new_content += "[](load)[](" + path + ")[](" + tags + ")\n"
            new_content += "<!-- load " + path + " " + tags + " -->\n"

            # se não for run, deve limpar o conteúdo não inserindo os arquivos
            if action == Action.RUN:
                if len(fenced) > 0:
                    new_content += "\n```" + ext + "\n"
                if os.path.isfile(path):
                    if len(filter) > 0:
                        output = subprocess.run(["filter", path], stdout=subprocess.PIPE)
                        data = output.stdout.decode("utf-8")
                        new_content += data
                        if data[-1] != "\n":
                            new_content += "\n"
                    elif len(extract) > 0:
                        tag = extract[0].split("=")[1]
                        data = Load.extract_between_tags(open(path).read(), tag)
                        new_content += data
                        if len(data) == 0 or data[-1] != "\n":
                            new_content += "\n"
                    else:
                        data = open(path).read()
                        new_content += open(path).read()
                        if data[-1] != "\n":
                            new_content += "\n"
                else:
                    print("warning: file", path, "not found")
                if fenced:
                    new_content += "```\n\n"
            new_content += "<!-- load -->"
        
        new_content += content[last:]
        return new_content


            

class Save:
    @staticmethod
    # execute filename and content
    def execute(file_content):
        regex = r"\[\]\(save\)\[\]\((.*?)\)\n```[a-z]*\n(.*?)```\n\[\]\(save\)"
        matches = re.finditer(regex, file_content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            path = match.group(1)
            content = match.group(2)
            exists = os.path.isfile(path)
            if exists:
                content_old = open(path).read()
            if not exists or content != content_old:
                with open(path, "w") as f:
                    print("file", path, "updated")
                    f.write(content)

class Main:
    @staticmethod
    def fix_path(target):
        target = os.path.normpath(target)
        if os.path.isdir(target):
            target = os.path.join(target, "Readme.md")
        pieces = target.split(os.sep)
        folder = "."
        if len(pieces) > 1:
            folder = os.sep.join(pieces[:-1])
        return target, folder

    @staticmethod
    def open_file(path): 
        if os.path.isfile(path):
            with open(path) as f:
                file_content = f.read()
                return True, file_content
        print("Warning: File", path, "not found")
        return False, "" 
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('targets', metavar='T', type=str, nargs='*', help='Readmes or folders')
    parser.add_argument('--quiet', '-q', action="store_true", help='quiet mode')
    parser.add_argument('--clean', '-c', action="store_true", help='clean mode')
    args = parser.parse_args()

    if len(args.targets) == 0:
        args.targets.append(".")
    
    action = Action.RUN if not args.clean else Action.CLEAN

    for target in args.targets:
        path, folder = Main.fix_path(target)
        result, original = Main.open_file(path)
        if not result:
            continue
        updated = original
        updated_toc = Toc.execute(updated, action)
        updated_toc = Toch.execute(updated_toc, action)
        if updated != updated_toc:
            updated = updated_toc
        updated = Load.execute(updated, action)
        updated = Drafts.execute(target, updated, action)
        Save.execute(updated)
        
        if updated != original:
            with open(path, "w") as f:
                f.write(updated)
                hook = os.path.abspath(path).split(os.sep)[-2]
                print(hook + " : mdpp updading")

if __name__ == '__main__':
    main()

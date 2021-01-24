#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tempfile
import argparse
from kkbase import Base
import subprocess
from subprocess import PIPE
import re


class HTML:
    """
    generate a html page from infile
    if remote_server not null, all reference to images begining with __
    will be updates to full url
    """

    @staticmethod
    def _generate_html(title: str, content: str, enable_latex: bool) -> str:
        temp_dir = tempfile.TemporaryDirectory()
        outfile = os.path.join(temp_dir.name, "out.html")
        infile = os.path.join(temp_dir.name, "in.md")
        with open(infile, "w") as f:
            f.write(content)

        fulltitle = title.replace('!', '\\!').replace('?', '\\?')
        cmd = ["pandoc", infile, '--metadata', 'pagetitle=' + fulltitle, '-s', '-o', outfile]
        if enable_latex:
            cmd.append("--mathjax")
        try:
            p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            stdout, stderr = p.communicate()
            if stdout != "" or stderr != "":
                print(stdout)
                print(stderr)
            with open(outfile) as f:
                return f.read()
        except Exception as e:
            print("Erro no comando pandoc:", e)
            exit(1)

    @staticmethod
    def insert_remote_url(content: str, remote_url: str) -> str:
        regex = r"\[(.*)\]\((\s*)([^:\s]*)(\s*)\)"
        subst = "[\\1](" + remote_url + "\\3)"
        result = re.sub(regex, subst, content, 0, re.MULTILINE)
        return result

    @staticmethod
    #  remote_master is something like https://raw.githubusercontent.com/qxcodefup/arcade/master
    def generate(base: Base, insert_hook: bool, enable_latex: bool, remote_master_url: str, output_file: str):

        itens = sorted(base.itens.values(), key=lambda x: x.hook)
        for item in itens:
            hook = ("@" + item.hook) if insert_hook else ""

            payload = "\n".join(open(item.readme_path()).read().split("\n")[1:])
            if remote_master_url != "":
                remote_hook = remote_master_url.rstrip("/") + "/" + base.path + "/" + item.hook + "/"
                payload = HTML.insert_remote_url(payload, remote_hook)

            md_content = "## " + hook + "\n" + item.header + "\n" + payload
            header = " ".join([word for word in item.header.split(" ") if not word.startswith("#")])
            title = " ".join([hook, header])

            source = item.hook_path()
            destination = os.path.join(item.hook_path(), output_file)
            if not os.path.isfile(destination) or (os.path.getctime(source) > os.path.getctime(destination)):
                print("  regenerating html for hook", item.hook)
                html_content = HTML._generate_html(title, md_content, enable_latex)
                with open(destination, "w") as f:
                    f.write(html_content)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--base', '-b', type=str, default='base')
    parser.add_argument('--output', '-o', type=str, default=".html", help="name of output file")
    parser.add_argument('--remote', '-r', type=str, default="", help="root remote path")
    parser.add_argument('--dindex', action='store_true', help="disable insert index in name")
    parser.add_argument('--dlatex', action='store_true', help="disable latex rendering")

    args = parser.parse_args()

    base = Base(args.base)
    HTML.generate(base, not args.dindex, not args.dlatex, args.remote, args.output)


if __name__ == '__main__':
    main()

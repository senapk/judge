#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import os
import configparser
from typing import List

tk_path = "tk"

class ITable:
    options_base = ["fup", "ed", "poo"]
    options_term = ["40", "60", "80", "100", "120", "140", "160", "180", "200"]
    options_view = ["side", "down"]
    options_mark = ["show", "hide"]
    options_exte = ["c", "cpp", "js", "ts", "py", "java", "hs"]

    @staticmethod
    def choose(intro, opt_list, par = ""):
        if par in opt_list:
            return par
        print(intro + "[ " + ", ".join(opt_list) + " ]: ", end="")
        value = input().lower()
        if value not in opt_list:
            return ITable.choose(intro, opt_list)
        return value

    @staticmethod
    def cls():
        # os.system('cls' if os.name == 'nt' else 'clear')
        pass
        
    @staticmethod
    def validate_label(label):
        if len(label) != 3:
            return False
        for c in label:
            if not c.isdigit():
                return False
        return True

    @staticmethod
    def choose_label(label = ""):
        if ITable.validate_label(label):
            return label
        while True:
            print("Label: @", end="")
            label = input()
            if ITable.validate_label(label):
                break
        return label

    @staticmethod
    def action_down(ui_list: List[str], base: str) -> str:
        label = "" if len(ui_list) < 2 else ui_list[1]
        label = ITable.choose_label(label)

        ext = "" if len(ui_list) < 3 else ui_list[2]
        ext = ITable.choose("Choose extension ", ITable.options_exte, ext)

        print("{} {} {}".format(label, ext, base))
        subprocess.run([tk_path, "down", base, label, ext])
        return "down" + " " + label + " " + ext

    @staticmethod
    def action_run(ui_list, mark_mode, view_mode, term_size) -> str:
        label = "" if len(ui_list) < 2 else ui_list[1]
        label = ITable.choose_label(label)
        print("Running problem " + label + " ...")
        
        cmd = [tk_path, "run", "-f", label]
        if mark_mode == "hide":
            cmd.append("-r")
        if view_mode == "down":
            cmd.append("-v")
        cmd.append("-w")
        cmd.append(term_size)

        subprocess.run(cmd)
        return "run " + label

    @staticmethod
    def choose_base(ui_list: List[str]) -> str:
        if len(ui_list) == 2 and ui_list[1] in ITable.options_base:
            return ui_list[1]

        return ITable.choose("Choose database ", ITable.options_base)

    @staticmethod
    def choose_term(ui_list: List[str]) -> str:
        if len(ui_list) == 2 and ui_list[1] in ITable.options_term:
            return ui_list[1]
        return ITable.choose("Choose termsize ", ITable.options_term)

    @staticmethod
    def create_default_config(configfile):
        config = configparser.ConfigParser()
        config["DEFAULT"] = {
            "base": ITable.options_base[0],
            "term": ITable.options_term[0],
            "view": ITable.options_view[0],
            "mark": ITable.options_mark[0],
            "last_cmd": ""
        }
        with open(configfile, "w") as f:
            config.write(f)

    @staticmethod
    def not_str(value: str) -> str:
        if value == ITable.options_mark[0]:
            return ITable.options_mark[1]
        if value == ITable.options_mark[1]:
            return ITable.options_mark[0]
        
        if value == ITable.options_view[0]:
            return ITable.options_view[1]
        if value == ITable.options_view[1]:
            return ITable.options_view[0]

    @staticmethod
    def print_header(config):
        
        pad = lambda s, w: s + (w - len(s)) * " "

        base  = pad(config["DEFAULT"]["base"], 4).upper()
        term  = pad(config["DEFAULT"]["term"], 4)
        view  = pad(config["DEFAULT"]["view"], 4).upper()
        mark = pad(config["DEFAULT"]["mark"], 4).upper()
        last_cmd = config["DEFAULT"]["last_cmd"]

        # padding function using length
        print("┌─────┬─────┬─────┬─────┬─────┬────┐")
        print("│h.elp│b.ase│t.erm│v.iew│m.ark│r.un│")
        print("├─────┼┈┈┈┈┈┼┈┈┈┈┈┼┈┈┈┈┈┼┈┈┈┈┈┼────┤")
        print("│d.own│ {}│ {}│{} │{} │".format(base, term, view, mark) + "e.nd│");
        print("└─────┴─────┴─────┴─────┴─────┴────┘")
        print("(" + last_cmd + "): ", end="")

    @staticmethod
    def validate_config(config):
        if "DEFAULT" not in config:
            return False
        if "base" not in config["DEFAULT"] or config["DEFAULT"]["base"] not in ITable.options_base:
            return False
        if "term" not in config["DEFAULT"] or config["DEFAULT"]["term"] not in ITable.options_term:
            return False
        if "view" not in config["DEFAULT"] or config["DEFAULT"]["view"] not in ITable.options_view:
            return False
        if "mark" not in config["DEFAULT"] or config["DEFAULT"]["mark"] not in ITable.options_mark:
            return False
        if "last_cmd" not in config["DEFAULT"]:
            return False
        return True

    @staticmethod
    def print_help():
        print("Digite a letra ou o comando e aperte enter.")
        print("h ou help: mostra esse help.")
        print("b ou base: muda a base de dados entre as disciplinas.")
        print("t ou term: muda a largura do terminal utilizado para mostrar os erros.")
        print("v ou view: alterna o modo de visualização de erros entre up_down e lado_a_lado.")
        print("m ou mark: show mostra os whitespaces e hide os esconde.")
        print("d ou down: faz o download do problema utilizando o label e a extensão.")
        print("r ou run : roda o problema utilizando sua solução contra os testes.")
        print("e ou end : termina o programa.")
        print("Na linha de execução já aparece o último comando entre (), para reexecutar basta apertar enter.")

    @staticmethod
    def search_config(filename) -> str:
        # recursively search for config file in parent directories
        path = os.getcwd()
        while True:
            configfile = os.path.join(path, filename)
            if os.path.exists(configfile):
                return configfile
            if path == "/":
                return ""
            path = os.path.dirname(path)

    @staticmethod
    def main():
        default_config_file = ".config.ini"
        config = configparser.ConfigParser()
        ITable.cls()

        configfile = ITable.search_config(default_config_file)
        if configfile != "":
            os.chdir(os.path.dirname(configfile))
        else:
            configfile = default_config_file
            print("Creating default config file")
            ITable.create_default_config(configfile)
        
        config.read(configfile)
        
        if not ITable.validate_config(config):
            ITable.create_default_config(configfile)
            config.read(configfile)

        while True: 
            ITable.print_header(config)

            line = input()
            if line == "":
                line = config["DEFAULT"]["last_cmd"]

            ui_list = line.split(" ")
            cmd = ui_list[0]

            if cmd == "e" or cmd == "end":
                break
            elif cmd == "h" or cmd == "help":
                ITable.print_help()
            elif cmd == "b" or cmd == "base":
                value: str = ITable.choose_base(ui_list)
                config["DEFAULT"]["base"] = value
                ITable.cls()
            elif cmd == "t" or cmd == "term":
                config["DEFAULT"]["term"] = ITable.choose_term(ui_list)
                ITable.cls()
            elif cmd == "v" or cmd == "view":
                config["DEFAULT"]["view"] = ITable.not_str(config["DEFAULT"]["view"])
                ITable.cls()
            elif cmd == "m" or cmd == "mark":
                config["DEFAULT"]["mark"] = ITable.not_str(config["DEFAULT"]["mark"])
                ITable.cls()
            elif cmd == "d" or cmd == "down":
                last_cmd = ITable.action_down(ui_list, config["DEFAULT"]["base"])
                config["DEFAULT"]["last_cmd"] = last_cmd
            elif cmd == "r" or cmd == "run":
                last_cmd = ITable.action_run(ui_list, config["DEFAULT"]["mark"], config["DEFAULT"]["view"], config["DEFAULT"]["term"])
                config["DEFAULT"]["last_cmd"] = last_cmd
            else:
                print("Invalid command")

            with open(default_config_file, "w") as f:
                config.write(f)

        with open(default_config_file, "w") as f:
            config.write(f)

ITable.main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import os
import configparser
from typing import List

tk_path = "tk"

options_base = ["fup", "ed", "poo"]
options_term = ["40", "60", "80", "100", "120", "140", "160", "180", "200"]
options_view = ["side", "down"]
options_mark = ["show", "hide"]
options_exte = ["c", "cpp", "js", "ts", "py", "java", "hs"]

def choose(intro, opt_list, par = ""):
    if par in opt_list:
        return par
    print(intro + "[ " + ", ".join(opt_list) + " ]: ", end="")
    value = input().lower()
    if value not in opt_list:
        return choose(intro, opt_list)
    return value

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')
    # pass
    
def validate_label(label):
    if len(label) != 3:
        return False
    for c in label:
        if not c.isdigit():
            return False
    return True

# def ask_and_load_label():
#     last_label_file = ".label.txt"
#     last_label = ""
#     if os.path.exists(last_label_file):
#         last_label = open(last_label_file).read()
    
#     label = input("label(" + last_label + "): ")
#     if label == "":
#         label = last_label
    
#     elif not validate_label(label):
#         print("view: label devem ser 3 números: ")
#         return ask_and_load_label()

#     open(last_label_file, "w").write(label)
#     return label

def choose_label(label = ""):
    if validate_label(label):
        return label
    while True:
        print("Label: @", end="")
        label = input()
        if validate_label(label):
            break
    return label

def action_down(ui_list: List[str], base: str) -> str:
    label = "" if len(ui_list) < 2 else ui_list[1]
    label = choose_label(label)

    ext = "" if len(ui_list) < 3 else ui_list[2]
    ext = choose("Choose extension ", options_exte, ext)

    print("{} {} {}".format(label, ext, base))
    subprocess.run([tk_path, "down", base, label, ext])
    return "down" + " " + label + " " + ext




def action_run(ui_list, mark_mode, view_mode, term_size) -> str:
    label = "" if len(ui_list) < 2 else ui_list[1]
    label = choose_label(label)
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

def choose_base(ui_list: List[str]) -> str:
    if len(ui_list) == 2 and ui_list[1] in options_base:
        return ui_list[1]

    return choose("Choose database ", options_base)


def choose_term(ui_list: List[str]) -> str:
    if len(ui_list) == 2 and ui_list[1] in options_term:
        return ui_list[1]
    return choose("Choose termsize ", options_term)

def create_default_config(configfile):
    config = configparser.ConfigParser()
    config["DEFAULT"] = {
        "base": options_base[0],
        "term": options_term[0],
        "view": options_view[0],
        "mark": options_mark[0],
        "last_cmd": ""
    }
    with open(configfile, "w") as f:
        config.write(f)

def not_str(value: str) -> str:
    if value == options_mark[0]:
        return options_mark[1]
    if value == options_mark[1]:
        return options_mark[0]
    
    if value == options_view[0]:
        return options_view[1]
    if value == options_view[1]:
        return options_view[0]

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

def validate_config(config):
    if "DEFAULT" not in config:
        return False
    if "base" not in config["DEFAULT"] or config["DEFAULT"]["base"] not in options_base:
        return False
    if "term" not in config["DEFAULT"] or config["DEFAULT"]["term"] not in options_term:
        return False
    if "view" not in config["DEFAULT"] or config["DEFAULT"]["view"] not in options_view:
        return False
    if "mark" not in config["DEFAULT"] or config["DEFAULT"]["mark"] not in options_mark:
        return False
    if "last_cmd" not in config["DEFAULT"]:
        return False
    return True

def print_help():
    print("Just write the letter of the option you want to choose.")
    print("h ou help: print this help")
    print("b ou base: change discipline database")
    print("t ou term: change terminal size to show diff errors")
    print("v ou view: change view mode between up_down or side_by_side")
    print("m ou mark: change rendering mode between hide or show white spaces")
    print("d ou down: download a problem from the database using label and extension")
    print("r ou run: run a problem you have downloaded")
    print("e ou end: exit the program")

def main():
    default_config_file = ".config.ini"
    cls()
    config = configparser.ConfigParser()
    if not os.path.exists(default_config_file):
        print("Creating default config file")
        create_default_config(default_config_file)
    config.read(default_config_file)
    if not validate_config(config):
        create_default_config(default_config_file)
        config.read(default_config_file)


    while True: 
        print_header(config)

        line = input()
        if line == "":
            line = config["DEFAULT"]["last_cmd"]

        ui_list = line.split(" ")
        cmd = ui_list[0]

        if cmd == "e" or cmd == "end":
            break
        elif cmd == "h" or cmd == "help":
            print_help()
        elif cmd == "b" or cmd == "base":
            value: str = choose_base(ui_list)
            config["DEFAULT"]["base"] = value
            cls()
        elif cmd == "t" or cmd == "term":
            config["DEFAULT"]["term"] = choose_term(ui_list)
            cls()
        elif cmd == "v" or cmd == "view":
            config["DEFAULT"]["view"] = not_str(config["DEFAULT"]["view"])
            cls()
        elif cmd == "m" or cmd == "mark":
            config["DEFAULT"]["mark"] = not_str(config["DEFAULT"]["mark"])
            cls()
        elif cmd == "d" or cmd == "down":
            last_cmd = action_down(ui_list, config["DEFAULT"]["base"])
            config["DEFAULT"]["last_cmd"] = last_cmd
        elif cmd == "r" or cmd == "run":
            last_cmd = action_run(ui_list, config["DEFAULT"]["mark"], config["DEFAULT"]["view"], config["DEFAULT"]["term"])
            config["DEFAULT"]["last_cmd"] = last_cmd
        else:
            print("Invalid command")

        with open(default_config_file, "w") as f:
            config.write(f)

    with open(default_config_file, "w") as f:
        config.write(f)

main()

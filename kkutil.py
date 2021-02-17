# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
#
# import os
# from typing import List, Tuple, Optional
#
# class Util:
#     # join the many strings in the list using join
#     @staticmethod
#     def join(path_list: List[str]) -> str:
#         path_list = [os.path.normpath(x) for x in path_list]
#         path = ""
#         for x in path_list:
#             path = os.path.join(path, x)
#         return os.path.normpath(path)
#
#     @staticmethod
#     def key_filter(key: str) -> str:
#         key = key.replace("_", " ")
#         words = key.split(" ")
#
#         try:
#             _index = int(words[0])
#             del words[0]
#         except ValueError:
#             pass
#         return " ".join(words).strip()
#
#     # generate a relative path from source to destination
#     @staticmethod
#     def get_directions(source: str, destination: str) -> str:
#         source = os.path.normpath(source)
#         destination = os.path.normcase(destination)
#         source_list = source.split(os.sep)
#         destin_list = destination.split(os.sep)
#         while source_list[0] == destin_list[0]:  # erasing commom path
#             del source_list[0]
#             del destin_list[0]
#
#         return Util.join(["../" * (len(source_list) - 1)] + destin_list)
#
#     # returns a tuple with two strings
#     # the first  is the directory
#     # the second is the filename
#     @staticmethod
#     def split_path(path: str) -> Tuple[str, str]:
#         path = os.path.normpath(path)
#         vet: List[str] = path.split(os.path.sep)
#         if len(vet) == 1:
#             return ".", path
#         return Util.join(vet[0:-1]), vet[-1]
#
#     @staticmethod
#     def create_dirs_if_needed(path: str) -> None:
#         root, file = Util.split_path(path)
#         if not os.path.isdir(root):
#             os.makedirs(root)
#
#     # generate md link for the text
#     @staticmethod
#     def get_md_link(title: Optional[str]) -> str:
#         if title is None:
#             return ""
#         title = title.lstrip(" #").rstrip()
#         title = title.lower()
#         out = ''
#         for c in title:
#             if c == ' ' or c == '-':
#                 out += '-'
#             elif c == '_':
#                 out += '_'
#             elif c.isalnum():
#                 out += c
#         return out
#
#     @staticmethod
#     def only_hashtags(x: str) -> bool:
#         return len(x) == x.count("#") and len(x) > 0
#
#     # return two lists
#     # the first  with the words that        start with str p
#     # the second with the words that do not start with char p
#     @staticmethod
#     def split_list(word_list: List[str], prefix: List[str]) -> Tuple[List[str], List[str]]:
#         inside_list = []
#         for p in prefix:
#             inside_list += [x[(len(p)):] for x in word_list if x.startswith(p)]
#             word_list = [x for x in word_list if not x.startswith(p)]
#         return inside_list, word_list
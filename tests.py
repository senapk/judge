#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import tempfile
import os

from indexer import Util, Meta, Item, Sorter, FileItem, Board, Index, IndexConfig


class TestUtil(unittest.TestCase):
    def setUp(self):
        pass

    def test_filter_key(self):
        self.assertEqual(Util.key_filter("01_Teste_Infinito"), "Teste Infinito")

    def test_join(self):
        self.assertEqual("one", Util.join([".", "one"]))
        self.assertEqual("one/two/three", Util.join(["./one", "two", "./three"]))
        self.assertEqual("../one/two/three", Util.join(["..", "./one", "two", "./three"]))
        self.assertEqual("../two/three", Util.join(["..", "./one", "../two", "./three"]))

    def test_get_directions(self):
        self.assertEqual(Util.get_directions("./one.md", "./bin/two.md"), "bin/two.md")
        self.assertEqual(Util.get_directions("one.md", "two.md"), "two.md")
        self.assertEqual(Util.get_directions("folder/one.md", "two.md"), "../two.md")
        self.assertEqual(Util.get_directions("folder/one.md", "folder/two.md"), "two.md")
        self.assertEqual(Util.get_directions("folder1/one.md", "folder2/two.md"), "../folder2/two.md")
        self.assertEqual(Util.get_directions("folder1/folder2/one.md", "folder1/folder2/two.md"), "two.md")
        self.assertEqual(Util.get_directions("folder1/folder2/one.md", "folder1/two.md"), "../two.md")
        self.assertEqual(Util.get_directions("../folder2/one.md", "../folder1/two.md"), "../folder1/two.md")
        self.assertEqual(Util.get_directions("../folder2/one.md", "folder1/two.md"), "../../folder1/two.md")

    def test_split_path(self):
        self.assertEqual(Util.split_path("one.md"), (".", "one.md"))
        self.assertEqual(Util.split_path("a/one.md"), ("a", "one.md"))
        self.assertEqual(Util.split_path("./a/one.md"), ("a", "one.md"))
        self.assertEqual(Util.split_path("a/b/one.md"), ("a/b", "one.md"))

    def test_get_md_link(self):
        self.assertEqual(Util.get_md_link(""), "")
        self.assertEqual(Util.get_md_link("abc!@#$%&*()def"), "abcdef")
        self.assertEqual(Util.get_md_link("AbC Def"), "abc-def")
        self.assertEqual(Util.get_md_link("### abc"), "abc")
        self.assertEqual(Util.get_md_link("abc-_-def"), "abc-_-def")
        self.assertEqual(Util.get_md_link("123asd"), "123asd")

    def test_split_list(self):
        self.assertEqual(Util.split_list(["ac", "ab", "ba", "ca", "ax"], ["a"]), (["c", "b", "x"], ["ba", "ca"]))
        self.assertEqual(Util.split_list(["@abc", "#def", "ghi", "#jkl", "@mno"], ["@"]),
                         (["abc", "mno"], ["#def", "ghi", "#jkl"]))
        self.assertEqual(Util.split_list(["cat:abc", "#def", "ghi", "#jkl", "cat:mno"], ["cat:"]),
                         (["abc", "mno"], ["#def", "ghi", "#jkl"]))


class TestMeta(unittest.TestCase):

    def test_meta(self):
        self.assertEqual(str(Meta("hoje eu vou #dia #noite")), "T[hoje eu vou] t[dia,noite]")
        self.assertEqual(str(Meta("hoje")), "T[hoje]")
        self.assertEqual(str(Meta("hoje eu vou #dia cat:noite")), "T[hoje eu vou] c[noite] t[dia]")
        self.assertEqual(str(Meta("eu cat:a #b cat:d ia #e")), "T[eu ia] c[a,d] t[b,e]")
        self.assertEqual(str(Meta("eu cat:a #b cat:d ia date:e")), "T[eu ia] c[a,d] t[b] d[e]")
        self.assertEqual(str(Meta("eu cat:a #b cat:d sub: ia date:e")), "T[eu] s[ia] c[a,d] t[b] d[e]")
        self.assertEqual(str(Meta("eu cat:a #b cat:d sub: ia date:e la author:g author:u")),
                         "T[eu] s[ia la] c[a,d] t[b] a[g,u] d[e]")
        self.assertEqual(str(Meta("### eu")), "l[###] T[eu]")
        self.assertEqual(str(Meta("  eu   ### ## #ia")), "T[eu] t[ia]")

    def test_content(self):
        self.assertEqual(Meta("hoje eu vou #dia #noite").payload, "")
        self.assertEqual(Meta("hoje eu vou #dia #noite\n").payload, "")
        self.assertEqual(Meta("hoje eu vou #dia #noite\nlinha2 \nlinha 3\n").payload, "linha2 \nlinha 3\n")
        self.assertEqual(Meta("hoje eu vou #dia #noite\nlinha2 ").payload, "linha2 ")

    def test_assemble(self):
        sequence = "lTctads"
        self.assertEqual(Meta("hoje eu vou #dia #noite").assemble(sequence), "hoje eu vou #dia #noite")
        self.assertEqual(Meta("hoje").assemble(sequence), "hoje")
        self.assertEqual(Meta("hoje eu vou #dia cat:noite").assemble(sequence), "hoje eu vou cat:noite #dia")
        self.assertEqual(Meta("eu cat:a #b cat:d ia #e").assemble(sequence), "eu ia cat:a cat:d #b #e")
        self.assertEqual(Meta("eu cat:a #b cat:d ia date:e").assemble(sequence), "eu ia cat:a cat:d #b date:e")
        self.assertEqual(Meta("eu cat:a #b cat:d sub: ia date:e").assemble(sequence),
                         "eu cat:a cat:d #b date:e sub: ia")
        self.assertEqual(Meta("eu cat:a #b cat:d sub: ia date:e la author:g author:u").assemble("Tsctad"),
                         "eu sub: ia la cat:a cat:d #b author:g author:u date:e")
        self.assertEqual(Meta("### eu").assemble(sequence), "### eu")
        self.assertEqual(Meta("  eu   ### ## #ia").assemble(sequence), "eu #ia")


class TestItem(unittest.TestCase):

    def test_mount(self):
        self.assertEqual(str(Item("base/000/R.md")), "base:000:R.md")
        self.assertEqual(str(Item("b1/b2/000/R.md")), "b1/b2:000:R.md")
        self.assertEqual(str(Item("000/R.md")), ".:000:R.md")

    def test_getCover(self):
        item = Item("base/000/R.md")
        item.meta = Meta("## Exemplo de questao\n![figura](img.jpeg)\n")
        self.assertEqual(item.meta.cover, "img.jpeg")

        item.meta = Meta("## Exemplo de questao\n")
        self.assertEqual(item.meta.cover, None)

        # figura no título
        item.meta = Meta("## Exemplo de questao![fig](figura.jpg)\n")
        self.assertEqual(item.meta.cover, None)

        item.meta = Meta("## Exemplo de questao\n![](figura.jpg)\n")
        self.assertEqual(item.meta.cover, "figura.jpg")

        item.meta = Meta("## Exemplo de questao\n![fig](www.figura.jpg)\n")
        self.assertEqual(item.meta.cover, "www.figura.jpg")

        item.meta = Meta("## Exemplo de questao\n![fig](www.figura.jpg)\n![](pic.jpg)")
        self.assertEqual(item.meta.cover, "www.figura.jpg")


class SorterTest(unittest.TestCase):

    def setUp(self) -> None:
        self.itens = [Item("b/0/0.md", "## a teste 0 #fup"), Item("b/3/3.md", "## e teste 3 #poo"),
                      Item("b/1/1.md", "## c teste 1 #poo"), Item("b/4/4.md", "## b teste 4 #poo"),
                      Item("b/2/2.md", "## d teste 2 #ed"), Item("b/5/5.md", "## f teste 5 #ed")]

    def test_sort_by_hook(self):
        list_sorted = Sorter.sorted_by_key(self.itens, "hook")
        self.assertEqual([int(x.hook) for x in list_sorted], [0, 1, 2, 3, 4, 5])

    def test_sort_by_title(self):
        list_sorted = Sorter.sorted_by_key(self.itens, "fulltitle")
        self.assertEqual([int(x.hook) for x in list_sorted], [0, 4, 1, 2, 3, 5])

    def test_sort_by_tag(self):
        list_sorted = Sorter.sorted_by_key(self.itens, "tags")
        self.assertEqual([int(x.hook) for x in list_sorted], [2, 5, 0, 4, 1, 3])

    def test_group_by_tag(self):
        mapt = Sorter.group_by(self.itens, "tags")
        self.assertEqual([pair[0] for pair in mapt], ["ed", "fup", "poo"])
        self.assertEqual([int(x.hook) for x in mapt[0][1]], [2, 5])
        self.assertEqual([int(x.hook) for x in mapt[1][1]], [0])

        # default fulltitle sort
        self.assertEqual([int(x.hook) for x in mapt[2][1]], [4, 1, 3])

    def test_group_by_tag(self):
        mapt = Sorter.group_by(self.itens, "tags", "hook")
        self.assertEqual([pair[0] for pair in mapt], ["ed", "fup", "poo"])
        self.assertEqual([int(x.hook) for x in mapt[0][1]], [2, 5])  # ed
        self.assertEqual([int(x.hook) for x in mapt[1][1]], [0])
        self.assertEqual([int(x.hook) for x in mapt[2][1]], [1, 3, 4])

        # default fulltitle sort
        self.assertEqual([int(x.hook) for x in mapt[2][1]], [1, 3, 4])


class FileItemTest(unittest.TestCase):
    def test_load(self):
        item = FileItem.load_from_file("tests/000/Readme.md")
        self.assertEqual(item.fulltitle, "## Exemplo de questão #fup")
        self.assertEqual(item.payload, "![](img.jpg)")
        self.assertEqual(str(item), "tests:000:Readme.md")
        self.assertEqual(item.meta_str(), "l[##] T[Exemplo de questão] t[fup]")
        item.check_cover()

    def test_check_cover(self):
        with self.assertRaises(FileNotFoundError):
            FileItem.load_from_file("tests/000/ReadmeNoFig.md").check_cover()
        with self.assertRaises(FileNotFoundError):
            FileItem.load_from_file("tests/000/ReadmeNoFig.md").check_cover()

    def test_write(self):
        tmp_dir = tempfile.mkdtemp()
        path = os.path.join(tmp_dir, "Readme.md")
        item = Item(path, "## item item #tag cat:cat\n\ncontent1\n![](img.jpg)\n")
        FileItem.write_from_item(item)
        with open(path) as f:
            self.assertEqual(f.read(), "## item item #tag cat:cat\n\ncontent1\n![](img.jpg)\n")


class BoardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.itens = [Item("b/0/0.md", "## a teste 0 #fup"), Item("b/3/3.md", "## e teste 3 #poo"),
                      Item("b/1/1.md", "## c teste 1 #poo"), Item("b/4/4.md", "## b teste 4 #poo"),
                      Item("b/2/2.md", "## d teste 2 #ed"), Item("b/5/5.md", "## f teste 5 #ed")]

    def test_create(self):
        output = Board.generate(self.itens, "a.md", "fulltitle")
        expected = "[](b/0/0.md) : ## a teste 0 #fup\n" + \
                   "[](b/4/4.md) : ## b teste 4 #poo\n" + \
                   "[](b/1/1.md) : ## c teste 1 #poo\n" + \
                   "[](b/2/2.md) : ## d teste 2 #ed\n" + \
                   "[](b/3/3.md) : ## e teste 3 #poo\n" + \
                   "[](b/5/5.md) : ## f teste 5 #ed\n"
        self.assertEqual(output, expected)

    def test_create_sort2(self):
        output = Board.generate(self.itens, "b/a.md", "hook")
        expected = \
            "[](0/0.md) : ## a teste 0 #fup\n" + \
            "[](1/1.md) : ## c teste 1 #poo\n" + \
            "[](2/2.md) : ## d teste 2 #ed\n" + \
            "[](3/3.md) : ## e teste 3 #poo\n" + \
            "[](4/4.md) : ## b teste 4 #poo\n" + \
            "[](5/5.md) : ## f teste 5 #ed\n"
        self.assertEqual(output, expected)

    def test_create_sort3(self):
        output = Board.generate(self.itens, "c/a.md", "tag, title")
        expected = \
            "[](../b/2/2.md) : ## d teste 2 #ed\n" + \
            "[](../b/5/5.md) : ## f teste 5 #ed\n" + \
            "[](../b/0/0.md) : ## a teste 0 #fup\n" + \
            "[](../b/4/4.md) : ## b teste 4 #poo\n" + \
            "[](../b/1/1.md) : ## c teste 1 #poo\n" + \
            "[](../b/3/3.md) : ## e teste 3 #poo\n"
        self.assertEqual(output, expected)

    def test_load_no_change(self):
        board_content = \
            "[](0/0.md) : ## a teste 0 #fup\n" + \
            "[](1/1.md) : ## c teste 1 #poo\n" + \
            "[](2/2.md) : ## d teste 2 #ed\n" + \
            "[](3/3.md) : ## e teste 3 #poo\n" + \
            "[](4/4.md) : ## b teste 4 #poo\n" + \
            "[](5/5.md) : ## f teste 5 #ed\n"

        itens = Board.check_itens_for_update(board_content, "b/a.md", self.itens)
        self.assertEqual(len(itens), 0)

    def test_load_two_change(self):
        board_content = \
            "[](0/0.md) : ## a teste 0 #fup\n" + \
            "[](1/1.md) : ## c teste 1 #poo\n" + \
            "[](2/2.md) : ## d teste 6 #ed\n" + \
            "[](3/3.md) : ## e teste 7 #poo\n" + \
            "[](4/4.md) : ## b teste 4 #poo\n" + \
            "[](5/5.md) : ## f teste 5 #ed\n"

        itens = Board.check_itens_for_update(board_content, "b/a.md", self.itens)
        self.assertEqual(len(itens), 2)
        self.assertEqual(itens[0].fulltitle, "## d teste 6 #ed")
        self.assertEqual(itens[1].fulltitle, "## e teste 7 #poo")


class IndexTest(unittest.TestCase):
    def setUp(self) -> None:
        self.itens = [Item("b/0/0.md", "## a teste 0 #fup"), Item("b/3/3.md", "## e teste 3 #poo"),
                      Item("b/1/1.md", "## c teste 1 #poo"), Item("b/4/4.md", "## b teste 4 #poo"),
                      Item("b/2/2.md", "## d teste 2 #ed"), Item("b/5/5.md", "## f teste 5 #ed")]

    def test_generate(self):
        cfg = {
            "path": "index.md",
            "sort_by": "title", 
            "group_by": "tag",
            "insert_toc": 1,
            "insert_hook": 1, 
            "reverse_sort": 0,
            "key_filter": 0
        }

        out = Index.generate(self.itens, IndexConfig(cfg))
        expected = """
## Links
- [ed](#ed)
- [fup](#fup)
- [poo](#poo)

## ed

- [@2 d teste 2](b/2/2.md#d-teste-2-ed)
- [@5 f teste 5](b/5/5.md#f-teste-5-ed)

## fup

- [@0 a teste 0](b/0/0.md#a-teste-0-fup)

## poo

- [@4 b teste 4](b/4/4.md#b-teste-4-poo)
- [@1 c teste 1](b/1/1.md#c-teste-1-poo)
- [@3 e teste 3](b/3/3.md#e-teste-3-poo)
"""
        self.assertEqual(out, expected)


if __name__ == '__main__':
    unittest.main()

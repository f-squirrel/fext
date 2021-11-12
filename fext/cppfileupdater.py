from fext import nodefilter
from fext.node import Node
#from clang.cindex import CursorKind
#from string import Template
#import clang.cindex
#import os


class CppFileUpdater:
    def __init__(self, header_root: Node, filename: str):
        self._header_root = header_root
        self._cpp_root = nodefilter.NodeFilter(filename=filename).filter()
        with open(filename, "r") as f:
            self._cpp_content = f.read()
        #index = clang.cindex.Index.create()
        #translation_unit = index.parse(filename, args=['-std=c++17'])

    def update(self):
        pass

    def build(self):
        return self._build()

    def _build(self):
        pass


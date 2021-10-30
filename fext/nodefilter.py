import clang
import clang.cindex
from clang.cindex import CursorKind

from fext.node import Node

IMPORTANT_KINDS = [
            CursorKind.NAMESPACE,
            CursorKind.CLASS_DECL,
            CursorKind.STRUCT_DECL,
            CursorKind.CXX_METHOD,
            CursorKind.FUNCTION_DECL,
    ]


class NodeFilter:
    def __init__(self, filename):
        self._filename = filename

    def filter(self):
        index = clang.cindex.Index.create()
        translation_unit = index.parse(self._filename, args=['-std=c++17'])
        root = Node(translation_unit.cursor)
        for c in translation_unit.cursor.get_children():
            self._traverse(c, "", root)
        return root

    def _is_from_this_file(self, cursor):
        return cursor.translation_unit.spelling == str(cursor.location.file)

    def _traverse(self, cursor, offset, parent_node):
        if not self._is_from_this_file(cursor):
            return
        if cursor.kind not in IMPORTANT_KINDS:
            return
        if (cursor.kind == CursorKind.CXX_METHOD or cursor.kind == CursorKind.FUNCTION_DECL) and not cursor.is_definition():
            return
        node = Node(cursor)
        parent_node.children.append(node)
        for child in cursor.get_children():
            self._traverse(child, offset+"\t", node)


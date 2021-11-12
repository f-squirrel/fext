import clang
import clang.cindex
from clang.cindex import CursorKind
from clang.cindex import Cursor

from fext.node import Node


IMPORTANT_KINDS = [
            CursorKind.NAMESPACE,
            CursorKind.CLASS_DECL,
            CursorKind.STRUCT_DECL,
            CursorKind.CXX_METHOD,
            CursorKind.FUNCTION_DECL,
    ]


class NodeFilter:
    def __init__(self, filename: str):
        self._filename = filename

    def filter(self) -> Node:
        index = clang.cindex.Index.create()
        translation_unit = index.parse(self._filename, args=['-std=c++17'])
        root = Node(translation_unit.cursor)
        for c in translation_unit.cursor.get_children():
            self._traverse(c, "", root)
        return root

    def _is_from_this_file(self, cursor: Cursor) -> bool:
        return cursor.translation_unit.spelling == str(cursor.location.file)

    def _traverse(self, cursor: Cursor, offset: str, parent_node: Node):
        if not self._is_from_this_file(cursor):
            return
        if cursor.kind not in IMPORTANT_KINDS:
            return
        if (cursor.kind == clang.cindex.CursorKind.CXX_METHOD or cursor.kind == CursorKind.FUNCTION_DECL) and not cursor.is_definition():
            return
        node = Node(cursor)
        parent_node.children.append(node)
        for child in cursor.get_children():
            self._traverse(child, offset+"\t", node)


import clang
from clang.cindex import CursorKind


class MessagePrinter:
    def __init__(self, root, file_content):
        self._root = root
        self._file_content = file_content

    def _get_methods(self, node):
        output = []
        if node.cursor.kind == CursorKind.CXX_METHOD or node.cursor.kind == CursorKind.FUNCTION_DECL:
            output.append(node.cursor)
        for child in node.children:
            output.extend(self._get_methods(child))
        return output

    def print(self):
        methods = self._get_methods(self._root)
        for m in methods:
            location = m.location
            print("{f}:{l}:{c}: candidate: ".format(
                f=location.file,
                l=location.line,
                c=location.column,
            ))

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
            definition_obj = m.get_definition()
            definition_str = self._file_content[definition_obj.extent.start.offset:definition_obj.extent.end.offset]
            definition_str = definition_str[0:definition_str.index("{")]

            token = next(m.get_tokens())
            print("{f}:{l}:{c}: {m}".format(
                f=token.location.file,
                l=token.location.line,
                c=token.location.column,
                m=definition_str,
            ))

from clang.cindex import CursorKind

class HeaderFileUpdater:
    def __init__(self, root, header_content):
        self._header_content = header_content
        self._root= root

    def update(self):
        return self._update(self._get_methods(self._root))

    def _get_methods(self, node):
        output = []
        if node.cursor.kind == CursorKind.CXX_METHOD or \
            node.cursor.kind == CursorKind.FUNCTION_DECL:
            output.append(node.cursor)
        for child in node.children:
            output.extend(self._get_methods(child))
        return output

    def _get_body(self, cursor):
        for c in cursor.get_children():
            if c.kind == CursorKind.COMPOUND_STMT:
                return c
        return None

    def _update(self, methods):
        header_template = ""
        last_offset = 0
        for m in methods:
            extent = m.get_definition().extent
            declaration_str = "{d};".format(
                    d=self._header_content[extent.start.offset : self._get_body(m).extent.start.offset].rstrip())
            header_template += self._header_content[last_offset : extent.start.offset] + declaration_str
            last_offset = extent.end.offset
        header_template += self._header_content[last_offset:]
        return header_template


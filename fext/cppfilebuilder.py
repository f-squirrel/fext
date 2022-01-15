from fext.node import Node
from clang.cindex import Cursor
from clang.cindex import CursorKind
from string import Template
import os


class CppFileBuilder:
    def __init__(self, root: Node, header_content: str):
        self._header_content = header_content
        self._root = root

    def build(self) -> str:
        return self._build(self._root)

    def _build(self, node: Node) -> str:
        output_string = ""

        for c in node.children:
            child_out = self._build(c)
            if child_out:
                output_string += child_out

        if node.cursor.kind == CursorKind.TRANSLATION_UNIT:
            # if we reached the top, it means that there are no parents available
            output_string = '#include "{include}"\n{content}\n'.format(
                include=os.path.basename(node.cursor.spelling),
                content=output_string)
            return Template(output_string).substitute(parent='')

        if node.cursor.kind == CursorKind.NAMESPACE:
            return '\nnamespace {ns} {{{body}\n}} // {ns}'.format(
                ns=node.cursor.spelling,
                body=output_string)

        if node.cursor.kind == CursorKind.CXX_METHOD:
            return self._build_method(node.cursor)

        if node.cursor.kind == CursorKind.FUNCTION_DECL:
            return self._build_function(node.cursor)

        if node.cursor.kind == CursorKind.CLASS_DECL \
                or node.cursor.kind == CursorKind.STRUCT_DECL:
            return Template(output_string).substitute(
                parent="${{parent}}{}::".format(node.cursor.displayname))
        return ""

    def _get_body(self, cursor: Cursor) -> Cursor:
        for c in cursor.get_children():
            if c.kind == CursorKind.COMPOUND_STMT:
                return c
        return None

    def _extract_body(self, cursor: Cursor) -> str:
        body = self._get_body(cursor)
        return self._header_content[body.extent.start.offset: body.extent.end.offset]

    def _extract_args(self, cursor: Cursor) -> str:
        args = []
        for arg in cursor.get_arguments():
            args.append("{} {}".format(arg.type.spelling, arg.spelling))
        return ", ".join(args)

    def _build_method(self, cursor: Cursor) -> str:
        const_tag = "const " if cursor.is_const_method() else ""

        output_string = "\n{return_type} ${{parent}}{name}({args}) {const_tag}{body}\n".format(
            return_type=cursor.result_type.spelling,
            name=cursor.spelling,
            args=self._extract_args(cursor),
            const_tag=const_tag,
            body=self._extract_body(cursor))
        return output_string

    def _build_function(self, cursor: Cursor) -> str:
        output_string = "\n{return_type} ${{parent}}{name}({args}) {body}\n".format(
            return_type=cursor.result_type.spelling,
            name=cursor.spelling,
            args=self._extract_args(cursor),
            body=self._extract_body(cursor))
        return output_string

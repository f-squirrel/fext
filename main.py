import clang
import clang.cindex
import os

from clang.cindex import CursorKind
from string import Template

IMPORTANT_KINDS = [
            CursorKind.NAMESPACE,
            CursorKind.CLASS_DECL,
            CursorKind.STRUCT_DECL,
            CursorKind.CXX_METHOD,
            CursorKind.FUNCTION_DECL,
    ]

class MessagePrinter:
    def __init__(self, main_node, file_content):
        self._main_node = main_node
        self._file_content = file_content

    def _get_methods(self, node):
        output = []
        if node.cursor.kind == CursorKind.CXX_METHOD or node.cursor.kind == CursorKind.FUNCTION_DECL:
            output.append(node.cursor)
        for child in node.children:
            output.extend(self._get_methods(child))
        return output

    def print(self):
        methods = self._get_methods(self._main_node)
        for m in methods:
            location = m.location
            print("{f}:{l}:{c}: candidate: ".format(
                f=location.file,
                l=location.line,
                c=location.column,
            ))


class Filter:
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

class Node:
    def __init__(self, cursor):
        self.cursor = cursor
        self.children = []

def get_body(cursor):
    for c in cursor.get_children():
        if c.kind == CursorKind.COMPOUND_STMT:
            return c
    return None

def extract_body(cursor, content):
    body = get_body(cursor)
    return content[body.extent.start.offset: body.extent.end.offset]

def extract_args(cursor):
    args = []
    for arg in cursor.get_arguments():
        args.append("{} {}".format(arg.type.spelling, arg.spelling))
    return ", ".join(args)

def build_method(cursor, f):
    const_tag = "const " if cursor.is_const_method() else ""

    output_string = "\n{return_type} ${{parent}}{name}({args}) {const_tag}{body}\n".format(
            return_type=cursor.result_type.spelling,
            name=cursor.spelling,
            args=extract_args(cursor),
            const_tag=const_tag,
            body=extract_body(cursor, f))
    return output_string

def build_function(cursor, f):
    output_string = "\n{return_type} ${{parent}}{name}({args}) {body}\n".format(
            return_type=cursor.result_type.spelling,
            name=cursor.spelling,
            args=extract_args(cursor),
            body=extract_body(cursor, f))
    return output_string

def build_cpp(node, f):
    output_string = ""

    for c in node.children:
        child_out = build_cpp(c, f)
        if child_out:
            output_string+=child_out

    if node.cursor.kind == CursorKind.TRANSLATION_UNIT:
        # if we reached the top, it means that there are no parents available
        output_string = '#include "{include}"\n{content}\n'.format(
                include=os.path.basename(node.cursor.spelling),
                content = output_string)
        return Template(output_string).substitute(parent='')

    if node.cursor.kind == CursorKind.NAMESPACE:
        return '\nnamespace {ns} {{{body}\n}} // {ns}'.format(ns=node.cursor.spelling, body=output_string)

    if node.cursor.kind == CursorKind.CXX_METHOD:
        return build_method(node.cursor, f)

    if node.cursor.kind == CursorKind.FUNCTION_DECL:
        return build_function(node.cursor, f)

    if node.cursor.kind == CursorKind.CLASS_DECL or node.cursor.kind == CursorKind.STRUCT_DECL:
        return Template(output_string).substitute(parent="${{parent}}{}::".format(node.cursor.spelling))

    return output_string

def main():
    filename = 'test/header.hpp'
    filter = Filter(filename)
    root = filter.filter()
    with open(filename, 'r') as f:
        content = f.read()
        #output = build_cpp(root, content)
        #print(output)

        printer = MessagePrinter(root, content)
        printer.print()

if __name__ == "__main__":
    main()

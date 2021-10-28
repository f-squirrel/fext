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

class Node:
    def __init__(self, cursor):
        self.cursor = cursor
        self.children = []

def traverse(cursor, offset, parent_node):
    # filter includes
    if cursor.translation_unit.spelling != str(cursor.location.file):
        return
    if cursor.kind not in IMPORTANT_KINDS:
        return
    if (cursor.kind == CursorKind.CXX_METHOD or cursor.kind == CursorKind.FUNCTION_DECL) and not cursor.is_definition():
        return
    node = Node(cursor)
    parent_node.children.append(node)
    for child in cursor.get_children():
        traverse(child, offset+"\t", node)

def extract_body(cursor, content):
    compound = None
    for c in cursor.get_children():
        if c.kind == CursorKind.COMPOUND_STMT:
            compound = c
    return content[compound.extent.start.offset: compound.extent.end.offset]

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

def show_candidates(node):
    if node.cursor.kind == CursorKind.CXX_METHOD or node.cursor.kind == CursorKind.FUNCTION_DECL:
        location = node.cursor.location
        print("{f}:{l}:{c}: candidate: ".format(
            f=location.file,
            l=location.line,
            c=location.column
            ))
    for child in node.children:
        show_candidates(child)

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
    index = clang.cindex.Index.create()
    filename = 'test/header.hpp'
    translation_unit = index.parse(filename, args=['-std=c++17'])
    #for c in translation_unit.cursor.walk_preorder():
    #    print("kind: {}".format(c.kind))
    main_node = Node(translation_unit.cursor)
    for c in translation_unit.cursor.get_children():
        traverse(c, "", main_node)
    with open(filename, 'r') as f:
        content = f.read()
        output = build_cpp(main_node, content)
    print(output)

    show_candidates(main_node)

if __name__ == "__main__":
    main()

import clang
import clang.cindex
import os

from clang.cindex import CursorKind
from string import Template

from fext import messageprinter
from fext import nodefilter

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
    filter = nodefilter.NodeFilter(filename)
    root = filter.filter()
    with open(filename, 'r') as f:
        content = f.read()
        #output = build_cpp(root, content)
        #print(output)

        printer = messageprinter.MessagePrinter(root, content)
        printer.print()

if __name__ == "__main__":
    main()

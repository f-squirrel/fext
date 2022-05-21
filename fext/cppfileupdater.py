from fext import nodefilter
from fext.node import Node
# from clang.cindex import CursorKind
# from string import Template
import clang.cindex
from clang.cindex import Cursor
from clang.cindex import CursorKind
from string import Template

import logging
# import os


class CppFileUpdater:
    def __init__(self, header_root: Node, methods: list, header_content: str, filename: str):
        self._header_root = header_root
        logging.info("DIMA: cpp: {}".format(filename))
        # self._cpp_root = nodefilter.NodeFilter(filename=filename).filter()
        with open(filename, "r") as f:
            self._cpp_content = f.read()
        index = clang.cindex.Index.create()
        self._methods = methods
        self._header_content = header_content
        self._translation_unit = index.parse(filename, args=['-std=c++17'])

    # 1. go over nodes in the cpp
    # 2. find corresponding node in the header tree
    # 3. add the node from the header to the end of cpp node
    # 4. for the nodes that are not found, call cpp builder (?)
    def build2(self):
        return self._build(self._header_root)

    def _complete_method(self, methodr, parent):
        semantic_parent = method.semantic_parent.get_usr()
        while semantic_parent is not parent:
            semantic_parent = method

    def _find_parent_in_cpp(self, parent_in_header: Cursor):
        while parent_in_header.kind is not CursorKind.TRANSLATION_UNIT: # Reached the top
            print("Looking for {}".format(parent_in_header.displayname))
            parent_in_tu = self._find_in_cpp(parent_in_header)
            if parent_in_tu:
                print("found parent {}".format(parent_in_tu.displayname))
                break
            parent_in_header = parent_in_header.semantic_parent
        if not parent_in_tu:
            parent_in_tu = self._translation_unit.cursor
        return parent_in_tu

    def build(self):
        print("THIS FILE")
        pos_and_method_str = []
        for method in self._methods:
            print("Wokring on {}".format(method.displayname))
            parent_in_header = method.semantic_parent
            print(parent_in_header.kind)
            parent_in_tu = self._find_parent_in_cpp(parent_in_header)
            method_str=self._build_method(method, parent_in_tu)
            if method.kind == CursorKind.CXX_METHOD:
                pass
                # method_str = Template(method_str).substitute(parent=''+method.semantic_parent.spelling + '::')
                # method_str = Template(method_str).substitute(parent='${{parent}}'+method.semantic_parent.spelling + '::')
            if method.kind == CursorKind.FUNCTION_DECL:
                method_str = Template(method_str).substitute(parent='')

            print("offset: s: {}, e: {}".format(parent_in_tu.extent.start.offset, parent_in_tu.extent.end.offset))
            pos_and_method_str.append((parent_in_tu.extent.end.offset, method_str))
        pos_and_method_str.sort(key=lambda pm: pm[0]) # sort by offset
        for offset, method_str in pos_and_method_str:
            print(offset, method_str)

    def _get_body(self, cursor: Cursor) -> Cursor:
        for c in cursor.get_children():
            if c.kind == CursorKind.COMPOUND_STMT:
                return c
        return None

    def _extract_args(self, cursor: Cursor) -> str:
        args = []
        for arg in cursor.get_arguments():
            args.append("{} {}".format(arg.type.spelling, arg.spelling))
        return ", ".join(args)

    def _extract_body(self, cursor: Cursor) -> str:
        body = self._get_body(cursor)
        return self._header_content[body.extent.start.offset: body.extent.end.offset]

    def _build_method(self, cursor: Cursor, parent_cursor: Cursor) -> str:
        const_tag = "const " if cursor.is_const_method() else ""

        output_string = "\n{return_type} ${{parent}}{name}({args}) {const_tag}{body}\n".format(
            return_type=cursor.result_type.spelling,
            name=cursor.spelling,
            args=self._extract_args(cursor),
            const_tag=const_tag,
            body=self._extract_body(cursor))

        semantic_parent = cursor.semantic_parent
        while semantic_parent.get_usr() != parent_cursor.get_usr():
            if semantic_parent.kind == CursorKind.CLASS_DECL:
                output_string = Template(output_string).substitute(parent='${parent}'+ semantic_parent.spelling + '::')
            elif semantic_parent.kind == CursorKind.NAMESPACE:
                output_string = "namespace {} {{\n{}}}".format(semantic_parent.spelling, output_string)
            else:
                assert False
            semantic_parent = semantic_parent.semantic_parent

        output_string = Template(output_string).substitute(parent='')
        return output_string

    def _build_function(self, cursor: Cursor) -> str:
        output_string = "\n{return_type} ${{parent}}{name}({args}) {body}\n".format(
            return_type=cursor.result_type.spelling,
            name=cursor.spelling,
            args=self._extract_args(cursor),
            body=self._extract_body(cursor))
        return output_string

    def _find_in_cursor(self, cursor: Cursor, kind: CursorKind):
        print("kind: {}".format(cursor.kind))
        for c in cursor.get_children():
            print("kind: {}".format(c.kind))
            if c.kind == kind:
                return c
        return None

    def _is_from_this_file(self, cursor: Cursor) -> bool:
        #logging.debug("not from this {}".format(cursor.displayname))
        #logging.debug("from this {}".format(cursor.translation_unit.spelling))
        return cursor.translation_unit.spelling == str(cursor.location.file)

    def _find_in_cpp(self, cursor_to_find, hint_cursor = None):
        cursor = hint_cursor if hint_cursor else self._translation_unit.cursor
        for c in cursor.walk_preorder():
            if not self._is_from_this_file(c):
                continue
            print("LOOKING INTO {}".format(c.displayname))
            if c.get_usr() == cursor_to_find.get_usr():
                print("FOUND {}".format(c.displayname))
                return c
        return None

    def _build(self, node):
        cpp = self._find_in_cpp(node.cursor)
        if cpp:
            logging.debug("Found displayname: {}".format(cpp.displayname))
        for c in node.children:
            child_out = self._build(c)
            if child_out:
                pass

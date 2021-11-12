from clang.cindex import Cursor


class Node:
    def __init__(self, cursor: Cursor):
        self.cursor = cursor
        self.children = []


import clang
import clang.cindex

# List of kinds to recurse in:
# namespace
# class declaration
# function body

# function signature in cpp:
# return_type class_name::cursor.spelling(arguments) const {}
def traverse(cursor, offset):
    print("{}{}: name: {}".format(offset, cursor.kind, cursor.spelling))
    if cursor.kind == clang.cindex.CursorKind.CXX_METHOD:
        print("{}start: {}, end: {}".format(offset, cursor.extent.start, cursor.extent.end))
        print("{}is_static_method: {}".format(offset, cursor.is_static_method()))
        print("{}is_definition: {}".format(offset, cursor.is_definition()))
        print("{}is_const_method: {}".format(offset, cursor.is_const_method()))
        print("{}is_virtual_method: {}".format(offset, cursor.is_virtual_method()))
        #print("{}storage_class: {}".format(offset, cursor.storage_class))
        print("{}result_type: {}".format(offset, cursor.result_type.spelling))
        #print("{}displayname: {}".format(offset, cursor.displayname))
    #if cursor.kind == clang.cindex.CursorKind.DECL_STMT:
    #    print("{}start: {}, end: {}".format(offset, cursor.extent.start, cursor.extent.end))
    if cursor.kind == clang.cindex.CursorKind.COMPOUND_STMT:
        print("{}start: {}, end: {}".format(offset, cursor.extent.start, cursor.extent.end))
        pass
    for child in cursor.get_children():
        traverse(child, offset+"\t")

def main():
    index = clang.cindex.Index.create()
    translation_unit = index.parse('test/header.hpp', args=['-std=c++17'])
    for c in translation_unit.cursor.get_children():
        traverse(c, "")

if __name__ == "__main__":
    main()

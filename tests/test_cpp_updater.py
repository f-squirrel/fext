import unittest
from fext import diagnostic
from fext import nodefilter
from fext import cppfileupdater


class TestCppBuilder(unittest.TestCase):

    def test_messages(self):
        filename = "tests/input/cpp_builder_case.h"
        expected_filename = "tests/expected_output/multiple_declaration.txt"

        filter = nodefilter.NodeFilter(filename)
        root = filter.filter()
        with open(filename, 'r') as f:
            content = f.read()
            diag = diagnostic.Diagnostic(root, content)
            methods = diag._get_methods(diag._root)
            updater = cppfileupdater.CppFileUpdater(root, methods, content, "tests/input/cpp_builder_case.cpp")
            updater.build()
            #with open(expected_filename, 'r') as expected_file:
            #    expected_filename = expected_file.read()
            #    self.assertEqual(out, expected_filename)


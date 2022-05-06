import unittest
from fext import diagnostic
from fext import nodefilter
from fext import cppfilebuilder


class TestCppBuilder(unittest.TestCase):

    def test_messages(self):
        filename = "tests/input/multiple_declarations.h"
        expected_filename = "tests/expected_output/multiple_declaration.txt"

        filter = nodefilter.NodeFilter(filename)
        root = filter.filter()
        with open(filename, 'r') as f:
            content = f.read()
            builder = cppfilebuilder.CppFileBuilder(root, content)
            out = builder.build()
            with open(expected_filename, 'r') as expected_file:
                expected_filename = expected_file.read()
                self.assertEqual(out, expected_filename)

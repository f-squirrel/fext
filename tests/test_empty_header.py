import unittest
from fext import messageprinter
from fext import nodefilter

EXPECTED_OUTPUT = ''

class TestEmptyHeader(unittest.TestCase):

    def test_messages_empty_header(self):
        filename = "tests/test_input/empty_header.h"

        filter = nodefilter.NodeFilter(filename)
        root = filter.filter()
        with open(filename, 'r') as f:
            content = f.read()
            printer = messageprinter.MessagePrinter(root, content)
            self.assertEqual(printer.print(), EXPECTED_OUTPUT)

    def test_messages_empty_header_with_includes(self):
        filename = "tests/test_input/empty_header_with_include.h"

        filter = nodefilter.NodeFilter(filename)
        root = filter.filter()
        with open(filename, 'r') as f:
            content = f.read()
            printer = messageprinter.MessagePrinter(root, content)
            self.assertEqual(printer.print(), EXPECTED_OUTPUT)

if __name__ == '__main__':
    unittest.main()

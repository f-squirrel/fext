
import unittest
from fext import diagnostic
from fext import nodefilter


EXPECTED_OUTPUT = '''tests/test_input/multiple_declarations.h:8:5: virtual void virtual_method ()
tests/test_input/multiple_declarations.h:13:5: void foo(int a, bool b)
tests/test_input/multiple_declarations.h:16:5: static void zzz()
tests/test_input/multiple_declarations.h:17:5: inline static void aaa()
tests/test_input/multiple_declarations.h:19:5: void const_method() const
tests/test_input/multiple_declarations.h:20:5: void virtual_method () override
tests/test_input/multiple_declarations.h:21:5: auto auto_method()
tests/test_input/multiple_declarations.h:26:9: void c_method()
tests/test_input/multiple_declarations.h:31:5: void f()
tests/test_input/multiple_declarations.h:45:9: void foo(int v)
tests/test_input/multiple_declarations.h:48:1: inline void free_function()
tests/test_input/multiple_declarations.h:53:1: template<>
inline void free_function<int>(int i)
tests/test_input/multiple_declarations.h:56:1: inline void free_inline_function(int a)'''


class TestMiltipleDeclarations(unittest.TestCase):

    def test_messages(self):
        filename = "tests/test_input/multiple_declarations.h"

        filter = nodefilter.NodeFilter(filename)
        root = filter.filter()
        with open(filename, 'r') as f:
            content = f.read()
            diag = diagnostic.Diagnostic(root, content)
            self.assertEqual(diag.show().strip(), EXPECTED_OUTPUT)

if __name__ == '__main__':
    unittest.main()


from fext import cppfilebuilder
from fext import messageprinter
from fext import nodefilter

def main():
    filename = 'test/header.hpp'
    filter = nodefilter.NodeFilter(filename)
    root = filter.filter()
    with open(filename, 'r') as f:
        content = f.read()
        builder = cppfilebuilder.CppFileBuilder(root, content)
        print(builder.build())

        printer = messageprinter.MessagePrinter(root, content)
        printer.print()

if __name__ == "__main__":
    main()

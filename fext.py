#!/usr/bin/env python3

import argparse
from fext import cppfilebuilder
from fext import messageprinter
from fext import nodefilter


def parse_args():
    parser = argparse.ArgumentParser(prog="fext", description="Function Extractor")

    parser.add_argument("--config", default=".fext.config", help="Path to config file (default: %(default)s)")
    parser.add_argument("--fix", action="store_true", help="Fix headers")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dir", help="Directory to parse")
    group.add_argument("--file", help="File to parse")

    return parser.parse_args()


def main():
    args = parse_args()

    filename = args.file

    filter = nodefilter.NodeFilter(filename)
    root = filter.filter()
    with open(filename, 'r') as f:
        content = f.read()

        if args.fix:
            builder = cppfilebuilder.CppFileBuilder(root, content)
            print(builder.build())
        else:
            printer = messageprinter.MessagePrinter(root, content)
            printer.print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import argparse
from fext import cppfilebuilder
from fext import cppfileupdater
from fext import diagnostic
from fext import nodefilter
from fext import headerfileupdater
import os


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
            header_updater = headerfileupdater.HeaderFileUpdater(root, content)
            print("Generated Header:\n{}".format(header_updater.update()))
            file = os.path.splitext(filename)[0] + ".cpp"
            if os.path.exists(file):
                updater = cppfileupdater.CppFileUpdater(root, file)
                print("Updated CPP:\n{}".format(updater.build()))
            else:
                builder = cppfilebuilder.CppFileBuilder(root, content)
                print("Generated CPP:\n{}".format(builder.build()))

        else:
            diag = diagnostic.Diagnostic(root, content)
            print(diag.show())


if __name__ == "__main__":
    main()

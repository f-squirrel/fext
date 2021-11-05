# Function Extractor

## Purpose

The purpose of the tool is to identify methods and functions defined in header files and
automatically move the definitions to corresponding translation units.  If a translation
unit does not exist, the tool creates it.

## Caveats

* Function Extractor expects to receive valid C/C++ code as input
* Highly recommended to run it only for commited code
* The tool does not offer custom formatting. If needed, [clang-format](https://clang.llvm.org/docs/ClangFormat.html) can be used.

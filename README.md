# Function Extractor

## Purpose

The purpose of the tool is to identify methods and functions defined in header files and
automatically move the definitions to corresponding translation units.  If a translation
unit does not exist, the tool creates it.

## Caveats

* Function Extractor expects to receive a valid C/C++ code as an input
* Highly recommended to run it only for already commited code
* The tool does not support any special formatting, if needed run clang-tidy over the changed/created files

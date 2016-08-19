# cppmangle

A library for demangling and mangling Visual Studio C++ names.

## Installation

Simply download from PyPI or download from Github.

    $ pip install cppmangle

## Getting started

The installation will install a package named `cppmangle` and a command-line
script `cppdemangle`.

Pass the script one or more mangled names to get them demangled.

    $ cppdemangle '?get_minion_stats@@YA?AUminion_stats@@H@Z'
    struct minion_stats __cdecl get_minion_stats(int)

You can also pass a filename prefixed with an at-sign, the script will
demangle each line in the file.

    $ cppdemangle @names.txt

## Using the library

You can also use the library from Python code by importing `cppmangle` module.
Use `demangle` function to turn the mangled name into a AST object (see
the `ast` module for more) and `mangle` to turn it back to a string.
The function `cdecl_sym` will turn the AST object into a string containing
a C++ declaration.

    >>> from cppmangle import demangle, cdecl_sym
    >>> demangle('?get_minion_stats@@YA?AUminion_stats@@H@Z')
    <cppmangle.ast.Function object at 0x02754F30>
    >>> cdecl_sym(_)
    'struct minion_stats __cdecl get_minion_stats(int)'

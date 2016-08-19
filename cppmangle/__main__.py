from .mangle import mangle, demangle
from .cdecl import cdecl_sym
import argparse

def main():
    ap = argparse.ArgumentParser(fromfile_prefix_chars='@')
    ap.add_argument('name', nargs='+')
    args = ap.parse_args()

    for name in args.name:
        dem = demangle(name)
        print(cdecl_sym(dem))

from .msvc import msvc_mangle, msvc_demangle

def mangle(name):
    return msvc_mangle(name)

def demangle(obj):
    return msvc_demangle(obj)

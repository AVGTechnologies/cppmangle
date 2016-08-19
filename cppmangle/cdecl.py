from ast import *

_cvs = ('', 'const ', 'volatile ', 'const volatile ')
_class_kinds = ('union', 'struct', 'class', 'enum')

def _cdecl_templ_arg(arg):
    if isinstance(arg, int):
        return str(arg)
    return cdecl_type(arg)

def _cdecl_name(name):
    if isinstance(name, SpecialName):
        return name.desc
    if isinstance(name, TemplateId):
        return '{}<{}>'.format(name.name, ', '.join(_cdecl_templ_arg(arg) for arg in name.args))
    return name

def _cdecl_qname(qname):
    return '::'.join(_cdecl_name(name) for name in qname)

def cdecl_type(type, obj_name=''):
    prefixes = []
    suffixes = []
    prio = 0

    if obj_name:
        prefixes.append(obj_name)

    while True:
        if isinstance(type, SimpleType):
            prefixes.append(_cvs[type.cv])
            prefixes.append(' ')
            prefixes.append(type.basic_type.desc)
            break

        if isinstance(type, ClassType):
            prefixes.append(' ')
            prefixes.append(_cdecl_qname(type.qname))
            prefixes.append(' ')
            prefixes.append(_class_kinds[type.kind])
            break

        if isinstance(type, ArrayType):
            if prio > 1:
                prefixes.append('(')
                suffixes.append(')')
            prio = 1
            for dim in type.dims:
                suffixes.append('[{}]'.format(dim))
            type = type.target
            continue

        if isinstance(type, PtrType):
            prio = 2
            if type.ref:
                prefixes.append('& ')
            else:
                prefixes.append('* ')
            type = type.target
            continue

        if isinstance(type, FunctionType):
            prefixes.append('__{} '.format(type.cconv.desc))
            if prio != 0:
                prefixes.append('(')
                suffixes.append(')')
                prio = 0
            suffixes.append('(')
            suffixes.append(', '.join(cdecl_type(param) for param in type.params))
            suffixes.append(')')
            type = type.ret_type
            continue

        raise RuntimeError('unk')

    return ''.join(reversed(prefixes)).strip() + ''.join(suffixes)

def cdecl_sym(sym):
    if isinstance(sym, Function):
        r = []
        if sym.access_spec is not None:
            r.extend((sym.access_spec.desc, ': '))
        if sym.kind == fn_virtual:
            r.append('virtual ')
        if sym.kind == fn_class_static:
            r.append('static ')
        r.append(cdecl_type(sym.type, _cdecl_qname(sym.qname)))
        return ''.join(r)
    raise RuntimeError('unk')

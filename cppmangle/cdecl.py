from .ast import *

_cvs = ('', 'const ', 'volatile ', 'const volatile ')
_class_kinds = ('union', 'struct', 'class', 'enum')

def _cdecl_templ_arg(arg):
    if isinstance(arg, int):
        return str(arg)
    return cdecl_type(arg)

def _cdecl_name(name, prev):
    if name == n_constructor:
        return prev, None
    if name == n_destructor:
        return '~{}'.format(prev), None
    if isinstance(name, SpecialName):
        return name.desc, None
    if isinstance(name, TemplateId):
        return '{}<{}>'.format(name.name, ','.join(_cdecl_templ_arg(arg) for arg in name.args)), name.name
    return name, name

def cdecl_qname(qname):
    names = []
    base_name = None
    for name in qname:
        full_name, base_name = _cdecl_name(name, base_name)
        names.append(full_name)
    return '::'.join(names)

def cdecl_type(type, obj_name=''):
    prefixes = []
    suffixes = []
    prio = 0

    if obj_name:
        prefixes.append(obj_name)

    while True:
        if isinstance(type, SimpleType):
            if type.basic_type == t_none:
                break

            prefixes.append(_cvs[type.cv])
            prefixes.append(' ')
            prefixes.append(type.basic_type.desc)
            break

        if isinstance(type, ClassType):
            prefixes.append(_cvs[type.cv])
            prefixes.append(' ')
            prefixes.append(cdecl_qname(type.qname))
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
                prefixes.append(_cvs[type.cv])
                prefixes.append('* ')
            type = type.target
            continue

        if isinstance(type, FunctionType):
            if not prefixes or prefixes[-1][0] != '*':
                prefixes.append(' ')
            prefixes.append('__{}'.format(type.cconv.desc))
            if prio != 0:
                prefixes.append('(')
                suffixes.append(')')
                prio = 0
            suffixes.append('(')
            suffixes.append(','.join(cdecl_type(param) for param in type.params))
            suffixes.append(')')
            if type.this_cv is not None:
                suffixes.append(_cvs[type.this_cv])
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
        r.append(cdecl_type(sym.type, cdecl_qname(sym.qname)))
        return ''.join(r)
    raise RuntimeError('unk')

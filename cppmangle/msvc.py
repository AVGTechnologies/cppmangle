import speg
from .ast import *

def _transpose(m):
    return dict((m[k], k) for k in m)

_basic_type_map = {
    '@': t_none,
    'X': t_void,
    '_N': t_bool,
    'D': t_char,
    'C': t_schar,
    'E': t_uchar,
    'F': t_sshort,
    'G': t_ushort,
    'H': t_sint,
    'I': t_uint,
    'J': t_slong,
    'K': t_ulong,
    '_J': t_slonglong,
    '_K': t_ulonglong,
    '_W': t_wchar,
    'M': t_float,
    'N': t_double,
    'O': t_longdouble,
    'Z': t_ellipsis,
    }

_basic_type_map_inv = _transpose(_basic_type_map)

_cc_map = {
    'A': cconv_cdecl,
    'E': cconv_thiscall,
    'G': cconv_stdcall,
    'I': cconv_fastcall,
    }

_cc_map_inv = _transpose(_cc_map)

_class_kind_map = {
    'T': k_union,
    'U': k_struct,
    'V': k_class,
    'W4': k_enum,
    }
_class_kind_map_inv = _transpose(_class_kind_map)

_special_names_map = {
    '0': n_constructor,
    '_F': n_def_constr_closure,
    '1': n_destructor,
    'A': n_op_subscript,
    'R': n_op_call,
    'C': n_op_member,
    'E': n_op_inc,
    'F': n_op_dec,
    '2': n_op_new,
    '_U': n_op_new_arr,
    '3': n_op_delete,
    '_V': n_op_delete_arr,
    'D': n_op_deref,
    '7': n_op_lnot,
    'S': n_op_bnot,
    'J': n_op_mem_ptr,
    'D': n_op_mul,
    'K': n_op_div,
    'L': n_op_mod,
    'H': n_op_add,
    'G': n_op_sub,
    '6': n_op_shl,
    '5': n_op_shr,
    'M': n_op_lt,
    'O': n_op_gt,
    'N': n_op_le,
    'P': n_op_ge,
    '8': n_op_eq,
    '9': n_op_neq,
    'I': n_op_band,
    'U': n_op_bor,
    'T': n_op_xor,
    'V': n_op_land,
    'W': n_op_lor,
    '4': n_op_assign,
    'X': n_op_assign_mul,
    '_0': n_op_assign_div,
    '_1': n_op_assign_mod,
    'Y': n_op_assign_add,
    'Z': n_op_assign_sub,
    '_3': n_op_assign_shl,
    '_2': n_op_assign_shr,
    '_4': n_op_assign_band,
    '_5': n_op_assign_bor,
    '_6': n_op_assign_xor,
    'Q': n_op_comma,
    'B': n_op_cast,
    '_7': n_vtable,
    }

_special_names_map_inv = _transpose(_special_names_map)

def _p_simple_name(p):
    nl = p.get('names')
    with p:
        ref = int(p(r'\d'))
        return nl[ref]

    with p:
        special_name = p(r'\?_?[0-9A-Z]')[1:]
        return _special_names_map[special_name]

    n = p(r'[^@]+@')[:-1]
    if n not in nl:
        p.set_global('names', nl + (n,))
    return n

def _p_int(p):
    neg = bool(p.opt(r'\?'))

    dig = p.opt(r'\d')
    if dig:
        r = int(dig) + 1
    else:
        t = p('[A-P]+@')[:-1]
        r = 0
        for ch in t:
            r = 16*r + (ord(ch) - ord('A'))

    return -r if neg else r

def _p_name(p):
    with p:
        p(r'\?\$')
        name = p(_p_simple_name)

        type_args = []
        while not p.opt('@'):
            if p.opt(r'\$0'):
                type_args.append(p(_p_int))
            else:
                p.set('names', ())
                arg, _ = p(_p_type)
                type_args.append(arg)
        return TemplateId(name, type_args)
    return p(_p_simple_name)

def _p_qname(p):
    qname = []
    with p:
        while not p.opt('@'):
            qname.append(p(_p_name))
            p.commit()
    return tuple(qname[::-1])

def _p_basic_type(p):
    c = p(r'[@XDCEFGHIJKMNOZ]|_[NJKW]')
    return SimpleType(0, _basic_type_map[c]), len(c) >= 2

_cvs = [0, cv_const, cv_volatile, cv_const | cv_volatile]

def _p_type(p):
    with p:
        kind = p('T|U|V|W4')[0]
        kind = ord(kind) - ord('T')
        qname = p(_p_qname)
        return ClassType(0, kind, qname), True

    with p:
        # arrays
        p('Y')
        dim_count = p(_p_int)
        dims = tuple(p(_p_int) for i in xrange(dim_count))
        target, reg = p(_p_type)
        return ArrayType(dims, target), True

    with p:
        # pointer to fn
        cv = _cvs[ord(p('[PQRS]6')[0]) - ord('P')]
        fn_type = p(_p_fn_type)
        return PtrType(cv, fn_type, False, as_default), True

    with p:
        # pointer types
        kind = p('[APQRS]')
        addr_space = as_msvc_x64_absolute if p('E?') else as_default
        target_cv = p('[A-D]')
        target, reg = p(_p_type)
        target.cv = _cvs[ord(target_cv) - ord('A')]

        cv = _cvs[ord(kind) - ord('P')] if kind != 'A' else 0
        return PtrType(cv, target, kind == 'A', addr_space), True

    return p(_p_basic_type)

def _is_void_or_ellipsis(type):
    return isinstance(type, SimpleType) and type.basic_type in (t_void, t_ellipsis)

def _p_fn_type(p):
    cconv = _cc_map[p('[AEGI]')] #if qname[-1] not in _noncv_member_funcs else cconv_thiscall

    ret_cv = p(r'(\?[A-D])?')
    ret, reg = p(_p_type)
    if ret_cv:
        ret.cv = ord(ret_cv[1]) - ord('A')
    params = []

    with p:
        while not p.opt('@'):
            with p:
                reg_ref = p('\d')
                param_type = p.get('param_types')[int(reg_ref)]

            if not p:
                param_type, reg = p(_p_type)
                if reg:
                    param_types = p.get('param_types') + (param_type,)
                    p.set_global('param_types', param_types)

            params.append(param_type)
            p.commit()
            if _is_void_or_ellipsis(param_type):
                break

    p('Z')
    return FunctionType(cconv, ret, params, 0)

def _p_root(p):
    p.set_global('names', ())
    p.set_global('param_types', ())

    p(r'\?')
    qname = p(_p_qname)

    with p:
        # non-member function
        p('[YZ]')
        access_class = None
        kind = fn_free

    if not p:
        # member function
        modif = p('[A-V]')
        modif = ord(modif) - ord('A')
        access_class = (access_private, access_protected, access_public)[modif // 8]
        modif = modif % 8
        if modif in (2, 3):
            kind = fn_class_static
        elif modif in (4, 5):
            kind = fn_virtual
        else:
            kind = fn_instance


    can_have_cv = kind in (fn_instance, fn_virtual)
    if can_have_cv:
        addr_space = as_msvc_x64_absolute if p('E?') else as_default
        this_cv = ord(p('[A-D]')) - ord('A')
    else:
        addr_space = as_default
        this_cv = None

    type = p(_p_fn_type)
    p(p.eof)

    type.this_cv = this_cv

    return Function(qname, type, kind, access_class, addr_space)

def msvc_demangle(s):
    return speg.peg(s, _p_root)

def _m_int(arg):
    r = []
    if arg < 0:
        r.append('?')
        arg = -arg

    if 1 <= arg <= 10:
        r.append(str(arg - 1))
    elif arg == 0:
        r.append('A@')
    else:
        digs = []
        while arg != 0:
            digs.append('ABCDEFGHIJKLMNOP'[arg % 16])
            arg = arg // 16
        digs.reverse()
        r.extend(digs)
        r.append('@')
    return ''.join(r)

def _m_templ_arg(arg):
    if isinstance(arg, int):
        return '$0{}'.format(_m_int(arg))
    return _m_type(arg, {}, {})

def _m_qname(qname, nl):
    r = []
    for name in qname[::-1]:
        pos = nl.get(name)
        if pos is not None:
            r.append(str(pos))
            continue

        if isinstance(name, SpecialName):
            r.append('?{}'.format(_special_names_map_inv[name]))
        elif isinstance(name, TemplateId):
            r.append('?${}@{}@'.format(name.name, ''.join(_m_templ_arg(arg) for arg in name.args)))
        else:
            r.append('{}@'.format(name))
            if len(nl) < 9:
                nl[name] = len(nl)

    return '{}@'.format(''.join(r))

def _m_type(type, nl, tl):
    if isinstance(type, SimpleType):
        return _basic_type_map_inv[type.basic_type]
    if isinstance(type, PtrType):
        if type.ref:
            kind = 'A'
        else:
            kind = 'PQRS'[type.cv]
        if isinstance(type.target, FunctionType):
            return '{}6{}'.format(kind, _m_fn_type(type.target, nl, tl))
        else:
            return '{}{}{}{}'.format(kind, 'E' if type.addr_space == as_msvc_x64_absolute else '', 'ABCD'[type.target.cv], _m_type(type.target, nl, tl))
    if isinstance(type, ArrayType):
        return 'Y{}{}{}'.format(_m_int(len(type.dims)), ''.join(_m_int(dim) for dim in type.dims), _m_type(type.target, nl, tl))
    if isinstance(type, ClassType):
        qname = _m_qname(type.qname, nl)
        return '{}{}'.format(_class_kind_map_inv[type.kind], qname)
    raise RuntimeError('whoops')

def _m_fn_type(type, nl, tl):
    cconv = _cc_map_inv[type.cconv]

    if isinstance(type.ret_type, ClassType):
        ret_cv = '?{}'.format('ABCD'[type.ret_type.cv])
    else:
        ret_cv = ''

    ret = '{}{}'.format(ret_cv, _m_type(type.ret_type, nl, tl))

    params = []
    for param in type.params:
        cannon = _m_type(param, {}, {})
        if len(cannon) == 1:
            params.append(cannon)
            continue

        ref = tl.get(cannon)
        if ref is not None:
            params.append(str(ref))
            continue

        p = _m_type(param, nl, tl)
        params.append(p)
        if len(tl) < 9:
            tl[cannon] = len(tl)

    term = '' if type.params and _is_void_or_ellipsis(type.params[-1]) else '@'
    return '{}{}{}{}Z'.format(cconv, ret, ''.join(params), term)

def msvc_mangle(obj):
    nl = {}
    tl = {}
    if isinstance(obj, Function):
        qname = _m_qname(obj.qname, nl)
        type = _m_fn_type(obj.type, nl, tl)

        if obj.kind == fn_free:
            modif = 'Y'
        else:
            if obj.kind == fn_class_static:
                modif = 2
            elif obj.kind == fn_virtual:
                modif = 4
            else:
                modif = 0

            if obj.access_spec == access_protected:
                modif += 8
            elif obj.access_spec == access_public:
                modif += 16

            modif = chr(ord('A') + modif)

        addr_space = 'E' if obj.addr_space == as_msvc_x64_absolute else ''
        can_have_cv = obj.kind in (fn_instance, fn_virtual)
        this_cv = 'ABCD'[obj.type.this_cv] if can_have_cv else ''

        return '?{}{}{}{}{}'.format(qname, modif, addr_space, this_cv, type)

    raise RuntimeError('unknown obj')

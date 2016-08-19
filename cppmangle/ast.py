class _Enum(object):
    def __init__(self, desc):
        self.desc = desc

    def __repr__(self):
        return '{}({!r})'.format(self.__class__, self.desc)

class Type(object):
    def __init__(self, cv):
        self.cv = cv

cv_const = 1
cv_volatile = 2

class SimpleType(Type):
    def __init__(self, cv, basic_type):
        self.basic_type = basic_type
        self.cv = cv

class BasicType(_Enum):
    pass

t_void = BasicType('void')
t_bool = BasicType('bool')
t_char = BasicType('char')
t_schar = BasicType('signed char')
t_uchar = BasicType('unsigned char')
t_sshort = BasicType('short int')
t_ushort = BasicType('unsigned short int')
t_sint = BasicType('int')
t_uint = BasicType('unsigned int')
t_slong = BasicType('long')
t_ulong = BasicType('unsigned long')
t_slonglong = BasicType('long long')
t_ulonglong = BasicType('unsigned long long')
t_wchar = BasicType('wchar_t')
t_float = BasicType('float')
t_double = BasicType('double')
t_longdouble = BasicType('long double')
t_ellipsis = BasicType('...')

class PtrType(Type):
    def __init__(self, cv, target, ref):
        super(PtrType, self).__init__(cv)
        self.target = target
        self.ref = ref

k_union = 0
k_struct = 1
k_class = 2
k_enum = 3

class ClassType(Type):
    def __init__(self, cv, kind, qname):
        super(ClassType, self).__init__(cv)
        self.kind = kind
        self.qname = qname

class FunctionType(Type):
    def __init__(self, cconv, ret_type, params, this_cv):
        super(FunctionType, self).__init__(0)
        self.cconv = cconv
        self.ret_type = ret_type
        self.params = params
        self.this_cv = this_cv

class ArrayType(Type):
    def __init__(self, dims, target):
        super(ArrayType, self).__init__(0)
        self.dims = dims
        self.target = target

class Name(object):
    pass

class SpecialName(Name):
    def __init__(self, desc):
        self.desc = desc

    def __repr__(self):
        return 'SpecialName({!r})'.format(self.desc)

n_constructor = SpecialName("<constructor>")
n_def_constr_closure = SpecialName("<default constructor closure>")
n_destructor = SpecialName("<destructor>")
n_op_subscript = SpecialName("operator[]")
n_op_call = SpecialName("operator()")
n_op_member = SpecialName("operator->")
n_op_inc = SpecialName("operator++")
n_op_dec = SpecialName("operator--")
n_op_new = SpecialName("operator new")
n_op_new_arr = SpecialName("operator new[]")
n_op_delete = SpecialName("operator delete")
n_op_delete_arr = SpecialName("operator delete[]")
n_op_deref = SpecialName("operator*")
n_op_addr = SpecialName("operator&")
n_op_plus = SpecialName("operator+")
n_op_minus = SpecialName("operator-")
n_op_lnot = SpecialName("operator!")
n_op_bnot = SpecialName("operator~")
n_op_mem_ptr = SpecialName("operator->*")
n_op_mul = SpecialName("operator*")
n_op_div = SpecialName("operator/")
n_op_mod = SpecialName("operator%")
n_op_add = SpecialName("operator+")
n_op_sub = SpecialName("operator-")
n_op_shl = SpecialName("operator<<")
n_op_shr = SpecialName("operator>>")
n_op_lt = SpecialName("operator<")
n_op_gt = SpecialName("operator>")
n_op_le = SpecialName("operator<=")
n_op_ge = SpecialName("operator>=")
n_op_eq = SpecialName("operator==")
n_op_neq = SpecialName("operator!=")
n_op_band = SpecialName("operator&")
n_op_bor = SpecialName("operator|")
n_op_xor = SpecialName("operator^")
n_op_land = SpecialName("operator&&")
n_op_lor = SpecialName("operator||")
n_op_assign = SpecialName("operator=")
n_op_assign_mul = SpecialName("operator*=")
n_op_assign_div = SpecialName("operator/=")
n_op_assign_mod = SpecialName("operator%=")
n_op_assign_add = SpecialName("operator+=")
n_op_assign_sub = SpecialName("operator-=")
n_op_assign_shl = SpecialName("operator<<=")
n_op_assign_shr = SpecialName("operator>>=")
n_op_assign_band = SpecialName("operator&=")
n_op_assign_bor = SpecialName("operator|=")
n_op_assign_xor = SpecialName("operator^=")
n_op_comma = SpecialName("operator,")
n_op_cast = SpecialName("operator <cast>")
n_vtable = SpecialName("<vtable>")

class TemplateId(Name):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class CallingConv(_Enum):
    pass
cconv_cdecl = CallingConv('cdecl')
cconv_stdcall = CallingConv('stdcall')
cconv_thiscall = CallingConv('thiscall')
cconv_fastcall = CallingConv('fastcall')

class AccessSpecifier(_Enum):
    pass
access_public = AccessSpecifier('public')
access_protected = AccessSpecifier('protected')
access_private = AccessSpecifier('private')

class FunctionKind(_Enum):
    pass
fn_free = FunctionKind('<free fn>')
fn_instance = FunctionKind('<non-static non-virtual member fn>')
fn_virtual = FunctionKind('<virtual member fn>')
fn_class_static = FunctionKind('<static member fn>')

class Function(object):
    def __init__(self, qname, type, kind, access_spec):
        self.qname = qname
        self.type = type
        self.kind = kind
        self.access_spec = access_spec

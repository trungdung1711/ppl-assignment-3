"""
 * @author nhphung
"""
from AST import * 
from Visitor import *
from Utils import Utils
from StaticError import *
from functools import reduce

#==================================
# WARNING
#==================================
from enum import Enum


#==================================
# DEPRECATED
#==================================
# class MType:
#     def __init__(self,partype,rettype):
#         self.partype = partype
#         self.rettype = rettype

#     def __str__(self):
#         return "MType([" + ",".join(str(x) for x in self.partype) + "]," + str(self.rettype) + ")"

# class Symbol:
#     def __init__(self,name,mtype,value = None):
#         self.name = name
#         self.mtype = mtype
#         self.value = value

#     def __str__(self):
#         return "Symbol(" + str(self.name) + "," + str(self.mtype) + ("" if self.value is None else "," + str(self.value)) + ")"
#==================================
# DEPRECATED
#==================================

#==================================
# SCOPE/OBJECT/TYPE STRUCTURE- GO
#==================================
'''
Object = *Func      O
    | *Var          O
    | *Const        O
    | *TypeName     O
'''

'''
Type = *Basic       O
    | *Array        O
    | *Signature    O
    | *Named        O
    | *Interface    O
    | *Void         +
'''
#==================================
# TYPE
#==================================
class ZType(ABC):
    pass

class BasicKind(Enum):
    INT     = 'int'
    FLOAT   = 'float'
    BOOL    = 'boolean'
    STRING  = 'string'
class Basic(ZType):
    def __init__(self, kind : BasicKind):
        self.kind = kind
class Array(ZType):
    def __init__(self, len, elem):
        self.len    : int    = len
        self.elem   : ZType  = elem
class Signature(ZType):
    def __init__(self, recv, params, result):
        self.recv    : Var        = recv    # None if function
        self.params  : List[Var]  = params  # Empty []
        self.result  : Var        = result  # Return nothing -> Var(Void)
class Named(ZType):
    """
    Represents a struct type

    Attributes:
        fields (list): A list of variables (Var) associated with the named entity.
        methods (list): A list of functions (Func) associated with the named entity.
    """
    def __init__(self):
        self.fields     = [] # List[Var]
        self.methods    = [] # List[Func]


    def has_field(self, name : str):
        fields_name = map(lambda var: var.name, self.fields)
        return (name in fields_name)
    

    def add_field(self, field):
        self.fields.append(field)


    def add_method(self, method):
        self.methods.append(method)


    def has_name(self, name):
        field_names = [field.name for field in self.fields]
        method_names = [method.name for method in self.methods]

        names = field_names + method_names
        if name in names:
            return True
        return False
    

    # func (h Human) eat(num int, [4]Array) int
    # recv is not important anymore
    def has_method(self, func):
        name = func.name

        # check for the name
        method_name = map(lambda func : func.name, self.methods)
        if name not in method_name:
            return False
        
        # get the method
        method = self.get_method(name)

        # check for signature
        return identical(func.type, method.type)


    def get_method(self, name):
        return next((method for method in self.methods if method.name == name), None)
    

    def get_field(self, name):
        return next((field for field in self.fields if field.name == name), None)
class Interface(ZType):
    def __init__(self):
        self.methods    = [] # List[Func]


    def add_method(self, method):
        self.methods.append(method)


    def get_method(self, name):
        return next((method for method in self.methods if method.name == name), None)
class Void(ZType):
    """
    Represent the absent of the type, it is not a real type
    in the type system. Its main purpose is to tell the type
    checker that a function doesn't return anything.

    Inherits:
        ZType: The base class for type definitions in the system.

    Note:
    """
    pass

def identical(t1 : ZType, t2 : ZType) -> bool:

    if t1 is t2:
        # for struct
        return True
    
    elif type(t1) != type(t2):
        return False
    
    elif isinstance(t1, Void) and isinstance(t2, Void):
        return True
    
    elif isinstance(t1, Basic) and isinstance(t2, Basic):
        return t1.kind == t2.kind
    
    elif isinstance(t1, Array) and isinstance(t2, Array):
        return t1.len == t2.len and identical(t1.elem, t2.elem)
    
    elif isinstance(t1, Signature) and isinstance(t2, Signature):
        # len of params
        if len(t1.params) != len(t2.params):
            return False
        
        # type of return
        if not identical(t1.result.type, t2.result.type):
            return False
        
        return all(identical(v1.type, v2.type) for v1, v2 in zip(t1.params, t2.params))


    elif isinstance(t1, Named) and isinstance(t2, Named):
        return t1 is t2
    
    elif isinstance(t1, Interface) and isinstance(t2, Interface):
        return t1 is t2

    else:
        return False


#==================================
# OBJECT
#==================================
class ZObject(ABC):
    def __init__(self, parent, name, typ, declared = True):
        self.parent     : ZScope   = parent
        self.name       : str      = name
        self.type       : ZType    = typ
        self.declared   : bool     = declared


    def set_type(self, typ):
        self.type = typ


    def set_parent(self, scope):
        self.parent = scope


    def set_declared(self):
        self.declared = True


    def set_undeclared(self):
        self.declared = False

class Func(ZObject):
    pass
class Var(ZObject):
    def __init__(self, parent, name, typ, is_field=False):
        self.is_field = is_field
        super().__init__(parent, name, typ)
class Const(ZObject):
    def __init__(self, parent, name, typ, value):
        self.value = value
        self.eval = False
        super().__init__(parent, name, typ)
class TypeName(ZObject):
    """
    Represent a type declaration
    int, string, ...
    Human, Animal, Person, ...
    Attributes:
        None
    Methods:
        None
    """

    pass


#==================================
# SCOPE
#==================================
class ZScope:
    def __init__(self, parent, children, number, elems, isFunc):
        self.parent     : ZScope                = parent    # None if it is the universe scope
        self.children   : List[ZScope]          = children  # List[Scope]
        self.number     : int                   = number    # int
        self.elems      : dict[str, ZObject]    = elems     # Dict[string, Object]
        self.isFunc     : bool                  = isFunc    # bool


    def len(self):
        return len(self.elems)
    

    def num_children(self):
        return len(self.children)
    

    def child(self, i):
        return self.children[i]
    

    def resolve(self, name):
        """Used internally to set declared and set undeclared
        for look_up to work, resolve to name if it exists, no
        matter where it is declared, used by global scope only

        Args:
            name (str): name to resolve

        Returns:
            Object: the object to resolve
        """
        if name in self.elems:
            return self.elems[name]
        return None


    def look_up(self, name):
        """Look up a name in the current scope, 
        prevent the declaration pass of to return the 
        undeclared object by using declared

        Args:
            name (str): Name to look up

        Returns:
            ZObject: Object found, otherwise None
        """
        if name in self.elems and self.elems[name].declared:
            return self.elems[name]
        return None
    

    def look_up_parent(self, name):
        """Look up a name in the current scope
        up to the universcope in the scope chain
        if found a name in a scope, stop. Prevent incorrect resolution
        by using Object.declared

        Args:
            name (str): The name to resolve

        Returns:
            Object: [Func, Const, Var, TypeName]
        """
        s = self
        while s is not None:
            obj = s.look_up(name=name)
            if obj is not None:
                return obj
            s = s.parent
        return None


    def insert(self, obj : ZObject):
        obj.set_parent(self)
        self.elems[obj.name] = obj


    def refresh_global(self):
        for value in self.elems.values():
            if isinstance(value, (Var, Const)):
                value.set_undeclared()


    def drop_var_const(self):
        new_elems = {

        }
        for obj in self.elems.values():
            if isinstance(obj, (Var, Const)):
                pass
            else:
                new_elems[obj.name] = obj
        self.elems = new_elems


#==================================
# UTILITY FUNCTION
#==================================
def new_scope(parent : ZScope):
    """Simulate the function NewScope in Go, return
    a new empty scope, contained in the given parent. Adapt
    eager initilization rather lazy initialization 

    Args:
        parent (Scope): the parent scope

    Returns:
        Scope: the newly created scope
    """
    s = ZScope(parent=parent, children=[], number=0, elems={}, isFunc=False)
    if parent is not None:
        parent.children.append(s)
        s.number = len(parent.children)
    return s


#==================================
# ACTUALLY, SEMANTIC CHECKER
# CAN DECIDE HOW TO TRAVERSE
#==================================
class StaticChecker(BaseVisitor,Utils):
        
    #==================================
    # USED TO INITIALIZE PREDEFINED FUNCTION ?
    #==================================
    def __init__(self, ast):
        self.ast = ast
        self.universe_scope = new_scope(parent=None)
        #==================================
        # UNIVERSE SCOPE SETTINGS
        #==================================


    #==================================
    # LOGIC FOR SEMANTIC ANALYSIS
    #==================================
    def check(self):
        # can I do this multiple times?
        # YES :)

        # testing
        # a : int = 100
        # if isinstance(a, int):
        #     print('a is an int')
        # return

        #==================================
        # DECLARATION PASS
        #==================================
        # universe_scope is used for built-in things
        # global_scope is used for package
        global_scope = new_scope(parent=self.universe_scope)

        parameters = {
            'pass' : 1,
            'global_scope' : global_scope,
            'scope' : global_scope
        }
        self.visit(self.ast, param=parameters)


        #==================================
        # SECOND PASS - fields, interface
        #==================================
        global_scope.refresh_global()
        parameters = {
            'pass' : 2,
            'global_scope' : global_scope,
            'scope' : global_scope
        }
        self.visit(self.ast, param=parameters)
        
    
        #==================================
        # THIRD PASS - FUNC, METH collecting
        #==================================
        global_scope.refresh_global()
        parameters = {
            'pass' : 3,
            'scope' : global_scope,
            'global_scope' : global_scope
        }
        self.visit(self.ast, param=parameters)


        #==================================
        # FIN PASS - TYPE CHECKING
        #==================================
        global_scope.refresh_global()
        global_scope.drop_var_const()
        # global_scope just contains
        # TypeName
        # Func
        parameters = {
            'pass' : 4,
            'scope' : global_scope
        }
        self.visit(self.ast, param=parameters)


    #==================================
    # TRAVERSING LOGIC
    # PASS ANY NUMBER OF ARGUMENTS
    #==================================
    def visitProgram(self, ast, param):
        pass_num = param['pass']
        if pass_num == 1:
            # pass 1: declaration pass [Const]
            [self.visit(decl, param=param) for decl in ast.decl]
        
        elif pass_num == 2:
            # pass 2: collection pass  [Const]
            [self.visit(decl, param=param) for decl in ast.decl]

        elif pass_num == 3:
            # pass 3: function and method collection pass [Const]
            [self.visit(decl, param=param) for decl in ast.decl]

        elif pass_num == 4:
            # pass 4: type checking pass [Const]
            [self.visit(decl, param=param) for decl in ast.decl]

        else:
            pass


    def visitVarDecl(self, ast, param):
        # Simple case

        pass_num = param['pass']
        name = ast.varName
        varType = ast.varType
        varInit = ast.varInit

        if pass_num == 1:
            global_scope = param['global_scope']
            if global_scope.look_up(name) is not None:
                raise Redeclared(k=Variable(), n=name)
            else:
                obj = Var(global_scope, name=name, typ=None, is_field=False)
                global_scope.insert(obj)
        
        elif pass_num == 2:
            scope = param['scope']
            scope.resolve(name).set_declared()

        elif pass_num == 3:
            scope = param['scope']
            scope.resolve(name).set_declared()
            
        # elif pass_num == 4:
        # default behaviour
        else:
            scope = param['scope']
            if scope.look_up(name) is not None:
                raise Redeclared(k=Variable(), n=name)
            
            else:
                obj = Var(parent=scope, name=name, typ=None)
                typ = None

                if varType is not None and varInit is not None:
                    # ensure the type to have
                    # the same type
                    init_type = self.visit_type(varType, param)
                    expr_type = self.visit_expr(varInit, param)

                    if not self.check_var(init_type, expr_type):
                        # print('Check ' + name)
                        # print(f'{type(init_type)} and {type(expr_type)}')
                        raise TypeMismatch(ast)
                    
                    typ = init_type

                elif varType is None:
                    # get the type from expr
                    typ = self.visit_expr(varInit, param)

                elif varInit is None:
                    # get the type from type
                    typ = self.visit_type(varType, param)

                obj.set_type(typ)

                scope.insert(obj)

        # else:
        #     pass


    def check_array(self, t1: Array, t2: Array) -> bool:
        if t1.len != t2.len:
            return False

        # Recursive check for nested arrays
        if isinstance(t1.elem, Array) and isinstance(t2.elem, Array):
            return self.check_array(t1.elem, t2.elem)

        # Special case: allow float ← int promotion
        if identical(t1.elem, Basic(BasicKind.FLOAT)) and \
        identical(t2.elem, Basic(BasicKind.INT)):
            return True

        # Fallback: strict match
        return identical(t1.elem, t2.elem)


    def check_interface(self, t1 : Interface, t2 : Named) -> bool:
        # the struct must implement all methods
        # in the interface
        methods = t1.methods
        for method in methods:
            if not t2.has_method(method):
                return False
        return True


    def check_var(self, init_type, expr_type) -> bool:
        if identical(init_type, expr_type):
            # assign the type of any
            return True
        
        elif identical(init_type, Basic(BasicKind.FLOAT)) and \
             identical(expr_type, Basic(BasicKind.INT)):
            # assign the type of float
            return True
        
        elif isinstance(init_type, Array) and isinstance(expr_type, Array):
            # print('check')
            # print(f'{init_type.len} and {expr_type.len}')
            return self.check_array(init_type, expr_type)
        
        elif isinstance(init_type, Interface) and isinstance(expr_type, Named):
            return self.check_interface(init_type, expr_type)
        
        else:
            return identical(init_type, expr_type)


    def visitConstDecl(self, ast, param):
        pass_num = param['pass']
        name = ast.conName
        expr = ast.iniExpr

        if pass_num == 1:
            global_scope = param['global_scope']
            if global_scope.look_up(name) is not None:
                raise Redeclared(k=Constant(), n=name)
            else:
                obj = Const(None, name, None, None)
                global_scope.insert(obj)
            return

        elif pass_num == 2:
            # look up will find it
            # GLOBAL SCOPE
            scope = param['scope']

            # enable this object to be found 
            # by look_up
            obj = scope.resolve(name)
            obj.set_declared()

            # Case: StructLiteral -> Named type [object]
            # Case: ArrayLiteral  -> Array [created]

            # Case: Id -> return Object, not Type
            # Other case -> return Type
            # if isinstance(expr, Id):
            #     typ = self.id_helper(expr, param)
            # else:
            #     typ = self.visit(expr, param)

            typ = self.visit_expr(expr, param)

            if isinstance(typ, (Basic)):
                # evaluate value
                parameters = {
                    'pass' : 99,
                    'scope' : scope
                }

                value = self.visit_expr(expr, parameters)
                obj.set_type(typ)
                obj.value = value
        
        elif pass_num == 3:
            scope = param['scope']
            scope.resolve(name).set_declared()

        # elif pass_num == 4:
        # default and main pass
        else:
            scope = param['scope']

            # 1. Check for redeclared
            if scope.look_up(name) is not None:
                raise Redeclared(k=Constant(), n=name)
            else:
                obj = Const(parent=scope, name=name, typ=None, value=None)

                # 2. type checking
                typ = self.visit_expr(expr, param)
                obj.set_type(typ)

                if isinstance(typ, Basic):
                    parameters = {
                        'pass' : 99,
                        'scope' : scope
                    }
                    value = self.visit_expr(expr, parameters)
                    obj.value = value
                else:
                    # SOS
                    pass

                scope.insert(obj)
        # else:
        #     pass

    class Operator(Enum):
        ADD     = '+'
        SUB     = '-'
        MUL     = '*'
        DIV     = '/'
        MOD     = '%'
        EQ      = '=='
        NEQ     = '!='
        LT      = '<'
        GT      = '>'
        LTE     = '<='
        GTE     = '>='
        NOT     = '!'
        AND     = '&&'
        OR      = '||'


    def visitBinaryOp(self, ast, param):
        op = ast.op
        X = ast.left
        Y = ast.right
        type_X = None
        type_Y = None
        pass_num = param['pass']

        if pass_num == 99:
            # type checking is done
            # if isinstance(X, Id):
            #     value_X = self.id_helper(ast=X, param=param)
            # else:
            #     value_X = self.visit(X, param)

            # if isinstance(Y, Id):
            #     value_Y = self.id_helper(ast=Y, param=param)
            # else:
            #     value_Y = self.visit(Y, param)
            value_X = self.visit_expr(X, param)
            value_Y = self.visit_expr(Y, param)

            if op == StaticChecker.Operator.ADD.value:
                return value_X + value_Y
            elif op == StaticChecker.Operator.SUB.value:
                return value_X - value_Y
            elif op == StaticChecker.Operator.MUL.value:
                return value_X * value_Y
            elif op == StaticChecker.Operator.DIV.value:
                return value_X / value_Y
            elif op == StaticChecker.Operator.MOD.value:
                return value_X % value_Y
            elif op == StaticChecker.Operator.EQ.value:
                return value_X == value_Y
            elif op == StaticChecker.Operator.NEQ.value:
                return value_X != value_Y
            elif op == StaticChecker.Operator.LT.value:
                return value_X < value_Y
            elif op == StaticChecker.Operator.GT.value:
                return value_X > value_Y
            elif op == StaticChecker.Operator.LTE.value:
                return value_X <= value_Y
            elif op == StaticChecker.Operator.GTE.value:
                return value_X >= value_Y
            elif op == StaticChecker.Operator.AND.value:
                return value_X and value_Y
            elif op == StaticChecker.Operator.OR.value:
                return value_X or value_Y


        # first guard -> Object is not [Const, Var] but [TypeName, Func]
        # if isinstance(X, Id):
        #     type_X = self.visit_expr(ast=X, param=param)
        # else:
        #     type_X = self.visit(X, param)

        # if isinstance(Y, Id):
        #     type_Y = self.id_helper(ast=Y, param=param)
        # else:
        #     type_Y = self.visit(Y, param)

        type_X = self.visit_expr(X, param)
        type_Y = self.visit_expr(Y, param)

        # type checking
        int_type        = Basic(kind=BasicKind.INT)
        float_type      = Basic(kind=BasicKind.FLOAT)
        string_type     = Basic(kind=BasicKind.STRING)
        boolean_type    = Basic(kind=BasicKind.BOOL)
        if op == StaticChecker.Operator.ADD.value:
            # +
            if identical(type_X, int_type) and identical(type_Y, int_type):
                # both int type
                return int_type
            elif identical(type_X, float_type) and identical(type_Y, float_type):
                # both float type
                return float_type
            elif identical(type_X, string_type) and identical(type_Y, string_type):
                # both string type
                return string_type
            
            elif (identical(type_X, int_type) and identical(type_Y, float_type)) \
                or (identical(type_Y, int_type) and identical(type_X, float_type)):
                # one is float and one is int -> coercion
                # specification, at run time -> change from int to float
                return float_type
            
            else:
                raise TypeMismatch(ast)

        elif op == StaticChecker.Operator.SUB.value or \
             op == StaticChecker.Operator.MUL.value or \
             op == StaticChecker.Operator.DIV.value:
            # -, *, /
            if identical(type_X, int_type) and identical(type_Y, int_type):
                # both int type
                return int_type
            elif identical(type_X, float_type) and identical(type_Y, float_type):
                # both float type
                return float_type
            
            elif (identical(type_X, int_type) and identical(type_Y, float_type)) \
                or (identical(type_Y, int_type) and identical(type_X, float_type)):
                # one is float and one is int -> coercion
                # specification, at run time -> change from int to float
                return float_type
            
            else:
                raise TypeMismatch(ast)
            
        elif op == StaticChecker.Operator.MOD.value:
            # %
            if identical(type_X, int_type) and identical(type_Y, int_type):
                return int_type
            
            else:
                raise TypeMismatch(ast)

        elif op == StaticChecker.Operator.EQ.value or \
             op == StaticChecker.Operator.NEQ.value or \
             op == StaticChecker.Operator.GT.value or \
             op == StaticChecker.Operator.LT.value or \
             op == StaticChecker.Operator.GTE.value or \
             op == StaticChecker.Operator.LTE.value:
            # ==, !=, >, <, >=, <=
            if identical(type_X, int_type) and identical(type_Y, int_type):
                # both int type
                return boolean_type
            elif identical(type_X, float_type) and identical(type_Y, float_type):
                # both float type
                return boolean_type
            elif identical(type_X, string_type) and identical(type_Y, string_type):
                # both string type
                return boolean_type
            
            else:
                raise TypeMismatch(ast)
            
        elif op == StaticChecker.Operator.AND.value or \
             op == StaticChecker.Operator.OR.value:
            # &&, ||
            if identical(type_X, boolean_type) and identical(type_Y, boolean_type):
                # both boolean type
                return boolean_type
            
            else:
                raise TypeMismatch(ast)
            
        else:
            # SOS
            pass


    def visitUnaryOp(self, ast, param):
        op = ast.op
        X = ast.body
        type_X = None
        pass_num = param['pass']

        if pass_num == 99:
            # type is finish, just evaluation
            # For literal, it is OK
            # But for Id -> break
            # if isinstance(X, Id):
            #     value_X = self.id_helper(X, param)
            # else:
            #     value_X = self.visit(X, param)

            value_X = self.visit_expr(X, param)

            if op == StaticChecker.Operator.NOT.value:
                return not value_X
            elif op == StaticChecker.Operator.SUB.value:
                return - value_X

        # first guard from [TypeName], [Func]
        # if isinstance(X, Id):
        #     type_X = self.id_helper(X, param)
        # else:
        #     type_X = self.visit(X, param)

        type_X = self.visit_expr(X, param)

        # type checking
        int_type = Basic(kind=BasicKind.INT)
        float_type = Basic(kind=BasicKind.FLOAT)
        boolean_type = Basic(kind=BasicKind.BOOL)

        if op == StaticChecker.Operator.NOT.value:
            # !
            if identical(type_X, boolean_type):
                return boolean_type
            
            else:
                raise TypeMismatch(ast)
        elif op == StaticChecker.Operator.SUB.value:
            # -
            if identical(type_X, int_type) or identical(type_X, float_type):
                return type_X
            
            else:
                raise TypeMismatch(ast)


    def visit_expr(self, ast, param):
        # wrapper for expression type constraints
        # evaluation
        if param['pass'] == 99:
            if isinstance(ast, Id):
                # SOS
                # Not handling errors
                obj = self.visit(ast, param)
                return obj.value


        if isinstance(ast, Id):
            obj = self.visit(ast, param)
            if obj is None:
                raise Undeclared(k=Identifier(), n=ast.name)
            
            elif isinstance(obj, (TypeName, Func)):
                pass

            elif isinstance(obj, (Var, Const)):
                return obj.type


        elif isinstance(ast, (FuncCall, MethCall)):
            typ = self.visit(ast, param)
            if identical(typ, Void()):
                raise TypeMismatch(ast)
            
            return typ


        else:
            return self.visit(ast, param)


    def visitIntLiteral(self, ast, param):
        pass_num = param['pass']

        if pass_num == 99:
            return int(ast.value)

        return Basic(kind=BasicKind.INT)
    
    
    def visitFloatLiteral(self, ast, param):
        pass_num = param['pass']

        if pass_num == 99:
            return float(ast.value)

        return Basic(kind=BasicKind.FLOAT)
    
    
    def visitBooleanLiteral(self, ast, param):
        pass_num = param['pass']
        
        if pass_num == 99:
            return bool(ast.value)

        return Basic(kind=BasicKind.BOOL)
    

    def visitStringLiteral(self, ast, param):
        pass_num = param['pass']
        
        if pass_num == 99:
            return str(ast.value)

        return Basic(kind=BasicKind.STRING)


    def visitArrayLiteral(self, ast, param):
        '''
        var arr [SIZE][SIZE][SIZE]int = [SIZE][SIZE][SIZE]int{1, 2, 3}
        '''
        dimens = ast.dimens
        eleType = ast.eleType
        value = ast.value

        parameters = {
            'pass' : 99,
            'scope' : param['scope']
        }

        size = [self.visit_expr(expr, parameters) for expr in dimens]
        
        element_type = self.visit_type(eleType, param)
        array_type = reduce(lambda acc, cur: Array(len=cur, elem=acc), reversed(size), element_type)
        return array_type


    def visitStructLiteral(self, ast, param):
        '''
        var a Human = Human{name : "string", age : 100}
        '''
        name = ast.name
        elements = ast.elements
        typ = self.visit_type(Id(name), param)

        for field_name, expr in elements:
            # SOS
            if not typ.has_field(field_name):
                raise Undeclared(k=Field(), n=field_name)
            
            if True:
                # SOS
                # for the type mismatch of value
                pass

        return typ


    def visitNilLiteral(self, ast, param):
        return None


    #==================================
    # USING WRAPPTERS
    # can be in expr and can be a stmt
    #==================================
    def visitFuncCall(self, ast, param):
        # expr
        funName = ast.funName
        args = ast.args
        
        # 1. check for the name of the function
        # -> raise Undeclared function

        # 2. check for the signature
        # [type mismatch in express]
        # or type mismatch in function
        # parameter check

        # 3. return the type
        # of this expression (based on the signature)
        # but if it doesn't return
        # then there is no type
        # in Go, we have Basic/Array/Named/Interface
        # return Void, which will be used to
        # check in visit_expr -> reject that
        # case
        # but in the case of visit lhs ->
        # accept and reject other cases

        # errors:
        # 1. Undeclared function
        # 2. Wrong number of parameters
        # 3.0 wrong parameters, in expr in parameters
        # cause when visit the expr to create the type of
        # the parameter
        # 3. Parameters don't match
        # 4. visit_expr and visit_stmt must
        # check for the return type and check for that
        # which is the wrapper
        # just like visitId() just resolve
        # visit_expr, visit_type would choose how 
        # to work with that Obj
        # now wrapper would choose how to work with
        # the type
        # lhs and rhs woube be just expr
        # it is the role of the compiler
        # to make the code different 
        # but at this stage, it is quite the
        # same

        # get the object from visitId
        obj = self.visitId(Id(funName), param)
        if obj is None:
            raise Undeclared(k=Function(), n=funName)
        
        elif isinstance(obj, (TypeName, Var, Const)):
            # SOS
            # NOT HAPPEN
            pass

        elif isinstance(obj, Func):
            # correctly resolve
            # check for same parameters
            # function(a, b, 2 + 4)

            # visit the args to get all the type
            # check for the expression in that as well
            param_types = list(map(lambda var : var.type, obj.type.params))
            arg_types = list(map(lambda arg : self.visit_expr(arg, param), args))

            if not self.check_function(param_types, arg_types):
                raise TypeMismatch(ast)
            
            # it is Ok about that, then
            # return the return type
            # not that Void, meaning that this function
            # doesn't have a returned value

            return obj.type.result.type


    def visitMethCall(self, ast, param):
        # 1. check for the type of the receiver
        # it must be the Named or Interface
        # if it is not Named or Interface -> error

        # 2. Now we have the Named or Interface
        # we would check whether the methods exist
        # or not
        # self.methods to check for the method
        # name
        # raise undeclared method if there is no method found

        # 3. found method
        # get the params type
        # change to the list
        # call check_function to check for that
        # and return the type of this expression
        # visit_expr will collect that and raise
        # if the returned type is Void (represents a return-nothing-function)
        receiver = ast.receiver
        metName = ast.metName
        args = ast.args

        recv_type = self.visit_expr(receiver, param)

        if not isinstance(recv_type, (Named, Interface)):
            raise TypeMismatch(ast)
        
        # Named or interface type
        # Func object getting from Named or Interface
        # getting the name of the method
        method = recv_type.get_method(metName)
        if method is None:
            raise Undeclared(k=Method(), n=metName)

        # contain that method
        # now checking for the arguments and the parameters

        param_types = list(map(lambda var : var.type, method.type.params))
        arg_types = list(map(lambda arg : self.visit_expr(arg, param), args))

        if not self.check_function(param_types, arg_types):
            raise TypeMismatch(ast)
        
        return method.type.result.type


    def check_function(self, param_types, arg_types) -> bool:
        # 1. pass the list of parameters type
        # 2. pass the list of arguments type

        # SOS, not exact same type
        # but a struct obj can be passed to
        # interface if the struct types
        # are all implemented

        # len is different
        if len(param_types) != len(arg_types):
            return False
        
        # len is the same
        # must be same type
        # exactly the same -> identical
        return all(identical(t1, t2) for t1, t2 in zip(param_types, arg_types))
    

    def visitArrayCell(self, ast, param):
        # no need to check for dimention and size mismatch
        # check for the expression
        # in the arr[][][] to be int type
        arr = ast.arr
        idx = ast.idx
        
        # 1. must visit and get
        # the type of the expression
        # accept Array type only
        # also we have the information
        # about the len and the element
        # note that this is 
        # a bunch of operation
        # arr[2][3][4][5][6] -> a bunch of operation
        # return the type after these bunch of operation
        # and we won't check for out-of-bound index
        # cause we don't know, the index can be run-time
        # not compile-time, thus the compiler (semantic analysis)
        # just check for the type only

        # 2. for each of the expression
        # check for Basic(BasicKind.INT)
        # false -> raise type_mismatch
        # return the Array when getting 
        # that array subscription
        # return elem actually

        arr_type = self.visit_expr(arr, param)

        if not isinstance(arr_type, Array):
            raise TypeMismatch(ast)
        
        # [3][4]int
        # but arr[3][2][1] -> raise error
        # because in this case we won't know
        # the return turn actually
        # but in the assignment
        # there is no description about that
        # then no worry?

        # using reduce to make it
        # into something like ArrayCell(expr, expr)
        # arr[1][2][3]
        # in range -> still have the type returned
        # back
        index_types = list(map(lambda index: self.visit_expr(index, param), idx))
        if not self.check_array_cell(index_types):
            raise TypeMismatch(ast)
        
        # now return the type
        # there is no need to check for
        # out of bound
        # because there is no description
        # about that
        # and we can take the type returned back
        # without worrying about that
        # arr_type which is len and elem
        # arr[1] -> return arr_type.elem
        # arr[1][2] -> return arr_type.elem.elem
        # arr[1][2][3][4]

        # this one can cause error if
        # out of bound of the dimension
        # SOS
        return reduce(lambda acc, cur: arr_type.elem, index_types, arr_type)


    def check_array_cell(self, index_types) -> bool:
        return all(identical(t, Basic(BasicKind.INT)) for t in index_types)
    

    def visitFieldAccess(self, ast, param):
        receiver = ast.receiver
        field = ast.field

        recv_type = self.visit_expr(receiver, param)

        # print(f'{field} and {recv_type is None}')

        if not isinstance(recv_type, Named):
            raise TypeMismatch(ast)

        field_var = recv_type.get_field(field)

        if field_var is None:
            raise Undeclared(k=Field(), n=field)
        
        # print(f'{field} and {field_var.type is None}')
        # Var of field in Named

        return field_var.type


    def visitId(self, ast, param):
        name = ast.name
        scope = param['scope']

        # NOTE: Id will be resolved into
        # different kinds of [Object]
        return scope.look_up_parent(name)

   
    def visitFuncDecl(self, ast, param):
        pass_num = param['pass']
        name = ast.name
        params = ast.params
        retType = ast.retType

        if pass_num == 1:
            global_scope = param['global_scope']

            if global_scope.look_up(name) is not None:
                raise Redeclared(k=Function(), n=name)
            else:
                obj = Func(parent=None, name=name, typ=None)
                typ = Signature(None, [], None)
                obj.set_type(typ)
                global_scope.insert(obj)
            return

        elif pass_num == 2:
            pass

        elif pass_num == 3:
            # create the signature for this function
            # assign this signature to th obj
            scope = param['scope']
            obj = scope.look_up(name)

            # obj_type = Signature(None, [], None)
            # obj.set_type(obj_type)

            # create Var object and store the type
            # inside Signature
            
            # check for redeclared
            test = []
            for param_decl in params:
                if param_decl.parName in test:
                    raise Redeclared(k=Parameter(), n=param_decl.parName)
                else:
                    test.append(param_decl.parName)

            # normal flow
            # no redeclared
            # create Var for each of them
            # and then add them to Signature
            for param_decl in params:
                var = self.visit(param_decl, param)
                obj.type.params.append(var)

            # for the result
            # VoidType -> None
            # Other would be a type
            # if len(obj_type.params) == 0:
            #     obj_type.params = None

            # result_type = self.visit_type(retType, param)
            # if result_type is None:
            #     result_var = None
            # else:
            #     result_var = Var(None, 'A', result_type)
            result_type = self.visit_type(retType, param)
            result_var = Var(None, 'return', result_type)
            obj.type.result = result_var

        elif pass_num == 4:
            # TODO:
            # Go inside a function
            # 1. Add a child scope - function scope
            # 2. Declare the parameter by create Var and
            # add to the current scope
            # 3. Add a child scope
            # 4. Pass this child scope along side
            # and with a flag of inside function
            # and the return type to check for case
            # return wrong types, or expect a return
            # but return is given
            pass

        else:
            pass


    def visitParamDecl(self, ast, param):
        # TODO:
        # - create Var - Type
        parName = ast.parName
        parType = ast.parType

        var = Var(parent=None, name=parName, typ=None, is_field=False)

        param_type = self.visit_type(parType, param)
        var.set_type(param_type)
        return var


    def visitStructType(self, ast, param):
        pass_num = param['pass']
        name = ast.name
        if pass_num == 1:
            global_scope = param['global_scope']
            if global_scope.look_up(name) is not None:
                raise Redeclared(k=Type(), n=name)
            else:
                obj = TypeName(parent=None, name=name, typ=None)
                typ = Named()
                obj.set_type(typ)
                global_scope.insert(obj)
            return

        elif pass_num == 2:
            # TODO:
            # - check for fields redeclared
            # - create Type of Object
            global_scope = param['global_scope']
            # We have the Object [TypeName]
            obj = global_scope.look_up(name)
            # Create the type
            # fields/methods
            # checking for fields
            test = []
            for name, typ in ast.elements:
                if name in test:
                    # found
                    raise Redeclared(k=Field(), n=name)
                else:
                    test.append(name)
            
            # normal flow, no exception, adding to Type
            # typ = Named()
            # obj.set_type(typ)
            for name, field_type in ast.elements:
                field_typ = self.visit_type(field_type, param)
                new_field = Var(parent=None, name=name, typ=field_typ, is_field=True)

                # print(f'{name}+{type(field_typ)}')
                obj.type.add_field(new_field)
            

        else:
            pass


    def visitIntType(self, ast, param):
        """Different from Go, type are all ast.Ident
        -> resolve to TypeName with Type inside
        but in this case, we don't really need that
        type is defined by ast, meaning that
        var int int -> would cause parsing errors
        while it is valid in Go, instead of looking 
        in the Scope chain -> return the TypeName,
        simulating the scope-chain LookUp

        Args:
            ast (AST node): the type node
            param (parameters): parameters used for logic

        Returns:
            Type: Type in Scope/Object/Type system
        """
        typ = Basic(kind=BasicKind.INT)

        return typ

    
    def visitFloatType(self, ast, param):
        typ = Basic(kind=BasicKind.FLOAT)

        return typ
    
    
    def visitBoolType(self, ast, param):
        typ = Basic(kind=BasicKind.BOOL)

        return typ

    
    def visitStringType(self, ast, param):
        typ = Basic(kind=BasicKind.STRING)

        return typ


    def visitArrayType(self, ast, param):
        dimens = ast.dimens
        eleType = ast.eleType
        # Used to get the const value
        scope = param['scope']

        size = []
        for expr in dimens:
            parameters = {
                'pass' : 99,
                'scope' : param['scope']
            }
            value = self.visit_expr(expr, parameters)
            size.append(value)

        # the element type ([][][]TYPE)
        element_type = self.visit_type(eleType, param)
        
        # no need to check for the values inside the
        # array literal, just calculate the size and then
        # return the new Array (Type)
        # using reduce
        # [1, 2, 3, 4] and a type
        # [4, 3, 2, 1] and a type
        # Array(1, Array(2, Array(3, Array(4, type))))
        array_type = reduce(lambda acc, cur: Array(len=cur, elem=acc), reversed(size), element_type)
        return array_type


    def visitVoidType(self, ast, param):
        return Void()
    

    def visit_type(self, ast, param):
        """wrapper of type deduction for ast.Ident
        prevent Object [Var, Func, Const], allow 
        TypeName only, expect type at this point

        Args:
            ast (_type_): _description_
            param (_type_): _description_

        Returns:
            _type_: _description_
        """
        if isinstance(ast, Id):
            # Resolve
            obj = self.visit(ast, param)

            # if (ast.name == 'Room'):
            #     print(f'{ast.name} + {type(obj)}')

            if obj is None:
                # SOS NOT HAPPEN
                # Type is undeclared
                pass
            
            if isinstance(obj, (Var, Const, Func)):
                # SOS NOT HAPPEN
                pass

            if isinstance(obj, TypeName):
                # correct
                # if (ast.name == 'Room'):
                #     print(type(obj.type))
                return obj.type

        else:
            return self.visit(ast, param)


    def visitInterfaceType(self, ast, param):
        pass_num = param['pass']
        name = ast.name
        methods = ast.methods

        if pass_num == 1:
            global_scope = param['global_scope']

            if global_scope.look_up(name) is not None:
                raise Redeclared(k=Type(), n=name)
            else:
                obj = TypeName(parent=None, name=name, typ=None)
                typ = Interface()
                obj.set_type(typ)
                global_scope.insert(obj)
            return
        
        elif pass_num == 2:
            scope = param['scope']
            obj = scope.look_up(name)
            # create the type of it
            # check for redeclared prototype
            test = []
            for method in methods:
                if method.name in test:
                    raise Redeclared(k=Prototype(), n=method.name)
                else:
                    test.append(method.name)

            # already check
            # typ = Interface()
            # obj.set_type(typ)

            for method in methods:
                func = self.visit(method, param)
                obj.type.add_method(func)

            return

        else:
            pass


    def visitPrototype(self, ast, param):
        name = ast.name
        params = ast.params
        retType = ast.retType

        # create a Func Object
        # create a Synature
        # a Signature would contain Var
        # receive is None
        method_var_list = []

        for method_param in params:
            param_type = self.visit_type(method_param, param)
            var = Var(None, 'A', param_type, False)
            method_var_list.append(var)

        # create the return type
        return_type = self.visit_type(retType, param)


        # VoidType handling
        # if return_var_type is None:
        #     return_var = None
        # else:
        #     return_var = Var(None, 'A', return_var_type)

        return_var = Var(None, 'return', return_type)

        signature = Signature(None, method_var_list, return_var)

        # Create this Func Object
        # with Signature
        func = Func(None, name, signature)
        return func


    def visitMethodDecl(self, ast, param):
        pass_num = param['pass']
        receiver = ast.receiver
        recType = ast.recType
        fun = ast.fun

        if pass_num == 1:
            pass

        elif pass_num == 2:
            pass

        elif pass_num == 3:
            var_type = self.visit_type(recType, param)
            obj_type = var_type
            receiver_var = Var(None, receiver, var_type)

            func = self.method_helper(fun, param)
            func.type.recv = receiver_var

            # check for redeclared
            method_name = func.name
            if obj_type.has_name(method_name):
                raise Redeclared(Method(), method_name)
            else:
                obj_type.add_method(func)

        else:
            pass


    def method_helper(self, ast, param):
        name = ast.name
        params = ast.params
        retType = ast.retType

        signature = Signature(None, [], None)
        func = Func(None, name, signature)
        
        # check for redeclared
        test = []
        for param_decl in params:
            if param_decl.parName in test:
                raise Redeclared(k=Parameter(), n=param_decl.parName)
            else:
                test.append(param_decl.parName)

        for param_decl in params:
            var = self.visit(param_decl, param)
            signature.params.append(var)

        result_type = self.visit_type(retType, param)
        # if result_type is None:
        #     result_var = None
        # else:
        #     result_var = Var(None, 'A', result_type)

        result_var = Var(None, 'return', result_type)
        signature.result = result_var

        return func


    def visitBlock(self, ast, param):
        member = ast.member
        # the scope is created in the fist place
        # we don't need to worry about that
        # just use the current scope and
        # call visit_stmt wrapper
        # using the current scope
        # in nested statement
        # when a scope is created
        # we add it to the child of the current scope
        # and using the new scope
        # from that point

        # param stores the current scope
        # meet something like if ->
        # the scope from that point is created
        # with the child
        # but for this the scope doesn't change
        # at all
        # meaning that we are operating in the same scope

        # note that we have to
        # store the function's signature
        # or to tell that we are in the function
        # when we meet the return statement
        # we would get the value -> to check
        # because return can be in any block
        # actually

        # wrong placement of break, continue, return
        # are not being checked in this case
        for m in member:
            self.visit_stmt(m, param)
 

    def visit_stmt(self, ast, param):
        # wrapper to handle statement in the block

        # before doing that we have a block, create new scope
        # set up the signature?
        # variable declaration
        # const declaration
        # assignment
        # if -> new scope
        # for -> new scope
        # break
        # continue
        # call statement -> check for return void(func, meth)
        # return must check the current function return type
        if isinstance(ast, VarDecl):
            self.visit(ast, param)

        elif isinstance(ast, ConstDecl):
            self.visit(ast, param)

        elif isinstance(ast, Assign):
            self.visit(ast, param)

        elif isinstance(ast, If):
            pass

        elif isinstance(ast, ForBasic):
            pass

        elif isinstance(ast, ForStep):
            pass

        elif isinstance(ast, ForEach):
            pass

        elif isinstance(ast, Break):
            pass

        elif isinstance(ast, Continue):
            pass

        elif isinstance(ast, MethCall):
            # must check for return type
            pass

        elif isinstance(ast, FuncCall):
            # must check for return type
            pass

        elif isinstance(ast, Return):
            # must check for function signature
            pass

        else:
            pass


    def visitAssign(self, ast, param):
        scope = param['scope']
        lhs = self.lhs
        rhs = self.rhs

        '''
        // if it is declared -> assigned -> check for type
        // if it is not declared -> declared -> Var
        a := 100

        // human Named type
        // the type has field name
        // type checking between
        human.name := "Dung"

        // arr must be an array type
        // get correct element (NOT HAPPEN)
        // type checking between
        arr[1] := 23
        '''

        # 1. getting the type of the right hand side
        # 2. catching errors like undeclared
        rhs_type = self.visit_expr(rhs, param)

        if isinstance(lhs, (FieldAccess, ArrayCell)):
            # visit this expression
            # to get the type
            # and check for type mismatch in
            # this assignment, note that
            # there are all expressions
            # then we can use expression returned type
            # to check, this is for type mismatch
            # the compiler in later phases
            # must ensure this meant to be writes
            # not load, but in this case
            # it is just like others normal expression
            # getting the two expression
            # an call check_assign

            # which will cause error just like an expression
            # no field
            # field access causes error if not int
            lhs_type = self.visit_expr(lhs, param)

            if not self.check_assign(lhs_type, rhs_type):
                raise TypeMismatch(ast)
            
            # It is OK with that assignment
            return

        elif isinstance(lhs, Id):
            name = lhs.name
            # look up the scope
            # if found obj of Const/Var
            # then getting the type and call check_var

            # else not found
            # create a new Var with the Type getting
            # from the right hand side
            # adding Var into the current scope

            # 1. we would found the Id in the scope chain
            obj = self.visit(lhs, param)

            if obj is None:
                # meaning that we don't find any
                # then, we can think this is
                # a new declaration
                # create a new obj of type Var
                # with the type of the rhs
                new_var = Var(scope, name, rhs_type)
                scope.insert(new_var)

            elif isinstance(obj, (TypeName, Func, Const)):
                # SOS
                # NOT HAPPEN
                pass

            elif isinstance(obj, Var):
                # assignment for this variable
                # found, then we would check for
                # the check_assign between the two
                lhs_type = obj.type
                if not self.check_assign(lhs_type, rhs_type):
                    raise TypeMismatch(ast)


    def check_assign(self, lhs_type, rhs_type) -> bool:
        if identical(lhs_type, rhs_type):
            # assign the type of any
            return True
        
        elif identical(lhs_type, Basic(BasicKind.FLOAT)) and \
             identical(rhs_type, Basic(BasicKind.INT)):
            # assign the type of float
            return True
        
        elif isinstance(lhs_type, Array) and isinstance(rhs_type, Array):
            # print('check')
            # print(f'{init_type.len} and {expr_type.len}')
            return self.check_array(lhs_type, rhs_type)
        
        elif isinstance(lhs_type, Interface) and isinstance(rhs_type, Named):
            return self.check_interface(lhs_type, rhs_type)
        
        else:
            return identical(lhs_type, rhs_type)


    def visit_lhs(self, ast, param):
        # there is only 3 cases
        # field_access
        # array_index
        # and ID

        # in the case of field_access
        # visit_expr -> return the type
        # which is used to compare with
        # the type of the rhs (check-var)

        # in the case array_access
        # visit_expr -> return the type
        # which will be used to compare with 
        # the type of the rhs

        # in the case of Id
        # case 1: -> resolve
        # and we found a declared variable in the scope chain
        # then it is an assignment :=
        # then we return the type for
        # type checking

        # case 2: -> there is no
        # declaration about that
        # then this becomes a declaration
        # create Var and use the type of the rhs
        # add this to the current scope
        pass


    def visitIf(self, ast, param):
        # check for the condition
        # create a new scope
        # visit the Block (if then)

        # for the else part
        # it could be another If -> visitIf
        # or it could be Block -> create
        # a new scope and visit that
        return None


    def visitForBasic(self, ast, param):
        cond = ast.cond
        loop = ast.loop
        # same logic
        # just check for the condition of boolean type
        # create another scope and call visit Block
        scope = param['scope']
        # create a new scope from this current scope
        for_scope = new_scope(parent=scope)

        # setting a new parameters with
        # a new scope to use
        parameters = {
            'scope' : for_scope
        }

        # check for the type of the expression to
        # be boolean in the for loop
        # same thing, from this empty scope
        # or from the current scope, that is the same thing
        condition_type = self.visit_expr(cond, parameters)

        if not identical(condition_type, Basic(BasicKind.BOOL)):
            raise TypeMismatch(ast)
        
        # condition is correct
        # now, it is the time to
        # play inside the block
        # with a newly create scope
        self.visit(loop, parameters)

 
    def visitForStep(self, ast, param):
        init = ast.init
        cond = ast.cond
        upda = ast.upda
        loop = ast.loop
        # getting the current scope
        scope = param['scope']
        # for a := 1 ; a < 100 ; a := a + 1 {}

        # so it is just assignment
        # find through the scope chain
        # and assign that value
        # or declaration
        # create new value in the current scope
        # new scope from here
        for_scope = new_scope(parent=scope)
        # then using this scope from now one
        parameters = {
            'scope' : for_scope
        }

        # now visit the init
        # which can be either assignment/declaration
        # which can create a new Var (assingment logic)
        # create a new Var if no declaration before
        # or it is just simple assignment
        # for declaration inside var as well, 
        # which case raise error in itself

        # just treat them as the normal statement
        # if there is error ->
        # then this is because of the statement
        # not about this for statement
        # using the new for_scope
        # using the current scope
        # visit_stmt will add new 
        # Var to the current scope
        # So it is up-to-date
        self.visit_stmt(init, parameters)

        # now, checking for the return turn of the expression
        # if there is type mismatch in this expression
        # raise exception in this expression
        condition_type = self.visit_expr(cond, parameters)

        # but in the case of not boolean type
        # then although this expression is correct
        # but in the case of the ForStep
        # it is totally wrong -> raise
        if not identical(condition_type, Basic(BasicKind.BOOL)):
            raise TypeMismatch(ast)
        
        # condition type is totally correct
        # then checking for the update
        # which is a normal assign, and we can consider
        # it is a statement, if it is not declared -> declared
        # continue to visit that assignment
        # should be pure assignment
        # not declare in this case
        self.visit_stmt(upda, parameters)

        # after preparation
        # it is the time we could visit
        # the block of the for loop
        # with the newly created scope
        self.visit(loop, parameters)


    def visitForEach(self, ast, param):
        idx = ast.idx
        value = ast.value
        arr = ast.arr
        loop = ast.loop
        scope = param['scope']
        # this is just an empty scope
        # look up the parent scope
        # still relies on the old scope
        for_scope = new_scope(parent=scope)
        parameters = {
            'scope' : for_scope
        }
        # same logic as the others statement
        # create a new scope
        # assignment -> declared with the variable
        # and then visit the Block
        
        # must handle the case of _
        # for index, value := range array
        # in the normal case
        # we would have
        # create index as type int
        # value as type element in the array type
        # and we have to ensure that array
        # must be in Array, not any other cases
        # raise type mismatch about this
        # also in the case of Id(_) ->
        # then we don't need to create a Var int
        # just create a Var of value 

        # note it is the pure assignment actually
        # not declaration
        # to be able to use
        # then index must be declared -> assignment -> int -> not found -> undeclared
        # value must be declared -> assignment -> type of element -> undeclared
        # this is not the same as assignment, because
        # in the case of assignment -> we declare undeclared value

        # index and value must be declared before
        # if not -> raise undeclared (not declare in the current scope)

        # of the array
        # if index is _, no need to check for
        # for index, value := range arr
        # we know that index and value is always Id
        # -> search through the scope
        # the expression must return an thing of array type
        # we have to check that the elem type of the array
        # match with the type of value
        # in the case of Id('_') -> no need for declared

        # we have to check that idx must be in Basic(BasicKind.INT)
        # and type of value must match the type of the element of the
        # return array in the expression

        # there is no need to check for the declaration
        # or assign the value of int

        # checking for the array type in the expression
        # resolve the expression type
        # by visiting self.visit_expr
        # if the result is not in Array
        # raise TypeMismatch
        # else if there is error within that expression
        # like type mismatch -> causing error
        # can raise undeclared
        array_type = self.visit_expr(arr, parameters)

        # in the case the result doesn't in Array
        # but other like Basic, Named, ...
        # it is not the array
        if not isinstance(array_type, Array):
            raise TypeMismatch(ast)

        # checking for the index_type


        if idx.name in ['_']:
            pass

        else:
            # must check for the declaration
            # if it is not declaration raise -> undeclared
            # if it is delcaration -> getting the type
            # this is the same as expression
            
            # could raise undeclared -> if it is not found
            # could be modified to raise
            # if resolve to something weird like function
            # or typename
            # can raise undeclared
            index_type = self.visit_expr(idx, parameters)

            # checking for the type of this index
            if not identical(index_type, Basic(BasicKind.INT)):
                raise TypeMismatch(ast)
        
        # checking for the value type
        # before doing that
        # we would have to check for the type of the expression

        # now for the value
        # checking and getting the value value
        # if it is not declared -> raise undeclared
        # because visit_expr can handle this well
        # with ast.Ident
        # obj, not in Const or Var -> may raise
        # in the case of expecting a function
        # but found something which is not a function
        # SOS -> change that behaviour
        value_type = self.visit_expr(value, parameters)

        # now we have to check that
        # the type of the value must be the same the type
        # it must match the type of elem of the array
        # if not -> raise type mismatch
        # [3]int -> int, but value float -> false
        # assume there is just one dimentional array
        # but my assignment can handle multi-dimentional array
        if not identical(value_type, array_type.elem):
            raise TypeMismatch(ast)
        
        # now checking is done
        # let go to the block
        # inside this one
        # because we don't introduce new variable
        # we have to use the one outside this scope,
        # thus we have to find through the parent scope for
        # that variable
        self.visit(loop, parameters)


    def visitContinue(self, param):
        return None
    

    def visitBreak(self, param):
        return None
    

    def visitReturn(self, param):
        # we have the wrapper
        # then we could check for the return
        # type
        # wrapper would send this status code
        # for this to realize and raise error
        return None
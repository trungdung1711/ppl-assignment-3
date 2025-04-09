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
    | *Struct       O
    | *Signature    O
    | *Named        O
    | *Interface    O
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
        self.recv    : Var        = recv
        self.params  : List[Var]  = params
        self.result  : Var        = result
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
class Interface(ZType):
    def __init__(self):
        self.methods    = [] # List[Func]


    def add_method(self, method):
        self.methods.append(method)


def identical(t1 : ZType, t2 : ZType) -> bool:
    if t1 is t2:
        return True
    
    elif type(t1) != type(t2):
        return False
    
    elif isinstance(t1, Basic) and isinstance(t2, Basic):
        return t1.kind == t2.kind
    
    elif isinstance(t1, Array) and isinstance(t2, Array):
        # SOS
        pass
    elif isinstance(t1, Signature) and isinstance(t2, Signature):
        # SOS
        # not happen
        # resolving ID
        pass
    elif isinstance(t1, Named) and isinstance(t2, Named):
        # SOS
        # not happen
        # resolving ID
        pass
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


    # def parent(self):
    #     return self.parent
    

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
        }
        self.visit(self.ast, param=parameters)


        #==================================
        # SECOND PASS - fields collecting
        #==================================
        # in the temp_global_scope
        # just get the needed one
        global_scope.refresh_global()
        parameters = {
            'pass' : 2,
            'global_scope' : global_scope,
            'scope' : global_scope
        }
        self.visit(self.ast, param=parameters)
        
    
        #==================================
        # THIRD PASS - FUNC collecting
        #==================================
        global_scope.refresh_global()
        parameters = {
            'pass' : 3,
            'scope' : global_scope,
            'global_scope' : global_scope
        }
        self.visit(self.ast, param=parameters)



    #==================================
    # TRAVERSING LOGIC
    # PASS ANY NUMBER OF ARGUMENTS
    #==================================
    def visitProgram(self, ast, param):
        pass_num = param['pass']
        if pass_num == 1:
            # pass 1: declaration pass
            [self.visit(decl, param=param) for decl in ast.decl]
        
        elif pass_num == 2:
            # pass 2: collection pass
            [self.visit(decl, param=param) for decl in ast.decl]

        elif pass_num == 3:
            # pass 3: function and method collection pass
            [self.visit(decl, param=param) for decl in ast.decl]

        else:
            pass


    # Biểu thức khởi tạo cho biến và hằng: 
    # Biểu thức này có các toán hạng là hằng, 
    # chỉ sử dụng các phép toán từ mức 2 đến mức 
    # 7 trong bảng độ ưu tiên phép toán. 
    # Không có gọi hàm hay phương thức. 
    # Hằng trong các biểu thức này là hằng có tên 
    # (của một khai báo hằng trước đó) 
    # hoặc không tên. Các hằng không tên kiểu tích hợp 
    # như StructLiteral và ArrayLiteral 
    # thì chỉ xuất hiện một mình trong các biểu thức này 
    # chứ không tham gia vào phép toán nào khác 
    # (không thiết kế test mà các hằng kiểu tích hợp 
    # tham gia phép toán khác).
    def visitVarDecl(self, ast, param):
        pass_num = param['pass']
        global_scope = param['global_scope']
        name = ast.varName

        if pass_num == 1:
            if global_scope.look_up(name) is not None:
                raise Redeclared(k=Variable(), n=name)
            else:
                obj = Var(None, name=name, typ=None, is_field=False)
                global_scope.insert(obj)
            return
        
        elif pass_num == 2:
            scope = param['scope']
            scope.resolve(name).set_declared()
            pass

        elif pass_num == 3:
            scope = param['scope']
            scope.resolve(name).set_declared()
            pass
    

    # Biểu thức khởi tạo cho biến và hằng: 
    # Biểu thức này có các toán hạng là hằng, 
    # chỉ sử dụng các phép toán từ mức 2 đến mức 
    # 7 trong bảng độ ưu tiên phép toán. 
    # Không có gọi hàm hay phương thức. 
    # Hằng trong các biểu thức này là hằng có tên 
    # (của một khai báo hằng trước đó) 
    # hoặc không tên. 
    # ###################################
    # Các hằng không tên kiểu tích hợp
    # NOTE: This would require struct collection
    # như StructLiteral và ArrayLiteral 
    # thì chỉ xuất hiện một mình trong các biểu thức này 
    # chứ không tham gia vào phép toán nào khác 
    # (không thiết kế test mà các hằng kiểu tích hợp 
    # tham gia phép toán khác).
    # const CONSTANT = always evaluated at compile time
    def visitConstDecl(self, ast, param):
        pass_num = param['pass']
        name = ast.conName
        global_scope = param['global_scope']
        expr = ast.iniExpr

        if pass_num == 1:
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
            if isinstance(expr, Id):
                typ = self.id_helper(expr, param)
            else:
                typ = self.visit(expr, param)

            if isinstance(typ, (Basic)):
                # evaluate value
                parameters = {
                    'pass' : 99,
                    'scope' : scope
                }

                value = self.visit(expr, parameters)
                obj.set_type(typ)
                obj.value = value
            return
        
        elif pass_num == 3:
            scope = param['scope']
            scope.resolve(name).set_declared()

        else:
            pass


    #==================================
    # TYPE CHECKING HAPPENING
    #==================================
    '''
    Type = *Basic       O [int, string, ...]
        | *Array        O [[4]int, [1]float]
        | *Signature    O 
        | *Named        O 
        | *Interface    O 
    '''


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
        '''
        Expression context
        '''
        op = ast.op
        X = ast.left
        Y = ast.right
        type_X = None
        type_Y = None
        pass_num = param['pass']

        if pass_num == 99:
            # type checking is done
            if isinstance(X, Id):
                value_X = self.id_helper(ast=X, param=param)
            else:
                value_X = self.visit(X, param)

            if isinstance(Y, Id):
                value_Y = self.id_helper(ast=Y, param=param)
            else:
                value_Y = self.visit(Y, param)

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
        if isinstance(X, Id):
            type_X = self.id_helper(ast=X, param=param)
        else:
            type_X = self.visit(X, param)

        if isinstance(Y, Id):
            type_Y = self.id_helper(ast=Y, param=param)
        else:
            type_Y = self.visit(Y, param)

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
        '''
        Expression context
        '''
        op = ast.op
        X = ast.body
        type_X = None
        pass_num = param['pass']

        if pass_num == 99:
            # type is finish, just evaluation
            # For literal, it is OK
            # But for Id -> break
            if isinstance(X, Id):
                value_X = self.id_helper(X, param)
            else:
                value_X = self.visit(X, param)
            if op == StaticChecker.Operator.NOT.value:
                return not value_X
            elif op == StaticChecker.Operator.SUB.value:
                return - value_X

        # first guard from [TypeName], [Func]
        if isinstance(X, Id):
            type_X = self.id_helper(X, param)
        else:
            type_X = self.visit(X, param)

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


    def visit_expression(self, ast, param):
        pass_num = param['pass']
        if pass_num == 99:
            # evaluation
            if isinstance(ast, Id):
                pass
            return

        # type checking
        if isinstance(ast, Id):
            # visit the Id node -> resolve to [Object]
            # current scope
            obj = self.visit(ast, param)
            if obj is None:
                # faild to resolve
                raise Undeclared(k=Identifier(), n=ast.name)
            
            elif isinstance(obj, (TypeName, Func)):
                '''
                Type checking error: ./tests/9.test:18:18: Human (type) is not an expression
                exit status 1

                Type checking error: ./tests/9.test:18:18: invalid operation: operator - not defined on doSomething (value of type func())
                exit status 1
                '''
                # resolve to weird things
                # SOS, may be NOT HAPPEN
                pass
            elif isinstance(obj, (Var, Const)):
                # correctly resolve
                # get the type and return
                return obj.type
        else:
            return self.visit(ast, param)


    # Used specifically for expression
    def id_helper(self, ast, param):
        # visit the Id node -> resolve to [Object]
        # current scope
        pass_num = param['pass']
        if pass_num == 99:
            # type checking is done
            # So it is OK
            obj = self.visit(ast, param)
            return obj.value

        obj = self.visit(ast=ast, param=param)
        if obj is None:
            # faild to resolve
            raise Undeclared(k=Identifier(), n=ast.name)
        elif isinstance(obj, (TypeName, Func)):
            '''
            Type checking error: ./tests/9.test:18:18: Human (type) is not an expression
            exit status 1

            Type checking error: ./tests/9.test:18:18: invalid operation: operator - not defined on doSomething (value of type func())
            exit status 1
            '''
            # resolve to weird things
            # SOS, may be NOT HAPPEN
            pass
        elif isinstance(obj, (Var, Const)):
            # correctly resolve
            # get the type and return
            return obj.type


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
        # possible errors
        # generically recursive
        # SIZE is not int type (others)                         NOT HAPPEN
        # SIZE is not constant (not evaluale at compile time)   NOT HAPPEN
        # elements have different types with type               NOT HAPPEN
        # MUST CACULATE THE SIZE AND RETURN THE Array back
        dimens = ast.dimens
        eleType = ast.eleType
        value = ast.value   # may be used to check for type NOT HAPPEN

        # SIZE is always IntLiteral and Const (resolve)

        size = []
        for expr in dimens:
            if isinstance(expr, Id):
                typ = self.id_helper(expr, param)
                parameters = {
                    'pass' : 99,
                    'scope' : param['scope']
                }
                if isinstance(typ, (Array, Named)):
                    # SOS
                    pass
                value = self.id_helper(expr, param)
                size.append(value)

            else:
                # case IntLiteral
                parameters = {
                    'pass' : 99,
                    'scope' : param['scope']
                }
                value = self.visit(expr, parameters)
                size.append(value)
        
        # for the type
        # not the array, but can be IntType, FloatType
        # StringType, BoolType, Id
        # if isinstance(eleType, Id):
        #     obj = self.visit(eleType, param)
        #     if obj is None:
        #         # undeclared type. NOT HAPPEN
        #         pass
        #     if isinstance(obj, (Var, Const, Func)):
        #         # NOT HAPPEN
        #         pass
        #     if isinstance(obj, TypeName):
        #         # correct, can be Named or Interface
        #         # Getting the type
        #         typ = obj.type
        # else:
        #     # other case rather than Id
        #     obj = self.visit(eleType, param)
        #     typ = obj.type

        # handle for us, when the type is ID, and other cases
        # only get the Type object
        element_type = self.visit_type(eleType, param)
        
        # no need to check for the values inside the
        # array literal, just calculate the size and then
        # return the new Array (Type)
        # using reduce
        # [1, 2, 3, 4] and a type
        # [4, 3, 2, 1] and a type
        # Array(1, Array(2, Array(3, Array(4, type))))
        array_type = reduce(lambda acc, cur: Array(len=cur, elem=acc), size.reversed(), element_type)
        return array_type
    

    def visitStructLiteral(self, ast, param):
        '''
        var a Human = Human{name : "string", age : 100}
        '''
        # 1. getting the current scope
        scope = param['scope']

        # 2. getting the node's information
        name = ast.name
        elements = ast.elements
        # NOTE:
        # - possible errors
        # - [Human] cannot be found -> Undeclared Type -> NOT HAPPEN    O
        # - type mismatch between field and value -> NOT HAPPEN         O
        # - [name], [age] cannot be found -> Undeclared field           O
        # - [name] can appear many times -> NOT HAPPEN                  O

        # 3. resolve Object -> TypeName not [Var, Func, Const]

        typ = self.visit_type(Id(name), param)

        fields = typ.fields
        for field_name, expr in elements:
            # name, expr
            field_type = self.visit(expr)
            if not typ.has_field(field_name):
                # SOS
                raise Undeclared(k=Field(), n=field_name)
            
            if True:
                # Type mismatch between expr and field's type
                # NOT HAPPEN
                pass
            
            # The actual type object stored in
            # TypeName object [fields, Methods]
            # Identity comparison
            # Allow for identity comparison, t1 == t2
            return typ


    def visitNilLiteral(self, ast, param):
        return None
    

    #==================================
    # DIFFERENTIATE BETWEEN expr and stmt
    #==================================
    def visitFuncCall(self, ast, param):
        # funcName must be resolve to be 
        # Func object
        # Check for Signature and args type
        funcName = ast.funName
        args = ast.args
        return None
    

    def visitMethCall(self, ast, param):
        reveicer = ast.receiver
        metName = ast.metName
        args = ast.args
        return None
    

    def visitArrayCell(self, ast, param):
        # no need to check for dimention and size mismatch
        arr = ast.arr
        idx = ast.idx
        return None
    

    def visitFieldAccess(self, ast, param):
        receiver = ast.receiver
        field = ast.field
        return None
    

    '''
    Object = *Func      O - represent a function (foo(), boo())
        | *Var          O - represent a variable (a, b, c)
        | *Const        O - represent a const (PI, SIZE)
        | *TypeName     O - represent a typename (Human, Computer)
    '''
    def visitId(self, ast, param):
        name = ast.name
        scope = param['scope']

        # NOTE: Id will be resolved into
        # different kinds of [Object]
        return scope.look_up_parent(name)
    #==================================
    # TYPE CHECKING HAPPENING
    #==================================
    
   
    # pass 3, along with MethodDecl
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
                global_scope.insert(obj)
            return

        elif pass_num == 2:
            pass

        elif pass_num == 3:
            # create the signature for this function
            # assign this signature to th obj
            scope = param['scope']
            obj = scope.look_up(name)

            obj_type = Signature(None, [], None)
            obj.set_type(obj_type)

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
                obj_type.params.append(var)

            # for the result
            # VoidType -> None
            # Other would be a type
            if len(obj_type.params) == 0:
                obj_type.params = None

            result_type = self.visit_type(retType, param)
            if result_type is None:
                result_var = None
            else:
                result_var = Var(None, 'A', result_type)
            obj_type.result = result_var

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
        global_scope = param['global_scope']
        name = ast.name
        if pass_num == 1:
            if global_scope.look_up(name) is not None:
                raise Redeclared(k=Type(), n=name)
            else:
                obj = TypeName(parent=None, name=name, typ=None)
                global_scope.insert(obj)
            return

        elif pass_num == 2:
            # TODO:
            # - check for fields redeclared
            # - create Type of Object

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
            typ = Named()
            obj.set_type(typ)
            for name, field_type in ast.elements:
                # we must get the name
                # we must get the type
                # scope would be the current scope
                # allow us to resolve for Const of Array
                # from point of declaration

                field_typ = self.visit_type(field_type, param)

                # if isinstance(field_type, Id):
                #     obj = self.visit(field_type, parameters)
                #     if obj is None:
                #         # NOT HAPPEN
                #         pass
                #     elif isinstance(obj, (Func, Var, Const)):
                #         # NOT HAPPEN
                #         pass
                #     elif isinstance(obj, TypeName):
                #         field_typ = obj.type
                
                # else:
                #     # normal type
                #     # should change because this is different from Id
                #     # should be unified
                #     # IntType()
                #     # StringType()
                #     # ArrayType()
                #     field_typ = self.visit(field_type, parameters)


                new_field = Var(parent=None, name=name, typ=field_typ, is_field=True)
                obj.type.add_field(new_field)
            
            return

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
            if isinstance(expr, Id):
                # ensure resolve to Const/Var
                # assume always calcualted
                # prevent weird Object
                # but not prevent weird basic type
                # like string, float, bool, Struct, Array
                # SOS
                typ = self.id_helper(expr, param)
                parameters = {
                    'pass' : 99,
                    'scope' : param['scope']
                }
                if isinstance(typ, (Array, Named)):
                    # SOS
                    # NOT HAPPEN
                    # ALWAYS RESOLVE TO CONST
                    # FLOAT/STRING?
                    # NOT HAPPEN
                    pass
                value = self.id_helper(expr, param)
                size.append(value)

            else:
                # case IntLiteral
                parameters = {
                    'pass' : 99,
                    'scope' : param['scope']
                }
                value = self.visit(expr, parameters)
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


    # Used for function
    def visitVoidType(self, ast, param):
        return None
    

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

            if obj is None:
                # SOS NOT HAPPEN
                pass
            
            if isinstance(obj, (Var, Const, Func)):
                # SIS NOT HAPPEN
                pass

            if isinstance(obj, TypeName):
                # correct
                return obj.type
        else:
            # IntType
            # StringType
            # BoolType
            # FloatType
            # ArrayType
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
                global_scope.insert(obj)
            return
        
        elif pass_num == 2:
            scope = param['scope']
            # TODO:
            # - check for prototypes redeclared
            # - create Type of Object
            # - Create Func object, Signature for it
            # - Add it to the Interface Type of
            # - The TypeName object

            # look up the object again -> TypeName
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
            typ = Interface()

            for method in methods:
                func = self.visit(method, param)
                typ.add_method(func)

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
        return_var_type = self.visit_type(retType, param)


        # VoidType handling
        if return_var_type is None:
            return_var = None
        else:
            return_var = Var(None, 'A', return_var_type, False)

        signature = Signature(None, method_var_list, return_var)

        # Create this Func Object
        # with Signature
        func = Func(None, name, signature)
        return func


    # pass 3, after all fields
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
            scope = param['scope']
            # TODO:
            # collect the methods of 
            # a struct
            # create the Func
            # and the Signature
            # to store this into the TypeName
            # Named type of the struct
            # Named is previously created to store
            # field
            # checking for methods redeclared
            # the receiver -> we know that 
            # there will be no error about that
            
            # NOT CHOOSE TO REUSE self.visit(FuncDecl)
            # different logic
            # create Func and add to the Named
            # but in the case of Func,
            # we find that Obj, and add the Signature to it
            # but it is not the case of MethodDecl

            # 1. Find that which TypeName object

            # Create a Func - with Signature
            # And add it to Named, which
            # is obj_type

            # create the signature for this function
            # assign this signature to th obj
            # scope = param['scope']
            # obj = scope.look_up(name)

            # obj_type = Signature(None, [], None)
            # obj.set_type(obj_type)

            # create Var object and store the type
            # inside Signature
            
            # receiver_var
            # there will be no error
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

        # Create a new Func - Signature
        # different in the case of FuncDecl
        # when we find the Func in the global_scope
        # and add the signature
        # in this case we create a new Func - Signature
        # and then add this Func to methods
        # remember to check for the 
        # redeclared fields as well

        signature = Signature(None, [], None)
        func = Func(None, name, signature)
        
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
            signature.params.append(var)

        # for the result
        # VoidType -> None
        # Other would be a type
        if len(signature.params) == 0:
            signature.params = None

        result_type = self.visit_type(retType, param)
        if result_type is None:
            result_var = None
        else:
            result_var = Var(None, 'A', result_type)
        signature.result = result_var

        return func


    def visitBlock(self, param):
        return None
 

    def visitAssign(self, param):
        return None
   
   
    def visitIf(self, param):
        return None
    

    def visitForBasic(self, param):
        return None
 

    def visitForStep(self, param):
        return None


    def visitForEach(self, param):
        return None


    def visitContinue(self, param):
        return None
    

    def visitBreak(self, param):
        return None
    

    def visitReturn(self, param):
        return None
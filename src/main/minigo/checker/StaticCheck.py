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


    def __eq__(self, value):
        if isinstance(value, Basic):
            return self.kind == value.kind
        return False
    

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
    

def identical(t1 : ZType, t2 : ZType) -> bool:
    pass


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


#Biểu thức khởi tạo cho biến và hằng: 
# Biểu thức này có các toán hạng là hằng, 
# chỉ sử dụng các phép toán từ mức 2 đến mức 7 
# trong bảng độ ưu tiên phép toán. 
# Không có gọi hàm hay phương thức. 
# Hằng trong các biểu thức này là hằng có tên 
# (của một khai báo hằng trước đó) hoặc không tên. 
# Các hằng không tên kiểu tích hợp như StructLiteral
#  và ArrayLiteral thì chỉ xuất hiện một mình 
# trong các biểu thức này chứ không tham gia 
# vào phép toán nào khác 
# (không thiết kế test mà các hằng 
# kiểu tích hợp tham gia phép toán khác).
class Const(ZObject):
    def __init__(self, parent, name, typ, value):
        self.value = value
        self.eval = False
        super().__init__(parent, name, typ)


class TypeName(ZObject):
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
        matter where it is declared

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
        #==================================
        # it seems that this is the same as
        # Scope/Object/Type-like structure
        # The checker in Go
        #==================================


    #==================================
    # LOGIC FOR SEMANTIC ANALYSIS
    #==================================
    def check(self):
        # can I do this multiple times?
        # YES :)
        #==================================
        # DECLARATION PASS
        #==================================
        # universe_scope is used for built-in things
        # global_scope is used for package
        universe_scope = new_scope(parent=None)
        #==================================
        # UNIVERSE SCOPE SETTINGS
        #==================================
        global_scope = new_scope(parent=universe_scope)

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
            'global_scope' : global_scope
        }
        self.visit(self.ast, param=parameters)
        return


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
            global_scope.look_up(name).set_declared()
            pass

        else:
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
        expr = self.iniExpr

        if pass_num == 1:
            if global_scope.look_up(name) is not None:
                raise Redeclared(k=Constant(), n=name)
            else:
                obj = Const(None, name, None, None)
                global_scope.insert(obj)
            return

        elif pass_num == 2:
            # look up will find it
            scope = param['scope']
            obj = scope.resolve(name)
            obj.set_declared()
            # now using look_up, we can find it
            # TODO: must resolve the value and the type
            # if it is RESOLVABLE
            # calculate value and type -> type mismatch

            if isinstance(expr, (StructLiteral, ArrayLiteral)):
                # skip for now, don't calculate
                pass
            else:
                # TODO:
                # can be calculated at compile time
                # calculate and type check -> get the Type and
                # also the value
                # assign, note that we ensure that the
                # contain only Id (Const) and IntLiteral
                # expression -> Id -> Check for Type
                # in Go -> Reject weird in expression
                # must get the type and the value
                # type checking
                parameters = {
                    'scope': scope
                }

                # in this pass, we know that it can be calcualted
                # in general case -> should return a type
                # and then we can calculate it later on?
                typ = self.visit(ast=expr, param=parameters)
                pass

        else:
            pass


    #==================================
    # TYPE CHECKING HAPPENING
    #==================================
    def visitBinaryOp(self, ast, param):
        return None
    
    
    def visitUnaryOp(self, ast, param):
        return None
    

    def visitIntLiteral(self, ast, param):
        return None
    
    
    def visitFloatLiteral(self, ast, param):
        return None
    
    
    def visitBooleanLiteral(self, ast, param):
        return None
    
    
    def visitStringLiteral(self, ast, param):
        return None
    

    def visitArrayLiteral(self, ast, param):
        return None
    

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
        obj = scope.look_up_parent(name)
        if obj is None:
            '''
            Type checking error: ./tests/8.test:6:17: undefined: <Type>
            exit status 1
            '''
            # NOT HAPPEN
            pass
        elif isinstance(obj, (Var, Const, Func)):
            '''
            Type checking error: ./tests/8.test:6:17: <Type> is not a type
            exit status 1
            '''
            # NOT HAPPEN
            pass
        elif isinstance(obj, TypeName):
            # Found the correct Object
            # Get the type Named
            typ = obj.type
            '''
            Type checking error: ./tests/8.test:5:45: unknown field <field> in struct literal of type <type>
            exit status 1
            '''
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
            
            # After type checking
            # Return the type back
            # Allow pointer
            return typ
    

    def visitNilLiteral(self, ast, param):
        return None
    

    def visitFuncCall(self, ast, param):
        return None
    

    def visitMethCall(self, ast, param):
        return None
    

    def visitArrayCell(self, ast, param):
        return None
    

    def visitFieldAccess(self, ast, param):
        return None
    

    '''
    Object = *Func      O - represent a function (foo(), boo())
        | *Var          O - represent a variable (a, b, c)
        | *Const        O - represent a const (PI, SIZE)
        | *TypeName     O - represent a typename (Human, Computer)
    '''
    def visitId(self, ast, param):
        # pass_num = param['pass']
        name = ast.name
        scope = param['scope']

        # NOTE: Id will be resolved into
        # different kinds of [Object]
        return scope.look_up_parent(name)
    #==================================
    # TYPE CHECKING HAPPENING
    #==================================
    
   
    def visitFuncDecl(self, ast, param):
        pass_num = param['pass']

        if pass_num == 1:
            global_scope = param['global_scope']

            name = ast.name
            if global_scope.look_up(name) is not None:
                raise Redeclared(k=Function(), n=name)
            else:
                obj = Func(parent=None, name=name, typ=None)
                global_scope.insert(obj)
            return

        elif pass_num == 2:
            # TODO: 
            # - check for param redeclared
            # - create Type of Object
            pass

        else:
            pass


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
            for name, typ in ast.elements:
                # we must get the name
                # we must get the type
                # scope would be the current scope
                # allow us to resolve for Const of Array
                # from point of declaration
                parameters = {
                    'pass' : 2,
                    'scope' : global_scope
                }
                field_type = self.visit(typ, param=parameters)
                # checking to get the type from TypeName or Array
                if isinstance(field_type, TypeName):
                    # TODO:
                    # get the type of Object
                    # assign with Var
                    pass
                elif isinstance(field_type, Array):
                    # TODO:
                    # assign the type with Var
                    pass
            # create Var object with Type and add to this type
            # for each of the fields -> get the Type
            # by visit the Type?
            # must create Var-Type and store that in Named

            pass

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
        obj = TypeName(None, 'int', typ)
        return obj

    
    def visitFloatType(self, ast, param):
        typ = Basic(kind=BasicKind.FLOAT)
        obj = TypeName(None, 'float', typ)
        return obj
    
    
    def visitBoolType(self, ast, param):
        typ = Basic(kind=BasicKind.BOOL)
        obj = TypeName(None, 'boolean', typ)
        return obj

    
    def visitStringType(self, ast, param):
        typ = Basic(kind=BasicKind.STRING)
        obj = TypeName(None, 'string', typ)
        return obj


    def visitArrayType(self, ast, param):
        dimens = ast.dimens
        typ = ast.eleType
        # Used to get the const value
        scope = param['scope']
        # must calculate all the const -> know the size
        # visit the type to get the type [TypeName] object
        # IntLiteral or ID -> can be calculated to value
        # Can be IntLiteral -> value or Id -> Const -> Get value
        # we have a list of expression -> must return 
        # Array in a recursive way
        # resolve to a list of size [1, 2, 3, 4, 5]
        # reverse the list [5, 4, 3, 2, 1]
        # resolve to the type -> TypeName or (Not Array)
        # usign reduce
        # reduce(lambda acc, cur : Array(cur, acc), list, type)
        # return that one -> recursively defined array type

        # now the problem is to calculate all the number
        # because of the constraints -> All int, or Id
        # must be resolve to an int -> no need to check
        # for type mismatch
        # then we would calculate all const in the ways
        # then use LookUpParent to find that and have the len part


    # Used for function
    def visitVoidType(self, param):
        return None


    def visitInterfaceType(self, ast, param):
        pass_num = param['pass']

        if pass_num == 1:
            global_scope = param['global_scope']

            name = ast.name
            if global_scope.look_up(name) is not None:
                raise Redeclared(k=Type(), n=name)
            else:
                obj = TypeName(parent=None, name=name, typ=None)
                global_scope.insert(obj)
            return
        
        elif pass_num == 2:
            # TODO:
            # - check for prototypes redeclared
            # - create Type of Object
            pass

        else:
            pass


    def visitMethodDecl(self, ast, param):
        pass_num = param['pass']

        if pass_num == 1:
            pass

        elif pass_num == 2:
            # TODO: 
            # check for method redeclared
            # create Type for Object
            # adding methods to struct
            pass


    def visitParamDecl(self, ast, param):
        return None


    def visitPrototype(self, param):
        return None


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
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
# SCOPE/OBJECT/TYPE STRUCTURE
#==================================
'''
Object = *Func      O
    | *Var          O
    | *Const        O
    | *TypeName     O
    | *Label        X
    | *PkgName      X
    | *Builtin      O
    | *Nil          O
'''

'''
Type = *Basic       O
    | *Pointer      X
    | *Array        O
    | *Slice        X
    | *Map          X
    | *Chan         X
    | *Struct       O
    | *Tuple        X
    | *Signature    O
    | *Alias        X
    | *Named        O
    | *Interface    O
    | *Union        X
    | *TypeParam    X
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


class Signature(ZType):
    def __init__(self, recv, params, result):
        self.recv    : Var        = recv
        self.params  : List[Var]  = params
        self.result  : Var        = result


#==================================
# OBJECT
#==================================
class ZObject(ABC):
    def __init__(self, parent, name, typ):
        self.parent : ZScope   = parent
        self.name   : str      = name
        self.type   : ZType    = typ


    def set_type(self, typ):
        self.type = typ


    def set_parent(self, scope):
        self.parent = scope


class Func(ZObject):
    pass


class Var(ZObject):
    def __init__(self, parent, name, typ, is_field):
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


    def look_up(self, name):
        if name in self.elems:
            return self.elems[name]
        return None
    

    def look_up_parent(self, name):
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
        # used in the first case to evaluate value of const
        temp_global_scope = new_scope(parent=universe_scope)
        parameters = {
            'pass' : 1,
            'global_scope' : global_scope,
            'temp_global_scope' : temp_global_scope,
        }
        self.visit(self.ast, param=parameters)


        #==================================
        # SECOND PASS
        #==================================
        parameters = {
            'pass' : 2,
            'global_scope' : global_scope
        }
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
        if pass_num == 1:
            name = ast.varName
            temp_global_scope = param['temp_global_scope']

            if temp_global_scope.look_up(name) is not None:
                raise Redeclared(k=Variable(), n=name)
            else:
                obj = Var(None, name=name, typ=None, is_field=False)
                temp_global_scope.insert(obj)
            return
        
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
        if pass_num == 1:
            name = ast.conName
            temp_global_scope = param['temp_global_scope']
            if temp_global_scope.look_up(name) is not None:
                raise Redeclared(k=Constant(), n=name)
            else:
                # evaluate the value because of the constraint
                # can be evaluated
                # must evaluate the type and the value
                # TODO: evaluate the type and the value
                # the expression is restricted (if not -> catch more errors)
                obj = Const(None, name, None, None)
                temp_global_scope.insert(obj)
        
        else:
            pass


    def visitBinaryOp(self, param):
        return None
    
    
    def visitUnaryOp(self, param):
        return None
    

    def visitId(self, param):
        return None
    

    def visitIntLiteral(self, param):
        return None
    
    
    def visitFloatLiteral(self, param):
        return None
    
    
    def visitBooleanLiteral(self, param):
        return None
    
    
    def visitStringLiteral(self, param):
        return None
    

    def visitArrayLiteral(self, param):
        return None
    

    def visitStructLiteral(self, param):
        return None
    

    def visitNilLiteral(self, param):
        return None


    def visitIntType(self, param):
        return None
    
    
    def visitFloatType(self, param):
        return None
    
    
    def visitBoolType(self, param):
        return None
    
    
    def visitStringType(self, param):
        return None
    
   
    def visitFuncDecl(self, ast, param):
        pass_num = param['pass']
        if pass_num == 1:
            global_scope = param['global_scope']
            temp_global_scope = param['temp_global_scope']

            name = ast.name
            if temp_global_scope.look_up(name) is not None:
                raise Redeclared(k=Function(), n=name)
            else:
                obj = Func(parent=None, name=name, typ=None)
                global_scope.insert(obj)
                temp_global_scope.insert(obj)
            return

        else:
            pass


    def visitStructType(self, ast, param):
        pass_num = param['pass']
        if pass_num == 1:
            global_scope = param['global_scope']
            temp_global_scope = param['temp_global_scope']

            name = ast.name
            if temp_global_scope.look_up(name) is not None:
                raise Redeclared(k=Type(), n=name)
            else:
                obj = TypeName(parent=None, name=name, typ=None)
                global_scope.insert(obj)
                temp_global_scope.insert(obj)
            
        else:
            return


    def visitInterfaceType(self, ast, param):
        pass_num = param['pass']
        if pass_num == 1:
            global_scope = param['global_scope']
            temp_global_scope = param['temp_global_scope']

            name = ast.name
            if temp_global_scope.look_up(name) is not None:
                raise Redeclared(k=Type(), n=name)
            else:
                obj = TypeName(parent=None, name=name, typ=None)
                global_scope.insert(obj)
                temp_global_scope.insert(obj)
            
        else:
            return


    def visitMethodDecl(self, ast, param):
        pass_num = param['pass']
        if pass_num == 1:
            pass

        else:
            return


    def visitParamDecl(self, ast, param):
        return None


    def visitPrototype(self, param):
        return None
    

    def visitVoidType(self, param):
        return None
    

    def visitArrayType(self, param):
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
    
    
    def visitFuncCall(self, param):
        return None
    

    def visitMethCall(self, param):
        return None
    

    def visitArrayCell(self, param):
        return None
    

    def visitFieldAccess(self, param):
        return None
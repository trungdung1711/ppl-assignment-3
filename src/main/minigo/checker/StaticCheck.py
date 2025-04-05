"""
 * @author nhphung
"""
from AST import * 
from Visitor import *
from Utils import Utils
from StaticError import *
from functools import reduce


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
class ZType(ABC):
    pass


class Signature(ZType):
    def __init__(self, recv, params, result):
        self.recv    : Var        = recv
        self.params  : List[Var]  = params
        self.result  : Var        = result


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


class TypeName(ZObject):
    pass


class ZScope:
    def __init__(self, parent, children, number, elems, isFunc):
        self.parent     : ZScope             = parent    # None if it is the universe scope
        self.children   : List[ZScope]       = children  # List[Scope]
        self.number     : int               = number    # int
        self.elems      : dict[str, ZObject] = elems     # Dict[string, Object]
        self.isFunc     : bool              = isFunc    # bool


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
        temp_global_scope = []
        parameters = {
            'pass' : 1,
            'global_scope' : global_scope,
            'temp_global_scope' : temp_global_scope,
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
        else:
            pass


    def visitVarDecl(self, ast, param):
        pass_num = param['pass']
        if pass_num == 1:
            name = ast.varName
            temp_global_scope = param['temp_global_scope']
            if name in temp_global_scope:
                raise Redeclared(k=Variable(), n=name)
            else:
                temp_global_scope.append(name)
            return
        
        else:
            pass
    

    def visitConstDecl(self, ast, param):
        pass_num = param['pass']
        if pass_num == 1:
            name = ast.conName
            temp_global_scope = param['temp_global_scope']
            if name in temp_global_scope:
                raise Redeclared(k=Constant(), n=name)
            else:
                temp_global_scope.append(name)
            return
        
        else:
            pass
    
   
    def visitFuncDecl(self, ast, param):
        pass_num = param['pass']
        if pass_num == 1:
            global_scope = param['global_scope']
            temp_global_scope = param['temp_global_scope']

            name = ast.name
            if name in temp_global_scope:
                raise Redeclared(k=Function(), n=name)
            else:
                obj = Func(parent=None, name=name, typ=None)
                global_scope.insert(obj)
                temp_global_scope.append(name)
            return

        else:
            pass


    def visitStructType(self, ast, param):
        pass_num = param['pass']
        if pass_num == 1:
            global_scope = param['global_scope']
            temp_global_scope = param['temp_global_scope']

            name = ast.name
            if name in temp_global_scope:
                raise Redeclared(k=Type(), n=name)
            else:
                obj = TypeName(parent=None, name=name, typ=None)
                global_scope.insert(obj)
                temp_global_scope.append(name)
            
        else:
            return


    def visitInterfaceType(self, ast, param):
        pass_num = param['pass']
        if pass_num == 1:
            global_scope = param['global_scope']
            temp_global_scope = param['temp_global_scope']

            name = ast.name
            if name in temp_global_scope:
                raise Redeclared(k=Type(), n=name)
            else:
                obj = TypeName(parent=None, name=name, typ=None)
                global_scope.insert(obj)
                temp_global_scope.append(name)
            
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
    
    
    def visitIntType(self, param):
        return None
    
    
    def visitFloatType(self, param):
        return None
    
    
    def visitBoolType(self, param):
        return None
    
    
    def visitStringType(self, param):
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
    

    def visitBinaryOp(self, param):
        return None
    
    
    def visitUnaryOp(self, param):
        return None
    
    
    def visitFuncCall(self, param):
        return None
    

    def visitMethCall(self, param):
        return None
    

    def visitId(self, param):
        return None
    

    def visitArrayCell(self, param):
        return None
    

    def visitFieldAccess(self, param):
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
"""
 * @author nhphung
"""
from AST import * 
from Visitor import *
from Utils import Utils
from StaticError import *
from functools import reduce

class MType:
    def __init__(self,partype,rettype):
        self.partype = partype
        self.rettype = rettype

    def __str__(self):
        return "MType([" + ",".join(str(x) for x in self.partype) + "]," + str(self.rettype) + ")"

class Symbol:
    def __init__(self,name,mtype,value = None):
        self.name = name
        self.mtype = mtype
        self.value = value

    def __str__(self):
        return "Symbol(" + str(self.name) + "," + str(self.mtype) + ("" if self.value is None else "," + str(self.value)) + ")"
    

#==================================
# DATA STRUCTURE FOR SEMANTIC CHECKER
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
class Type(ABC):
    @abstractmethod
    def string():
        pass


class Object(ABC):
    @abstractmethod
    def parent(self):
        pass

    def name(self):
        pass

    @abstractmethod
    def type(self):
        pass

    @abstractmethod
    def set_type(self, type):
        pass

    @abstractmethod
    def set_parent(self, scope):
        pass


class Scope:
    def __init__(self, parent, children, number, elems, isFunc):
        self.parent     = parent    # Scope
        self.children   = children  # List[Scope]
        self.number     = number    # int
        self.elems      = elems     # Dict[string, Object]
        self.isFunc     = isFunc    # bool


    def parent(self):
        return self.parent
    

    def len(self):
        return len(self.elems)
    

    def num_children(self):
        return len(self.children)
    

    def child(self, i):
        return self.children[i]


#==================================
# UTILITY FUNCTION
#==================================
def new_scope(parent : Scope):
    """Simulate the function NewScope in Go, return
    a new empty scope, contained in the given parent. Adapt
    eager initilization rather lazy initialization 

    Args:
        parent (Scope): the parent scope

    Returns:
        Scope: the newly created scope
    """
    s = Scope(parent, [], 0, {}, False)
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
        print('check')
        self.visit(self.ast, (1, 2, 3, 4, 5))
        return


    #==================================
    # TRAVERSING LOGIC
    # PASS ANY NUMBER OF ARGUMENTS
    #==================================
    def visitProgram(self, ast, param):
        print('program')
        return
    
    
    def visitParamDecl(self, ast, param):
        return None
    
    
    def visitVarDecl(self, ast, param):
        return None
    

    def visitConstDecl(self, param):
        return None
    
   
    def visitFuncDecl(self, param):
        return None
    

    def visitMethodDecl(self, param):
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
    

    def visitStructType(self, param):
        return None


    def visitInterfaceType(self, param):
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
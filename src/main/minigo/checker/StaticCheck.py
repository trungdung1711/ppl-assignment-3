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


#==================================
# ACTUALLY, SEMANTIC CHECKER
# CAN DECIDE HOW TO TRAVERSE
#==================================
class StaticChecker(BaseVisitor,Utils):
        
    #==================================
    # USED TO INITIALIZE PREDEFINED FUNCTION ?
    #==================================
    def __init__(self,ast):
        self.ast = ast
        self.global_envi = [Symbol("getInt",MType([],IntType())),Symbol("putIntLn",MType([IntType()],VoidType()))]


    #==================================
    # CHECK WILL BE CALLED TO START TRAVERSING
    #==================================
    def check(self):
        # can I do this multiple times?
        return self.visit(self.ast,self.global_envi)
    

    #==================================
    # IMPLEMENTATION FOR THESE METHODS
    # PASS ANY NUMBER OF ARGUMENTS
    #==================================
    def visitProgram(self, ast, param):
        return None
    
    
    def visitVarDecl(self, param):
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
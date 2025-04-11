# 2210573
# 3/7/2025
from MiniGoVisitor import MiniGoVisitor
from MiniGoParser import MiniGoParser
from AST import *



class ASTGeneration(MiniGoVisitor):
    '''
    #==============================
    AST: AST.IntLiteral
    - value : int
    #==============================
    '''
    # 3/7/2025 -> for value of different base -> don't cast from str to int
    def visitInteger_literal(self, ctx:MiniGoParser.Integer_literalContext):
        '''
            SOS: although we have the value of int, but the result 
            is used with str(self.value) ->
            - pass int -> str
            - pass str -> str

            - different base -> int -> str -> different
        '''
        if ctx.DECIMAL_INTEGER():
            # text = ctx.DECIMAL_INTEGER().getText()
            # base = 10
            return IntLiteral(ctx.DECIMAL_INTEGER().getText())
        elif ctx.BINARY_INTEGER():
            text = ctx.BINARY_INTEGER().getText()
            # base = 2
            return IntLiteral(ctx.BINARY_INTEGER().getText())
        elif ctx.OCTAL_INTEGER():
            # text = ctx.OCTAL_INTEGER().getText()
            # base = 8
            return IntLiteral(ctx.OCTAL_INTEGER().getText())
        elif ctx.HEXA_INTEGER():
            # text = ctx.HEXA_INTEGER().getText()
            # base = 16
            return IntLiteral(ctx.HEXA_INTEGER().getText())
    

    '''
    #==============================
    AST: AST.BooleanLiteral
    - value : bool
    #==============================
    '''
    # 3/7/2024, fixing boolean literal -> use getText()
    def visitBoolean_literal(self, ctx:MiniGoParser.Boolean_literalContext):
        return BooleanLiteral(value=ctx.TRUE().getText()) if ctx.TRUE() else BooleanLiteral(value=ctx.FALSE().getText())
    

    '''
    #==============================
    AST: AST.Break
    #==============================
    '''
    def visitBreak_statement(self, ctx:MiniGoParser.Break_statementContext):
        return Break()
    

    '''
    #==============================
    AST: AST.Continue
    #==============================
    '''
    def visitContinue_statement(self, ctx:MiniGoParser.Continue_statementContext):
        return Continue()
    

    '''
    #==============================
    AST: AST.Return
    - expr : Expr
    #==============================
    '''
    def visitReturn_statement(self, ctx:MiniGoParser.Return_statementContext):
        return Return(expr=self.visit(ctx.expression())) if ctx.expression() else Return(expr=None)
    

    '''
    #==============================
    AST: AST.IntType
         AST.FloatType
         AST.BoolType
         AST.StringType
    #==============================
    '''
    def visitPrimitive_type(self, ctx:MiniGoParser.Primitive_typeContext):
        if ctx.INT():
            return IntType()
        elif ctx.FLOAT():
            return FloatType()
        elif ctx.BOOLEAN():
            return BoolType()
        elif ctx.STRING():
            return StringType()


    '''
    #==============================
    AST: AST.ArrayType
    - dimens : List[Expr]
    - eleType : Type
    #==============================
    '''
    def visitArray_type(self, ctx:MiniGoParser.Array_typeContext):
        return ArrayType(dimens=self.visit(ctx.dimension_list()), eleType=self.visit(ctx.primitive_type())) if ctx.primitive_type() else ArrayType(dimens=self.visit(ctx.dimension_list()), eleType=Id(name=ctx.ID().getText()))
    

    def visitDimension_list(self, ctx:MiniGoParser.Dimension_listContext):
        return [self.visit(ctx.dimension())] if ctx.getChildCount() == 1 else [self.visit(ctx.dimension())] + self.visit(ctx.dimension_list())
    

    def visitDimension(self, ctx:MiniGoParser.DimensionContext):
        return self.visit(ctx.integer_literal()) if ctx.integer_literal() else Id(name=ctx.ID().getText())
    

    '''
    #==============================
    AST: AST.ArrayLiteral
    - dimens : List[Expr]
    - eleType : Type
    - value : NestedList
        - NestedList : PrimLit | List[NestedList]
    #==============================
    '''
    def visitArray_literal(self, ctx:MiniGoParser.Array_literalContext):
        array_type = self.visit(ctx.array_type())
        return ArrayLiteral(dimens=array_type.dimens, eleType=array_type.eleType, value=self.visit(ctx.array_element_list()))
    

    def visitArray_element_list(self, ctx:MiniGoParser.Array_element_listContext):
        return [self.visit(ctx.array_element())] if ctx.getChildCount() == 1 else [self.visit(ctx.array_element())] + self.visit(ctx.array_element_list())
    

    # 3/7/2025, adding ID as a value of array_element, as python 
    # is a dynamic type PL
    def visitArray_element(self, ctx:MiniGoParser.Array_elementContext):
        if ctx.array_element_literal():
            return self.visit(ctx.array_element_literal())
        elif ctx.ID():
            return Id(ctx.ID().getText())
        elif ctx.array_element_list():
            return self.visit(ctx.array_element_list())
        # return self.visit(ctx.array_element_literal()) if ctx.array_element_literal() else self.visit(ctx.array_element_list())
    

    # 3/7/2025 -> fixing float literal, don't cast the string to float
    def visitArray_element_literal(self, ctx:MiniGoParser.Array_element_literalContext):
        if ctx.integer_literal():
            return self.visit(ctx.integer_literal())
        elif ctx.FLOATING_POINT():
            return FloatLiteral(value=ctx.FLOATING_POINT().getText())
        elif ctx.STRING_LITERAL():
            return StringLiteral(value=ctx.STRING_LITERAL().getText())
        elif ctx.boolean_literal():
            return self.visit(ctx.boolean_literal())
        elif ctx.NIL():
            return NilLiteral()
        elif ctx.struct_literal():
            return self.visit(ctx.struct_literal())


    '''
    #==============================
    AST: AST.StructLiteral
    - name str
    - elements : List[Tuple[str, Expr]]
    #==============================
    '''
    def visitStruct_literal(self, ctx:MiniGoParser.Struct_literalContext):
        return StructLiteral(name=ctx.ID().getText(), elements=self.visit(ctx.struct_element_list()))
    

    def visitStruct_element_list(self, ctx:MiniGoParser.Struct_element_listContext):
        return [] if ctx.getChildCount() == 0 else self.visit(ctx.struct_element_prime())
    

    def visitStruct_element_prime(self, ctx:MiniGoParser.Struct_element_primeContext):
        return [self.visit(ctx.struct_element())] if ctx.getChildCount() == 1 else [self.visit(ctx.struct_element())] + self.visit(ctx.struct_element_prime())
    

    def visitStruct_element(self, ctx:MiniGoParser.Struct_elementContext):
        return (ctx.ID().getText(), self.visit(ctx.expression()))


    '''
    #==============================
    AST: AST.ArrayCell
    - arr : Expr
    - idx : List[Expr]
    AST: AST.FieldAccess
    - receiver : Expr
    - field : str
    AST: AST.Id
    - name : str
    #==============================
    '''
    def visitLhs(self, ctx:MiniGoParser.LhsContext):
        if ctx.field_access():
            return self.visit(ctx.field_access())
        elif ctx.array_index():
            return self.visit(ctx.array_index())
        elif ctx.ID():
            return Id(name=ctx.ID().getText())
    

    def visitField_access(self, ctx:MiniGoParser.Field_accessContext):
        return FieldAccess(receiver=self.visit(ctx.expression()), field=ctx.ID().getText())
    

    # 3/5/2025 -> SOS fix the bug of ArrayCell
    def visitArray_index(self, ctx:MiniGoParser.Array_indexContext):
        # return ArrayCell(arr=self.visit(ctx.expression()), idx=self.visit(ctx.index_list()))
        '''
            - Attempt to fix the bug of ArrayCell
        '''
        # result should be an ArrayCell
        expression = self.visit(ctx.expression())
        if isinstance(expression, ArrayCell):
            # prevent expression to greedily consume the index_list
            [expression.idx.append(index) for index in self.visit(ctx.index_list())]
            return expression
        else:
            # normal case
            return ArrayCell(arr=self.visit(ctx.expression()), idx=self.visit(ctx.index_list()))


    def visitIndex_list(self, ctx:MiniGoParser.Index_listContext):
        return [self.visit(ctx.index())] if ctx.getChildCount() == 1 else [self.visit(ctx.index())] + self.visit(ctx.index_list())
    

    def visitIndex(self, ctx:MiniGoParser.IndexContext):
        return self.visit(ctx.expression())
    

    '''
    #==============================
    AST: AST.If
    - expr : Expr
    - thenStmt : Stmt
    - elseStmt : Stmt
    #==============================
    '''
    def visitIf_statement(self, ctx:MiniGoParser.If_statementContext):
        return self.visit(ctx.if_part())


    def visitIf_part(self, ctx:MiniGoParser.If_partContext):
        return If(expr=self.visit(ctx.expression()), thenStmt=self.visit(ctx.block()), elseStmt=self.visit(ctx.else_part())) if ctx.else_part() else If(expr=self.visit(ctx.expression()), thenStmt=self.visit(ctx.block()), elseStmt=None)


    def visitElse_part(self, ctx:MiniGoParser.Else_partContext):
        return self.visit(ctx.if_part()) if ctx.if_part() else self.visit(ctx.block())
    

    '''
    #==============================
    AST: AST.FuncCall
    - funName : str
    - args : List[Expr]
    #==============================
    '''
    def visitCall_statement(self, ctx:MiniGoParser.Call_statementContext):
        return self.visit(ctx.function_call_statement()) if ctx.function_call_statement() else self.visit(ctx.method_call_statement())
    

    def visitFunction_call_statement(self, ctx:MiniGoParser.Function_call_statementContext):
        return FuncCall(funName=ctx.ID().getText(), args=self.visit(ctx.argument_list()))
    

    def visitArgument_list(self, ctx:MiniGoParser.Argument_listContext):
        return self.visit(ctx.argument_prime()) if ctx.argument_prime() else []
    

    def visitArgument_prime(self, ctx:MiniGoParser.Argument_primeContext):
        return [self.visit(ctx.argument())] if ctx.getChildCount() == 1 else [self.visit(ctx.argument())] + self.visit(ctx.argument_prime())
    

    def visitArgument(self, ctx:MiniGoParser.ArgumentContext):
        return self.visit(ctx.expression())


    '''
    #==============================
    AST: AST.MethCall
    - receiver : Expr
    - metName : str
    - args : List[Expr]
    #==============================
    '''
    def visitMethod_call_statement(self, ctx:MiniGoParser.Method_call_statementContext):
        return MethCall(receiver=self.visit(ctx.expression()), metName=ctx.ID().getText(), args=self.visit(ctx.argument_list()))


    '''
    #==============================
    AST: AST.StructType
    - name : str
    - elements : List[Tuple[str, Type]]
    - methods : List[MethodDecl]
    #==============================
    '''
    def visitType_declaration(self, ctx:MiniGoParser.Type_declarationContext):
        return self.visit(ctx.struct_declaration()) if ctx.struct_declaration() else self.visit(ctx.interface_declaration())


    def visitStruct_declaration(self, ctx:MiniGoParser.Struct_declarationContext):
        return StructType(name=ctx.ID().getText(), elements=self.visit(ctx.property_declaration_list()), methods=[])


    def visitProperty_declaration_list(self, ctx:MiniGoParser.Property_declaration_listContext):
        return [self.visit(ctx.property_declaration())] if ctx.getChildCount() == 1 else [self.visit(ctx.property_declaration())] + self.visit(ctx.property_declaration_list())


    def visitProperty_declaration(self, ctx:MiniGoParser.Property_declarationContext):
        return (ctx.ID().getText(), self.visit(ctx.type_part()))


    def visitType_part(self, ctx:MiniGoParser.Type_partContext):
        if ctx.primitive_type():
            return self.visit(ctx.primitive_type())
        elif ctx.ID():
            return Id(name=ctx.ID().getText())
        elif ctx.array_type():
            return self.visit(ctx.array_type())


    '''
    #==============================
    AST: AST.InterfaceType
    - name : str
    - methods : List[Prototype]
    #==============================
    '''
    def visitInterface_declaration(self, ctx:MiniGoParser.Interface_declarationContext):
        return InterfaceType(name=ctx.ID().getText(), methods=self.visit(ctx.prototype_list()))


    def visitPrototype_list(self, ctx:MiniGoParser.Prototype_listContext):
        return [self.visit(ctx.prototype())] if ctx.getChildCount() == 1 else [self.visit(ctx.prototype())] + self.visit(ctx.prototype_list())


    '''
    #==============================
    AST: AST.Prototype
    - name : str
    - params : List[Type]
    - retType : Type
    #==============================
    '''
    def visitPrototype(self, ctx:MiniGoParser.PrototypeContext):
        return Prototype(name=ctx.ID().getText(), params=[param_decl.parType for param_decl in self.visit(ctx.field_list())], retType=self.visit(ctx.type_part())) if ctx.type_part() else Prototype(name=ctx.ID().getText(), params=[param_decl.parType for param_decl in self.visit(ctx.field_list())], retType=VoidType())


    def visitFunction_declaration(self, ctx:MiniGoParser.Function_declarationContext):
        return self.visit(ctx.func_declaration()) if ctx.func_declaration() else self.visit(ctx.method_declaration())


    '''
    #==============================
    AST: AST.FuncDecl
    - name : str
    - params : List[ParamDecl]
    - retType : Type
    - block : Block
    #==============================
    '''
    def visitFunc_declaration(self, ctx:MiniGoParser.Func_declarationContext):
        return FuncDecl(name=ctx.ID().getText(), params=self.visit(ctx.field_list()), retType=self.visit(ctx.type_part()), body=self.visit(ctx.block())) if ctx.type_part() else FuncDecl(name=ctx.ID().getText(), params=self.visit(ctx.field_list()), retType=VoidType(), body=self.visit(ctx.block()))


    '''
    #==============================
    AST: AST.ParamDecl
    - parName : str
    - parType : Type
    #==============================
    '''
    def visitField_list(self, ctx:MiniGoParser.Field_listContext):
        return self.visit(ctx.field_prime()) if ctx.field_prime() else []


    def visitField_prime(self, ctx:MiniGoParser.Field_primeContext):
        return self.visit(ctx.field()) if ctx.getChildCount() == 1 else self.visit(ctx.field()) + self.visit(ctx.field_prime())


    def visitField(self, ctx:MiniGoParser.FieldContext):
        return [ParamDecl(parName=parName, parType=self.visit(ctx.type_part())) for parName in self.visit(ctx.name_list())]


    def visitName_list(self, ctx:MiniGoParser.Name_listContext):
        return [ctx.ID().getText()] if ctx.getChildCount() == 1 else [ctx.ID().getText()] + self.visit(ctx.name_list())


    '''
    #==============================
    AST: AST.MethodDecl
    - receiver : str
    - recType : Type
    - fun : FuncDecl
    #==============================
    '''
    def visitMethod_declaration(self, ctx:MiniGoParser.Method_declarationContext):
        return MethodDecl(receiver=ctx.ID(0).getText(), recType=self.visit(ctx.type_part(0)), fun=FuncDecl(name=ctx.ID(1).getText(), params=self.visit(ctx.field_list()), retType=self.visit(ctx.type_part(1)), body=self.visit(ctx.block()))) if ctx.type_part(1) else MethodDecl(receiver=ctx.ID(0).getText(), recType=self.visit(ctx.type_part(0)), fun=FuncDecl(name=ctx.ID(1).getText(), params=self.visit(ctx.field_list()), retType=VoidType(), body=self.visit(ctx.block())))
    

    '''
    #==============================
    AST: AST.Assign
    - lhs : LHS
    - rhs : Expr
    #==============================
    '''
    def visitAssignment_statement(self, ctx:MiniGoParser.Assignment_statementContext):
        '''
            - The two self.visit(ctx.lhs()) are the same but
            diffirent objects
        '''
        if self.visit(ctx.assignment_operator()) is None:
            return Assign(lhs=self.visit(ctx.lhs()), rhs=self.visit(ctx.expression()))
        return Assign(lhs=self.visit(ctx.lhs()), rhs=BinaryOp(op=self.visit(ctx.assignment_operator()), left=self.visit(ctx.lhs()), right=self.visit(ctx.expression())))


    '''
    #==============================
    AST: AST.BinaryOp
    - op : str
    - left : Expr
    - right : Expr
    #==============================
    '''
    def visitAssignment_operator(self, ctx:MiniGoParser.Assignment_operatorContext):
        if ctx.ASS():
            return None
        elif ctx.ADD_ASS():
            return str('+')
        elif ctx.SUB_ASS():
            return str('-')
        elif ctx.MUL_ASS():
            return str('*')
        elif ctx.DIV_ASS():
            return str('/')
        elif ctx.MOD_ASS():
            return str('%')
        

    def visitFor_statement(self, ctx:MiniGoParser.For_statementContext):
        if ctx.basic_for_statement():
            return self.visit(ctx.basic_for_statement())
        elif ctx.ini_for_statement():
            return self.visit(ctx.ini_for_statement())
        elif ctx.range_for_statement():
            return self.visit(ctx.range_for_statement())


    '''
    #==============================
    AST: AST.ForBasic
    - cond : Expr
    - loop : Block
    #==============================
    '''
    def visitBasic_for_statement(self, ctx:MiniGoParser.Basic_for_statementContext):
        return ForBasic(cond=self.visit(ctx.expression()), loop=self.visit(ctx.block()))


    '''
    #==============================
    AST: AST.ForStep
    - init : Stmt
    - cond : Expr
    - upda : Assign
    - loop : Block
    #==============================
    '''
    def visitIni_for_statement(self, ctx:MiniGoParser.Ini_for_statementContext):
        return ForStep(init=self.visit(ctx.ini()), cond=self.visit(ctx.expression()), upda=self.visit(ctx.for_assignment()), loop=self.visit(ctx.block()))
    

    def visitIni(self, ctx:MiniGoParser.IniContext):
        return self.visit(ctx.for_assignment()) if ctx.for_assignment() else self.visit(ctx.init_declaration())
    

    def visitFor_assignment(self, ctx:MiniGoParser.For_assignmentContext):
        if self.visit(ctx.assignment_operator()) is None:
            return Assign(lhs=Id(name=ctx.ID().getText()), rhs=self.visit(ctx.expression()))
        return Assign(lhs=Id(name=ctx.ID().getText()), rhs=BinaryOp(op=self.visit(ctx.assignment_operator()), left=Id(name=ctx.ID().getText()), right=self.visit(ctx.expression())))
    

    # 3/4/2025 -> creating VarDecl
    def visitInit_declaration(self, ctx:MiniGoParser.Init_declarationContext):
        return VarDecl(varName=ctx.ID().getText(), varType=self.visit(ctx.type_part()), varInit=self.visit(ctx.expression())) if ctx.type_part() else VarDecl(varName=ctx.ID().getText(), varType=None, varInit=self.visit(ctx.expression()))
    

    '''
    #==============================
    AST: AST.ForEach
    - idx : Id
    - value : Id
    - arr : Expr
    - loop : Block
    #==============================
    '''
    def visitRange_for_statement(self, ctx:MiniGoParser.Range_for_statementContext):
        return ForEach(idx=Id(ctx.ID(0).getText()), value=Id(ctx.ID(1).getText()), arr=self.visit(ctx.expression()), loop=self.visit(ctx.block()))


    def visitExpression(self, ctx:MiniGoParser.ExpressionContext):
        return self.visit(ctx.ex1()) if ctx.getChildCount() == 1 else BinaryOp(op=str('||'), left=self.visit(ctx.expression()), right=self.visit(ctx.ex1()))
    

    def visitEx1(self, ctx:MiniGoParser.Ex1Context):
        return self.visit(ctx.ex2()) if ctx.getChildCount() == 1 else BinaryOp(op=str('&&'), left=self.visit(ctx.ex1()), right=self.visit(ctx.ex2()))
    

    def visitEx2(self, ctx:MiniGoParser.Ex2Context):
        return self.visit(ctx.ex3()) if ctx.getChildCount() == 1 else BinaryOp(op=self.visit(ctx.relational_operator()), left=self.visit(ctx.ex2()), right=self.visit(ctx.ex3()))
    

    def visitRelational_operator(self, ctx:MiniGoParser.Relational_operatorContext):
        if ctx.DOUBLE_EQUAL():
            return str('==')
        elif ctx.NOT_EQUAL():
            return str('!=')
        elif ctx.LESS_THAN():
            return str('<')
        elif ctx.LESS_THAN_OR_EQUAL():
            return str('<=')
        elif ctx.GREATER_THAN():
            return str('>')
        elif ctx.GREATER_THAN_OR_EQUAL():
            return str('>=')
        

    def visitEx3(self, ctx:MiniGoParser.Ex3Context):
        return self.visit(ctx.ex4()) if ctx.getChildCount() == 1 else BinaryOp(op=self.visit(ctx.binary_add_sub()), left=self.visit(ctx.ex3()), right=self.visit(ctx.ex4()))


    def visitBinary_add_sub(self, ctx:MiniGoParser.Binary_add_subContext):
        return str('+') if ctx.ADD() else str('-')
    

    def visitEx4(self, ctx:MiniGoParser.Ex4Context):
        return self.visit(ctx.ex5()) if ctx.getChildCount() == 1 else BinaryOp(op=self.visit(ctx.mul_div_mod()), left=self.visit(ctx.ex4()), right=self.visit(ctx.ex5()))


    def visitMul_div_mod(self, ctx:MiniGoParser.Mul_div_modContext):
        if ctx.MUL():
            return str('*')
        elif ctx.DIV():
            return str('/')
        elif ctx.MOD():
            return str('%')
    

    '''
    #==============================
    AST: AST.UnaryOp
    - op : str
    - body : Expr
    #==============================
    '''
    def visitEx5(self, ctx:MiniGoParser.Ex5Context):
        return self.visit(ctx.ex6()) if ctx.getChildCount() == 1 else UnaryOp(op=self.visit(ctx.unary_not_sub()), body=self.visit(ctx.ex5()))
    

    def visitUnary_not_sub(self, ctx:MiniGoParser.Unary_not_subContext):
        return str('!') if ctx.NOT() else str('-')
    

    def visitEx6(self, ctx:MiniGoParser.Ex6Context):
        if ctx.ex7():
            return self.visit(ctx.ex7())
        elif ctx.index_list():
            return ArrayCell(arr=self.visit(ctx.ex6()), idx=self.visit(ctx.index_list()))
        elif ctx.argument_list():
            return MethCall(receiver=self.visit(ctx.ex6()), metName=ctx.ID().getText(), args=self.visit(ctx.argument_list()))
        else:
            return FieldAccess(receiver=self.visit(ctx.ex6()), field=ctx.ID().getText())
    

    def visitEx7(self, ctx:MiniGoParser.Ex7Context):
        if ctx.literal():
            return self.visit(ctx.literal())
        elif ctx.argument_list():
            return FuncCall(funName=ctx.ID().getText(), args=self.visit(ctx.argument_list()))
        elif ctx.expression():
            return self.visit(ctx.expression())
        else:
            return Id(ctx.ID().getText())
    

    '''
    #==============================
    AST: AST.FloatLiteral
    - value : float
    AST: AST.StringLiteral
    - value : str
    #==============================
    '''
    def visitLiteral(self, ctx:MiniGoParser.LiteralContext):
        '''
            SOS: Convert text to the value or not
        '''
        if ctx.integer_literal():
            return self.visit(ctx.integer_literal())
        elif ctx.FLOATING_POINT():
            return FloatLiteral(value=ctx.FLOATING_POINT().getText())
        elif ctx.STRING_LITERAL():
            return StringLiteral(value=ctx.STRING_LITERAL().getText())
        elif ctx.boolean_literal():
            return self.visit(ctx.boolean_literal())
        elif ctx.NIL():
            return NilLiteral()
        elif ctx.array_literal():
            return self.visit(ctx.array_literal())
        elif ctx.struct_literal():
            return self.visit(ctx.struct_literal())
        

    '''
    #==============================
    AST: AST.Block
    - member : List[BlockMember]
    #==============================
    '''
    def visitBlock(self, ctx:MiniGoParser.BlockContext):
        return Block(member=self.visit(ctx.block_member_list()))
    

    def visitBlock_member_list(self, ctx:MiniGoParser.Block_member_listContext):
        return [self.visit(ctx.block_member())] if ctx.getChildCount() == 1 else [self.visit(ctx.block_member())] + self.visit(ctx.block_member_list())
    

    def visitBlock_member(self, ctx:MiniGoParser.Block_memberContext):
        return self.visit(ctx.statement())
    

    '''
    #==============================
    AST: AST.VarDecl
    - varName : str
    - varType : Type
    - varInit : Expr
    #==============================
    '''
    def visitVariable_declaration(self, ctx:MiniGoParser.Variable_declarationContext):
        if not ctx.expression():
            return VarDecl(varName=ctx.ID().getText(), varType=self.visit(ctx.type_part()), varInit=None)
        elif not ctx.type_part():
            return VarDecl(varName=ctx.ID().getText(), varType=None, varInit=self.visit(ctx.expression()))
        else:
            return VarDecl(varName=ctx.ID().getText(), varType=self.visit(ctx.type_part()), varInit=self.visit(ctx.expression()))
        

    '''
    #==============================
    AST: AST.ConstDecl
    - conName : str
    - conType : Type
    - iniExpr : Expr
    #==============================
    '''
    def visitConstant_declaration(self, ctx:MiniGoParser.Constant_declarationContext):
        return ConstDecl(conName=ctx.ID().getText(), conType=None, iniExpr=self.visit(ctx.expression()))
    

    '''
    #==============================
    AST: AST.Program
    - decl : List[Decl]
    #==============================
    '''
    def visitProgram(self, ctx:MiniGoParser.ProgramContext):
        return Program(decl=self.visit(ctx.declaration_list()))
    

    def visitDeclaration_list(self, ctx:MiniGoParser.Declaration_listContext):
        return [self.visit(ctx.declaration())] if ctx.getChildCount() == 1 else [self.visit(ctx.declaration())] + self.visit(ctx.declaration_list())
    

    def visitDeclaration(self, ctx:MiniGoParser.DeclarationContext):
        if ctx.constant_declaration():
            return self.visit(ctx.constant_declaration())
        elif ctx.variable_declaration():
            return self.visit(ctx.variable_declaration())
        elif ctx.type_declaration():
            return self.visit(ctx.type_declaration())
        elif ctx.function_declaration():
            return self.visit(ctx.function_declaration())
    

    def visitStatement(self, ctx:MiniGoParser.StatementContext):
        if ctx.variable_declaration():
            return self.visit(ctx.variable_declaration())
        elif ctx.constant_declaration():
            return self.visit(ctx.constant_declaration())
        elif ctx.assignment_statement():
            return self.visit(ctx.assignment_statement())
        elif ctx.if_statement():
            return self.visit(ctx.if_statement())
        elif ctx.for_statement():
            return self.visit(ctx.for_statement())
        elif ctx.break_statement():
            return self.visit(ctx.break_statement())
        elif ctx.continue_statement():
            return self.visit(ctx.continue_statement())
        elif ctx.call_statement():
            return self.visit(ctx.call_statement())
        elif ctx.return_statement():
            return self.visit(ctx.return_statement())
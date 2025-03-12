// 2210573
// 3/7/2025
grammar MiniGo;

@lexer::header {
# 2210573
from lexererr import *
}

@lexer::members {
# store the previous token type
previousTokenType = None


def emit(self):
    tk = self.type
    if tk == self.UNCLOSE_STRING:       
        result = super().emit();
        raise UncloseString(result.text);
    elif tk == self.ILLEGAL_ESCAPE:
        result = super().emit();
        raise IllegalEscape(result.text);
    elif tk == self.ERROR_CHAR:
        result = super().emit();
        raise ErrorToken(result.text); 
    else:
        return super().emit();


# Override higher-level method
# def nextToken(self): 
#     next_token = super().nextToken()
#
#     self.previousTokenType = next_token.type
#
#     return next_token


# Override the emitToken() called by emit()
def emitToken(self, token:Token):
    # set the previousToken to be the current token
    self.previousTokenType = token.type
    # call the emitToken()
    super().emitToken(token)
}

options{
	language=Python3;
}


// ANTLR prioritizes rules based on order

/*
    - The @lexer::header section in an ANTLR .g4 file 
    is a special directive used to inject custom code 
    into the generated lexer.

    - When ANTLR generates the Python lexer, 
    it will include this code at the top of the lexer file.

    - Yes, via inline actions
 */


/*
    - Defines custom methods inside the lexer class.

    - Inside the lexer class

    - Yes, via methods

    - If error handling gets complex, 
    using @lexer::members to define separate functions makes 
    the code cleaner and more maintainable.
 */


// LEXER RULES

// TOKENS
/* 
    - keywords, 
    - identifiers, 
    - operators, 
    - separators, 
    - literals
*/

/*
    keywords:
    - reserved words
    - cannot be used as identifiers
*/
INTERFACE           : 'interface' ;
CONTINUE            : 'continue' ;
BOOLEAN             : 'boolean' ;
RETURN              : 'return' ;
STRUCT              : 'struct' ;
STRING              : 'string' ;
FLOAT               : 'float' ;
CONST               : 'const' ;
BREAK               : 'break' ;
RANGE               : 'range' ;
FALSE               : 'false' ;
TRUE                : 'true' ;
FUNC                : 'func' ;
TYPE                : 'type' ;
ELSE                : 'else' ;
FOR                 : 'for' ;
INT                 : 'int' ;
VAR                 : 'var' ;
NIL                 : 'nil' ;
IF                  : 'if' ;

/*
    operators:
    - +, -, *, /, %
    - ==, !=, <, <=, >, >=
    - &&, ||, !
    - =, +=, -=, *=, /=, %=
    - .
 */
// longer rule
AND                     : '&&' ;
OR                      : '||' ;
ADD_ASS                 : '+=' ;
SUB_ASS                 : '-=' ;
MUL_ASS                 : '*=' ;
DIV_ASS                 : '/=' ;
MOD_ASS                 : '%=' ;
ASS                     : ':=' ;
DOUBLE_EQUAL            : '==' ;
NOT_EQUAL               : '!=' ;
LESS_THAN_OR_EQUAL      : '<=' ;
GREATER_THAN_OR_EQUAL   : '>=' ;
// shorter rule
ADD                     : '+' ;
SUB                     : '-' ;
MUL                     : '*' ;
DIV                     : '/' ;
MOD                     : '%' ;
EQUAL                   : '=' ;
LESS_THAN               : '<' ;
GREATER_THAN            : '>' ;
DOT                     : '.' ;
NOT                     : '!' ;

/*
    separators:
    - (, )
    - {, }
    - [, ]
    - ,
    - ;
 */
LP                      : '(' ;
RP                      : ')' ;
LB                      : '[' ;
RB                      : ']' ;
LCB                     : '{' ;
RCB                     : '}' ;
COMMA                   : ',' ;
// This COLON doesn't have in the separator
COLON                   : ':' ;
SEMICOLON               : ';' ;

/*
    literals:
    - integer literal
        + decimal
        + binary
        + octal
        + hexa
    - floating-point literal
    - string literal
    - boolean literal
    - nil literal
*/
DECIMAL_INTEGER         : '0' | [1-9] [0-9]* ;
BINARY_INTEGER          : '0' [bB] [0-1]+ ;
OCTAL_INTEGER           : '0' [oO] [0-7]+ ;
HEXA_INTEGER            : '0' [xX] [0-9a-fA-F]+ ;
// FLOATING_POINT is refering DOT again which is not intuitive
FLOATING_POINT          : INTEGER '.' FRACTION? EXPONENT? ;
    fragment INTEGER            : DIGIT+ ;
    fragment FRACTION           : DIGIT+ ;
    fragment EXPONENT           : [eE] [+-]? DIGIT+ ;
// handling raw characters
// raw \n -> X
// raw \t -> O
// raw \r -> X
STRING_LITERAL          : '"' (~[\\"\r\n] | ESCAPE_SEQUENCE)* '"';
    // \n
    // \t
    // \r
    // \"
    // \\
    fragment ESCAPE_SEQUENCE    : '\\' [ntr"\\];
/* 
    identifiers:
    - variable names
    - constant names
    - type names
    - function names
    - other user-defined elements
*/
ID                     : (LETTER | UNDERSCORE) (LETTER | DIGIT | UNDERSCORE)*;
    fragment LETTER         : [a-zA-Z] ;
    fragment DIGIT          : [0-9] ;
    fragment UNDERSCORE     : '_' ;

// Comments
SINGLE_LINE_COMMENT : '//' ~[\r\n]*                             -> skip;
// first version: MULTI_LIME_COMMENT  :  '/*' .*? '*/';             --- Dont support nested comment
// second version: NON-GREEDY
//        + if nested many times and correctly    --- Only one token
//        + Can allow multiple multi-line comment, each with nested and doesn't cause problem
//        + Can handle the case of /* com/*ment */
//        + Have the same behaviour as real Go: /* com*/ment */
//        + Can handle this one: /* com/*/**/*/ment */
MULTI_LIME_COMMENT  :  '/*' (MULTI_LIME_COMMENT | .)*? '*/'     -> skip;

// blanks, tabs, formfeeds, carriage returns and newlines
WHITESPACE          : [ \t\f\r]+                                -> skip ;

/*
    How nextToken() works
    - Check If We Are at the End of Input (EOF):

    - Try to Match a Token Using Lexer Rules:

    - If a rule matches, it triggers an action (e.g., emit(), skip(), or more()).

    - If no action is specified, the default behavior is to emit the token.

    - Then the { ... } block is called whenever the lexer matches the NEWLINE token.

    - AFTER executing the action, the lexer either emits or skips the NEWLINE token 
    (depending on whether it calls emit(), skip(), or does nothing).
 */
NEWLINE             : '\n'
{
# logic to decide whether to skip or replace the NEWLINE with a SEMICOLON token
# add NIL literal as it can be part of the expression
must_be_replaced_when_before_NEWLINE_set = {
    # ID
    self.ID,
    # integer
    self.DECIMAL_INTEGER,
    self.BINARY_INTEGER,
    self.OCTAL_INTEGER,
    self.HEXA_INTEGER,
    # floating point
    self.FLOATING_POINT,
    # boolean
    self.TRUE,
    self.FALSE,
    # string literal
    self.STRING_LITERAL,
    # keyword for type
    self.INT,
    self.FLOAT,
    self.BOOLEAN,
    self.STRING,
    # keywords
    self.RETURN,
    self.CONTINUE,
    self.BREAK,
    # closed token
    self.RP,
    self.RB,
    self.RCB,
    # nil
    self.NIL
}
if self.previousTokenType in must_be_replaced_when_before_NEWLINE_set:
    # set the current token to be semicolon_token   -> emit() -> emitToken()
    self.type = self.SEMICOLON
    self.text = ';'
    self.emit()
    # self.emitToken(semicolon_token)
else:
    self.skip()
};


/*
    How parser interact with lexer
    - When the parser requests a token, CommonTokenStream calls lexer.nextToken()

    - Step 1: skip() Marks the Token for Skipping
    self.skip() prevents the token from being returned to the parser.
    ANTLR immediately calls nextToken() again to fetch another token.

    - If NEWLINE is skipped, the parser never sees it, and previousTokenType 
    remains unchanged.

    - CommonTokenStream calls lexer.nextToken() repeatedly to preload tokens.

    - It stores tokens internally, except skipped tokens.

    - The parser fetches tokens from CommonTokenStream, not directly from the lexer.

    - The skipped token is never added to CommonTokenStream.

    - The lexer calls nextToken() again to get a new token.
*/

// Handling errors
/*
    - UnclosedString(<unclosed string>): when the lexer detects an unterminated
    string. The unclosed string is from the beginning of the string (without the
    quote) to the newline or end of file, exclusively.
 */

/*
    - No lexer errors are raised 
    because every part of the input matches a valid token rule.

    - ven though "vars" is not a valid keyword, 
    it still follows the ID rule, so the lexer accepts it.

    - The parser now consumes the tokens generated by the lexer.

    - It tries to match them to the defined grammar rules (syntax rules).

    - Boom! The parser throws a syntax error because "vars" is unexpected.

    - Lexer only produces ErrorToken when it encounters an unrecognized character.

    - If all characters match valid tokens, 
    the lexer finishes successfully—even if the tokens don't form a valid statement.

    - The parser is responsible for checking 
    if the sequence of tokens makes sense grammatically.
*/

//                                                        BAD ESCAPE DETECTION
ILLEGAL_ESCAPE      : '"' (~[\\"\r\n] | ESCAPE_SEQUENCE)* '\\' ~[ntr"\\]
{
    text = self.text
    raise IllegalEscape(text)
};

UNCLOSE_STRING      : '"' (~[\\"\r\n] | ESCAPE_SEQUENCE)*
{
    text = self.text
    raise UncloseString(text)
};

ERROR_CHAR          : .
{
    raise ErrorToken(self.text)
};
// -------------------------------------------


// PARSER RULES
// Write the grammar using BNF not EBNF
program             : declaration_list EOF
                    ;
    declaration_list    : declaration declaration_list
                        | declaration
                        ;

// should not be inside a block
// CHECK - type_declaration -> Type
declaration         : constant_declaration  // global things            O
                    | variable_declaration  // global things            O
                    | type_declaration      // struct or interface      O
                    | function_declaration  // a function               O
                    ;
    // MAP
    type_declaration    : struct_declaration
                        | interface_declaration
                        ;
        // MAP
        struct_declaration  : TYPE ID STRUCT LCB property_declaration_list RCB SEMICOLON
                            ;
            // struct_name             : ID 2/21/2025 -> replace struct_name
            //                         ;
            // a non-empty list
            // MAP
            property_declaration_list   : property_declaration property_declaration_list
                                        | property_declaration
                                        ;
                // MAP
                property_declaration        : ID type_part SEMICOLON
                                            ;
                    // property_name               : ID 2/21/2025 -> replace property_name
                    //                             ;
        // CHECK - should rename for AST alignment
        // 2/26/2025 fixing the name for AST alignment
        // MAP
        interface_declaration   : TYPE ID INTERFACE LCB prototype_list RCB SEMICOLON
                                ;
            // interface_name          : ID 2/21/2025 -> replace interface_name
            //                         ;
            // non-empty list of method declaration
            // MAP
            prototype_list          : prototype prototype_list
                                    | prototype
                                    ;
                // MAP
                prototype               : ID LP field_list RP type_part SEMICOLON
                                        | ID LP field_list RP           SEMICOLON
                                        ;

    // not the same as C/C++ when the declaration can be separated from function definition
    // 2/26/2025 fixing the intermediate rule
    // making the function_declaration more correct and align with teacher's AST
    // and prototype in interface declaration
    // MAP
    function_declaration: func_declaration
                        | method_declaration
                        ;
        // MAP
        func_declaration            : FUNC ID LP field_list RP type_part block SEMICOLON
                                    | FUNC ID LP field_list RP           block SEMICOLON
                                    ;
                    // function_name               : ID 2/21/2025 replace function_name
                    //                             ;
            // 2/26/2025 -> fixing parameter_list to align with real Go
            // field list
            // parameter_list              : parameter_prime
            //                             | 
            //                             ;
            // 2/26/2025 -> replace parameter_list with field_list -> more like Go
            // MAP
            field_list                  : field_prime
                                        |
                                        ;
                // MAP
                field_prime             : field COMMA field_prime
                                        | field
                                        ;
                    // name_list can contain one or a list of ID
                    // return [] -> then return list of ID + same type -> list of ParamDecl -> a field -> field_list
                    // MAP
                    field                   : name_list type_part
                                            ;
                        // as like in Go's AST tree when each ast.Field contain
                        //------Name : list of pointer ast.Ident
                        //------Type : pointer ast.Ident
                        // MAP
                        name_list               : ID COMMA name_list
                                                | ID
                                                ;
                // 2/26/2025 -> commenting out redundant rules
                // parameter_prime             : parameter COMMA parameter_prime
                //                             | parameter
                //                             ;
                            // cause ambiguity, but solved based on ANTLR ordering rule
                    // parameter                   : name_type
                    //                             | same_type_list
                    //                             ;
                        // same_type_list          : name_list type_part
                        //                         ;
                            // name_list               : ID COMMA name_list
                            //                         | ID 2/26/2025 -> comment this redundant rule
                            //                         ;
                                        // name                    : ID 2/21/2025 replace name ->
                                        //                         ;
                    // name_type                   : ID type_part
                    //                                 ;
            // MAP
            block                           : LCB block_member_list RCB
                                            ;
                // MAP
                block_member_list               : block_member block_member_list
                                                | block_member
                                                ;
                    // MAP
                    block_member                    : statement
                                                    ;
            // NOTE: whether or not, there is a statement end???
            // CHECK
            // 2/26/2025 fixing long rule -> short rule and more specific to be easier to create AST node
            // and align with the AST teacher's structure
        // MAP
        method_declaration          : FUNC LP ID type_part RP ID LP field_list RP type_part block SEMICOLON
                                    | FUNC LP ID type_part RP ID LP field_list RP           block SEMICOLON
                                    ;
// it doesn't contain function_declaration, thus a block should have multiple statements
// check-out list for AST generation
// MAP
statement           : variable_declaration  // O    O
                    | constant_declaration  // O    O
                    | assignment_statement  // O    O
                    | if_statement          // O    O
                    | for_statement         // O    O
                    | break_statement       // O    O
                    | continue_statement    // O    O
                    | call_statement        // O    O
                    | return_statement      // O    O
                    ;
    // variable_declaration    : VAR variable_name type? initialisation? ;
    // NOTES
    // fixing
    // Comment out the fourth rule, as there must be at least type or initialisation
    // MAP
    variable_declaration    : VAR ID type_part EQUAL expression SEMICOLON
                            | VAR ID type_part                  SEMICOLON
                            | VAR ID           EQUAL expression SEMICOLON
                            // | VAR ID                          
                            ;
        // variable_name           : ID 2/21/2025 replace variable_name -> 
        //                         ;
        // MAP
        type_part               : primitive_type     // representing type of variable
                                | ID                 // can be type of Struct or Interface (user defined)
                                | array_type
                                ;
            // MAP
            primitive_type          : INT
                                    | FLOAT
                                    | BOOLEAN
                                    | STRING
                                    ;
            // parser would allow wrong type, but not the case of semantic analysis
            // composite_type          : ID 2/25/2025 replace composite_type
            //                         ;
            // array_type              : dimension_list (primitive_type | composit_type);
            // should be the expression while the semantic analysis would reject the incorrect one
            // based on the MiniGo specification:
            // - only allow integer_literal and constant only
            // - different from array indexing in expression actually
            // MAP
            // should be recursively defined, as like Go
            // CHECK
            array_type              : dimension_list primitive_type 
                                    | dimension_list ID
                                    ;
                // MAP
                dimension_list          : dimension dimension_list 
                                        | dimension
                                        ;
                    // MAP
                    dimension               : LB integer_literal RB
                                            | LB ID              RB
                                            ;
                        // the parser cannot determine 
                        // whether an identifier actually refers to a constant
                        // constant                : ID 2/21/2025 replace constant
                        //                         ;
        // value must be computable at compile time
        // initialisation          : EQUAL expression 2/21/2025
        //                         ;
            // MAP
            expression              : expression OR ex1
                                    | ex1
                                    ;
                // MAP
                ex1                     : ex1 AND ex2
                                        | ex2 
                                        ;
                    // MAP
                    ex2                     : ex2 relational_operator ex3
                                            | ex3
                                            ;
                        // MAP
                        relational_operator     : DOUBLE_EQUAL
                                                | NOT_EQUAL
                                                | LESS_THAN
                                                | LESS_THAN_OR_EQUAL
                                                | GREATER_THAN
                                                | GREATER_THAN_OR_EQUAL
                                                ;
                        // MAP
                        ex3                     : ex3 binary_add_sub ex4
                                                | ex4
                                                ;
                            // MAP
                            binary_add_sub          : ADD
                                                    | SUB
                                                    ;
                            // MAP
                            ex4                     : ex4 mul_div_mod ex5
                                                    | ex5
                                                    ;
                                // MAP
                                mul_div_mod             : MUL
                                                        | DIV
                                                        | MOD
                                                        ;
                                // MAP
                                ex5                     : unary_not_sub ex5
                                                        | ex6
                                                        ;
                                    // MAP
                                    unary_not_sub           : NOT
                                                            | SUB
                                                            ;
                                    // get the element in the array (expression)
                                    // get the element of the struct type
                                    // call the method of the struct type
                                    // CHECK -> create MethCall
                                    // 2/25/2025 modify the array access expression to
                                    // follow the AST's structure
                                    // AST unification happens at this state
                                    // with the LHS and expression
                                    // ArrayCell
                                    // FieldAccess
                                    // MethCall
                                    // MAP
                                    ex6                     : ex6 index_list                     // array access
                                                            | ex6 DOT ID LP argument_list RP     // with the receiver before the DOT operator
                                                            | ex6 DOT ID                         // 2/25/2025 - deleting intermediate function_call rule
                                                            | ex7                                // at this point -> create MethCall()
                                                            ;
                                        // function call
                                        // MAP
                                        ex7                     : literal
                                                                | ID                        // can be merged and let semantic analysis to handle??
                                                                | ID LP argument_list RP    // 2/25/2025 - deleting intermediate parser rule
                                                                | LP expression RP          // result from other operator
                                                                ;                           // at this point -> create FuncCall
                                            // CHECK
                                            // call                    : function_call 2/25/2025 -> removing unused parser rule
                                            //                         // | method_call - already represented by DOT operator
                                            //                         ;
                                                // function_call           : ID LP argument_list RP - 2/25/2025 remove function_call
                                                //                         ; -> making it embedded into other rules for intuition
                                            // MAP
                                            literal                 : integer_literal
                                                                    | FLOATING_POINT
                                                                    | STRING_LITERAL
                                                                    | boolean_literal
                                                                    | NIL
                                                                    | array_literal
                                                                    | struct_literal
                                                                    ;
                                                // MAP
                                                integer_literal         : DECIMAL_INTEGER
                                                                        | BINARY_INTEGER
                                                                        | OCTAL_INTEGER
                                                                        | HEXA_INTEGER
                                                                        ;
                                                // MAP
                                                boolean_literal         : TRUE
                                                                        | FALSE;
                                                // must always have the [array_type] part
                                                // but inside, it can be 
                                                // expression (in the case of multiple array): allow array_type
                                                // not the expression but in the type of LCB
                                                // NOTE: the value inside must be fixed
                                                // fixing-array_literal can't be nullable
                                                // MAP
                                                array_literal           : array_type LCB array_element_list RCB
                                                                        ;
                                                    // MAP
                                                    array_element_list      : array_element COMMA array_element_list
                                                                            | array_element
                                                                            ;
                                                            // allowing type deduction
                                                            // Take one part of the array_literal
                                                            // array_literal           : [array_type] (LCB element_array_list RCB)
                                                            // CHECK!
                                                            // 25/2/2025 change the name for this special literal
                                                        // MAP
                                                        // 3/7/2025 fixing the ID of the array literal
                                                        // as python is a dynamic type PL
                                                        array_element           : array_element_literal           // which can allow typed array literal
                                                                                | ID                           // Just contain PrimLit (only), not ID
                                                                                | LCB array_element_list RCB      // can be seen as another array_literal
                                                                                ;
                                                                                // 2/25/2025 removing the ID part, as alligned with the AST teacher's structure, NO ID
                                                            // there is no array literal
                                                            // MAP
                                                            array_element_literal   : integer_literal
                                                                                    | FLOATING_POINT
                                                                                    | STRING_LITERAL
                                                                                    | boolean_literal
                                                                                    | NIL
                                                                                    | struct_literal
                                                                                    ;
                                                // MAP
                                                struct_literal          : ID LCB struct_element_list RCB
                                                                        ;
                                                    // MAP
                                                    struct_element_list     : struct_element_prime
                                                                            |
                                                                            ;
                                                        // MAP
                                                        struct_element_prime    : struct_element COMMA struct_element_prime
                                                                                | struct_element
                                                                                ;
                                                            // MAP
                                                            struct_element          : ID COLON expression
                                                                                    ;
                                                                // field_name              : ID 2/21/2025 replace field_name
                                                                //                         ;
        // // MAP - default behaviour
        // statement_end       : SEMICOLON      - 2/21/2025 -> SEMICOLON
        //                     // | NEWLINE
        //                     ;
    // different between Go and C/C++
    // In Go, const means "absolutely immutable and evaluable at compile time."
    // Go doesn't allow 
    // var z = 100
	// const m = z + 100
    // -----
    // In C/C++, const only means "this value cannot be changed after initialization," 
    // but it does not have to be evaluable at compile time.
    // In C++, const int y = x + 10; is allowed, but x might change later, causing confusion.
    // note about constexpr
    // CHECK
    // MAP
    constant_declaration    : CONST ID EQUAL expression SEMICOLON;
        // const_name              : ID; 2/21/2025
        // should be a general expression (no need to separate them)
        // Go does not allow const for array, struct, slice, or map types.
        // Valid constant types: int, float, bool, string, complex.
        // value                   : expression 2/21/2025
        //                         // | literal_constant-redundant, as expression can be resolve to literal actually
        //                         ;
            // literal_constant        : integer_literal
            //                         | FLOATING_POINT
            //                         | STRING_LITERAL
            //                         | boolean_literal
            //                         ;
    // MAP
    // 2/27/2025 fixing the assignment statement to fit the AST's structure
    assignment_statement    : lhs assignment_operator expression SEMICOLON
                            ;
        // 2/27/2025 -> there is no reuse part of the
        // assignment part -> no need for doing that
        // assignment_part     : lhs assignment_operator expression
        //                     ;
        // MAP
        assignment_operator     : ASS
                                | ADD_ASS
                                | SUB_ASS
                                | MUL_ASS
                                | DIV_ASS
                                | MOD_ASS
                                ;
        // note, we must allow them to be chained together
        // allow expression in []
        // the left hand side is separately defined from the expression
        // only ASS can be changed to declaration if the expression in the right hand side
        // does contain the value
        // the other operator will be rejected by semantic analysis

        // Here, both foo().bar()[1].baz(); and myArray[2][3] use chaining, 
        // but they are not part of expressions. 
        // This means the parser must recognize them without relying on 
        // the normal expression grammar.

        // parse the same as the expression actually
        // lhs                     : lhs DOT field_name
        //                         | lhs LB expression RB
        //                         | scalar_variable
        //                         ;
        // 2/25/2024 fixing the lhs rule for alignment with the AST
        // more specific case of the lhs
        // MAP
        // SOS
        // fixing the expression recursive affects lhs
        // idea the expression of array_index must not include
        // array_index -> wrong case
        // -> must include array_index for a[1].c[2]
        lhs                     : field_access
                                | array_index
                                | ID
                                ;
            // MAP in expression, we would have to map again
            field_access            : expression DOT ID
                                    ;
            // MAP
            // should be expression that dont' contain the array access
            // if there is expression that contains array access
            // expression will catch all and only left one for the
            // left hand side
            // problem with lhs and expression
            // SOS, expression will eat the index_list ->
            // only left one
            array_index             : expression index_list
                                    ;
                // MAP
                index_list              : index index_list
                                        | index
                                        ;
                // MAP
                index                   : LB expression RB
                                        ;
            // scalar_variable         : ID 2/21/2025
            //                         ;
        // rhs                     : expression 2/21/2025
        //                         ;   // value must be compatible with the type of lhs
    // How about the  which enforces the ending of the statement ???
    // must be check again for correct AST generation
    // may not explicitly represented in AST
    // NOTE: adding ???
    // else if list
    // NOTE can be define as recursive rule
    // CHECK - 2/25/2025 - modify if_statement for AST structure, solving the
    // SEMI at the end of the if_statement
    // MAP
    // 2/27/2025 fixing the name of the statement for correct naming, and align with AST
    if_statement            : if_part SEMICOLON
                            // | if_part           SEMICOLON
    //                         | IF LP expression RP block           SEMICOLON
                            // | IF LP expression RP block             SEMICOLON
                            // | IF LP expression RP block   SEMICOLON

                            ;
        // same as if_statement but doesn't have SEMI at the end -> allow recursive in else part
        // MAP
        if_part                 : IF LP expression RP block else_part
                                | IF LP expression RP block
                                ;
        // MAP
        else_part               : ELSE if_part
                                | ELSE block
                                ;
        // boolean_expression      : expression 2/21/2025
        //                         ;
        // else_if_list            : else_if else_if_list | else_if 
        //                         ;
            // else_if                 : ELSE IF LP expression RP block 2/25/2025 moving to use if_statement_recursive
            //                         ;                                         to align the AST structure
        // else_block                  : ELSE block
        //                             ;
    /*
        for statement: 
            - basic form
            - form with initialization
            - form for iterating over an array
     */
    // NOTE: add 
    // MAP
    for_statement           : basic_for_statement
                            | ini_for_statement
                            | range_for_statement
                            ;
        // change to condition for synchronisation
        // MAP
        basic_for_statement     : FOR expression block SEMICOLON
                                ;
        // if you want the  to be nothing, then in the same line of [}
        // you would continue to write the program -> no SEMI is inserted
        // if you enter -> SEMI, there must be grammar SEMI to catch this as a part 
        // of the grammar
        // 2/27/2025, fixing the for statement for AST's compatibility
        // 2/2/27/2025, using for_assignment which is the AssignStmt specific in For
        // MAP
        // MUST
        ini_for_statement       : FOR ini SEMICOLON expression SEMICOLON for_assignment block SEMICOLON
                                ;
            // there can be mistake at that point, but I choose to risk
            // NOTE: omit the declaration in for loop
            // MAP
            ini                     : for_assignment
                                    //init_assignment
                                    | init_declaration
                                    ;
                // 2/27/2025 create a new rule used exclusively in ini_for_statement
                // ease the creation of AST
                // MAP
                for_assignment          : ID assignment_operator expression
                                        ;
                    // for_lhs                 : ID 2/25/2025
                    //                         ;
                // NOTE
                // 2/27/2025 may convert it into Assign with lhs ID and rhs Expr
                // MAP
                // 3/4/2025 -> change it to VarDecl
                // the specification clearly states variable declaration with initialization
                // -> grammar rule
                init_declaration        : VAR ID type_part EQUAL expression
                                        | VAR ID           EQUAL expression
                                        ;
            // condition               : expression
            //                         ;
        // MAP
        range_for_statement     : FOR ID COMMA ID ASS RANGE expression block SEMICOLON
                                ;
            // index                   : ID 2/21/2025
            //                         ;   // if it is an UNDERSCORE character -> may be handled in semantic analysis
            // value_array             : ID 2/21/2025
            //                         ;
            // should be defined as expression
            // element access
            // return from function
            // array                   : expression 2/21/2025
            //                         ;
                                // inside the for_statement handled by semantic analysis (context stack)
    // MAP
    break_statement             : BREAK SEMICOLON
                                ;
    // MAP
    continue_statement          : CONTINUE SEMICOLON
                                ;
    // Here, both foo().bar()[1].baz(); and myArray[2][3] use chaining, 
    // but they are not part of expressions. 
    // This means the parser must recognize them without relying on 
    // the normal expression grammar.

    // CHECK, must create the same FuncCall and MethCall
    // with expression -> need modify to be unified in AST
    // MAP
    call_statement              : function_call_statement
                                | method_call_statement
                                ;
        // MAP
        function_call_statement     : ID LP argument_list RP SEMICOLON
                                    // function_call SEMICOLON - 2/25/2025 deleting intermediate rule
                                    ;
            // MAP
            argument_list           : argument_prime
                                    | 
                                    ;
                // MAP
                argument_prime          : argument COMMA argument_prime
                                        | argument
                                        ;
                    // MAP
                    argument                : expression
                                            ;
        // problematic
        // NOTE
        // grammartically prevent weird expression
        // but unified CallExpr
        // MAP
        method_call_statement       : expression DOT ID LP argument_list RP SEMICOLON
                                    // expression DOT function_call SEMICOLON - 2/25/2025 deleting intermediate rule
                                    ;
    // MAP
    return_statement            : RETURN expression SEMICOLON
                                | RETURN            SEMICOLON
                                ;
/*
    what semantic analysis (semantic checking) do, not the parser's job: 
        - scope
        - type compatible
        - operation is allowed for a type
        - assignment but not declaration -> add to the symbol table
        - scope hierarchy
 */
// -------------------------------------------
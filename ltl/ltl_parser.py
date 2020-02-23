from __future__ import print_function

import inspect
from contextlib import contextmanager

from ply import yacc, lex
from .ltl_lexer import LTLLexer

from .ltl_common import *


class error(Exception):
    pass


class LTLParser(object):
    
    start = "property_list"
        
    def __init__(self, **kwargs):

        self.lexer = LTLLexer()
        
        self.lexer.build()
        self.tokens = self.lexer.tokens
        
        self.parser = yacc.yacc( module=self, tabmodule="__ltl_parsetab", **kwargs)
        self.assumptions = []
        self.assertions = []
        
    def parse(self, text, *args, **kwargs):
        return self.parser.parse(text, self.lexer, *args, **kwargs)

    precedence = (
        ('right', 'IMPLIES'),
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'NOT'),
        
        ('left', 'LTL_U', 'LTL_R' ),
        ('left', 'LTL_G', 'LTL_F', 'LTL_X' ),
        
        ('left', 'LTL_S', 'LTL_T'),
        ('left', 'LTL_Y', 'LTL_Z', 'LTL_H', 'LTL_O' ),
        
        ('left', 'EQUALS', 'NOT_EQUALS'),
    )

    def p_property_list(self, p):
        """ property_list  : property
                           | property_list property """

    def p_property(self, p):
        """ property : assumption 
                     | assertion """

    def p_assumption(self, p):
        """ assumption : ASSUME ltl_formula optsemi """
        self.assumptions.append( p[2] )

    def p_assertion(self, p):
        """ assertion : optassert ltl_formula optsemi """
        self.assertions.append( p[2] )
        
    def p_ltl_formula_G(self, p):
        " ltl_formula : LTL_G ltl_formula "
        p[0] = GNode(p[2])

    def p_ltl_formula_F(self, p):
        " ltl_formula : LTL_F ltl_formula "
        p[0] = FNode(p[2])

    def p_ltl_formula_X(self, p):
        " ltl_formula : LTL_X ltl_formula "
        p[0] = XNode(p[2])

    def p_ltl_formula_U(self, p):
        " ltl_formula : ltl_formula LTL_U ltl_formula "
        p[0] = UNode(p[1], p[3])
        
    def p_ltl_formula_R(self, p):
        " ltl_formula : ltl_formula LTL_R ltl_formula "
        p[0] = RNode(p[1], p[3])
        
    def p_ltl_formula_Y(self, p):
        " ltl_formula : LTL_Y ltl_formula "
        p[0] = YNode(p[2])

    def p_ltl_formula_Z(self, p):
        " ltl_formula : LTL_Z ltl_formula "
        p[0] = ZNode(p[2])

    def p_ltl_formula_H(self, p):
        " ltl_formula : LTL_H ltl_formula "
        p[0] = HNode(p[2])

    def p_ltl_formula_O(self, p):
        " ltl_formula : LTL_O ltl_formula "
        p[0] = ONode(p[2])

    def p_ltl_formula_S(self, p):
        " ltl_formula : ltl_formula LTL_S ltl_formula "
        p[0] = SNode(p[1], p[3])
        
    def p_ltl_formula_T(self, p):
        " ltl_formula : ltl_formula LTL_T ltl_formula "
        p[0] = TNode(p[1], p[3])
        
    def p_ltl_formula_OR(self, p):
        " ltl_formula : ltl_formula OR ltl_formula "
        p[0] = ORNode(p[1], p[3])
        
    def p_ltl_formula_AND(self, p):
        " ltl_formula : ltl_formula AND ltl_formula "
        p[0] = ANDNode(p[1], p[3])
        
    def p_ltl_formula_IMPLIES(self, p):
        " ltl_formula : ltl_formula IMPLIES ltl_formula "
        p[0] = IMPLIESNode(p[1], p[3])
        
    def p_ltl_formula_NOT(self, p):
        " ltl_formula : NOT ltl_formula "
        p[0] = NOTNode(p[2])
        
    def p_ltl_formula_PAREN(self, p):
        " ltl_formula : LPAREN ltl_formula RPAREN "
        p[0] = p[2]

    def p_ltl_formula_EQUALS(self, p):
        " ltl_formula : IDENTIFIER EQUALS IDENTIFIER "
        p[0] = EQUALSNode(p[1], p[3])
        
    def p_ltl_formula_NOT_EQUALS(self, p):
        " ltl_formula : IDENTIFIER NOT_EQUALS IDENTIFIER "
        p[0] = NOT_EQUALSNode(p[1], p[3])
        
    def p_ltl_formula_IDENTIFIER(self, p):
        " ltl_formula : IDENTIFIER "
        p[0] = IDENTIFIERNode(p[1])
        
    def p_ltl_formula_TRUE(self, p):
        " ltl_formula : TRUE "
        p[0] = TRUENode()

    def p_ltl_formula_FALSE(self, p):
        " ltl_formula : FALSE "
        p[0] = FALSENode()
        
    def p_optsemi(self, p):
        """ optsemi : 
                    | SEMI 
                    | COMMA """

    def p_optassert(self, p):
        """ optassert : 
                    | ASSERT """

    def p_error(self, e):
        raise error("Error: %s"%e)

    
def parse_ltl(text, **kwargs):

    parser = LTLParser(**kwargs)
    parser.parse(text)
    
    return parser.assumptions, parser.assertions


class NoWarningsLogger(lex.PlyLogger):
    def warning(self, msg, *args, **kwargs):
        return self


def parse_ltl_quiet(expr):
    import sys
    return parse_ltl(expr, errorlog=NoWarningsLogger(sys.stderr), write_tables=False, debug=False)


if __name__ == "__main__":

    import time, sys

    text = """

        ASSUME G !p & q

        ASSUME ! H p &H p
        ASSUME ! O p
        ASSUME ! Y p
    
        ASSUME !a!=b
        ASSUME !( a=b & c=d )
        ASSUME ! G ( a=b -> X X b!=c )
    
        ASSUME a
        ASSUME ! a
        ASSUME ! ! a
        ASSUME ! ! ! a
        
        ASSUME TRUE
        ASSUME ! TRUE
        
        ASSUME FALSE
        ASSUME ! FALSE
        
        ASSUME a | b
        ASSUME ! ( a | b )
        
        ASSUME a & b
        ASSUME ! ( a & b )
        
        ASSUME a -> b
        ASSUME ! ( a -> b )

        ASSUME G p
        ASSUME ! G p

        ASSUME F p
        ASSUME ! F p

        ASSUME X p
        ASSUME ! X p

        ASSUME a U b
        ASSUME ! ( a U b )

        ASSUME a R b
        ASSUME ! ( a R b )

        ASSUME ! G ( a -> ( b U c ) )
        ASSUME F( ! G ( a -> ( b U c ) ) )
        
        ASSERT G p
        ASSERT ! G p

        ASSERT G( F( (step_4) & O( step_1 & F( step_3 & O(step_2) ) ) ) )

        
    """

    assumptions, assertsions = parse_ltl_quiet(text)

    print("Assumptions:")

    for f in assumptions:
        
        print(f)
        print(nnf_normalize(f))
        print()

    print("Assertions:")

    for f in assertsions:
        
        f = NOTNode(f)
        
        print(f)
        print(nnf_normalize(f))
        print()

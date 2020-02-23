from __future__ import print_function

import ply.lex as lex

class LTLLexerError(Exception):
    pass

class LTLLexer(object):
    
    def __init__(self):
        pass
        
    def build(self, **kwargs):
        self.lexer = lex.lex(object=self, **kwargs)
        
    def input(self, text):
        self.lexer.input(text)
    
    def token(self):
        g = self.lexer.token()
        return g
        
    reserved = {
        "F" : "LTL_F",
        "G" : "LTL_G",
        "X" : "LTL_X",
        
        "U" : "LTL_U",
        "R" : "LTL_R",
        "V" : "LTL_R",
        
        'Z' : 'LTL_Z',
        'Y' : 'LTL_Y',
        'H' : 'LTL_H',
        'O' : 'LTL_O',
        
        "S" : "LTL_S",
        "T" : "LTL_T",

        "TRUE" : "TRUE",
        "FALSE" : "FALSE",
        
        "ASSERT" : "ASSERT",
        "ASSUME" : "ASSUME",        
    }

    tokens =  [
        'IDENTIFIER',
     
        'COMMA',
     
        'LPAREN',
        'RPAREN',
        
        'OR',
        'AND',
        'NOT',
        'IMPLIES',
        
        'EQUALS',
        'NOT_EQUALS',
        
        'SEMI',
    ] + list(set(reserved.values()))

    t_COMMA = r','

    t_LPAREN = r'\('
    t_RPAREN = r'\)'

    t_EQUALS = r'='
    t_NOT_EQUALS = r'!='
    
    t_SEMI = r';'

    t_OR = r'\|'
    t_AND = r'\&'
    t_NOT = r'!'
    t_IMPLIES = r'->'
    
    t_TRUE = r'1'
    t_FALSE = r'0'

    t_ignore = ' \t'
    t_ignore_COMMENT = r'(/\*(.|\n)*\*/)|(//.*)|(\#.*)'
    
    def t_IDENTIFIER(self, t):
        r'[0-9a-zA-Z_.:\[\]\\][0-9a-zA-Z_.:\[\]\-\\]*'
        t.type = LTLLexer.reserved.get(t.value, 'IDENTIFIER')
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        print("LTLLexer: Illegal character '%s'" %t.value[0])
        t.lexer.skip(1)

if __name__ == "__main__":
    
    text = r"""
        p T q
        ASSUME G !p & q V z
        ASSERT G ( !p -> q=y U r!=x ), G F p
        ASSUME G ( p -> q U r )
        ASSERT ! G ( sender.state=wait_for_ack -> Y H sender.state!=wait_for_ack )
    """
    
    clex = LTLLexer()

    clex.build()
    clex.input(text)
    
    while 1:
        tok = clex.token()
        
        if not tok: 
            break

        print(tok)

from .ltl_common import *

from . import fake_pyzz as pyzz

class build_monitor_exception(Exception):
    pass

class build_monitor_visitor(ltl_visitor):
    
    def __init__(self, N, symbols, init):
        super(build_monitor_visitor, self).__init__()

        # variable type counters
        self.zi = 0 # activators
        self.fi = 0 # fairness
        self.npi = 0 # non-pending
        self.xi = 0 # failed
        self.pi = 0 # prev

        self.N = N
        
        self.symbols = symbols
        
        self._prev = {}
        self._somepast = {}
        
        self.nopending = []
        self.failed = []
        self.fairnesses = []

        self.init = init
    
    def prev(self, f):
        
        if f in self._prev:
            return self._prev[f]
        
        ff = self.N.add_Flop()
        ff[0] = f

        self._prev[f] = ff
        
        self.pi += 1

        return ff
    
    def somepast(self, x):
        
        if x in self._somepast:
            return self._somepast[x]
            
        somepast = pyzz.somepast(self.N, x)
        self._somepast[x] = somepast

        return somepast

    def pwaitq(self, p, q):
        ff = self.N.add_Flop()
        next_ff = ff.ite( ~q, p&~q )
        ff[0] = next_ff
        
        return next_ff, ff

    def make_X(self, p, q):
        self.add_failed( ~self.init & self.prev(p) & ~q )
        self.add_nopending( ~p )

    def make_F(self, p, q):
        pending, _ = self.pwaitq(p,q)
        self.add_nopending( ~pending )
        self.add_fairness( ~pending )
        
    def make_G(self, p, q):
        """ add G ( p -> G q ) """
        seen_p, _ = self.somepast(p)
        self.add_failed( seen_p & ~q )
        self.add_nopending( ~seen_p )
    
    def make_U(self, p, q, r):
        pending, _ = self.pwaitq(p, r)
        self.add_failed( pending & ~q )
        self.add_nopending( ~pending )
        self.add_fairness( ~pending )
    
    def make_R(self, p, q, r):
        pending, prev_pending = self.pwaitq(p, q)
        self.add_failed( p&~r | prev_pending&~r )
        self.add_nopending( ~pending )

    def make_O(self, p, q):
        seen_q, _ = self.somepast(q)
        self.add_failed( p & ~seen_q )

    def make_H(self, p, q):
        seen_not_q, _ = self.somepast(~q)
        self.add_failed( p & seen_not_q )

    def make_Y(self, p, q):
        prev_q = self.prev(q)
        self.add_failed( p & ~prev_q )

    def make_Z(self, p, q):
        prev_q = ~self.prev(~q)
        self.add_failed( p & ~prev_q )

    def make_S(self, p, q, r):
        ff = self.N.add_Flop()
        next_ff = ff.ite( r | q, r )
        ff[0] = next_ff
        self.add_failed( p & ~next_ff )

    def make_T(self, p, q, r):
        ff = self.N.add_Flop()
        next_ff = ~r | ff&~q
        ff[0] = next_ff
        self.add_failed( p & next_ff )

    def make_pi(self, n):
        pi = self.N.add_PI()
        self.zi += 1
        return pi
    
    def add_fairness(self, f):
        self.fairnesses.append(f)
        self.fi += 1
        
    def add_nopending(self, f):
        self.nopending.append(f)
        self.npi += 1

    def add_failed(self, f):
        self.failed.append(f)
        self.xi += 1

    def get_symbol(self, id):
        if id in self.symbols:
            return self.symbols[id]
        pi = self.N.add_PI()
        self.symbols[id] = pi
        return pi

    def visit_TRUENode(self, n):
        return self.N.get_True()

    def visit_FALSENode(self, n):
        return ~self.N.get_True()
    
    def visit_IDENTIFIERNode(self, n):
        return self.get_symbol(n.id)

    def visit_NOTNode(self, n):
        return ~self.visit(n.children[0])
    
    def visit_IMPLIESNode(self, n):
        return self.visit(n.children[0]).implies(self.visit(n.children[1]))
    
    def visit_ANDNode(self, n):
        return self.visit(n.children[0]) & self.visit(n.children[1])
    
    def visit_ORNode(self, n):
        return self.visit(n.children[0]) | self.visit(n.children[1])

    def visit_Node(self, n):
        pi = self.make_pi(n)
        make_op = getattr( self, "make_%s"%n.op )
        make_op( pi, *[ self.visit(c) for c in n.children ] )
        return pi


def build_model( vinst, assumptions, assertions ):
    
    kv = build_monitor_visitor(vinst.N, vinst.symbols, vinst.init)
    
    for f in assertions:
        vinst.init_constraints.append( kv.visit( nnf_normalize( NOTNode(f) ) ) )
        
    for f in assumptions:
        vinst.init_constraints.append ( kv.visit( nnf_normalize(f) ) )

    vinst.constraints += [ ~f for f in kv.failed ]
    vinst.pos.append( pyzz.conjunction(vinst.N, kv.nopending) )
    vinst.fairnesses += kv.fairnesses

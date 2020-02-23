from pyaig import *


class netlist(object):

    def __init__(self, aig=None):
        self.aig = aig or AIG()

    def add_Flop(self):
        return aigexpr.create_latch(self.aig)

    def add_PI(self):
        return aigexpr.create_pi(self.aig)

    def get_True(self):
        return aigexpr.const(self.aig, 1)

    def get_False(self):
        return aigexpr.const(self.aig, 0)

    def write_aiger(self, fname):
        write_aiger(self.aig, fname)

    def po_symbols(self):
        return { po_name:aigexpr(self.aig, po_fanin) for _, po_fanin, po_name in self.aig.iter_po_names() }

    @staticmethod
    def read_aiger(ff):
        return netlist(read_aiger(ff))


def conjunction(N, fs):
    return aigexpr(N.aig, N.aig.balanced_conjunction([f.get_f() for f in fs]))


def somepast(N, x):
    ff = N.add_Flop()
    next_ff = ff | x
    ff[0] = next_ff
    return next_ff, ff


class verification_instance(object):

    def __init__(self, N=None, symbols=None, init_constraints=None, constraints=None, pos=None, fairnesses=None, init = None):

        self.N = N or netlist()
        self.symbols = symbols or N.po_symbols()
        self._init = init
        self.init_constraints = init_constraints or []
        self.constraints = constraints or []
        self.pos = pos or []
        self.fairnesses = fairnesses or []
        
    @property
    def init(self):
        return self.get_init()

    def get_init(self):
        
        if not self._init:
            
            ff = self.N.add_Flop()
            ff[0] = self.N.get_True()
            self._init = ~ff
    
            self.symbols['_IS_INIT'] = self._init
            
        return self._init

import sys

from . import fake_pyzz as pyzz
from . import ltl_parser
from . import build_monitor

from pyaig import *


def build_base_aiger( vinst ):

    aig = vinst.N.aig
    for n, w in vinst.symbols.iteritems():
        if aig.name_has_po(n):
            continue
        aig.create_po( w.get_f(), n )

    is_init = vinst.get_init().get_f()
    
    for c in vinst.constraints:
        aig.create_po( c.get_f(), po_type=AIG.CONSTRAINT )
    
    for ic in vinst.init_constraints:
        aig.create_po( aig.create_implies( is_init, ic.get_f() ), po_type=AIG.CONSTRAINT )

    return aig


def build_safety_aiger( vinst ):
    
    aig = build_base_aiger(vinst)
    
    for po in vinst.pos:
        aig.create_po( po.get_f(), po_type=AIG.BAD_STATES )


def build_liveness_aiger( vinst ):
    
    aig = build_base_aiger(vinst)

    aig.create_justice([ aig.create_po(fc.get_f(), po_type=AIG.JUSTICE ) for fc in vinst.fairnesses ])
    

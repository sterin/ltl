import pyaig

from . import fake_pyzz as pyzz
from . import ltl_parser
from . import build_monitor
from . import build_aiger_1_9


def compile_ltl(aig, ltl_text, clean_pos=False):
    
    assumptions, assertions = ltl_parser.parse_ltl(ltl_text)

    def make_model():
        N = pyzz.netlist(pyaig.unflatten_aiger(pyaig.flatten_aiger(aig)))
        vinst = pyzz.verification_instance(N=N)
        build_monitor.build_model( vinst, assumptions, assertions )
        return vinst

    def clean(aig):
        if not clean_pos:
            return aig
        pos = [ po_id for po_id, _, po_type in aig.get_pos() if po_type != pyaig.AIG.OUTPUT ]
        return aig.clean(pos=pos)

    vinst_safe = make_model()
    build_aiger_1_9.build_safety_aiger(vinst_safe)

    vinst_live = make_model()
    build_aiger_1_9.build_liveness_aiger(vinst_live)

    return clean(vinst_safe.N.aig), clean(vinst_live.N.aig)

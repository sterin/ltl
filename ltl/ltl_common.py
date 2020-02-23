import inspect
from contextlib import contextmanager


class Node(object):
    def __init__(self, *args):
        self.children = list(args)
        self.op = self.__class__.__name__[:-4]
       
    def __str__(self):
        return write_formula(self)


class NoaryNode(Node): pass
class UnaryNode(Node): pass
class BinaryNode(Node): pass
        
class GNode(UnaryNode): pass
class FNode(UnaryNode): pass
class XNode(UnaryNode): pass

class UNode(BinaryNode): pass
class RNode(BinaryNode): pass

class ZNode(UnaryNode): pass
class YNode(UnaryNode): pass
class HNode(UnaryNode): pass
class ONode(UnaryNode): pass

class SNode(BinaryNode): pass
class TNode(BinaryNode): pass

class IMPLIESNode(BinaryNode): pass
class ANDNode(BinaryNode): pass
class ORNode(BinaryNode): pass
class NOTNode(UnaryNode): pass

class TRUENode(NoaryNode): pass
class FALSENode(NoaryNode): pass

class EQUALSNode(NoaryNode):
    def __init__(self, id, val):
        super(EQUALSNode, self).__init__()
        self.id = id
        self.val = val

class NOT_EQUALSNode(NoaryNode):
    def __init__(self, id, val):
        super(NOT_EQUALSNode, self).__init__()
        self.id = id
        self.val = val

class IDENTIFIERNode(NoaryNode):
    def __init__(self, id):
        super(IDENTIFIERNode, self).__init__()
        self.id = id

class ltl_visitor(object):

    def visit(self, node):
        for c in inspect.getmro(node.__class__):
            if c.__name__.endswith('Node'):
                method = 'visit_' + c.__name__
                visitor = getattr(self, method, None)
                if visitor:
                    return visitor(node)
        return self.generic_visit(node)
        
    def generic_visit(self, node):
        for c in node.children:
            self.visit(c)


class write_visitor(ltl_visitor):
    
    def visit_UnaryNode(self, n):
        return "%s ( %s ) "%( n.op, self.visit(n.children[0]) )

    def visit_BinaryNode(self, n):
        return "( %s %s %s )"%( self.visit(n.children[0]), n.op, self.visit(n.children[1]) )
        
    def visit_NoaryNode(self, n):
        return "%s"%n.op

    def visit_IDENTIFIERNode(self, n):
        return "%s"%n.id

    def visit_EQUALSNode(self, n):
        return "%s=%s"%(n.id, n.val)

    def visit_NOT_EQUALSNode(self, n):
        return "%s!=%s"%(n.id, n.val)


class nnf_visitor(ltl_visitor):
    
    op_map = {
        FNode : GNode,
        GNode : FNode,
        XNode : XNode,
        
        UNode : RNode,
        RNode : UNode,
        
        YNode : ZNode,
        ZNode : YNode,
        HNode : ONode,
        ONode : HNode,
        
        SNode : TNode,
        TNode : SNode,
        
        ANDNode : ORNode,
        ORNode : ANDNode,
    }    
    
    def __init__(self):
        super(nnf_visitor, self).__init__()
        self.negate = False
    
    def visit_children(self, n):
        return ( self.visit(c) for c in n.children )
            
    @contextmanager
    def negation(self):
        self.negate = not self.negate
        yield
        self.negate = not self.negate
    
    def visit_NOTNode(self, n):
        with self.negation():
            return self.visit(n.children[0])

    def visit_TRUENode(self, n):
        if self.negate:
            return FALSENode()
        else:
            return n

    def visit_FALSENode(self, n):
        if self.negate:
            return TRUENode()
        else:
            return n
    
    def visit_IDENTIFIERNode(self, n):
        if self.negate:
            return NOTNode(n)
        else:
            return n
    
    def visit_Node(self, n):
        if self.negate:
            T = nnf_visitor.op_map[type(n)]
        else:
            T = type(n)
        return T( *self.visit_children(n) )
    
    def visit_IMPLIESNode(self, n):
        with self.negation():
            c0 = self.visit( n.children[0] )
        c1 = self.visit( n.children[1] )
        
        if self.negate:
            return ANDNode( c0, c1 )
        else:
            return ORNode( c0, c1 )
    
    def visit_EQUALSNode(self, n):
        if self.negate:
            return NOT_EQUALSNode( n.id, n.val )
        else:
            return EQUALSNode( n.id, n.val )

    def visit_NOT_EQUALSNode(self, n):
        if self.negate:
            return EQUALSNode( n.id, n.val )
        else:
            return NOT_EQUALSNode( n.id, n.val )


_nnfv = nnf_visitor()


def nnf_normalize( n ):
    return _nnfv.visit(n)


def write_formula( n ):
    return write_visitor().visit( n )


def print_properties( assumptions, assertions ):
    for a in assertions:
        print(a)
    for a in assumptions:
        print(NOTNode(a))

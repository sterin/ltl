import pyaig
import ltl

import click


def make_delay(n):
    aig = pyaig.AIG()
    ff = aig.create_pi("X")
    for i in xrange(n):
        aig.create_po(ff, name='delay_%02d'%i)
        ff = aig.create_latch(next=ff)
    aig.create_po(ff, name='delay_%d'%(i+1))
    return aig


@click.group()
def cli():
    pass


@cli.command()
@click.argument('N', type=int)
@click.argument('output', type=click.File("wb"))
def delay(n, output):

    pyaig.write_aiger(make_delay(n), output)    


@cli.command()
@click.argument('N', type=int)
@click.argument('fname', type=click.Path(exists=True, dir_okay=False))
def bmc(n, fname):
    
    import pyzz

    N = pyzz.netlist.read_aiger(fname)

    names = N.names
    symbols = {names[w][0]:w[0] for w in N.get_POs() if w in names}

    print(pyzz.bmc.safety_bmc(N, n, symbols=symbols))


@cli.command()
def bmc_delay():

    aig = make_delay(10)
    safe_aig, live_aig = ltl.compile_ltl(aig, "ASSERT G X X !delay_10")

    import pyzz
    N = pyzz.netlist.unflatten_aiger( pyaig.flatten_aiger(safe_aig) )

    names = N.names
    symbols = {names[w][0]:w[0] for w in N.get_POs() if w in names}

    pyzz.bmc.safety_bmc(N, 50, symbols=symbols)


if __name__=='__main__':
    cli()
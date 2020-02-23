import click

import pyaig

from . import fake_pyzz as pyzz
from . import compile_ltl


@click.command()
@click.option('--in-aiger', type=click.Path(dir_okay=False, exists=True))
@click.option('--prop')
@click.option('--prop-file', type=click.File(mode='r'))
@click.option('--clean-pos/--no-clean-pos', default=False)
@click.argument('safety-aiger', type=click.Path(dir_okay=False))
@click.argument('liveness-aiger', type=click.Path(dir_okay=False))
def main(in_aiger, prop, prop_file, clean_pos, safety_aiger, liveness_aiger):

    if not prop and not prop_file:
        raise click.UsageError('provide one of --prop or --prop_file')        

    if prop and prop_file:
        raise click.UsageError("--prop and --prop_file are mutually exclusive")

    if prop:
        prop = 'ASSERT ' + prop
    else:
        prop = prop_file.read()

    if in_aiger:
        aig = pyaig.read_aiger(in_aiger)
    else:
        aig = pyaig.AIG()

    safe_aig, live_aig = compile_ltl(aig, prop, clean_pos)

    pyaig.write_aiger(safe_aig, safety_aiger)
    pyaig.write_aiger(live_aig, liveness_aiger)

    return 0


if __name__ == "__main__":
    main()

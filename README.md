# PyLTL: 

Generate monitor circuits for LTL formulas using the the algorithm described in the paper:

Koen Claessen, Niklas Eén, Baruch Sterin: A circuit approach to LTL model checking. FMCAD 2013

## Installation

Install using `pip`:

```shell
pip install .
```

## Example

The subdirectory `example/` contains a simple AIG circuit and an LTL property.

`delay_10.aig` is a simple circuit with a single primary input named `PI`. This input is passed through 10 latches that delay it for 1 to 10 cycles. The latches are initialized to zero. The circuit has 11 primary outputs named `delay_XX`, where `delay_00` is connected to the primary input, `delay_01` is connect to the latch that delays the input for 1 cycle, etc.

`propertyl.ltl` contains the formula 

```
ASSUME !delay_00
ASSUME X !delay_00
ASSERT G X X X !delay_10
```.

Run the following command to generate the verification monitors:

```shell
python -m ltl \
    --prop-file property.ltl \
    --in-aiger delay_10.aig \
    \
    delay_safe.aig \
    delay_live.aig
```

The output is two AIG files. The file `delay_safe.aig` contains the safety part of the property, and `delay_live.aig` contains the entire property, including liveness parts. See the paper for details about the differences.

One possible counter example for the generated safety AIG could be:

```
delay_00: 0 0 1 0 0 0 0 0 0 0 0 0 0
delay_01: 0 0 0 1 0 0 0 0 0 0 0 0 0
delay_02: 0 0 0 0 1 0 0 0 0 0 0 0 0
delay_03: 0 0 0 0 0 1 0 0 0 0 0 0 0
delay_04: 0 0 0 0 0 0 1 0 0 0 0 0 0
delay_05: 0 0 0 0 0 0 0 1 0 0 0 0 0
delay_06: 0 0 0 0 0 0 0 0 1 0 0 0 0
delay_07: 0 0 0 0 0 0 0 0 0 1 0 0 0
delay_08: 0 0 0 0 0 0 0 0 0 0 1 0 0
delay_09: 0 0 0 0 0 0 0 0 0 0 0 1 0
delay_10: 0 0 0 0 0 0 0 0 0 0 0 0 1
```

### Note:

The generated AIG is in [AIGER](http://fmv.jku.at/aiger/) 1.9.4 format, which means that there are multiple types of POs (Primary Outputs): regular outputs, bad-state outputs, constraints, and fairness constraints. The generated AIG contains all the POs of the input AIGER file and the names used in the LTL formulae. 

Unfortunately, [ABC](https://people.eecs.berkeley.edu/~alanmi/abc/) treats all non-constraint POs as bad-states. Regular POs should either be stripped manually, or the flag `--clean-pos` can be used to generate AIGER files with only bad-state/constraint POs.

```shell
python -m ltl \
    --prop property.ltl \
    --in-aiger delay_10.aig \
    \
    --clean-pos \
    \
    delay_safe.aig \
    delay_live.aig
```

### Using ABC to check the safety part of the property

It is then possible to use ABC to check the safety part of the property:

```
$ abc
UC Berkeley, ABC 1.01 (compiled Sep 15 2019 17:22:26)
abc 01> read delay_safe.aig 
Warning: The last 7 outputs are interpreted as constraints.
abc 02> fold
abc 03> bmc2 -v
Running "bmc2". AIG:  PI/PO/Reg = 6/1/17.  Node =     27. Lev =    10.
Params: FramesMax = 0. NodesDelta = 2000. ConfMaxOne = 0. ConfMaxAll = 0.
   0 : F =   85. O =   0.  And =    1427. Var =    1105. Conf =      0.    0 MB     0.02 sec
Output 0 of miter "delay_safe" was asserted in frame 12. Time =     0.02 sec
abc 03> 
```

Note that the `fold` command is required to instruct ABC to fold the constraints into the properties.

## Interfacing between the AIG and the monitor

If no AIG file is provided (no `--in-aiger` flag), the tool creates PIs (Primary Inputs) for each symbol in the property. 

If an AIG is file is provided (using the `--in-aiger` flag), the tool looks for for POs with the names in the property and uses them. If no PO exists with a name in the property, a fresh PI is created.


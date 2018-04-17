#!/usr/bin/env python

from collections import namedtuple
from itertools import chain
from math import log2, exp

import click
from dd.cudd import BDD
from toposort import toposort
from parsimonious import Grammar, NodeVisitor

AAG_GRAMMAR = Grammar(u'''
aag = header ios latches ios gates symbols comments?
header = "aag" _ id _ id _ id _ id _ id EOL

ios = io*
io = id EOL

latches = latch*
latch = id _ id EOL

gates = gate*
gate = id _ id _ id EOL

symbols = symbol*
symbol =  symbol_kind id _ symbol_name EOL
symbol_kind = ("i" / "o" / "l")
symbol_name = (~r".")+

comments = "c" EOL comment+
comment = (~r".")+ EOL

_ = ~r"\s"+
id = ~r"\d"+
EOL = "\\n"
''')


Header = namedtuple('Header', ['max_var_index', 'num_inputs',
                               'num_latches', 'num_outputs',
                               'num_ands'])
Symbol = namedtuple('Symbol', ['kind', 'index', 'name'])
AAG = namedtuple('AAG', ['header', 'inputs', 'outputs', 
                         'latches', 'gates', 'symbols', 'comments'])


class AAGVisitor(NodeVisitor):
    def generic_visit(self, _, children):
        return children

    def visit_id(self, node, children):
        return int(node.text)

    def visit_header(self, _, children):
        return Header(*children[2::2])

    def visit_io(self, _, children):
        return children[::2][0]
    
    def visit_latch(self, _, children):
        return children[::2]

    def visit_gate(self, _, children):
        return children[::2]
    
    def visit_aag(self, _, children):
        header, ios1, latches, ios2, gates, symbols, comments  = children
        ios = ios1 + ios2
        assert len(ios) == header.num_inputs + header.num_outputs
        inputs, outputs = ios[:header.num_inputs], ios[header.num_inputs:]
        return AAG(header, inputs, outputs, latches, gates, symbols, comments)

    def visit_symbol(self, node, children):
        return Symbol(children[0], children[1], children[3])

    def visit_symbol_kind(self, node, _):
        return node.text

    def visit_symbol_name(self, node, _):
        return node.text

    def visit_comments(self, node, _):
        return node.text


def parse(aag_str: str, rule: str = "aag"):
    return AAGVisitor().visit(AAG_GRAMMAR[rule].parse(aag_str))


def to_bdd(aag: AAG):
    assert len(aag.outputs) == 1
    assert len(aag.latches) == 0

    gate_deps = {a & -2: {b & -2, c & -2} for a,b,c in aag.gates}
    gate_lookup = {a & -2: (a, b, c) for a,b,c in aag.gates}
    eval_order = list(toposort(gate_deps))

    assert eval_order[0] <= set(aag.inputs)

    bdd = BDD()
    bdd.declare(*(f'x{i}' for i in aag.inputs))
    gate_nodes = {i: bdd.add_expr(f'x{i}') for i in aag.inputs}
    for gate in chain(*eval_order[1:]):
        out, i1, i2 = gate_lookup[gate]
        f1 = ~gate_nodes[i1 & -2] if i1 & 1 else gate_nodes[i1 & -2]
        f2 = ~gate_nodes[i2 & -2] if i2 & 1 else gate_nodes[i2 & -2]
        gate_nodes[out] = f1 & f2

    out = aag.outputs[0]
    return ~gate_nodes[out & -2] if out & 1 else gate_nodes[out & -2]


def parse_and_count(aag_str):
    aag = parse(aag_str)
    f = to_bdd(aag)

    n = aag.header.num_inputs
    return exp(log2(f.count(n)) - n)


@click.command()
@click.argument('path', type=click.Path(exists=True))
def main(path):
    with open(path, 'r') as f:
        print(parse_and_count(''.join(f.readlines())))
    

if __name__ == '__main__':
    main()

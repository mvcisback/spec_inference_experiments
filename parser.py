from collections import namedtuple

from parsimonious import Grammar, NodeVisitor

# aig = header inputs latches outputs gates symbols comments
# TODO: need to enable parsing false and true circuits

AAG_GRAMMAR = Grammar(u'''
aag = header ios latches ios gates symbols comments
header = "aag" _ id _ id _ id _ id _ id EOL

ios = io*
io = id EOL

latches = latch*
latch = id _ id EOL

gates = gate*
gate = id _ id _ id EOL

symbols = symbol*
symbol =  symbol_kind id _ (EOL / ~".")+
symbol_kind = ("i" / "o" / "l")

comments = comment*
comment = "c" ~r"."+

_ = ~r"\s"+
id = ~r"\d"+
EOL = "\\n"
''')


Header = namedtuple('Header', ['max_var_index', 'num_inputs',
                               'num_latches', 'num_outputs',
                               'num_ands'])
Symbol = namedtuple('Symbol', ['kind', 'name'])
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

    def visit_symbol(self, _, children):
        return Symbol(children[0], children[1])

    def visit_symbol_kind(self, node, _):
        return node.text


def parse(aag_str: str, rule: str = "aag"):
    return AAGVisitor().visit(AAG_GRAMMAR[rule].parse(aag_str))

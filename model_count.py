#!/usr/bin/env python
import click
import re
from pathlib import Path
from tempfile import mkdtemp
from subprocess import check_call, check_output

YOSYS_CMDS = """
read_verilog {0}
synth -top phi
write_blif {1}
"""

ABC_CMDS = """
read_blif {0}
strash
write_aiger -s {1}
"""

def get_map(lines):
    def parse_line(line):
        parse = re.match('^c\s(\d+)\s->\s(\d+).*', line)
        if parse is None:
            return None
        return parse.groups()

    return dict(filter(None, map(parse_line, lines)))
        

def get_n_inputs(lines):
    count = 0
    for l in lines:
        if l.startswith('c'):
            break
        if l.startswith('i'):
            count += 1
    return count


@click.command()
@click.argument('input_path', type=click.Path(exists=True))
def main(input_path):
    input_path = Path(input_path)

    root = Path(mkdtemp(prefix="model_count"))
    blif_path = root / f"{input_path.stem}.blif"
    aig_path = root / f"{input_path.stem}.aig"
    aag_path = root / f"{input_path.stem}.aag"
    cnf_path = root / f"{input_path.stem}.cnf"

    with (root / "yosys_cmd").open('w') as yosys_cmd_file:
        yosys_cmd_file.write(YOSYS_CMDS.format(input_path, blif_path))

    with (root / "abc_cmd").open('w') as abc_cmd_file:
        abc_cmd_file.write(ABC_CMDS.format(blif_path, aig_path))

    # TODO: Capture output in log file
    check_call(f"yosys -s {root / 'yosys_cmd'}",shell=True)
    check_call(f"abc -F {root / 'abc_cmd'}",shell=True)
    check_call(f"aigtoaig {aig_path} {aag_path}", shell=True)
    check_call(f"aigtocnf -m {aag_path} {cnf_path}", shell=True)

    with aag_path.open() as f:
        n_inputs = get_n_inputs(f.readlines())


    # The inputs are the first variables in the cnf.
    # Unused wires are dropped, so we need to first
    # build a map between aiger wires and cnf variables.
    with cnf_path.open() as f:
        var_mapping = get_map(f.readlines())
    
    # We need to count over all inputs that appear in cnf.
    counting_vars = list(filter(None, (var_mapping.get(str(2*i)) for i in range(1, n_inputs+1))))

    # Write special comment to indicate the counting variables
    with cnf_path.open('a') as f:
        f.write(f"c ind {' '.join(counting_vars)} 0")
    print(f"num counting vars: {len(counting_vars)}")

    output = check_output(f'scalmc {cnf_path}; exit 0;', shell=True)
    out = str(output.splitlines()[-1])
    print(out)
    match = re.match(".*Number of solutions.....(\d+)...(\d+).(\d+).*", out)

    if match is None:
        models = 0
    else:
        a,b,c = match.groups()
    
        models = int(a) * int(b)**int(c)

    print(models)
    print(models / (2**len(counting_vars)))


if __name__ == '__main__':
    main()


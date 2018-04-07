#!/usr/bin/env python
import click
from pathlib import Path

TEMPLATE = """
module step(input [0:2] x, input a, output [0:2] y);
   assign y = a == 1 ? x + 1 : x - 1;
endmodule

module steps
  (
   input        a0,
   input        a1,
   input [0:2]  x0,

   output [0:2] x1,
   output [0:2] x2,
   );

   step step0(.x(x0), .a(a0), .y(x1));
   step step1(.x(x1), .a(a1), .y(x2));
endmodule

module phi(
   input       a0,
   input       a1,
   input [0:2] x0,
   output      sat     
   );
   wire [0:2]  x1;
   wire [0:2]  x2;

   steps sample(.a0(a0), .a1(a1), .x0(x0) ,.x1(x1), .x2(x2));
   assign sat = {spec};
endmodule
"""

SPECS = [
    'x0 == 6 & x1 == 6 & x2 == 6',
    'x0 < 6 & x1 < 6 & x2 < 6',
    'x0 < 1 | x1 < 1 | x2 < 1',
    'x0 < 1 | x1 < 2',
    'x0 < 1',
    '1'
]


@click.command()
@click.argument('output', type=click.Path())
def main(output):
    output = Path(output)
    output.mkdir(exist_ok=True)
    
    for i, spec in  enumerate(SPECS):
        with (output / f"query_{i}.v").open('w') as f:
            f.write(TEMPLATE.format(spec=spec))
    

if __name__ == "__main__":
    main()

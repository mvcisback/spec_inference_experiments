#!/usr/bin/env python
import click
from pathlib import Path

TEMPLATE = """
module step(input [0:{k}] x, input a, output [0:{k}] y);
   assign y = a == 1 ? x + 1 : x - 1;
endmodule

module steps(
   input [0:{k}] ax,
   input [0:{k}] ay,
   input [0:{k}] x0,
   input [0:{k}] y0,
   output [0:{unrolled_k}]  posX,
   output [0:{unrolled_k}]  posY,
   );
   assign posX [0:{k}] = x0;
   assign posY [0:{k}] = y0;

   genvar      i;
   generate
      for(i=0; i<= {tau};i++)
        begin : ripple
           step sampleX(.a(ax[i]),
                        .x(posX[3*i:3*(i+1)-1]),
                        .y(posX[3*(i+1):3*(i+2)-1]));
           step sampleY(.a(ay[i]),
                        .x(posY[3*i:3*(i+1)-1]),
                        .y(posY[3*(i+1):3*(i+2)-1]));
        end
   endgenerate
endmodule


module phi(
   input [0:{k}] x0,
   input [0:{k}] y0,
   input [0:{tau}] ax,
   input [0:{tau}] ay,
   output      sat     
   );
   wire [0:{unrolled_k}]  posX;
   wire [0:{unrolled_k}]  posY;
   
   steps samples(.ax(ax), .ay(ay), .x0(x0), .y0(y0), .posX(posX), .posY(posY));

   assign sat = {spec};
endmodule
"""

def gen_template(tau, k, spec):
    return TEMPLATE.format(spec=gen_spec(tau, k, spec),
                           tau=tau-1, 
                           k=k-1, max_val=2**k-1, 
                           unrolled_k=(tau+1)*k-1)


def gen_spec(tau, k, spec):
    for i in range(tau+1):
        spec = spec.replace(f"x{i}", f"posX[{i*k}:{(i+1)*k-1}]")
        spec = spec.replace(f"y{i}", f"posY[{i*k}:{(i+1)*k-1}]")
    return spec
    

SPECS = [
    'x0 == 6 & x1 == 6 & x2 == 6',
    'x0 < 6 & x1 < 6 & x2 < 6',
    'x0 < 1 | x1 < 1 | x2 < 1',
    'x0 < 1 | x1 < 2',
    '(x0 < 1 | x1 < 2) & y2 > 3 & y1 > 3 & y0 > 3 & x1 > 0',
    'x0 < 1',
    '1'
]


@click.command()
@click.argument('output', type=click.Path())
@click.option('--horizon', type=int, default=2)
@click.option('--log-grid-size', type=int, default=3)
def main(output, horizon, log_grid_size):
    output = Path(output)
    output.mkdir(exist_ok=True)
    
    for i, spec in  enumerate(SPECS):
        with (output / f"query_{i}.v").open('w') as f:
            f.write(gen_template(horizon, log_grid_size, spec))
    

if __name__ == "__main__":
    main()

module step1d(input [0:2] x, input [0:1] a, output [0:2] x2);
   assign x2 = a == 2 ? x : (a == 1 ? x + 1 : x - 1);
endmodule

module actionX(input [0:2] a, output [0:1] aX);
   assign aX = (a == 0 | a == 4) ? 2 :
               ((a > 0 & a < 4) ? 1 : 0);
endmodule

module actionY(input [0:2] a, output [0:1] aY);
   assign aY = (a == 2 | a == 6) ? 2 :
               ((a > 6 | a < 2) ? 1 : 0);
endmodule

module step2d(input [0:2] x,
              input [0:2]  y,
              input [0:2]  a,
              output [0:2] x2,
              output [0:2] y2);
   wire [0:1]              aX;
   wire [0:1]              aY;

   actionX tempX(.a(a), .aX(aX));
   actionY tempY(.a(a), .aY(aY));
   
   step1d step1dX(.x(x), .x2(x2), .a(aX));
   step1d step1dY(.x(y), .x2(y2), .a(aY));
endmodule

module blue(input [0:2] x, input [0:2] y, output out);
   assign out = (x >= 3 & x <= 4) & (y >= 2 & y <= 5);
endmodule

module yellow(input [0:2] x, input [0:2] y, output out);
   assign out = (x == 0 | x == 7) & (y == 0 | y == 7);
endmodule

module brown(input [0:2] x, input [0:2] y, output out);
   assign out = (x >= 2 | x <= 5) & (y == 0 | y == 7);
endmodule

module red(input [0:2] x, input [0:2] y, output out);
   assign out = ((x == 1 | x == 6) & (y <= 1 | y == 4 | y == 5))
              | ((x == 0 | x == 7) & (y == 1 | y == 4 | y == 5));
endmodule

/*
module steps(
   input [0:1] ax,
   input [0:1] ay,
   input [0:2] x0,
   input [0:2] y0,
   output [0:8]  posX,
   output [0:8]  posY,
   );
   assign posX [0:2] = x0;
   assign posY [0:2] = y0;

   genvar      i;
   generate
      for(i=0; i<= 1;i++)
        begin : ripple
           step2d sample(.aX(ax[i]),
                         .x(posX[3*i:3*(i+1)-1]),
                         .x2(posX[3*(i+1):3*(i+2)-1]),
                         .aY(ay[i]),
                         .y(posY[3*i:3*(i+1)-1]),
                         .y2(posY[3*(i+1):3*(i+2)-1]));
        end
   endgenerate
endmodule
*/

module step1d(input [0:2] x, input [0:1] a, output [0:2] x2);
   assign x2 = (a == 2 | (x == 0 & a == 0) | (x == 7 & a == 1)) ? x : (a == 1 ? x + 1 : x - 1);
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

module sense_blue(input [0:2] x, input [0:2] y, output out);
   assign out = (x >= 3 & x <= 4) & (y >= 2 & y <= 5);
endmodule

module sense_yellow(input [0:2] x, input [0:2] y, output out);
   assign out = (x == 0 | x == 7) & (y == 0 | y == 7);
endmodule

module sense_brown(input [0:2] x, input [0:2] y, output out);
   assign out = (x >= 2 & x <= 5) & (y == 0 | y == 7);
endmodule

module sense_red(input [0:2] x, input [0:2] y, output out);
   assign out = ((x == 1 | x == 6) & (y <= 1 | y == 4 | y == 5))
              | ((x == 0 | x == 7) & (y == 1 | y == 4 | y == 5));
endmodule

module sense(input [0:2] x, input [0:2] y, output [0:3] out);
   sense_blue sb(.x(x), .y(y), .out(out[3]));
   sense_yellow sy(.x(x), .y(y), .out(out[2]));
   sense_brown sbr(.x(x), .y(y), .out(out[1]));
   sense_red sr(.x(x), .y(y), .out(out[0]));
endmodule

// Horizon: 48 steps. 48*3 - 1 = 143
// Horizon: 18 steps. 18*3 - 1 = 53
// Horizon: 4 steps. 4*3 - 1 = 11
module steps(
             input [0:2]   x0,
             input [0:2]   y0,
             input [0:11] a,
             output [0:3] blues,
             output [0:3] reds,
             output [0:3] yellows,
             output [0:3] browns
             );
   wire [0:11]            posX;
   wire [0:11]            posY;

   assign posX [0:2] = x0;
   assign posY [0:2] = y0;

   sense_blue blue0(.x(x0), .y(y0), .out(blues[0]));
   sense_yellow yellow0(.x(x0), .y(y0), .out(yellows[0]));
   sense_red red0(.x(x0), .y(y0), .out(reds[0]));
   sense_brown brown0(.x(x0), .y(y0), .out(browns[0]));

   genvar      i;
   generate
      for(i=0; i < 3; i++)
        begin : ripple
           step2d sample(.a(a[3*i:3*(i+1)-1]),
                         .x(posX[3*i:3*(i+1)-1]),
                         .x2(posX[3*(i+1):3*(i+2)-1]),
                         .y(posY[3*i:3*(i+1)-1]),
                         .y2(posY[3*(i+1):3*(i+2)-1]));

           sense_blue bluei(.x(posX[3*(i+1):3*(i+2)-1]),
                            .y(posY[3*(i+1):3*(i+2)-1]),
                            .out(blues[i+1]));

           sense_yellow yellowi(.x(posX[3*(i+1):3*(i+2)-1]),
                                .y(posY[3*(i+1):3*(i+2)-1]),
                                .out(yellows[i+1]));

           sense_red redi(.x(posX[3*(i+1):3*(i+2)-1]),
                          .y(posY[3*(i+1):3*(i+2)-1]),
                          .out(reds[i+1]));

           sense_brown browni(.x(posX[3*(i+1):3*(i+2)-1]),
                              .y(posY[3*(i+1):3*(i+2)-1]),
                              .out(browns[i+1]));
        end
   endgenerate
endmodule   

module phi(input [0:11] a,
           output out);
   wire [0:3]           blues;
   wire [0:3]           reds;
   wire [0:3]           yellows;
   wire [0:3]           browns;
   
   steps sample(.x0(3), .y0(0), .a(a), .blues(blues), .reds(reds),
                .yellows(yellows), .browns(browns));
   assign out = !(|reds);
endmodule

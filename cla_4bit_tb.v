`timescale 1ns/1ps
module cla_4bit_tb;
    reg [3:0] a, b;
    reg cin;
    wire [3:0] sum;
    wire cout;
    integer infile;
    reg [7:0] ain, bin, cin_in;
    integer r;

    cla_4bit uut(
        .a(a),
        .b(b),
        .cin(cin),
        .sum(sum),
        .cout(cout)
    );

    initial begin
        $dumpfile("cla_4bit.vcd");
        $dumpvars(0, cla_4bit_tb);
        infile = $fopen("input.txt", "r");
        if (infile == 0) begin
            $display("file error");
            $finish;
        end
        a = 0; b = 0; cin = 0;
        while ($fscanf(infile, "%d %d %d\n", ain, bin, cin_in) == 3) begin
            a = ain[3:0];
            b = bin[3:0];
            cin = cin_in[0];
            #5;
            $display("result a=%d b=%d cin=%d sum=%d cout=%d", a, b, cin, sum, cout);
        end
        $fclose(infile);
        #10;
        $finish;
    end
endmodule
ldi $r0 0x0040          #$v0
ldi $r1 0x0101          #$v1 
sl $r1 7
srl $r1 3
ldi $r2 0x000f          #$v2
ldi $r3 0x00f0          #$v3
ldi $r4 0x0000          #$t0
ldi $r5 0x0010          #$a0
ldi $r6 0x0005          #$a1

LO: move $r6 $r6        
brnz EXIT                                       # while $a1 > 0

        subi $r6 1                              # $a1 -= 1
        ldr $r4 $r5                             # $t0 = Mem[$a0]

        ldi $r7 0x0010
        sl $r7 4
        subr $r7 $r4 $r7
        brnz ELSE                               # if ($t0 > 0100hex)
                        sra $r0 3              # $v0 /= 8
                        or $r1 $r1 $r0          # $v3 |= $v2
                        ldi $r7 0x00ff
                        sl $r7 8
                        str $r5 $r7             # Mem[$a0] = FF00hex;
                        jmp FI
                ELSE: 
                        sl $r2 2
                        xor $r3 $r3 $r2
                        sti $r5 0x00ff
        FI: addi $r5 2
        jmp LO

EXIT: hlt
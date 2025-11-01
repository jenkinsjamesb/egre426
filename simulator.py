'''
simulator.py

BRISC simulator code

James Jenkins 2025
'''

from brisc_logging import log
from common import int_to_bits

from bitarray import bitarray
from bitarray.util import ba2int

class processor:

        def __init__(self):
                # Memory files
                self.data_memory = bitarray(256 * 8)
                self.text_memory = bitarray(256 * 8)

                # GP registers R0-R7
                self.register_file = [
                        bitarray(16),
                        bitarray(16),
                        bitarray(16),
                        bitarray(16),
                        bitarray(16),
                        bitarray(16),
                        bitarray(16),
                        bitarray(16)
                ]

                # Internal registers
                self.pc = bitarray(4)
                self.ir = bitarray(16)
                self.nzp = bitarray(3)
                
                # Internal signals
                self.opcode = bitarray(4)
                self.rd = bitarray(16)
                self.rs = bitarray(16)
                self.rt = bitarray(16)
                self.func = bitarray(3)
                self.imm = bitarray(9)
                self.jmp = bitarray(12)
                self.result = bitarray(16)

                # Other vars
                self.run = True
                self.cycle = 0

        def alu(self, op, a, b):
                '''ALU functionality.'''
                result = bitarray(16)

                # add
                if op in (bitarray("0001000"), bitarray("0011")):
                        result = ba_math("+", a, b, a_signed=True, b_signed=True)
                # sub
                if op in (bitarray("0001001"), bitarray("0100")):
                        result = ba_math("-", a, b, a_signed=True, b_signed=True)
                # mult
                if op in (bitarray("0001010"), bitarray("0101")):
                        result = ba_math("*", a, b, a_signed=True, b_signed=True)
                # div
                if op in (bitarray("0001011"), bitarray("0110")):
                        result = ba_math("/", a, b, a_signed=True, b_signed=True)
                # twos
                if op == bitarray("0001100"):
                        result = ba_math("*", a, -1, b_signed=True)

                # NOT     
                if op == bitarray("0010000"):
                        result = ~a
                # AND
                if op == bitarray("0010001"):
                        result = a & b
                # OR
                if op == bitarray("0010010"):
                        result = a | b
                # XOR
                if op == bitarray("0010011"):
                        result = a ^ b
                # NOR
                if op == bitarray("0010100"):
                        result = ~(a | b)
                        
                # sl
                if op == bitarray("0111"):
                        result = a << ba2int(b)
                # srl
                if op == bitarray("1000"):
                        result = a >> ba2int(b)
                # sra
                if op == bitarray("1001"):
                        a_shift = a >> ba2int(b)
                        a_shift[0:ba2int(b)] = a_shift[ba2int(b)]
                        result = a_shift

                # Set NZP registers
                if ba2int(result, signed=True) == 0:
                        self.nzp = bitarray("010")
                if ba2int(result, signed=True) < 0:
                        self.nzp = bitarray("100")
                if ba2int(result, signed=True) > 0:
                        self.nzp = bitarray("001")

                # Main alu output
                self.result = result

        def fetch(self):
                '''Processor fetch stage.'''
                # Convert PC bits to int, fetch bytes and inc. PC, then convert back to bits.

                bit_address = processor.ba_math("*", self.pc, 8, ret_int=True)

                self.pc_increment(2)
                
                self.ir = self.text_memory[bit_address:bit_address + 16]

                log(f"Cycle {self.cycle} instruction = {self.ir}")
                self.cycle += 1
                

        def decode(self):
                '''Processor decode stage.'''
                self.opcode = self.ir[0:4]
                self.rs = self.register_file[ba2int(self.ir[4:7])]
                self.rt = self.register_file[ba2int(self.ir[7:10])]
                self.rd = self.register_file[ba2int(self.ir[10:13])]
                self.func = self.ir[13:16]
                self.imm = self.ir[7:16]
                self.jmp = self.ir[4:16]

        def execute(self):
                '''Processor execute stage.'''

                # Branch/NOP
                if self.opcode == bitarray("0000"):
                        if (self.ir[4:7][0] & self.nzp[0]) or (self.ir[4:7][1] & self.nzp[1]) or (self.ir[4:7][2] & self.nzp[2]):
                                self.pc = processor.ba_math("+", self.pc, self.imm, b_signed=True)

                # R-type ALU instructions
                if self.opcode in (bitarray("0001"), bitarray("0010")):
                        self.alu(self.opcode + self.func, self.rt, self.rd)

                # I-type ALU instructions
                if self.opcode in (bitarray("0011"), bitarray("0100"), bitarray("0101"), bitarray("0110"), bitarray("0111"), bitarray("1000"), bitarray("1001")):
                        self.alu(self.opcode, self.rs, self.imm)

                # R-type GP data control instruction
                if self.opcode == bitarray("1010"):
                        # HLT
                        if self.func == bitarray("111"):
                                self.run = False

                # Store immediate mem[rs] = sext(imm)
                if self.opcode == bitarray("1011"):
                        data_mem[processor.ba_math("*", self.rs, 8)] = bitarray(int_to_bits(ba2int(self.imm, signed=True), 16))

                # Load immediate rs = sext(imm)
                if self.opcode == bitarray("1100"):
                        self.register_file[ba2int(self.ir[4:7])] = bitarray(int_to_bits(ba2int(self.imm, signed=True), 16))

                # Register save to mem[pc + sext(imm)] (J-type)
                if self.opcode == bitarray("1101"):
                        bit_offset = processor.ba_math("*", self.jmp, 8, a_signed=True)
                        base_address = processor.ba_math("+", self.pc, bit_offset, b_signed=True, ret_int=True)
                        data_mem[base_address:base_address + 8*16] = self.register_file[0] + self.register_file[1] + self.register_file[2] + self.register_file[3] + self.register_file[4] + self.register_file[5] + self.register_file[6] + self.register_file[7]

                # Register restore from mem[pc + sext(imm)] (J-type)
                if self.opcode == bitarray("1110"):
                        bit_offset = processor.ba_math("*", self.jmp, 8, a_signed=True)
                        base_address = processor.ba_math("+", self.pc, bit_offset, b_signed=True, ret_int=True)

                        for i in range(0, 7):
                                self.register_file[i] = data_mem[base_address + 16 * i]

                # Jump unconditionally to pc + sext(imm) (J-type)
                if self.opcode == bitarray("1111"):
                        bit_offset = processor.ba_math("*", self.jmp, 8, a_signed=True)
                        self.pc = processor.ba_math("+", self.pc, bit_offset, b_signed=True)

                        
        # Make static?
        def pc_increment(self, offset):
                pc_int = ba2int(self.pc)

                if type(offset) is int:
                        pc_int += offset

                if type(offset) is bitarray:
                        pc_int += ba2int(offset, signed=True)

                self.pc = bitarray(int_to_bits(pc_int, 16))


        @staticmethod
        def ba_math(op, a, b, a_signed=False, b_signed=False, ret_int=False):
                a_int = a
                b_int = b
                result = 0

                if type(a) is bitarray:
                        a_int = ba2int(a, signed=a_signed)

                if type(b) is bitarray:
                        b_int = ba2int(b, signed=b_signed)

                match(op):
                        case "+":
                                result = a_int + b_int
                        case "-":
                                result = a_int - b_int
                        case "*":
                                result = a_int * b_int
                        case "/":
                                result = a_int / b_int

                if ret_int:
                        return result
                else:
                        return bitarray(int_to_bits(result, 16))

        def start(self):
                while self.run:
                        self.fetch()
                        self.decode()
                        self.execute()
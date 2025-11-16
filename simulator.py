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

                self.controls = {
                        "write_dst_reg": False,
                        "write_dst_mem": False,
                        "write_src_reg": False,
                        "write_src_imm": False,
                }

                # Other vars
                self.run = True
                self.cycle = 0

        def alu(self, op, a, b):
                '''ALU functionality. Decode operation from relevant field(s) and set ALU result bus. All ALU ops set NZP.'''
                result = bitarray(16)

                # FIXME for certain I types b_signed should be false maybe idk if this is a good idea in retrospect

                # add
                if op in (bitarray("0001000"), bitarray("0011000")):
                        result = processor.ba_math("+", a, b, a_signed=True, b_signed=True)
                # sub
                if op in (bitarray("0001001"), bitarray("0100000")):
                        result = processor.ba_math("-", a, b, a_signed=True, b_signed=True)
                # mult
                if op in (bitarray("0001010"), bitarray("0101000")):
                        result = processor.ba_math("*", a, b, a_signed=True, b_signed=True)
                # div
                if op in (bitarray("0001011"), bitarray("0110000")):
                        result = processor.a_math("/", a, b, a_signed=True, b_signed=True)
                # twos
                if op == bitarray("0001100"):
                        result = processor.ba_math("*", a, -1, b_signed=True)

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
                if op == bitarray("0111000"):
                        result = a << ba2int(b)
                # srl
                if op == bitarray("1000000"):
                        result = a >> ba2int(b)
                # sra
                if op == bitarray("1001000"):
                        a_shift = a >> ba2int(b)
                        a_shift[0:ba2int(b)] = a_shift[ba2int(b)]
                        result = a_shift

                # Set NZP registers
                self.set_nzp(result)

                # Main alu output
                self.result = result

        def set_controls(self):
                '''Sets processor control signals.'''
                for signal in self.controls:
                        self.controls[signal] = False

                # All ALU instructions write to register
                if self.opcode in (bitarray("0001"), bitarray("0010"), bitarray("0011"), bitarray("0100"), bitarray("0101"), bitarray("0110"), bitarray("0111"), bitarray("1000"), bitarray("1001")):
                        self.controls["write_dst_reg"] = True

                # The GP 1010 instruction has to be parsed by func
                if self.opcode == bitarray("1010"):
                        # move | copy rt to rs
                        if self.func in (bitarray("000"), bitarray("001"), bitarray("011"), bitarray("100")):
                                self.controls["write_dst_reg"] = True

                        # str | store rt at mem[rs]
                        if self.func == bitarray("010"):
                                self.controls["write_dst_mem"] = True
                                self.controls["write_src_reg"] = True

                # Store immediate mem[rs] = sext(imm)
                if self.opcode == bitarray("1011"):
                        self.controls["write_dst_mem"] = True
                        self.controls["write_src_imm"] = True

                # Load immediate rs = sext(imm)
                if self.opcode == bitarray("1100"):
                        self.controls["write_dst_reg"] = True

        def set_nzp(self, input):
                '''Set NZP registers based on input.'''
                if ba2int(input, signed=True) == 0:
                        self.nzp = bitarray("010")
                if ba2int(input, signed=True) < 0:
                        self.nzp = bitarray("100")
                if ba2int(input, signed=True) > 0:
                        self.nzp = bitarray("001")

        def mem_access(self, address, source, num_bytes=16):
                '''Access up to 16 bytes of memory at byte address.'''
                int_address = address

                if type(address) == bitarray:
                        int_address = ba2int(address)

                bit_address = int_address * 8
                return source[bit_address:bit_address + 8 * num_bytes]

        def write_back(self, write_input):
                '''Performs write back with control signals and input.'''
                if self.controls["write_dst_reg"]:
                        self.register_file[ba2int(self.ir[4:7])] = write_input

                if self.controls["write_dst_mem"]:
                        bit_address = processor.ba_math("*", self.rs, 8, ret_int=True)
                        if self.controls["write_src_reg"]:
                                self.data_memory[bit_address:bit_address + 16] = write_input

                        if self.controls["write_src_imm"]:
                                self.data_memory[bit_address:bit_address + 16] = write_input
                                
        def fetch(self):
                '''Processor fetch stage.'''
                # Fetch 2 bytes from text memory and inc. PC
                self.ir = self.mem_access(self.pc, self.text_memory, 2)
                self.pc = processor.ba_math("+", self.pc, 2)
                
                log(f"Cycle {self.cycle} instruction = {self.ir}")

        def decode(self):
                '''Processor decode stage. Separates instruction register into the various fields. Sets control signals.'''
                self.opcode = self.ir[0:4]
                self.rs = self.register_file[ba2int(self.ir[4:7])]
                self.rt = self.register_file[ba2int(self.ir[7:10])]
                self.rd = self.register_file[ba2int(self.ir[10:13])]
                self.func = self.ir[13:16]
                self.imm = self.ir[7:16]
                self.jmp = self.ir[4:16]

                self.set_controls()

        def execute(self):
                '''Processor execute stage.'''
                exec_output = bitarray(16)

                # Branch/NOP
                if self.opcode == bitarray("0000"):
                        if (self.ir[4:7][0] & self.nzp[0]) or (self.ir[4:7][1] & self.nzp[1]) or (self.ir[4:7][2] & self.nzp[2]):
                                self.pc = processor.ba_math("+", self.pc, self.imm, b_signed=True) 

                # R-type ALU instructions
                if self.opcode in (bitarray("0001"), bitarray("0010")):
                        self.alu(self.opcode + self.func, self.rt, self.rd)
                        exec_output = self.result

                # I-type ALU instructions
                if self.opcode in (bitarray("0011"), bitarray("0100"), bitarray("0101"), bitarray("0110"), bitarray("0111"), bitarray("1000"), bitarray("1001")):
                        self.alu(self.opcode + bitarray(3), self.rs, self.imm)
                        exec_output = self.result

                # R-type GP data control instruction
                if self.opcode == bitarray("1010"):
                        # move | copy rt to rs
                        if self.func == bitarray("000"):
                                exec_output = self.rt
                                # Set NZP registers
                                self.set_nzp(self.rt)

                        # ldr | load mem[rt] to rs
                        if self.func == bitarray("001"):
                                exec_output = self.mem_access(self.rt, self.data_memory, 2)

                        # str | store rt at mem[rs]
                        if self.func == bitarray("010"):
                                exec_output = self.rt

                        # clr | zero register
                        if self.func == bitarray("011"):
                                exec_output = bitarray(16)

                        # lpc | load pc into rs
                        if self.func == bitarray("100"):
                                exec_output = self.pc

                        # swp | swap two registers
                        if self.func == bitarray("101"):
                                self.register_file[ba2int(self.ir[4:7])] = self.rt
                                self.register_file[ba2int(self.ir[7:10])] = self.rs

                        # rst | reset pc to 0
                        if self.func == bitarray("110"):
                                self.pc = bitarray(16)

                        # hlt | halt machine
                        if self.func == bitarray("111"):
                                self.run = False

                # Store immediate mem[rs] = sext(imm)
                if self.opcode == bitarray("1011"):
                        exec_output = bitarray(int_to_bits(ba2int(self.imm, signed=True), 16))

                # Load immediate rs = sext(imm)
                if self.opcode == bitarray("1100"):
                        exec_output = bitarray(int_to_bits(ba2int(self.imm, signed=True), 16))

                # Register save to mem[pc + sext(imm)] (J-type)
                if self.opcode == bitarray("1101"):
                        bit_offset = processor.ba_math("*", self.jmp, 8, a_signed=True)
                        base_address = processor.ba_math("+", self.pc, bit_offset, b_signed=True, ret_int=True)
                        self.data_memory[base_address:base_address + 8*16] = self.register_file[0] + self.register_file[1] + self.register_file[2] + self.register_file[3] + self.register_file[4] + self.register_file[5] + self.register_file[6] + self.register_file[7]

                # Register restore from mem[pc + sext(imm)] (J-type)
                if self.opcode == bitarray("1110"):
                        bit_offset = processor.ba_math("*", self.jmp, 8, a_signed=True)
                        base_address = processor.ba_math("+", self.pc, bit_offset, b_signed=True, ret_int=True)

                        for i in range(0, 7):
                                self.register_file[i] = self.data_mem[base_address + 16 * i:base_address + 16 * i + 16]

                # Jump unconditionally to pc + sext(imm) (J-type)
                if self.opcode == bitarray("1111"):
                        self.pc = processor.ba_math("+", self.pc, self.jmp, b_signed=True)

                self.write_back(exec_output)

        @staticmethod
        def ba_math(op, a, b, a_signed=False, b_signed=False, ret_int=False):
                '''Helper function for bitarray and integer math.'''
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

        def step(self):
                '''Step one instruction forward.'''
                self.fetch()
                self.decode()
                self.execute()
                self.cycle += 1

        def start(self):
                '''Run the processor.'''
                while self.run:
                        self.step()
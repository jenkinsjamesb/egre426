'''
brisc.py

BRISC (Brad's RISC) top level file for sample program runs

James Jenkins 2025
'''

from brisc_logging import init_log, log

from bitarray import bitarray

import assembler
from simulator import processor

# Simply grabs the assembly text from a file and returns it
def get_asm_from_file(filename):
        with open(filename, "r") as file:
                return file.read()

def main():
        init_log(logfile="log/assembly.log", quiet = True)

        # Load test.asm for debugging
        program_text = get_asm_from_file("ref/test.asm")

        # Assemble test.asm to binary
        binary = assembler.assemble(program_text)

        init_log(logfile="log/memory.log", quiet = False)

        # Create processor instance
        proc = processor()

        # Initialize memory file/registers (0s, then initial contents)

        # Data memory
        data_mem = bitarray(256 * 8)
        data_mem[0x0010 * 8:0x0010 * 8 + 16] = bitarray("0000_0001_0000_0001")
        data_mem[0x0010 * 8 + 16:0x0010 * 8 + 32] = bitarray("0000_0001_0001_0000")
        data_mem[0x0010 * 8 + 32:0x0010 * 8 + 48] = bitarray("0000_0000_0001_0001")
        data_mem[0x0010 * 8 + 48:0x0010 * 8 + 64] = bitarray("0000_0000_1111_0000")
        data_mem[0x0010 * 8 + 64:0x0010 * 8 + 80] = bitarray("0000_0000_1111_1111")

        proc.data_memory = data_mem

        # Load binary to program memory
        text_mem = bitarray(256 * 8)
        text_mem[0:] = bitarray(binary)

        proc.text_memory = text_mem

        # Start simulator
        proc.start()

if __name__ == "__main__":
        main()
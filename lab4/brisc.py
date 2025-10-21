'''
brisc.py

BRISC top level file

James Jenkins 2025
'''

from logging import init_log, log

import assembler


# Simply grabs the assembly text from a file and returns it
def get_asm_from_file(filename):
        with open(filename, "r") as file:
                return file.read()

# Functions to set initial machine state and begin simulation
def simulate():
        pass

def main():
        init_log(logfile="log/brisc.log", quiet = False)

        # Load test.asm for debugging
        program_text = get_asm_from_file("ref/test.asm")

        # Assemble test.asm to binary
        assembler.assemble(program_text)

        # Initialize memory file/registers (0s, then initial contents)
        
        
        # Load binary to end of memory


        # Set PC to start of Instruction memory 



if __name__ == "__main__":
        main()
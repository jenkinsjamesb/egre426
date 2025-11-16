from bitarray import bitarray
from bitarray.util import ba2int, ba2hex

def int_to_bits(integer, length):
        '''Helper function to create a bit string of required length from an integer.'''
        if integer < 0:
                integer = (1 << length) + integer

        return format(integer, f'0{length}b')

def insert_every(target, string, spacing):
        '''Inserts string into target every spacing characters.'''
        return string.join(target[i:i+spacing] for i in range(0,len(target),spacing))

def pretty_print_16(number):
        '''Pretty prints a 16-bit string or bitarray'''
        if type(number) == str:
                hex_string = format(int(number, 2), f"04x").upper()

        if type(number) == bitarray:
                hex_string = ba2hex(number).upper()
                number = int_to_bits(ba2int(number), 16)
        
        string = f"0x{hex_string}: {insert_every(number, " ", 4)}\n"

        return string

def format_memory(memory, columns):
        '''Formats a large memory bitarray into an HTML table with 16-bits/cell and columns columns.'''
        string = "<table><tr><th>Address:</th>"

        for column in range(columns):
                string += f"<th>+0x{format(column * 2, f"04x").upper()}</th>"

        for i in range(0, len(memory), 16):
                row_index = i % (columns * 16)
                if row_index == 0:
                        string += f"</tr><tr><th>0x{format(int(i / 8), f"04x").upper()}</th>"

                value = memory[i:i + 16]
                is_zero = value == bitarray(16)
                string += f"<td>{"" if is_zero else "<b>"}{pretty_print_16(value)}{"" if is_zero else "</b>"}</td>"

        string += "</tr></table>"

        return string


def format_memory_report(memory):
        string = "<table><tr class=\"report_color\"><th>Address</th><th>Hex Value</th><th>Binary Value</th></tr>"

        for i in range(0, len(memory), 16):
                string += f"<tr><th>0x{format(int(i / 8), f"04x").upper()}</th>"

                value = memory[i:i + 16]
                is_zero = value == bitarray(16)
                string += f"<td>{"" if is_zero else "<b>"}{pretty_print_16(value)[:6]}{"" if is_zero else "</b>"}</td><td>{"" if is_zero else "<b>"}{pretty_print_16(value)[8:]}{"" if is_zero else "</b>"}</td></tr>"


        string += "</table>"

        return string

def format_registers_report(register_file):
        string = "<table><tr class=\"report_color\"><th>Register</th><th>Hex Value</th><th>Binary Value</th></tr>"

        for i, register in enumerate(register_file):
                string += f"<tr><th>$r{i}</th>"

                value = register
                is_zero = value == bitarray(16)
                string += f"<td>{"" if is_zero else "<b>"}{pretty_print_16(value)[:6]}{"" if is_zero else "</b>"}</td><td>{"" if is_zero else "<b>"}{pretty_print_16(value)[8:]}{"" if is_zero else "</b>"}</td></tr>"


        string += "</table>"

        return string
'''
assembler.py

BRISC assembler code

James Jenkins 2025
'''

from brisc_logging import log
from common import int_to_bits

import re

opcode_mnemonic_lut = [
        [0b0000, "I", r"brn?z?p?|nop"],
        [0b0001, "R", r"addr|subr|mulr|divr|twos"],
        [0b0010, "R", r"not|and|or|xor|nor"],
        [0b0011, "I", r"addi"],
        [0b0100, "I", r"subi"],
        [0b0101, "I", r"muli"],
        [0b0110, "I", r"divi"],
        [0b0111, "I", r"sl"],
        [0b1000, "I", r"srl"],
        [0b1001, "I", r"sra"],
        [0b1010, "R", r"move|ldr|clr|lpc|str|swp|rst|hlt"],
        [0b1011, "I", r"sti"],
        [0b1100, "I", r"ldi"],
        [0b1101, "J", r"save"],
        [0b1110, "J", r"rest"],
        [0b1111, "J", r"jmp"]
]

func_mnemonic_lut = [
        [0b000, r"addr"],
        [0b001, r"subr"],
        [0b010, r"mulr"],
        [0b011, r"divr"],
        [0b100, r"twos"],

        [0b000, r"not"],
        [0b001, r"and"],
        [0b010, r"or"],
        [0b011, r"xor"],
        [0b100, r"nor"],

        [0b000, r"move"],
        [0b001, r"ldr"],
        [0b010, r"str"],
        [0b011, r"clr"],
        [0b100, r"lpc"],
        [0b101, r"swp"],
        [0b110, r"rst"],
        [0b111, r"hlt"]
]

br_register_lut = [
        [0b000, r"nop"],
        [0b001, r"brp"],
        [0b010, r"brz"],
        [0b011, r"brzp"],
        [0b100, r"brn"],
        [0b101, r"brnp"],
        [0b110, r"brnz"],
        [0b111, r"brnzp"]
]

def format_program_text(text):
        ''' Formats program text to easily-parseable lines, and removes comments and whitespace'''
        text_lines = text.split("\n")
        trimmed_text = ""
        
        for line in text_lines:
                line = line.split("#")[0] # Remove all text after a '#'
                line = line.strip() # Remove leading/trailing whitespace
                
                if line != "":
                        # If the line is labeled, prepend the next line with it. Otherwise, add the line to the text.
                        if line.endswith(":"):
                                trimmed_text += line + " "
                        else:
                                trimmed_text += line + "\n"
                
        return trimmed_text[:-1] # Return the trimmed text without the trailing newline

def first_pass_translate(text):
        '''Fills a translation table with an array of binary fields and labels'''

        text_lines = text.split("\n")
        translation_table = []
        label_lut = []

        # First translate pass, determine instruction type, opcode, operands
        for line_number, text_line in enumerate(text_lines):
                line_fields = text_line.split() # Break line into fields
                line_translation = []
                instruction_type = ""
                
                # Check for a label, append the line number and name to the label lut, and prune it.
                if line_fields[0].endswith(":"):
                        label_lut.append([line_number, line_fields[0][:-1]])
                        line_fields = line_fields[1:]

                # Match the mnemonic to an instruction in the LUT
                for index, row in enumerate(opcode_mnemonic_lut):
                        if re.match(row[2], line_fields[0]):
                                line_translation.append(int_to_bits(row[0], 4)) # Append the opcode to the translation
                                instruction_type = row[1]
                                break

                # Handle rest of the fields according to instruction type
                match instruction_type:
                        case "R":
                                translate_r_type(line_fields, line_translation)

                        case "I":
                                translate_i_type(line_fields, line_translation)

                        case "J":
                                translate_j_type(line_fields, line_translation)

                        case _:
                                log(f"Error determining instruction type of {text_line}")
                                exit(1)

                translation_table.append(line_translation)

        return translation_table, label_lut

# Main instruction parsers, get passed the unfinished translation row and complete it (minus labels)
def translate_r_type(line_fields, line_translation):
        # Pull in up to 3 register fields, pad the rest
        count = 0
        for field in line_fields[1:]:
                # For each field, check for a register id and append the bit string to the translation
                line_translation.append(int_to_bits(int(re.match(r"\$r(\d+)", field).group(1)), 3))
                count += 1

        for i in range(3 - count):
                line_translation.append("000")
        
        # Find the Func field mapping for the mnemonic
        for mapping in func_mnemonic_lut:
                if re.match(mapping[1], line_fields[0]):
                        line_translation.append(int_to_bits(mapping[0], 3))

def translate_i_type(line_fields, line_translation):
        # If branch, evaluate nzp flags and label. Otherwise, load rs and imm fields into translation
        if line_fields[0].startswith("br"):
                rs = 0
                if line_fields[0].find("n") != -1:
                        rs += 4
                if line_fields[0].find("z") != -1:
                        rs += 2
                if line_fields[0].find("p") != -1:
                        rs += 1
                line_translation.append(int_to_bits(rs, 3))
                line_translation.append(line_fields[1])
        else:
                line_translation.append(int_to_bits(int(re.match(r"\$r(\d+)", line_fields[1]).group(1)), 3))
                line_translation.append(int_to_bits(int(line_fields[2], 0), 9))

def translate_j_type(line_fields, line_translation):
        line_translation.append(line_fields[1])

def link_labels(table, label_lut):
        '''Looks through the translation table for labels, then consults the LUT to calculate real PC offset'''
        
        for line_number, translation in enumerate(table):
                # If the last value is not binary, it's a label.
                # NOTE: don't look at this. I am sorry
                if not re.match(r"[0-1]+", translation[-1]):
                        target_line = 0
                        for label_mapping in label_lut:
                                if label_mapping[1] == translation[-1]:
                                        target_line = label_mapping[0]
                        if len(translation) == 3:
                                translation[-1] = int_to_bits(2 * (target_line - (line_number + 1)), 9)
                        else:
                                translation[-1] = int_to_bits(2 * (target_line - (line_number + 1)), 12)

def merge_and_check_binary(table):
        binary = ""
        for line_number, line in enumerate(table):
                instruction = "".join(line)
                if len(instruction) != 16:
                        log(f"ERROR: problem assembling instruction #{line_number + 1}")
                        exit(1)
                else:
                        binary += instruction
        return binary

def assemble(program_text):
        log(f"Assembly started with program text:\n{program_text}")

        formatted_text = format_program_text(program_text)
        log(f"Program text formatted. Result:\n{formatted_text}")

        translation_table, label_lut = first_pass_translate(formatted_text)
        log(f"Translation first pass complete. First pass translation table:\n{translation_table}")
        log(f"Label LUT:\n{label_lut}")

        link_labels(translation_table, label_lut)
        log("Label linking complete. Merging translation table to binary...")

        binary_string = merge_and_check_binary(translation_table)
        log(f"Merge complete. Binary string is: {binary_string}")

        # Helper code to generate a translation file for reference use & debugging
        with open("ref/translation.txt", "w") as file:
                asm_lines = formatted_text.split("\n")
                for i in range(int(len(binary_string) / 16)):
                        file.write(asm_lines[i] + "\n")

                        instruction = binary_string[i * 16:i * 16 + 16]

                        file.write(f"{hex(int(instruction, 2))}: {instruction}\n")

        return binary_string
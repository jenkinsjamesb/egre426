from bitarray import bitarray

def int_to_bits(integer, length):
        '''Helper function to create a bit string of required length from an integer.'''
        if integer < 0:
                integer = (1 << length) + integer

        return format(integer, f'0{length}b')

def insert_every(target, string, spacing):
        '''Inserts string into target every spacing characters.'''
        return string.join(target[i:i+spacing] for i in range(0,len(target),spacing))
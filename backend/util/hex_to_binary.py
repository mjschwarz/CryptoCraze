from backend.util.crypto_hash import crypto_hash


# Table – Convert hex digit to binary representation
HEX_TO_BINARY_CONVERSION_TABLE = {
    '0': '0000',
    '1': '0001',
    '2': '0010',
    '3': '0011',
    '4': '0100',
    '5': '0101',
    '6': '0110',
    '7': '0111',
    '8': '1000',
    '9': '1001',
    'a': '1010',
    'b': '1011',
    'c': '1100',
    'd': '1101',
    'e': '1110',
    'f': '1111',
    'A': '1010',
    'B': '1011',
    'C': '1100',
    'D': '1101',
    'E': '1110',
    'F': '1111'
}

def hex_to_binary(hex_string):
    """
    Convert hexidecimal string to binary string
    :param hex_string: <str> Hexidecimal string to convert
    :return <str> Equivalent binary string
    """
    binary_string = ''

    for char in hex_string:
        binary_string += HEX_TO_BINARY_CONVERSION_TABLE[char]

    return binary_string


# -- TESTING AND EXPERIMENTATION -- #

def main():
    number = 451
    hex_number = hex(number)[2:]
    print(f'hex_number: {hex_number}')

    binary_number = hex_to_binary(hex_number)
    print(f'binary_number: {binary_number}')

    original_number = int(binary_number, 2)
    print(f'original_number: {original_number}')

    hex_to_binary_crypto_hash = hex_to_binary(crypto_hash('test_data'))
    print(f'hex_to_binary_crypto_hash: {hex_to_binary_crypto_hash}')


if __name__ == '__main__':
    main()

# -- TESTING AND EXPERIMENTATION -- #

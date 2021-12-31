from hashlib import sha256
from json import dumps


def crypto_hash(*args):
    """
    Return SHA-256 hash of all arguments
    :param *args: <any> Data fed to hash algorithm
    :return <str> Hash string (hexadecimal representation)
    """
    stringified_args = map(dumps, args)
    joined_data = '^'.join(stringified_args)
    return sha256(joined_data.encode('utf-8')).hexdigest()


# -- TESTING AND EXPERIMENTATION -- #

def main():
    print(f"crypto_hash(): {crypto_hash('one', 2, [3, 55, 99])}")


if __name__ == '__main__':
    main()

# -- END TESTING AND EXPERIMENTATION -- #

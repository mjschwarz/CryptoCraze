from uuid import uuid4
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.utils import (
    encode_dss_signature, decode_dss_signature)
from json import dumps
from backend.config import STARTING_BALANCE


class Wallet:
    """
    Individual wallet for miner
    - Keep track of miner's balance
    - Allow miner to authorize Transactions
    """
    def __init__(self, blockchain=None):
        """
        Initialize Wallet with address, public and private keys, and balance
        """
        self.blockchain = blockchain
        self.address = str(uuid4())[:8]
        self.private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
        self.public_key = self.private_key.public_key()
        # Serialize public key to string format
        self.serialize_public_key()

    @property
    def balance(self):
        return Wallet.calculate_balance(self.blockchain, self.address)

    def sign(self, data):
        """
        Generate signature based on data using local private key
        :param data: <any> Data to be signed
        :return: <str> Signed data
        """
        return decode_dss_signature(self.private_key.sign(dumps(data).encode('utf-8'), 
                                        ec.ECDSA(SHA256())))

    def serialize_public_key(self):
        """
        Reset public key to serialized version
        :return: None
        """
        self.public_key = self.public_key.public_bytes(
                            encoding=serialization.Encoding.PEM, 
                            format=serialization.PublicFormat.SubjectPublicKeyInfo
                            ).decode('utf-8')

    @staticmethod
    def verify(public_key, data, signature):
        """
        Verify a signature based on public key and data
        :param public_key: <Public Key Object> Public key object
        :param data: <any> Unencoded data
        :param signature: <str> Signature
        :return: <bool> True if valid signature, False if not
        """
        deserialized_public_key = serialization.load_pem_public_key(public_key.encode('utf-8'), 
                                                                        default_backend)
        r, s = signature

        try:
            deserialized_public_key.verify(encode_dss_signature(r, s), 
                                            dumps(data).encode('utf-8'), 
                                            ec.ECDSA(SHA256()))
            return True
        except InvalidSignature:
            return False

    @staticmethod
    def calculate_balance(blockchain, address):
        """
        Calculate balance of address
        - Balance = sum of output values belonging to address 
            since its most recent Transaction (payment)
        :param blockchain: <Blockchain> Blockchain being searched
        :param address: <str> Address owning balance being calculated
        :return: <float> Balance contained at address
        """
        balance = STARTING_BALANCE

        if not blockchain:
            return balance

        for block in blockchain.chain:
            for transaction in block.data:
                # Address conducts transaction (payment) – reset balance to 'change'
                if transaction['input']['address'] == address:
                    balance = transaction['output'][address]
                elif address in transaction['output']:
                    balance += transaction['output'][address]

        return balance


# -- TESTING AND EXPERIMENTATION -- #

def main():
    wallet = Wallet()
    print(f'wallet.__dict__: {wallet.__dict__}')

    data = { 'foo': 'bar' }
    signature = wallet.sign(data)
    print(f'signature: {signature}')

    should_be_valid = Wallet.verify(wallet.public_key, data, signature)
    print(f'should_be_valid: {should_be_valid}')

    should_be_invalid = Wallet.verify(Wallet().public_key, data, signature)
    print(f'should_be_invalid: {should_be_invalid}')


if __name__ == '__main__':
    main()

# -- END TESTING AND EXPERIMENTATION -- #

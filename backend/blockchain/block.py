from time import time_ns
from backend.util.crypto_hash import crypto_hash
from backend.util.hex_to_binary import hex_to_binary
from backend.config import MINE_RATE


# Data to be included in genesis Block
GENESIS_DATA = {
    'timestamp': 1,
    'prev_hash': 'genesis_prev_hash',
    'hash': 'genesis_hash',
    'data': [],
    'difficulty': 10,
    'nonce': 'genesis_nonce'
}

class Block:
    """
    Unit of Storage
    """
    def __init__(self, timestamp, prev_hash, hash, data, difficulty, nonce):
        """
        Initializes a Block
        :param timestamp: <int> Current timestamps (ns since Epoch)
        :param prev_hash: <str> Hash of previous Block
        :param hash: <str> Hash of current Block
        :param data: <any> Data stored in Block
        :param difficulty: <int> Number of leading 0's required in (binary representation of) hash
        :param nonce: <int> Arbitrary number to calculate hash
        """
        self.timestamp = timestamp
        self.prev_hash = prev_hash
        self.hash = hash
        self.data = data
        self.difficulty = difficulty
        self.nonce = nonce

    def __repr__(self):
        """
        String representation of Block
        :return: <str>
        """
        return (
            'Block('
            f'timestamp: {self.timestamp}, '
            f'prev_hash: {self.prev_hash}, '
            f'hash: {self.hash}, '
            f'data: {self.data}, '
            f'difficulty: {self.difficulty}, '
            f'nonce: {self.nonce})')

    def __eq__(self, other_block):
        """
        Define what it means for Blocks to be equal
        """
        return self.__dict__ == other_block.__dict__

    def to_json(self):
        """
        Serialize Block into dictionary of attributes
        :return: <dict> Block as dictionary
        """
        return self.__dict__

    @staticmethod
    def genesis():
        """
        Generate genesis Block
        :return: <Block> Genesis Block
        """
        return Block(**GENESIS_DATA)

    @staticmethod
    def from_json(block_json):
        """
        Deserialize a JSON representation into Block
        :param block_json: <json> JSON representation of Block
        :return: <Block> Restored Block
        """
        return Block(**block_json)

    @staticmethod
    def mine_block(prev_block, data):
        """
        Mine a Block until hash found meeting 'Proof of Work' difficulty requirement
        :param prev_block: <Block> Previous Block in Blockchain
        :param data: <any> Data to be stored in new Block
        :return: <Block> New Block to be added to Blockchain
        """
        timestamp = time_ns()
        prev_hash = prev_block.hash
        difficulty = Block.adjust_difficulty(prev_block, timestamp)
        nonce = 0
        hash = crypto_hash(timestamp, prev_hash, data, difficulty, nonce)

        while hex_to_binary(hash)[0:difficulty] != '0' * difficulty:
            nonce += 1
            timestamp = time_ns()
            difficulty = Block.adjust_difficulty(prev_block, timestamp)
            hash = crypto_hash(timestamp, prev_hash, data, difficulty, nonce)
            

        return Block(timestamp, prev_hash, hash, data, difficulty, nonce)

    @staticmethod
    def adjust_difficulty(prev_block, new_timestamp):
        """
        Calculate difficulty adjustment according to mine rate
        :param prev_block: <Block> Previous Block in Blockchain
        :param new_timestamp: <int> Timestamp of Block to be mined
        :return: <int> Adjusted difficulty
        """
        # Block mined too slowly
        if (new_timestamp - prev_block.timestamp) < MINE_RATE:
            return prev_block.difficulty + 1

        # Block mined too quickly
        return max(prev_block.difficulty - 1, 1)

    @staticmethod
    def is_valid_block(prev_block, block):
        """
        Validate Block
        
        Requirements:
            - Block has correct prev_hash reference
            - Block must meet 'Proof of Work' requirement
            - Difficulty must adjust by 1
            - Block hash must be valid combination of Block fields
        
        :param prev_block: <Block> Previous Block in Blockchain
        :param block: <Block> Block being validated
        :return: None
        :raises Exception: Throw if any field of Block incorrect
        """
        if block.prev_hash != prev_block.hash:
            raise Exception('Block prev_hash incorrect')

        try:
            int(block.hash, 16)
        except Exception as e:
            raise Exception('Block hash incorrect')

        if hex_to_binary(block.hash)[0:block.difficulty] != '0' * block.difficulty:
            raise Exception("'Proof of Work' requirement not met")

        if abs(prev_block.difficulty - block.difficulty) > 1:
            raise Exception('Block difficulty must only adjust by 1')

        reconstructed_hash = crypto_hash(
            block.timestamp, 
            block.prev_hash, 
            block.data, 
            block.difficulty,
            block.nonce)

        if block.hash != reconstructed_hash:
            raise Exception('Block hash incorrect')


# -- TESTING AND EXPERIMENTATION -- #

def main():
    genesis_block = Block.genesis()
    bad_block = Block.mine_block(genesis_block, 'foo')
    bad_block.prev_hash = 'evil_data'
    
    try:
        Block.is_valid_block(genesis_block, bad_block)
    except Exception as e:
        print(f'is_valid_block: {e}')


if __name__ == '__main__':
    main()

# -- TESTING AND EXPERIMENTATION -- #

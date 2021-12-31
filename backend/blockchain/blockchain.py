from backend.blockchain.block import Block
from backend.wallet.transaction import Transaction
from backend.config import MINING_REWARD_INPUT
from backend.wallet.wallet import Wallet


class Blockchain:
    """
    Public ledger of transactions
    """
    def __init__(self):
        """
        Initialize Blockchain with only genesis Block
        """
        self.chain = [Block.genesis()]

    def __repr__(self):
        """
        String representation of Blockchain
        :return: <str>
        """
        return f'Blockchain: {self.chain}'

    def add_block(self, data):
        """
        Add Block to end of Blockchain
        :param data: <any> Data contained in new Block
        :return: None
        """
        self.chain.append(Block.mine_block(self.chain[-1], data))

    def replace_chain(self, chain):
        """
        Determine if local chain should be replaced and
        Replace if conditions met

        Requirements:
            - Incoming chain longer than local chain
            - Incoming chain is valid

        :param chain: <list> Incoming chain
        :return: None
        :raises Exception: Throw if local chain not replaced
        """
        if len(chain) <= len(self.chain):
            raise Exception('Cannot replace – Incoming chain must be longer')

        try:
            Blockchain.is_valid_chain(chain)
        except Exception as e:
            raise Exception(f'Cannot replace - Incoming chain invalid: {e}')

        self.chain = chain

    def to_json(self):
        """
        Serialize Blockchain into list of Blocks
        :return: <list> Chain
        """
        return list(map(lambda block: block.to_json(), self.chain))

    @staticmethod
    def from_json(chain_json):
        """
        Deserialize list of serialized Blocks into Blockchain
        :param chain_json: <json> JSON representation of chain
        :return: <Blockchain> Restored Blockchain
        """
        blockchain = Blockchain()
        blockchain.chain = list(map(lambda block_json: Block.from_json(block_json), chain_json))
        return blockchain

    @staticmethod
    def is_valid_chain(chain):
        """
        Validate chain
        Requirements:
            - Chain must begin with genesis Block
            - Each Block must be valid (see Block.is_valid_block)
        :param chain: <list> Chain being validated
        :return: None
        :raises Exception: Throw if any Block invalid
        """
        # Genesis Block
        if chain[0] != Block.genesis():
            raise Exception('Genesis Block invalid')

        # Mined Blocks
        for i in range (1, len(chain)):
            block = chain[i]
            prev_block = chain[i - 1]
            Block.is_valid_block(prev_block, block)

        # Validate all Transactions
        Blockchain.is_valid_transaction_chain(chain)

    @staticmethod
    def is_valid_transaction_chain(chain):
        """
        Enforce rules of chain (of Blocks of Transactions)
        Requirements:
            - Each Transaction only appears once in chain
            - Only one mining reward per Block
            - Each Transaction must be valid
        :param chain: <list> Chain being validated
        :return: None
        :raises Exception: Throw if any requirement violated
        """
        transaction_ids = set()

        for i in range(len(chain)):
            block = chain[i]
            has_mining_reward = False

            for transaction_json in block.data:
                transaction = Transaction.from_json(transaction_json)
                
                # Duplicate Transaction
                if transaction.id in transaction_ids:
                    raise Exception(f'Invalid chain – Transaction {transaction.id} is not unique')

                transaction_ids.add(transaction.id)

                # Mining reward
                if transaction.input == MINING_REWARD_INPUT:
                    # Extra mining rewards
                    if has_mining_reward:
                        raise Exception(f'Invalid chain – Block {block.hash} has more than one mining reward')

                    has_mining_reward = True
                # Normal Transaction
                else:
                    historic_blockchain = Blockchain() 
                    historic_blockchain.chain = chain[:i]
                    historic_balance = Wallet.calculate_balance(historic_blockchain, transaction.input['address'])

                    # Sender balance modified
                    if historic_balance != transaction.input['amount']:
                        raise Exception(f'Invalid chain - Transaction {transaction.id} has invalid input amount')

                Transaction.is_valid_transaction(transaction)


# -- TESTING AND EXPERIMENTATION -- #

def main():
    blockchain = Blockchain()
    blockchain.add_block('one')
    blockchain.add_block('two')
    print(blockchain)


if __name__ == '__main__':
    main()

# -- TESTING AND EXPERIMENTATION -- #

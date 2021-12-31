from uuid import uuid4
from time import time_ns
from backend.config import MINING_REWARD, MINING_REWARD_INPUT
from backend.wallet.wallet import Wallet


class Transaction:
    """
    Document exchange of currency from sender to recipient(s)
    """
    def __init__(self, sender_wallet=None, recipient=None, amount=None, id=None, output=None, input=None):
        self.id = id or str(uuid4())[:8]
        self.output = output or self.create_output(sender_wallet, recipient, amount)
        self.input = input or self.create_input(sender_wallet, self.output)

    def create_output(self, sender_wallet, recipient, amount):
        """
        Structure output data for Transaction
        :param sender_wallet: <Wallet> Wallet of sender
        :param recipient: <str> Address of recipient
        :param amount: <float> Transaction amount
        :return: <dict> Output data of Transaction
        """
        # Not enough funds
        if amount > sender_wallet.balance:
            raise Exception('Amount exceeds balance')

        output = {}
        output[recipient] = amount
        output[sender_wallet.address] = sender_wallet.balance - amount

        return output

    def create_input(self, sender_wallet, output):
        """
        Structure input data for Transaction
        Sign Transaction and include sender's public key and address
        :param sender_wallet: <Wallet> Wallet of sender
        :param output: <dict> Output data of Transaction
        :return: <dict> Input data of Transaction
        """
        return {
            'timestamp': time_ns(),
            'amount': sender_wallet.balance,
            'address': sender_wallet.address,
            'public_key': sender_wallet.public_key,
            'signature': sender_wallet.sign(output)
        }

    def update(self, sender_wallet, recipient, amount):
        """
        Update Transaction with existing or new recipient
        :param sender_wallet: <Wallet> Wallet of sender
        :param recipient: <str> Address of recipient
        :param amount: <float> Transaction amount
        :return: None
        """
        # Not enough funds
        if amount > self.output[sender_wallet.address]:
            raise Exception('Amount exceeds balance')

        # Modify existing transaction amount with recipient
        if recipient in self.output:
            self.output[recipient] += amount
        # New recipient
        else:
            self.output[recipient] = amount

        self.output[sender_wallet.address] -= amount
        self.input = self.create_input(sender_wallet, self.output)

    def to_json(self):
        """
        Serialize Transaction
        :return: <dict> Dictionary representation of Transaction
        """
        return self.__dict__

    @staticmethod
    def from_json(transaction_json):
        """
        Deserialize JSON representation of Transaction back to Transaction
        :param transaction_json: <json> JSON representation of Transaction
        :return: <Transaction> Restored Transaction
        """
        return Transaction(**transaction_json)

    @staticmethod
    def is_valid_transaction(transaction):
        """
        Validate a transaction
        :param transaction: <Transaction> Transaction being validated
        :return: None
        :raises Exception: Throw if Transaction invalid
        """
        # Mining reward
        if transaction.input == MINING_REWARD_INPUT:
            # Mining reward output requirements:
            # - only have one entry
            # - entry amount is mining reward value
            if list(transaction.output.values()) != [MINING_REWARD]:
                raise Exception('Invalid transaction - Mining reward invalid')
            return

        # Normal transaction
        output_total = sum(transaction.output.values())

        if transaction.input['amount'] != output_total:
            raise Exception('Invalid transaction – Output values invalid')

        if not Wallet.verify(transaction.input['public_key'], transaction.output, transaction.input['signature']):
            raise Exception('Invalid transaction - Signature invalid')

    @staticmethod
    def reward_transaction(miner_wallet):
        """
        Generate reward Transaction to award miner
        :param miner_wallet: <Wallet> Wallet of miner
        :return: <Transaction> Reward Transaction
        """
        output = {}
        output[miner_wallet.address] = MINING_REWARD

        return Transaction(input=MINING_REWARD_INPUT, output=output)           


# -- TESTING AND EXPERIMENTATION -- #

def main():
    transaction = Transaction(Wallet(), 'recipient', 15)
    print(f'transaction.__dict__: {transaction.__dict__}')

    transaction_json = transaction.to_json()

    restored_transaction = Transaction.from_json(transaction_json)

    print(f'restored_transaction.__dict__: {restored_transaction.__dict__}')


if __name__ == '__main__':
    main()

# -- END TESTING AND EXPERIMENTATION -- #

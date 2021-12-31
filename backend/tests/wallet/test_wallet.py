from backend.wallet.wallet import Wallet
from backend.blockchain.blockchain import Blockchain
from backend.config import STARTING_BALANCE
from backend.wallet.transaction import Transaction


def test_verify_valid_signature():
    # Valid
    data = {'spam': 'eggs_over_easy'}
    wallet = Wallet()
    signature = wallet.sign(data)

    assert Wallet.verify(wallet.public_key, data, signature)

def test_verify_invalid_signature():
    # Invalid
    data = {'spam': 'eggs_over_easy'}
    wallet = Wallet()
    signature = wallet.sign(data)

    assert not Wallet.verify(Wallet().public_key, data, signature)

def test_calculate_balance():
    blockchain = Blockchain()
    wallet = Wallet()

    # No transactions – balance is unchanged
    assert Wallet.calculate_balance(blockchain, wallet.address) == STARTING_BALANCE

    amount = 73
    transaction = Transaction(wallet, 'recipient', amount)
    blockchain.add_block([transaction.to_json()])

    # Balance is reduced by transaction amount
    assert Wallet.calculate_balance(blockchain, wallet.address) == STARTING_BALANCE - amount

    recieved_amount_1 = 49
    recieved_transaction_1 = Transaction(Wallet(), wallet.address, recieved_amount_1)

    recieved_amount_2 = 13
    recieved_transaction_2 = Transaction(Wallet(), wallet.address, recieved_amount_2)

    blockchain.add_block([recieved_transaction_1.to_json(), recieved_transaction_2.to_json()])

    # Balance is increased by incoming transaction amounts
    assert Wallet.calculate_balance(blockchain, wallet.address) == STARTING_BALANCE - amount + recieved_amount_1 + recieved_amount_2
    
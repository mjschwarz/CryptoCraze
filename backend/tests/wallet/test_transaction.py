import pytest
from backend.wallet.transaction import Transaction
from backend.wallet.wallet import Wallet
from backend.config import MINING_REWARD, MINING_REWARD_INPUT


def test_transaction():
    sender_wallet = Wallet()
    recipient = 'recipient'
    amount = 50
    transaction = Transaction(sender_wallet, recipient, amount)

    # Ouput data contains amount
    assert transaction.output[recipient] == amount

    # Output data contains 'change' amount
    assert transaction.output[sender_wallet.address] == sender_wallet.balance - amount

    # Input data contains timestamp
    assert 'timestamp' in transaction.input

    # Input data amount is sender balance
    assert transaction.input['amount'] == sender_wallet.balance

    # Input data address is sender address
    assert transaction.input['address'] == sender_wallet.address

    # Input data public key is sender public key
    assert transaction.input['public_key'] == sender_wallet.public_key

    # Valid transaction
    assert Wallet.verify(transaction.input['public_key'], transaction.output, transaction.input['signature'])

def test_transaction_exceeds_balance():
    # Not enough funds
    with pytest.raises(Exception, match='Amount exceeds balance'):
        Transaction(Wallet(), 'recipient', 9999)

def test_transaction_update_exceeds_balance():
    sender_wallet = Wallet()
    transaction = Transaction(sender_wallet, 'recipient', 5)

    # Not enough funds
    with pytest.raises(Exception, match='Amount exceeds balance'):
        Transaction(sender_wallet, 'new_recipient', 9999)

def test_transaction_update():
    # Valid
    sender_wallet = Wallet()
    first_recipient = 'first_recipient'
    first_amount = 99
    
    transaction = Transaction(sender_wallet, first_recipient, first_amount)

    next_recipient = 'next_recipient'
    next_amount = 55

    transaction.update(sender_wallet, next_recipient, next_amount)

    # Output data contains second recipient amount
    assert transaction.output[next_recipient] == next_amount

    # Output data modifies sender balance after update
    assert transaction.output[sender_wallet.address] == sender_wallet.balance - first_amount - next_amount

    # Valid transaction
    assert Wallet.verify(transaction.input['public_key'], transaction.output, transaction.input['signature'])

    to_first_again_amount = 77
    transaction.update(sender_wallet, first_recipient, to_first_again_amount)

    # Output data contains first recipient amount after multiple updates
    assert transaction.output[first_recipient] == first_amount + to_first_again_amount

    # Output data modifies sender balance after update
    assert transaction.output[sender_wallet.address] == sender_wallet.balance - first_amount - next_amount - to_first_again_amount

    # Valid transaction
    assert Wallet.verify(transaction.input['public_key'], transaction.output, transaction.input['signature'])

def test_valid_transaction():
    # Valid
    Transaction.is_valid_transaction(Transaction(Wallet(), 'recipient', 99))

def test_valid_transaction_invalid_outputs():
    # Invalid - modify transaction amount
    sender_wallet = Wallet()
    transaction = Transaction(sender_wallet, 'recipient', 99)
    transaction.output[sender_wallet.address] = 9999

    with pytest.raises(Exception, match='Invalid transaction – Output values invalid'):
        Transaction.is_valid_transaction(transaction)

def test_valid_transaction_invalid_signature():
    # Invalid - incorrect signature
    transaction = Transaction(Wallet(), 'recipient', 99)
    transaction.input['signature'] = Wallet().sign(transaction.output)

    with pytest.raises(Exception, match='Invalid transaction - Signature invalid'):
        Transaction.is_valid_transaction(transaction)

def test_reward_transaction():
    miner_wallet = Wallet()
    transaction = Transaction.reward_transaction(miner_wallet)

    # Transaction input/output data are custom reward values
    assert transaction.input == MINING_REWARD_INPUT
    assert transaction.output[miner_wallet.address] == MINING_REWARD

def test_valid_reward_transaction():
    # Valid
    reward_transaction = Transaction.reward_transaction(Wallet())
    Transaction.is_valid_transaction(reward_transaction)
    
def test_valid_reward_transaction_extra_recipient():
    # Invalid
    reward_transaction = Transaction.reward_transaction(Wallet())
    reward_transaction.output['extra_recipient'] = 50

    with pytest.raises(Exception, match='Mining reward invalid'):
        Transaction.is_valid_transaction(reward_transaction)

def test_valid_reward_transaction_invalid_amount():
    # Invalid
    miner_wallet = Wallet()
    reward_transaction = Transaction.reward_transaction(miner_wallet)
    reward_transaction.output[miner_wallet.address] = 9999

    with pytest.raises(Exception, match='Mining reward invalid'):
        Transaction.is_valid_transaction(reward_transaction)
        
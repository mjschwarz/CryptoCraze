import pytest
from backend.blockchain.blockchain import Blockchain
from backend.blockchain.block import GENESIS_DATA
from backend.wallet.wallet import Wallet
from backend.wallet.transaction import Transaction


def test_blockchain_instance():
    blockchain = Blockchain()

    # Blockchain begins with genesis Block
    assert blockchain.chain[0].hash == GENESIS_DATA['hash']

def test_add_block():
    blockchain = Blockchain()
    data = 'test-data'
    blockchain.add_block(data)

    # Data field of final Block in chain same as newly added Block
    # (New Block should be added to end of chain)
    assert blockchain.chain[-1].data == data

@pytest.fixture
def blockchain_seven_blocks():
    blockchain = Blockchain()
    
    for i in range(7):
        blockchain.add_block([Transaction(Wallet(), 'recipient', i).to_json()])

    return blockchain

def test_is_valid_chain(blockchain_seven_blocks):
    # Valid
    Blockchain.is_valid_chain(blockchain_seven_blocks.chain)

def test_is_valid_chain_bad_genesis(blockchain_seven_blocks):
    # Invalid genesis Block
    blockchain_seven_blocks.chain[0].hash = 'bad_hash'
    with pytest.raises(Exception, match='Genesis Block invalid'):
        Blockchain.is_valid_chain(blockchain_seven_blocks.chain)

def test_is_valid_chain_bad_mined(blockchain_seven_blocks):
    # Invalid mined Block
    blockchain_seven_blocks.chain[3].prev_hash = 'abc123'
    with pytest.raises(Exception, match='Block prev_hash incorrect'):
        Blockchain.is_valid_chain(blockchain_seven_blocks.chain)

def test_replace_chain(blockchain_seven_blocks):
    # Replaced
    blockchain = Blockchain()
    blockchain.replace_chain(blockchain_seven_blocks.chain)

    assert blockchain.chain == blockchain_seven_blocks.chain

def test_replace_chain_not_longer(blockchain_seven_blocks):
    # NOT Replaced
    blockchain = Blockchain()
    blockchain.replace_chain(blockchain_seven_blocks.chain)

    with pytest.raises(Exception, match='Cannot replace – Incoming chain must be longer'):
        blockchain_seven_blocks.replace_chain(blockchain.chain)

def test_replace_chain_bad_chain(blockchain_seven_blocks):
    # NOT Replaced
    blockchain = Blockchain()
    blockchain_seven_blocks.chain[2].hash = 'ABC'

    with pytest.raises(Exception, match='Incoming chain invalid'):
        blockchain.replace_chain(blockchain_seven_blocks.chain)

def test_valid_transaction_chain(blockchain_seven_blocks):
    # Valid
   Blockchain.is_valid_transaction_chain(blockchain_seven_blocks.chain)

def test_valid_transaction_chain_duplicate_transactions(blockchain_seven_blocks):
    # Invalid
    transaction = Transaction(Wallet(), 'recipient', 1).to_json()

    blockchain_seven_blocks.add_block([transaction, transaction])

    with pytest.raises(Exception, match='is not unique'):
        Blockchain.is_valid_transaction_chain(blockchain_seven_blocks.chain)

def test_valid_transaction_chain_multiple_rewards(blockchain_seven_blocks):
    # Invalid
    reward_1 = Transaction.reward_transaction(Wallet()).to_json()
    reward_2 = Transaction.reward_transaction(Wallet()).to_json()

    blockchain_seven_blocks.add_block([reward_1, reward_2])

    with pytest.raises(Exception, match='more than one mining reward'):
        Blockchain.is_valid_transaction_chain(blockchain_seven_blocks.chain)

def test_valid_transaction_chain_bad_transaction(blockchain_seven_blocks):
    # Invalid
    bad_transaction = Transaction(Wallet(), 'recipient', 1)
    bad_transaction.input['signature'] = Wallet().sign(bad_transaction.output)

    blockchain_seven_blocks.add_block([bad_transaction.to_json()])

    with pytest.raises(Exception, match='Invalid transaction'):
        Blockchain.is_valid_transaction_chain(blockchain_seven_blocks.chain)

def test_valid_transaction_chain_bad_historic_balance(blockchain_seven_blocks):
    # Invalid
    wallet = Wallet()
    bad_transaction = Transaction(wallet, 'recipient', 1)
    bad_transaction.output['address'] = 8888
    bad_transaction.input['amount'] = 8889
    bad_transaction.input['signature'] = wallet.sign(bad_transaction.output)

    blockchain_seven_blocks.add_block([bad_transaction.to_json()])

    with pytest.raises(Exception, match='invalid input amount'):
        Blockchain.is_valid_transaction_chain(blockchain_seven_blocks.chain)
        
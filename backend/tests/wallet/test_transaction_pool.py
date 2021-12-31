from backend.wallet.transaction_pool import TransactionPool
from backend.wallet.transaction import Transaction
from backend.wallet.wallet import Wallet
from backend.blockchain.blockchain import Blockchain


def test_set_transaction():
    transaction_pool = TransactionPool()
    transaction = Transaction(Wallet(), 'recipient', 5)

    transaction_pool.set_transaction(transaction)

    # Transaction added to pool
    assert transaction_pool.transaction_map[transaction.id] == transaction

def test_clear_blockchain_transactions():
    transaction_pool = TransactionPool()
    transaction_1 = Transaction(Wallet(), 'recipient', 1)
    transaction_2 = Transaction(Wallet(), 'recipient', 2)

    transaction_pool.set_transaction(transaction_1)
    transaction_pool.set_transaction(transaction_2)
    
    blockchain = Blockchain()
    blockchain.add_block([transaction_1.to_json(), transaction_2.to_json()])

    # Transactions added to pool
    assert transaction_1.id in transaction_pool.transaction_map
    assert transaction_1.id in transaction_pool.transaction_map

    transaction_pool.clear_blockchain_transactions(blockchain)

    # Transactions removed from pool
    assert not transaction_1.id in transaction_pool.transaction_map
    assert not transaction_1.id in transaction_pool.transaction_map

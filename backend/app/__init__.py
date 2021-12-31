import os
from random import randint
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from backend.blockchain.blockchain import Blockchain
from backend.pubsub import PubSub
from backend.wallet.wallet import Wallet
from backend.wallet.transaction import Transaction
from backend.wallet.transaction_pool import TransactionPool


app = Flask(__name__)
CORS(app, resources={ r'/*': { 'origins': 'http://localhost:3000' } })
blockchain = Blockchain()
wallet = Wallet(blockchain)
transaction_pool = TransactionPool()
pubsub = PubSub(blockchain, transaction_pool)

# GET
@app.route('/')
def route_default():
    return 'Welcome to the Blockchain'

# GET
@app.route('/blockchain')
def route_blockchain():
    return jsonify(blockchain.to_json())

# QUERY
@app.route('/blockchain/range')
def route_blockchain_range():
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))

    return jsonify(blockchain.to_json()[::-1][start:end])

# GET
@app.route('/blockchain/length')
def route_blockchain_length():
    return jsonify(len(blockchain.chain))

# GET
@app.route('/blockchain/mine')
def route_blockchain_mine():
    transaction_data = transaction_pool.transaction_data()
    transaction_data.append(Transaction.reward_transaction(wallet).to_json())
    blockchain.add_block(transaction_data)
    block = blockchain.chain[-1]
    pubsub.broadcast_block(block)
    transaction_pool.clear_blockchain_transactions(blockchain)

    return jsonify(block.to_json())

# POST
@app.route('/wallet/transact', methods=['POST'])
def route_wallet_transact():
    transaction_data = request.get_json()
    transaction = transaction_pool.existing_transaction(wallet.address)
    
    # Existing transaction exists - modify it
    if transaction:
        transaction.update(wallet, transaction_data['recipient'],  transaction_data['amount'])
    # Create new transaction
    else:
        transaction = Transaction(wallet, transaction_data['recipient'],  transaction_data['amount'])

    pubsub.broadcast_transaction(transaction)

    return jsonify(transaction.to_json())

# GET
@app.route('/wallet/info')
def route_wallet_info():
    return jsonify({'address': wallet.address, 'balance': wallet.balance})

# GET
@app.route('/known-addresses')
def route_known_addresses():
    known_addresses = set()

    for block in blockchain.chain:
        for transaction in block.data:
            known_addresses.update(transaction['output'].keys())

    return jsonify(list(known_addresses))

# GET
@app.route('/transactions')
def route_transactions():
    return jsonify(transaction_pool.transaction_data())


# -- TESTING AND EXPERIMENTATION -- #

ROOT_PORT = 5000
PORT = ROOT_PORT

# Run peers who can make requests
if os.environ.get('PEER') == 'True':
    PORT = randint(5001, 6000)
    result = requests.get(f'http://localhost:{ROOT_PORT}/blockchain')
    result_blockchain = Blockchain.from_json(result.json())

    try:
        blockchain.replace_chain(result_blockchain.chain)
        print('\n-- Successfully synchronized the local chain')
    except Exception as e:
        print(f'\n-- Error synchronizing: {e}')

# Seed blockchain with transactions
if os.environ.get('SEED_DATA') == 'True':
    for i in range(10):
        blockchain.add_block([
            Transaction(Wallet(), Wallet().address, randint(2, 50)).to_json(),
            Transaction(Wallet(), Wallet().address, randint(2, 50)).to_json()
        ])

    for i in range(3):
        transaction_pool.set_transaction(Transaction(Wallet(), Wallet().address, randint(2, 50)))

## -- END TESTING AND EXPERIMENTATION -- ##

app.run(port=PORT)

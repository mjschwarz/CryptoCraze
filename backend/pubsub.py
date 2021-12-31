from time import sleep
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback
from backend.blockchain.block import Block
from backend.wallet.transaction import Transaction


pnconfig = PNConfiguration()
pnconfig.subscribe_key = # Subscribe Key from PubNub
pnconfig.publish_key = # Publish Key from PubNub

CHANNELS = {
    'TEST': 'TEST',
    'BLOCK': 'BLOCK',
    'TRANSACTION': 'TRANSACTION'
}

class Listener(SubscribeCallback):
    """
    Custom Listener object to override methods in PubNub SubscribeCallback class
    """
    def __init__(self, blockchain, transaction_pool):
        """
        Initialize Listener with Blockchain
        """
        self.blockchain = blockchain
        self.transaction_pool = transaction_pool

    def message(self, pubnub, message_object):
        """
        Print message object to console
        :param pubnub: <PubNub> PubNum object being listened to
        :param message_object: <Message> Message object recieved
        :return: None
        """
        print(f'\n-- Channel: {message_object.channel} | Message: {message_object.message}')

        # Add Block to Blockchain (if new chain valid)
        if message_object.channel == CHANNELS['BLOCK']:
            block = Block.from_json(message_object.message)
            potential_chain = self.blockchain.chain[:]
            potential_chain.append(block)

            try:
                self.blockchain.replace_chain(potential_chain)
                self.transaction_pool.clear_blockchain_transactions(self.blockchain)
                print(f'\n-- Successfully replaced local chain')
            except Exception as e:
                print(f'\n-- Did not replace chain: {e}')
        # Add Transaction to TransactionPool
        elif message_object.channel == CHANNELS['TRANSACTION']:
            transaction = Transaction.from_json(message_object.message)
            self.transaction_pool.set_transaction(transaction)
            print(f'\n-- New transaction added to pool')


class PubSub:
    """
    Handles Publish/Subscribe layer of app
    Provides communication between nodes of Blockchain network
    """
    def __init__(self, blockchain, transaction_pool):
        """
        Initialize PubSub with PNConfig, channels, and Listener (with Blockchain)
        """
        self.pubnub = PubNub(pnconfig)
        self.pubnub.subscribe().channels(CHANNELS.values()).execute()
        self.pubnub.add_listener(Listener(blockchain, transaction_pool))

    def publish(self, channel, message):
        """
        Publish message object to channel
        :param channel: <Channel> Channel to publish to
        :param message: <Message> Message to publish
        :return: None
        """
        self.pubnub.publish().channel(channel).message(message).sync()

    def broadcast_block(self, block):
        """
        Broadcast Block to all nodes
        :param block: <Block> Block to broadcast
        :return: None
        """
        self.publish(CHANNELS['BLOCK'], block.to_json())

    def broadcast_transaction(self, transaction):
        """
        Broadcast Transaction to all nodes
        :param transaction: <Transaction> Transaction to broadcast
        :return: None
        """
        self.publish(CHANNELS['TRANSACTION'], transaction.to_json())


# -- TESTING AND EXPERIMENTATION -- #

def main(): 
    pubsub = PubSub()

    sleep(1)

    pubsub.publish(CHANNELS['TEST'], {'foo': 'bar'})

if __name__ == '__main__':
    main()

# -- END TESTING AND EXPERIMENTATION -- #

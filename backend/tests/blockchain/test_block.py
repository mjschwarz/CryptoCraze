from time import sleep, time_ns
import pytest
from backend.blockchain.block import Block, GENESIS_DATA
from backend.config import MINE_RATE, SECONDS
from backend.util.hex_to_binary import hex_to_binary


def test_genesis():
    genesis = Block.genesis()

    # Block class able to be instantiated
    assert isinstance(genesis, Block)

    # Block fields correctly generated
    for key, value in GENESIS_DATA.items():
        assert getattr(genesis, key) == value

def test_mine_block():
    prev_block = Block.genesis()
    data = 'test-data'
    block = Block.mine_block(prev_block, data)

    # Block class able to be instantiated
    assert isinstance(block, Block)
    
    # Block fields correctly generated
    assert block.data == data
    assert block.prev_hash == prev_block.hash

    # 'Proof of Work' leading 0's difficulty requirement met
    assert hex_to_binary(block.hash)[0:block.difficulty] == '0' * block.difficulty

def test_quickly_mined_block():
    prev_block = Block.mine_block(Block.genesis(), 'foo')
    mined_block = Block.mine_block(prev_block, 'bar')

    # Difficulty increased if Block mined too quickly
    assert mined_block.difficulty == prev_block.difficulty + 1

def test_slowly_mined_block():
    prev_block = Block.mine_block(Block.genesis(), 'spam')
    sleep(MINE_RATE / SECONDS)
    mined_block = Block.mine_block(prev_block, 'eggs')

    # Difficulty decreased if Block mined too slowly
    assert mined_block.difficulty == prev_block.difficulty - 1

def test_block_difficulty_floored_at_1():
    prev_block = Block(time_ns(), 'test_prev_hash', 'test_hash', 'test_data', 1, 0)
    sleep(MINE_RATE / SECONDS)
    mined_block = Block.mine_block(prev_block, 'foo')

    # Difficulty cannot go below 1
    assert mined_block.difficulty == 1

@pytest.fixture
def prev_block():
    return Block.genesis()

@pytest.fixture
def block(prev_block):
    return Block.mine_block(prev_block, 'test_data')

def test_is_valid_block(prev_block, block):
    # Valid
    Block.is_valid_block(prev_block, block)

def test_is_valid_block_bad_prev_hash(prev_block, block):
    # Invalid prev_hash
    block.prev_hash = 'bad_prev_hash'
    with pytest.raises(Exception, match='Block prev_hash incorrect'):
        Block.is_valid_block(prev_block, block)

def test_is_valid_block_bad_proof_of_work(prev_block, block):
    # 'Proof of Work' requirement not met
    block.hash = 'fff'
    with pytest.raises(Exception, match="'Proof of Work' requirement not met"):
        Block.is_valid_block(prev_block, block)

def test_is_valid_block_jumped_difficulty(prev_block, block):
    # Jumped difficulty
    jumped_difficulty = prev_block.difficulty + 10
    block.difficulty = jumped_difficulty
    block.hash = f'{"0" * jumped_difficulty}abc123'
    with pytest.raises(Exception, match='Block difficulty must only adjust by 1'):
        Block.is_valid_block(prev_block, block)

def test_is_valid_block_bad_hash(prev_block, block):
    # Invalid hash
    block.hash = '00000000000000000000000123abc'
    with pytest.raises(Exception, match='Block hash incorrect'):
        Block.is_valid_block(prev_block, block)

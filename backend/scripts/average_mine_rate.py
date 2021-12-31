from time import time_ns
from backend.blockchain.blockchain import Blockchain
from backend.config import SECONDS


# -- TESTING AND EXPERIMENTATION -- #

blockchain = Blockchain()
times = []

# Test the average mining rate
# Should converge to MINE_RATE
for i in range(1000):
    start_time = time_ns()
    blockchain.add_block(i)
    end_time = time_ns()
    
    time_to_mine = (end_time - start_time) / SECONDS
    times.append(time_to_mine)

    average_time = sum(times) / len(times)

    print(f'Difficulty: {blockchain.chain[-1].difficulty}')
    print(f'Time to mine: {time_to_mine}s')
    print(f'Average time to mine: {average_time}s\n')

# -- END TESTING AND EXPERIMENTATION -- #

from backend.util.crypto_hash import crypto_hash


def test_crypto_hash():
    # Support arguments of different types
    assert crypto_hash(1, [2, 3, 4], 'five') == '7f50760053c473080a73863af4d0c258ca04fb652a279554c91ca7def587020e'

    # Data in different order yields different hash
    assert crypto_hash(1, [2, 3, 4], 'five') != crypto_hash([2, 3, 4], 'five', 1)
    
    # Regression test hash accuracy
    assert crypto_hash('foo') == 'b2213295d564916f89a6a42455567c87c3f480fcd7a1c15e220f17d7169a790b'
    
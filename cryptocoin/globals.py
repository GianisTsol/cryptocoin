VERSION = 1

MAX_NONCE = 2 ** 32  # 4 billion
BLOCK_TIME = 4 * 60  # 4 minutes

GENESIS = {
    "height": 0,
    "hash": "0000093159910241ca872fdace67fbd9c058335170fee7416bd67c8014bcae51",
    "txs": [],
    "nonce": 1530704,
    "diff": 20,
    "prev": "0000000000000000000000000000000000000000000000000000000000000000",
    "time": 1642943236,
    "version": "0000",
}

##########################

MINER_THREADS = 16

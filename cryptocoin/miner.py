from .block import Block, Tx
from .globals import *
import time
import hashlib


class Miner:
    def __init__(self, chain, network):
        self.chain = chain
        self.net = network
        self.public = 0

    def proof_of_work(sel, header, difficulty_bits):
        target = 2 ** (256 - difficulty_bits)
        for nonce in range(MAX_NONCE):
            hash_result = hashlib.sha256(f"{header}{nonce}".encode()).hexdigest()

            if int(hash_result, 16) < target:
                return (hash_result, nonce)

        return None, nonce

    def coinbase_tx(self, block):
        rew = block.get_reward()

        tx = Tx(
            src={
                "send": -1,
                "amount": rew,
                "recv": block.author,
                "fee": 0,
                "sig": "",
                "time": block.time,
                "hash": 0,
            }
        )

        tx.hash = tx.calculate_hash()
        return tx

    def calculate_diff(self, block):
        diff = block.prev.diff

        lastblocktime = BLOCK_TIME + 1
        if len(self.chain.chain) > 1:
            lastblocktime = block.prev.time - block.prev.prev.time

        if lastblocktime < BLOCK_TIME:
            diff += 1
        elif lastblocktime < BLOCK_TIME:
            diff -= 1
        return diff

    def mine(self):
        block = Block(self.chain.chain[-1])
        block.height = block.prev.height + 1
        block.time = time.time()
        block.diff = self.calculate_diff(block)
        block.author = self.public
        block.txs = self.net.pending
        block.txs.append(self.coinbase_tx(block))

        header = block.header()

        # this takes time
        hash_result, nonce = self.proof_of_work(header, block.diff)

        block.hash = hash_result
        block.nonce = nonce

        return block

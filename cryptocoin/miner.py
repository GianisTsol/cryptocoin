from .block import Block, Tx
from .globals import *
import time
import hashlib
import threading
import multiprocessing as mp
from . import crypto_funcs as cf


def proof_of_work(header, difficulty_bits, r=(0, MAX_NONCE)):
    target = 2 ** (256 - difficulty_bits)
    for nonce in range(r[0], r[1]):
        hash_result = hashlib.sha256(f"{header}{nonce}".encode()).hexdigest()

        if int(hash_result, 16) < target:
            return (hash_result, nonce)

    return None, 0


class Miner:
    def __init__(self, chain, network):
        self.chain = chain
        self.net = network
        self.address = 0
        self.flag = True

    def coinbase_tx(self, block):
        rew = block.get_reward()

        tx = Tx(
            src={
                "send": -1,
                "amount": rew,
                "recv": self.address,
                "fee": 0,
                "key": "",
                "sig": "",
                "time": block.time,
                "hash": 0,
            }
        )

        tx.hash = tx.calculate_hash()
        return tx

    def calculate_diff(self, block):
        diff = self.chain.get_block(-1).diff

        lastblocktime = BLOCK_TIME + 1
        if len(self.chain.chain) > 1:
            lastblocktime = self.chain.get_block(-1).time - self.chain.get_block(-2).time

        if lastblocktime < BLOCK_TIME:
            diff += 1
        elif lastblocktime < BLOCK_TIME:
            diff -= 1
        return diff

    def get_thread_range(self, i):
        NONCE_PER_THREAD = MAX_NONCE // MINER_THREADS

        return ((i - 1) * NONCE_PER_THREAD, i * NONCE_PER_THREAD)

    def reload(self):
        self.flag = False

    @staticmethod
    def worker(*args):
        header, difficulty_bits, r, return_dict = args
        res = proof_of_work(header, difficulty_bits, r)
        return_dict["res"] = res

    def mine(self):
        txs = [i for i in self.net.pending.copy() if i.mine_valid(self.chain.chain)]
        block = Block()
        block.prev = self.chain.chain[-1].hash
        block.height = self.chain.height() + 1
        block.time = int(time.time())
        block.diff = self.calculate_diff(block)
        block.txs = txs

        block.txs.append(self.coinbase_tx(block))

        header = block.header()

        # this takes time
        threads = []
        pool = mp.Pool(mp.cpu_count())

        manager = mp.Manager()
        return_dict = manager.dict()

        for i in range(1, MINER_THREADS):
            p = mp.Process(
                target=self.worker,
                args=[header, block.diff, self.get_thread_range(i), return_dict],
            )
            p.start()
            threads.append(p)

        while "res" not in return_dict:
            if not self.flag:
                return_dict["res"] = 0, 0
                break  # in case new block is found, stop mining

        for i in threads:
            i.terminate()
            i.join()

        hash_result, nonce = return_dict["res"]
        pool.close()

        block.hash = hash_result
        block.nonce = nonce

        return block

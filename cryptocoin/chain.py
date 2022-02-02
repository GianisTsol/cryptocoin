import hashlib
import json
from . import crypto_funcs as cf
import time

from .block import Block, Tx
from .globals import *


class Chain:
    def __init__(self):
        self.chain = []
        self.height = 0
        self.genesis()

    def genesis(self):
        self.chain.append(Block(GENESIS))

    def load(self):
        with open("chain.json", "r") as f:
            chain = json.load(f)
            for i in chain:
                self.add_block(Block(i))

    def save(self):
        with open("chain.json", "w") as f:
            # dump all except genesis
            json.dump(self.chain[1:], f, default=lambda x: x.dict())

    def validate(self, n=0):
        prev = self.height + 1
        if n == 0 or n > self.height:
            n = self.height

        for i in list(reversed(self.chain))[1:n:1]:
            prev -= 1
            if i.height != prev:
                print(f"HEIGHT INCONSISTANCY CHAIN INVALID at block {prev}")
                return False
            if i.prev != self.chain[i.height - 1].hash:
                print("HASH INCONSISTANCY CHAIN INVALID")
                return False
            if not i.valid():
                print("BLOCK NOT VALID")
                return False
        return True

    def get_block(self, index):
        if index < self.height:
            return self.chain[index]
        else:
            return None

    def add_block(self, block):
        if type(block) == dict:
            block = Block(block)
        elif type(block) == Block:
            pass
        else:
            return

        if block.valid():
            self.height = block.height
            self.chain.append(block)
            return True

        return False

    def purge_block(self):
        self.chain.pop(-1)
        self.height -= 1

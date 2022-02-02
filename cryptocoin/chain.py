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
        self.chain.append(Block(None, GENESIS))

    def load(self):
        with open("chain.json", "r") as f:
            chain = json.load(f)
            for i in chain:
                self.add_block(Block(self.chain[-1], i))

    def save(self):
        with open("chain.json", "w") as f:
            # dump all except genesis
            json.dump(self.chain[1:], f, default=lambda x: x.dict())

    def validate(self):
        prev = 0
        # genesis block has no valid prev objand cause errors
        for i in self.chain[1:]:
            prev += 1
            if i.height != prev:
                print("HEIGHT INCONSISTANCY CHAIN INVALID")
                return False
            if not i.valid():
                print("BLOCK NOT VALID")
                return False
        return True

    def get_block(self, index):
        if index < self.height:
            return self.chain[index]

    def add_block(self, block):
        if block.valid():
            self.height = block.height
            self.chain.append(block)

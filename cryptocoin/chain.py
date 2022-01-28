import hashlib
import json
from . import crypto_funcs as cf
import time

from .block import Block, Tx
from .globals import *


class Chain:
    def __init__(self):
        self.chain = []
        self.genesis()

    def genesis(self):
        self.chain.append(Block(self.chain, GENESIS))

    def load(self):
        with open("chain.json", "r") as f:
            chain = json.load(f)
            for i in chain:
                self.chain.append(Block(self.chain[-1], i))

    def save(self):
        with open("chain.json", "w") as f:
            # dump all except genesis
            json.dump(self.chain[1:], f, default=lambda x: x.__dict__())

    def validate(self):
        prev = -1
        for i in self.chain:
            prev += 1
            if i.height != prev:
                print("HEIGHT INCONSISTANCY CHAIN INVALID")
                return False
            if not i.valid():
                print("BLOCK NOT VALID")
                return False
        return True

    def new_block(self, b):
        new = Block(self.chain, b)
        if not new.valid():
            return False
        if new not in self.chain:
            self.chain.append(new)

    def new_tx(self, t):
        new = Tx(t)
        if not new.valid():
            return False
        self.pending.append(new)

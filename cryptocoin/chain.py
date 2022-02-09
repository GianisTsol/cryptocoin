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
        self.chain.append(Block(GENESIS))

    def load(self):
        with open("chain.json", "r") as f:
            chain = json.load(f)
            for i in chain:
                self.add_block(Block(i))
        self.cleanup()

    def save(self):
        self.cleanup()  # make sure chain is all valid before save
        with open("chain.json", "w") as f:
            # dump all except genesis
            json.dump(self.chain[1:], f, default=lambda x: x.dict())

    def height(self):
        return self.chain[-1].height

    def validate(self, n=2):
        if n == 0 or n > self.height():
            n = self.height()

        chain = self.chain[1:]
        prev = 1
        for i in chain:
            if i.height != prev:
                print(f"HEIGHT INCONSISTANCY CHAIN INVALID at block {prev} - {i.height}")
                return False
            if i.prev != self.chain[i.height - 1].hash:
                print("HASH INCONSISTANCY CHAIN INVALID")
                return False
            if not i.valid():
                print("BLOCK NOT VALID")
                return False
            prev += 1
        return True

    def cleanup(self):
        while not self.validate(100):
            print("PURGING...")
            self.purge_block()

    def get_block(self, index):
        if index <= self.height():
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
            if block.height == self.chain[-1].height + 1:
                self.chain.append(block)

        # self.cleanup()  # make usre all is well and if not fix it

    def purge_block(self):
        if self.height() > 0:
            new = len(self.chain)
            self.chain.pop(-1)
            if len(self.chain) == new:
                print("TDFFFFF")

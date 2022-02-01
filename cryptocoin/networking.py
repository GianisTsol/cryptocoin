from pythonp2p import Node
from .block import Block, Tx
import json
import time


class Network(Node):
    def initialize(self, chain):
        self.pending = []
        self.chain = chain
        self.height = len(chain.chain) - 1

    def on_connect(self, node):
        self.send_message("height", self.chain.height)

    def on_message(self, d):
        print(d)
        if "data" in d and "type" in d:
            data = d["data"]
            type = d["type"]
        else:
            return
        if type == "block":
            print("BLOCK")
            self.new_block(data)
        elif type == "tx":
            self.new_tx(data)
        elif type == "sync":
            if 0 < data <= self.chain.chain[-1].height:
                self.send_message("block", self.chain.chain[data].dict())
        elif type == "getheight":
            self.send_message("height", self.chain.chain[-1].height)
        elif type == "height":
            if data > self.height:
                try:
                    self.height = int(data)
                except ValueError:
                    return
                self.sync()

    def sync(self):
        for i in range(len(self.chain), self.height):
            self.send_message("sync", i)

    def new_block(self, b):
        if type(b) != dict:
            return
        try:
            new = Block(self.chain.chain[-1], b)
        except:
            print("AAAA")
            return
        if not new.valid():
            return False
        if new not in self.chain.chain:
            self.chain.add_block(new)

    def new_tx(self, t):
        if type(t) != dict:
            return
        try:
            new = Tx(t)
        except:
            return

        if not new.valid():
            return False
        self.pending.append(new)

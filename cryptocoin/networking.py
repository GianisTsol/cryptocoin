from . import p2pbase
from .block import Block, Tx


class Network(p2pbase.Node):
    def initialize(self, chain):
        self.pending = []
        self.chain = chain

    def on_message(self, d):
        data = d["data"]
        type = d["type"]
        if type == "block":
            self.new_block(data["block"])
        elif type == "tx":
            self.new_tx(data["tx"])
        elif type == "sync":
            if data <= len(self.chain.chain):
                self.message("block", self.chain.chain[data].dict())
        elif type == "getheight":
            self.message("height", self.chain.chain[-1].height)

    def new_block(self, b):
        if type(b) != dict:
            return
        try:
            new = Block(self.chain.chain, b)
        except:
            return
        if not new.valid():
            return False
        if new not in self.chain.chain:
            self.chain.chain.append(new)

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

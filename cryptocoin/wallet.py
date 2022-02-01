from .block import Tx
from . import crypto_funcs as cf
import hashlib
import base64


class Wallet:
    def __init__(self, chain, peer):
        self.public = None
        self.private = None
        self.address = None

        self.chain = chain
        self.peer = peer

        self.pending = []

    def save(self):
        with open("wallet.pem", "wb") as f:
            f.write(cf.save_key(self.private))

    def load(self):
        with open("wallet.pem", "rb") as f:
            self.private, self.public = cf.load_key(f.read())
            self.address = self.public

    def new_transaction(self, to, amount, fee):
        if not self.get_balance(self.public) >= amount:
            return False
        tx = Tx()
        tx.transfer(self.public, to, amount, fee)
        tx.confirm(self.private)
        self.pending.append(tx)
        return True

    def publish_txs(self):
        for i in self.pending:
            if i.valid():
                self.peer.message("tx", i)

    def get_balance(self, wallet):
        balance = 0
        for i in self.chain.chain:
            for j in i.txs:
                if j.recv == wallet:
                    balance += j.amount - j.fee
        return balance

    def key_valid(self, key):
        pass  # TODO

from .globals import *
import hashlib
import math
import base64
from . import crypto_funcs as cf


class Tx:
    def __init__(self, src=None):
        self.send = ""  # wallet address of sender
        self.amount = 0
        self.fee = 0
        self.recv = ""  # wallet address of reciever
        self.key = ""
        self.sig = ""  # hash signed w send key
        self.hash = ""  # HASH IN INT 16
        self.time = 0

        if src:
            self.load(src)

    def load(self, s):
        self.send = s["send"]
        self.amount = s["amount"]
        self.fee = s["fee"]
        self.recv = s["recv"]
        self.key = s["key"]
        self.sig = s["sig"]
        self.hash = s["hash"]
        self.time = s["time"]

    def header(self):
        return f"{self.send}{self.amount}{self.recv}{self.time}{self.fee}"

    def calculate_hash(self):
        digest = self.header().encode()
        return base64.b64encode(hashlib.sha256(digest).digest()).decode()

    def mine_valid(self, chain):
        if not self.time < chain[-10].time:
            return False

        balance = 0
        for i in chain:
            for j in i.txs:
                if j.hash == self.hash:
                    return False
                if j.recv == wallet:
                    balance += j.amount - j.fee
        if balance > self.amount:
            return True

    def valid(self):
        # dont check sig on coinbase
        if self.send == -1:
            signed = True
            addr = True
        else:
            signed = cf.verify(self.hash, self.sig, self.key)
            addr = self.send == hashlib.sha256(self.key.encode()).hexdigest()

        checks = [
            self.hash == self.calculate_hash(),
            self.amount >= self.fee,
            signed,
            addr,
        ]
        return all(checks)

    def transfer(self, send, to, amount, fee):
        self.send = send
        self.to = to
        self.amount = amount
        self.fee = fee

    def confirm(self, private_key):
        self.hash = self.calculate_hash()
        self.sig = cf.sign(self.hash, private_key)

    def __hash__(self):
        return self.calculate_hash()

    def dict(self):
        return {
            "send": self.send,
            "recv": self.recv,
            "key": self.key,
            "amount": self.amount,
            "fee": self.fee,
            "sig": self.sig,
            "hash": self.hash,
            "time": self.time,
        }

    def __str__(self):
        return str(self.dict())

    def __repr__(self):
        return self.__str__()


class Block:
    def __init__(self, src=None):

        self.height = 0
        self.hash = 0
        self.prev = ""
        self.txs = []
        self.nonce = ""
        self.diff = 0
        self.time = 0
        self.version = VERSION

        if src:
            self.load(src)

    def load(self, s):
        self.height = s["height"]
        self.hash = s["hash"]
        self.prev = s["prev"]
        self.nonce = s["nonce"]
        self.diff = s["diff"]
        self.time = int(s["time"])
        self.version = s["version"]

        for i in s["txs"]:
            self.txs.append(Tx(i))

    def header(self):
        return f"{str(self.version).zfill(4)}{self.prev}{self.txs_hash()}{str(self.time).zfill(10)}{str(self.diff).zfill(3)}{self.nonce}"

    def get_reward(self):
        rew = 1
        for i in self.txs:
            if i.send != -1:
                rew += i.fee
        return rew

    def valid(self):
        header = self.header()

        if not self.hash == hashlib.sha256(header.encode()).hexdigest():
            print(f"HASH DOESNT MATCH FOR BLOCK {self.height}")
            return False

        for i in self.txs:
            if not i.valid():
                print("Invalid TX")
                return False

        coinbase = False
        for i in self.txs:
            if i.send == -1:
                if not coinbase:
                    coinbase = True
                    if not i.amount == self.get_reward() and not i.fee == 0:
                        return False
                else:
                    return False  # TOO MANY COINBASE TXS
        return True

    def txs_hash(self):
        if len(self.txs) > 0:
            txs = "".join([i.hash for i in self.txs]).encode()
        else:
            txs = b""
        txs = hashlib.sha256(txs).hexdigest()
        return txs

    def dict(self):
        return {
            "height": self.height,
            "hash": self.hash,
            "prev": self.prev,
            "txs": [i.dict() for i in self.txs],
            "nonce": self.nonce,
            "diff": self.diff,
            "time": int(self.time),
            "version": self.version,
        }

    def __str__(self):
        return f"({self.height}, {self.hash})"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return self.hash

from .globals import *
import hashlib


class Tx:
    def __init__(self, src=None):
        self.send = 0  # wallet address of sender/reciever
        self.amount = 0
        self.fee = 0
        self.recv = 0  # in/out, 0,1
        self.sig = 0  # hash signed w send key
        self.hash = 0  # HASH IN INT 16
        self.time = 0

        if src:
            self.load(src)

    def load(self, s):
        self.send = s["send"]
        self.amount = s["amount"]
        self.fee = s["fee"]
        self.recv = s["recv"]
        self.sig = s["sig"]
        self.hash = s["hash"]
        self.time = s["time"]

    def header(self):
        return f"{self.send}{self.amount}{self.recv}{self.time}{self.fee}"

    def calculate_hash(self):
        digest = self.header().encode()
        return hashlib.sha256(digest).hexdigest()

    def valid(self):
        # dont check sig on coinbase
        if self.send == -1:
            signed = True
        else:
            signed = cf.verify(self.sig, self.send)

        return self.hash == self.calculate_hash() and self.amount >= self.fee and signed

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
    def __init__(self, prev, src=None):

        self.height = 0
        self.hash = 0
        self.prev = prev  # object of prev block
        self.txs = []
        self.nonce = ""
        self.diff = 0
        self.time = 0
        self.version = VERSION
        self.author = 0

        if src:
            self.load(src)

    def load(self, s):
        self.height = s["height"]
        self.hash = s["hash"]
        if not self.prev:
            self.prev = s["prev"]
        self.nonce = s["nonce"]
        self.diff = s["diff"]
        self.time = s["time"]
        self.version = s["version"]
        self.author = s["author"]

        for i in s["txs"]:
            self.txs.append(Tx(i))

    def header(self):
        return f"{self.prev}{self.version}{self.txs_hash()}{self.time}{self.diff}{self.author}{self.nonce}"

    def get_reward(self):
        rew = 0  # TODO: ADD BLOCK REWARD SYSTEM AND SUPPLY LIMIT
        for i in self.txs:
            if i.send != -1:
                rew += i.fee
        return rew

    def valid(self):
        header = self.header()

        if not self.height == self.prev.height + 1:
            return False

        if not self.hash == hashlib.sha256(header.encode()).hexdigest():
            print(f"HASH DOESNT MATH FOR BLOCK {self.height}")
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
                    if not i.amount == self.get_reward() and i.fee == 0 and i.recv == self.author:
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
            "prev": self.prev.hash,
            "txs": [i.dict() for i in self.txs],
            "nonce": self.nonce,
            "diff": self.diff,
            "time": self.time,
            "version": self.version,
            "author": self.author,
        }

    def __str__(self):
        return f"({self.height}, {self.hash})"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return self.hash

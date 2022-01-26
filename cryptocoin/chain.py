import hashlib
import json
from . import crypto_funcs as cf
import time
from json import JSONEncoder

VERSION = 1


MAX_NONCE = 2 ** 32  # 4 billion
BLOCK_TIME = 4 * 60  # 4 minutes

GENESIS = {
    "height": 0,
    "hash": "000000b7cc1192ad69029d305283aa554a6fe4e26266b603f32781f8c0e5a8a1",
    "txs": [],
    "nonce": 15999950,
    "diff": 23,
    "prev": 0,
    "time": 1642943236,
    "version": 0,
    "author": "x",
}


def proof_of_work(header, difficulty_bits):
    target = 2 ** (256 - difficulty_bits)
    for nonce in range(MAX_NONCE):
        hash_result = hashlib.sha256(f"{header}{nonce}".encode()).hexdigest()

        if int(hash_result, 16) < target:
            return (hash_result, nonce)

    return None, nonce


class Block:
    def __init__(self, chain, src=None):

        self.chain = chain

        self.height = 0
        self.hash = 0
        self.prev = 0
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
        self.prev = s["prev"]
        self.nonce = s["nonce"]
        self.diff = s["diff"]
        self.time = s["time"]
        self.version = s["version"]
        self.author = s["author"]

        for i in s["txs"]:
            self.txs.append(Tx(i))

    @staticmethod
    def header(self):
        return f"{self.prev}{self.version}{self.txs_hash()}{self.time}{self.diff}{self.author}{self.nonce}"

    def valid(self):
        header = self.header(self)

        if not self.height == self.chain[self.height - 1].height:
            return False

        if not self.hash == hashlib.sha256(header.encode()).hexdigest():
            print(f"HASH DOESNT MATH FOR BLOCK {self.height}")
            return False

        for i in self.txs:
            if not i.valid():
                return False
        return True

    def txs_hash(self):
        if len(self.txs) > 0:
            txs = int("".join([i.hash for i in self.txs]), 16)
        else:
            txs = b""
        txs = hashlib.sha256(txs).hexdigest()
        return txs

    def calculate_diff(self):
        diff = self.chain[-1].diff

        lastblocktime = BLOCK_TIME + 1
        if len(self.chain) > 1:
            lastblocktime = self.chain[-1].time - self.chain[-2].time

        if lastblocktime < BLOCK_TIME:
            diff += 1
        elif lastblocktime < BLOCK_TIME:
            diff -= 1
        return diff

    def mine(self):
        self.height = self.chain[-1].height + 1
        self.prev = self.chain[-1].hash
        self.time = time.time()
        self.diff = self.calculate_diff()
        header = self.header(self)
        print(self.diff)
        hash_result, nonce = proof_of_work(header, self.diff)

        self.hash = hash_result
        self.nonce = nonce

    def __dict__(self):
        return {
            "height": self.height,
            "hash": self.hash,
            "prev": self.prev,
            "txs": self.txs,
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

    @staticmethod
    def header(self):
        return f"{self.send}{self.amount}{self.recv}{self.time}{self.fee}"

    def calculate_hash(self):
        digest = self.header(self)
        return hashlib.sha256(digest).digest()

    def valid(self):
        return (
            self.hash == self.calculate_hash()
            and cf.verify(self.sig, self.send)
            and self.amount > self.fee
        )

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

    def __str__(self):
        return {
            "send": self.send,
            "amount": self.amount,
            "fee": self.fee,
            "sig": self.sig,
            "hash": self.hash,
            "time": self.time,
        }

    def __repr__(self):
        return self.__str__()


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
                self.chain.append(Block(self.chain, i))

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

    def mine(self):
        new = Block(self.chain)
        new.mine()
        self.chain.append(new)
        print(self.validate())


class Wallet:
    def __init__(self, chain, peer):
        self.public = None
        self.private = None
        self.peer = peer

        self.pending = []

    # TODO: add load and save wallet keys
    def new_transaction(self, to, amount, fee):
        # TODO: ADD KEY VERIFICATION ETC
        tx = Tx()
        tx.transfer(self.public, to, amount, fee)
        tx.confirm(self.pivate)
        self.pending.append(tx)

    def publish_txs(self):
        for i in self.pending:
            if i.valid():
                self.peer.message("tx", i)

    def get_balance(self, wallet):
        balance = 0
        for i in self.chain:
            for j in i.txs:
                if j.to == wallet:
                    balance += j.amount - j.fee

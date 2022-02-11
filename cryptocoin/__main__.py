from .chain import Chain
from .networking import Network
from .wallet import Wallet
from .miner import Miner
from . import crypto_funcs as cf
import random

chain = Chain()
chain.load()

peer = Network(chain, port=random.randint(65400, 65499))
wallet = Wallet(chain, peer)
wallet.load()

while True:
    inp = input("> ")

    if inp == "mine":
        miner = Miner(chain, peer)
        miner.address = wallet.address
        new = miner.mine()
        chain.add_block(new)
        new.dict()
        peer.send_block(new.dict())

    if inp == "stop":
        peer.stop()

    if inp == "addr":
        print(peer.addr)

    if inp == "save":
        chain.save()

    if inp == "chain":
        print(chain.chain)
        chain.cleanup()

    if inp == "sync":
        peer.send_hsync()

    if inp == "keygen":
        public, private = cf.generate_keys()
        wallet.public = public
        wallet.private = private
        wallet.calc()
        # wallet.save()

    if inp == "save":
        chain.save()
        print(chain.chain)

    if "node " in inp:
        inp = inp.replace("node ", "")
        ip, port = inp.split(":")
        peer.send_pulse((ip, int(port)))

    if inp == "wallet":
        print(f"wallet: {wallet.address}")
        print(f"balance: {wallet.get_balance(wallet.address)} Coins")

    if inp == "tx":
        to = input("reciever: ")
        try:
            amount = int(input("Amount (/1000): "))
            fee = int(input("Fee: "))
            wallet.new_transaction(to, amount, fee)
            wallet.publish_txs()
        except ValueError:
            print("error")

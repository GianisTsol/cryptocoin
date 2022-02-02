from .chain import Chain
from .networking import Network
from .wallet import Wallet
from .miner import Miner
from . import crypto_funcs as cf

chain = Chain()
chain.load()

peer = Network(chain)
wallet = Wallet(chain, peer)
wallet.load()

while True:
    inp = input("> ")

    if inp == "mine":
        miner = Miner(chain, peer)
        miner.address = wallet.public
        new = miner.mine()
        chain.add_block(new)
        peer.send_block(new.dict())

    if inp == "start":
        peer.start()

    if inp == "stop":
        peer.stop()

    if inp == "save":
        chain.save()

    if inp == "chain":
        print(chain.chain)
        print(chain.validate())

    if inp == "sync":
        peer.send_hsync()

    if inp == "keygen":
        public, private = cf.generate_keys()
        wallet.public = public
        wallet.private = private
        wallet.save()

    if inp == "save":
        chain.save()
        print(chain.chain)

    if "node " in inp:
        peer.send_pulse((inp.replace("node ", ""), 65444))

    if inp == "wallet":
        print(f"wallet: {wallet.address}")
        print(f"balance: {wallet.get_balance(wallet.public)/1000} Coins")

    if inp == "tx":
        to = input("reciever: ")
        try:
            amount = int(input("Amount (/1000): "))
        except ValueError:
            print("invalid amount ;)")
        fee = int(input("Fee: "))
        wallet.new_transaction(to, amount, fee)
        wallet.publish_txs()

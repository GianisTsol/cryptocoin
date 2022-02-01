from .chain import Chain
from .networking import Network
from .wallet import Wallet
from .miner import Miner
from . import crypto_funcs as cf

chain = Chain()
chain.load()

peer = Network()
peer.initialize(chain)
wallet = Wallet(chain, peer)
wallet.load()

# peer.start()

while True:
    inp = input("> ")

    if inp == "mine":
        miner = Miner(chain, peer)
        miner.address = wallet.public
        new = miner.mine()
        peer.message("block", new.dict())
        chain.add_block(new)
        print(new.dict())

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
        peer.message("getheight", chain.chain[-1].height)

    if inp == "keygen":
        public, private = cf.generate_keys()
        wallet.public = public
        wallet.private = private
        wallet.save()

    if inp == "save":
        chain.save()
        print(chain.chain)

    if "connect " in inp:
        peer.connect_to(inp.replace("connect ", ""))

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

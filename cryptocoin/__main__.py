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
miner = Miner(chain, peer)
miner.public = wallet.public

while True:
    inp = input("> ")

    if inp == "mine":
        new = miner.mine()
        peer.message("block", new.dict())
        chain.add_block(new)
        print(new)

    if inp == "start":
        peer.start()

    if inp == "stop":
        peer.stop()

    if inp == "save":
        chain.save()
    if inp == "chain":
        print(chain.chain)
    if inp == "sync":
        peer.message("sync", chain.chain[-1].height)

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

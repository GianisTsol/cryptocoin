from .chain import Chain
from . import networking
from . import crypto_funcs as cf


class Peer(networking.Node):
    def on_message(self, d):
        data = d["data"]
        type = d["type"]
        if type == "block":
            chain.new_block(data["block"])
        elif type == "tx":
            chain.new_tx(data["tx"])
        elif type == "sync":
            if data <= len(chain.chain):
                self.message("block", chain.chain[data])
        elif type == "getheight":
            self.message("height", chain.chain[-1].height)


peer = Peer()

chain = Chain()
chain.load()


public = None
private = None

while True:
    inp = input("> ")

    if inp == "mine":
        chain.mine()
        peer.message("block", chain[-1])

    if inp == "start":
        peer.start()

    if inp == "stop":
        peer.stop()

    if inp == "save":
        chain.save()
        print(chain.chain)
    if inp == "chain":
        print(chain.chain)
    if inp == "sync":
        peer.message("sync", "")

    if inp == "keygen":
        public, private = cf.generate_keys()

    if inp == "connect":
        peer.connect(inp.replace("connect ", ""))

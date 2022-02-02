# from .block import Block, Tx
import json
import time
import socket
import threading

EVENT = "e"
EVENT = "t"
CONTENT = "d"
CONTENT = "c"


class Network:
    def __init__(self, chain, port=65444):
        super(Network, self)
        self.chain = chain
        self.known = []

        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sock.bind(("", self.port))

        self.recv_thread = threading.Thread(target=self.mainloop)
        self.recv_thread.start()

    def send(self, message, addr):
        message = json.dumps(message).encode()
        self.sock.sendto(message, addr)

    def net_send(self, message):
        for i in self.known:
            self.send(message, i)

    def mainloop(self):
        new = self.sock.recvfrom(1024)
        self.handle_msgs(new)

    def handle_msgs(self, msg):
        addr = msg[1]
        raw = json.loads(msg[0].decode())

        if type(raw) is not dict:
            return
        if EVENT not in raw and CONTENT not in raw:
            return

        event = raw[EVENT]
        data = raw[CONTENT]

        event_map = {
            "block": self.net_block,
            "tx": self.net_tx,
            "sync": self.net_sync,
            "height": self.net_height,
            "hsync": self.net_hsync,
            "peers": self.net_peers,
            "pulse": self.net_pulse,
            "beat": self.net_beat,
        }

        if event in event_map:
            event_map[event](data, addr)

    def send_peers(self):
        self.net_send({EVENT: "sync", CONTENT: self.known})

    def send_sync(self, height):
        self.net_send({EVENT: "sync", CONTENT: height})

    def send_hsync(self):
        self.net_send({EVENT: "hsync", CONTENT: ""})

    def send_pulse(self, addr):
        self.send({EVENT: "pulse", CONTENT: ""}, addr)

    def net_beat(self, data, addr):
        if addr in self.waiting:
            self.known.append(addr)

    def net_pulse(self, data, addr):
        if addr not in self.known:
            self.known.append(addr)
        self.send({EVENT: "beat", CONTENT: ""}, addr)

    def net_peers(self, data, addr):
        if type(data) is not list:
            return
        for i in data:
            if type(i) is not tuple:
                return
            if type(i[0]) is not str:
                return
            if type(i[1]) is not int:
                return
            self.known.append(i)

    def net_block(self, data, addr):
        # TODO: security, validation
        if self.chain.get_block(data["height"]) is None:
            self.chain.add_block(data)

    def net_tx(self, data, addr):
        # TODO add to miner pending
        pass

    def net_sync(self, data, addr):
        self.send({EVENT: "block", CONTENT: self.chain.get_block(data)}, addr)

    def net_height(self, data, addr):
        if self.chain.height < data:
            for i in range(data - self.chain.height):
                self.send_sync(i)

    def net_hsync(self, data, addr):
        self.send({EVENT: "height", CONTENT: self.chain.height}, addr)

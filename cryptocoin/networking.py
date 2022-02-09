from .block import Block, Tx
import json
import time
import socket
import threading
import hashlib

EVENT = "e"
CONTENT = "c"


class Network:
    def __init__(self, chain, port=65444):
        super(Network, self)
        self.daemon = True

        self.chain = chain
        self.known = []
        self.waiting = []
        self.sent = []

        # pending txs
        self.pending = []

        self.addr = ("0.0.0.0", port)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1)
        self.sock.bind(self.addr)

        self.terminate_flag = threading.Event()
        self.recv_thread = threading.Thread(target=self.mainloop)
        self.recv_thread.start()

    def send(self, message, addr):
        print(message)
        try:
            message = json.dumps(message).encode()
            self.sock.sendto(message, addr)
        except socket.error as e:
            print("error " + str(e))

    def net_send(self, message, exc=[]):
        for i in self.known:
            if i not in exc:
                self.send(message, i)

    def stop(self):
        self.terminate_flag.set()

    def mainloop(self):
        while not self.terminate_flag.is_set():
            try:
                new = self.sock.recvfrom(1024)
                self.handle_msgs(new)
            except socket.error:
                pass

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
            "psync": self.net_psync,
            "pulse": self.net_pulse,
            "beat": self.net_beat,
        }

        to_forward = ("block", "tx")

        if event in event_map:
            event_map[event](data, addr)

        # forward
        if event in to_forward:
            h = hashlib.md5(json.dumps(raw).encode()).hexdigest()
            if h in self.sent:
                return
            self.sent.append(h)
            self.net_send(raw, exc=[addr, self.addr])

    # ############ SEND ################
    def send_block(self, data):
        self.net_send({EVENT: "block", CONTENT: data})

    def send_tx(self, data):
        self.net_send({EVENT: "tx", CONTENT: data})

    def send_peers(self, addr):
        self.send({EVENT: "peers", CONTENT: self.known}, addr)

    def send_psync(self, addr):
        self.send({EVENT: "psync", CONTENT: ""}, addr)

    def send_sync(self, height):
        self.net_send({EVENT: "sync", CONTENT: height})

    def send_hsync(self):
        self.net_send({EVENT: "hsync", CONTENT: ""})

    def send_pulse(self, addr):
        if addr not in self.waiting:
            self.waiting.append(addr)
        self.send({EVENT: "pulse", CONTENT: ""}, addr)

    # ############ RECEIVE #############
    def net_psync(self, data, addr):
        self.send_peers(addr)

    def net_beat(self, data, addr):
        if addr in self.waiting:
            self.known.append(addr)

    def net_pulse(self, data, addr):
        if addr not in self.known:
            self.known.append(addr)
        self.send({EVENT: "beat", CONTENT: ""}, addr)
        self.send_peers(addr)

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
        self.chain.add_block(data)

    def net_tx(self, data, addr):
        tx = Tx(data)
        if not tx.valid():
            return
        if tx not in self.pending:
            self.pending.append(tx)

    def net_sync(self, data, addr):
        if self.chain.get_block(data) is not None:
            self.send({EVENT: "block", CONTENT: self.chain.get_block(data).dict()}, addr)

    def net_height(self, data, addr):
        if self.chain.height() < data:
            for i in range(self.chain.height() + 1, data + 1):
                self.send_sync(i)

    def net_hsync(self, data, addr):
        self.send({EVENT: "height", CONTENT: self.chain.height()}, addr)

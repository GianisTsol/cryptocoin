import hashlib
import ipaddress
import json
import socket
import sys
import threading
import time
import uuid

from . import crypto_funcs as cf

msg_del_time = 30
PORT = 65432


class NodeConnection(threading.Thread):
    def __init__(self, main_node, sock, id, host, port):

        super(NodeConnection, self).__init__()

        self.host = host
        self.port = port
        self.main_node = main_node
        self.sock = sock
        self.terminate_flag = threading.Event()
        self.last_ping = time.time()
        # Variable for parsing the incoming json messages
        self.buffer = ""

        # The id of the connected node
        self.public_key = cf.load_key(id)
        self.id = id

        self.main_node.debug_print("Connection " + self.host + ":" + str(self.port))

    def send(self, data):
        try:
            self.sock.sendall(data.encode("utf-8"))

        except Exception as e:
            self.main_node.debug_print("Exception: " + str(e))
            self.terminate_flag.set()

    def stop(self):
        self.terminate_flag.set()

    def run(self):
        self.sock.settimeout(10.0)

        while not self.terminate_flag.is_set():
            if time.time() - self.last_ping > self.main_node.dead_time:
                self.terminate_flag.set()
                print("node" + self.id + " is dead")

            try:
                message = self.sock.recv(4096)
                if message == "ping":
                    self.last_ping = time.time()
                else:
                    self.main_node.node_message(self, message)

            except socket.timeout:
                pass

            except Exception as e:
                self.terminate_flag.set()
                self.main_node.debug_print(e)

            time.sleep(0.01)

        self.main_node.node_disconnected(self)
        self.sock.settimeout(None)
        self.sock.close()
        del self.main_node.nodes_connected[self.main_node.nodes_connected.index(self)]
        time.sleep(1)


class Node(threading.Thread):
    def __init__(self, host="", port=65432):
        super(Node, self).__init__()

        self.terminate_flag = threading.Event()
        self.pinger = Pinger(self)  # start pinger
        self.debug = True

        self.dead_time = 45  # time to disconect from node if not pinged, nodes ping after 20s

        self.host = host
        self.ip = host  # own ip, will be changed by connection later
        self.port = port

        self.nodes_connected = []

        self.msgs = {}  # hashes of recieved messages
        self.peers = []

        self.id = uuid.uuid4()

        self.max_peers = 10

        hostname = socket.gethostname()

        self.local_ip = socket.gethostbyname(hostname)

        self.banned = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.debug_print("Initialisation of the Node on port: " + str(self.port))
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(10.0)
        self.sock.listen(1)

    def debug_print(self, msg):
        if self.debug:
            print("[debug] " + str(msg))

    def network_send(self, message, exc=[]):
        for i in self.nodes_connected:
            if i.host not in exc:
                i.send(json.dumps(message))

    def connect_to(self, host, port=PORT):

        if not self.check_ip_to_connect(host):
            self.debug_print("connect_to: Cannot connect!!")
            return False

        if len(self.nodes_connected) >= self.max_peers:
            self.debug_print("Peers limit reached.")
            return True

        for node in self.nodes_connected:
            if node.host == host:
                print("[connect_to]: Already connected with this node.")
                return True

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))

            sock.send(self.id.encode("utf-8"))
            connected_node_id = sock.recv(1024).decode("utf-8")

            if self.id == connected_node_id:
                self.debug_print("Possible own ip: " + host)
                if ipaddress.ip_address(host).is_private:
                    self.local_ip = host
                else:
                    self.ip = host
                self.banned.append(host)
                sock.close()
                return False

            thread_client = self.create_new_connection(sock, connected_node_id, host, port)
            thread_client.start()
            self.nodes_connected.append(thread_client)
            self.node_connected(thread_client)

        except Exception as e:
            self.debug_print("connect_to: Could not connect with node. (" + str(e) + ")")

    def create_new_connection(self, connection, id, host, port):
        return NodeConnection(self, connection, id, host, port)

    def stop(self):
        self.terminate_flag.set()

    def run(self):
        self.pinger.start()
        while not self.terminate_flag.is_set():
            try:
                connection, client_address = self.sock.accept()

                connected_node_id = connection.recv(2048).decode("utf-8")
                connection.send(self.id.encode("utf-8"))

                if self.id != connected_node_id:
                    thread_client = self.create_new_connection(
                        connection,
                        connected_node_id,
                        client_address[0],
                        client_address[1],
                    )
                    thread_client.start()

                    self.nodes_connected.append(thread_client)

                    self.node_connected(thread_client)

                else:
                    connection.close()

            except socket.timeout:
                pass

            except Exception as e:
                raise e

            time.sleep(0.01)

        self.pinger.stop()
        for t in self.nodes_connected:
            t.stop()

        self.sock.close()
        print("Node stopped")

    def ConnectToNodes(self):
        for i in self.peers:
            if not self.connect_to(i, PORT):
                # delete wrong / own ip from peers
                del self.peers[self.peers.index(i)]

    def message(self, type, data, ex=[]):
        # time that the message was sent
        dict = {"type": type, "data": data}
        if "time" not in dict:
            dict["time"] = str(time.time())

        self.network_send(dict, ex)

    def send_peers(self):
        self.message("peers", self.peers)

    def check_validity(self, msg):
        if not ("time" in msg and "type" in msg and "data" in msg):
            return False

        return True

    def check_expired(self, dta):
        sth = str(dta)
        msghash = hashlib.md5(sth.encode("utf-8")).hexdigest().decode()

        if float(time.time()) - float(dta["time"]) < float(msg_del_time):
            if msghash not in self.msgs:
                self.msgs[msghash] = time.time()
                return False
        else:
            # if message is expired
            self.debug_print("expired:" + dta["msg"])
            return True

    def announce(self, dta, n):
        self.message(dta["type"], dta["data"], dta, ex=n)
        if len(self.msgs) > len(self.peers) * 20:
            for i in self.msgs.copy():
                if time.time() - self.msgs[i] > msg_del_time:
                    del self.msgs[i]

    def data_handler(self, dta, n):
        if self.check_expired(dta):
            return False
        else:
            self.announce(dta, n)

        type = dta["type"]
        data = dta["data"]

        if type == "peers":
            # peers handling
            for i in data:
                if self.check_ip_to_connect(i):
                    self.peers.append(i)

            self.debug_print("Known Peers: " + str(self.peers))
            self.ConnectToNodes()  # cpnnect to new nodes
            return True

        else:
            self.on_message(dta)

    def check_ip_to_connect(self, ip):
        if (
            ip not in self.peers
            and ip != ""
            and ip != self.ip
            and ip != self.local_ip
            and ip not in self.banned
        ):
            return True
        else:
            return False

    def on_message(self, data):
        self.debug_print("Incomig Message: " + data)

    def on_connect(self, n):
        pass

    def loadstate(self, file="state.json"):
        with open(file, "r") as f:
            peers = json.load(f)
        for i in peers:
            self.connect_to(i)

    def savestate(self, file="state.json"):
        with open(file, "w+") as f:
            json.dump(self.peers, f)

    def node_connected(self, node):
        self.debug_print("node_connected: " + node.id)
        if node.host not in self.peers:
            self.peers.append(node.host)
        self.send_peers()
        self.on_connect(node)

    def node_disconnected(self, node):
        self.debug_print("node_disconnected: " + node.id)
        if node.host in self.peers:
            self.peers.remove(node.host)

    def node_message(self, node, data):
        try:
            json.loads(data)
        except json.decoder.JSONDecodeError:
            self.debug_print(f"Error loading message from {node.id}")
            return
        self.data_handler(json.loads(data), [node.host, self.ip])


class Pinger(threading.Thread):
    def __init__(self, parent):
        self.terminate_flag = threading.Event()
        super(Pinger, self).__init__()
        self.parent = parent
        self.dead_time = 30  # time to disconect from node if not pinged

    def stop(self):
        self.terminate_flag.set()

    def run(self):
        print("Pinger Started")
        while not self.terminate_flag.is_set():  # Check whether the thread needs to be closed
            for i in self.parent.nodes_connected:
                i.send("ping")
                time.sleep(20)
        print("Pinger stopped")

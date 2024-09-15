# CryptoCoin - A Simplified Cryptocurrency & P2P Network

**CryptoCoin** is a decentralized cryptocurrency built using Python. This project includes a peer-to-peer (P2P) network, transaction handling, and block validation. The core functionalities cover basic transaction creation, signing, hashing, and validation, as well as node communication over a P2P network.

## Features

### Blockchain Core
- **Transactions**: Secure and validate transactions using cryptographic signatures.
- **Blocks**: Bundle transactions in blocks, which are connected to previous blocks to maintain blockchain integrity.
- **Hashing and Signatures**: Ensure secure and tamper-proof data by using SHA-256 hashing and cryptographic signing.

### P2P Node Network
- **Peer Discovery**: Connect to multiple peers and propagate transactions and blocks.
- **Ping-based Health Checks**: Ensure nodes are active by sending regular pings.
- **Message Broadcasting**: Send and receive messages, including peer information, through the network.
- **Connection Management**: Nodes automatically disconnect from inactive or unresponsive peers.

## Installation

### Prerequisites
- Python 3.x
- Install the required dependencies via `pip`:
  ```bash
  pip install -r requirements.txt

Cloning the Repository

Clone this repository to your local machine:
 ```bash
 git clone https://github.com/GianisTsol/cryptocoin.git
 cd cryptocoin
 ```
Usage

1. Running a Node

To start a node, you can use the Node class. Each node communicates with peers over a P2P network using sockets.

Example:
 ```python
 from cryptocoin.node import Node

 # Create a new node listening on a specific port
 my_node = Node(host="localhost", port=65432)
 my_node.start()  # Start the node

Nodes will automatically ping peers to check for connectivity and propagate messages across the network.

2. Transactions and Blocks

The core of the blockchain is built around Tx (Transaction) and Block classes.

Example for creating a transaction:
 ```python
 from cryptocoin.tx import Tx

 # Create a transaction object
 transaction = Tx()
 transaction.transfer(sender_address, receiver_address, amount, fee)

 # Confirm the transaction by signing it transaction.confirm(sender_private_key)

 # Validate the transaction
 if transaction.valid():
     print("Transaction is valid")

Blocks can contain multiple transactions and are used to build the chain. They connect to the previous block via hashes, ensuring chain integrity.

3. Peer Communication

Each node can connect to other peers via the connect_to() method. This allows nodes to exchange messages such as transactions, blocks, and peer lists.

Example for connecting to a peer:
 ```python
 my_node.connect_to("192.168.1.2", 65432)

4. Saving and Loading State

The node’s peer list can be saved and loaded from a file. This allows nodes to reconnect to previous peers on restart.

Save state:
 ```python
 my_node.savestate("state.json")

Load state:
 ```python
 my_node.loadstate("state.json")

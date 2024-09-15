CryptoCoin - A Simplified Cryptocurrency & P2P Network

CryptoCoin is a decentralized cryptocurrency built using Python. This project includes a peer-to-peer (P2P) network, transaction handling, and block validation. The core functionalities cover basic transaction creation, signing, hashing, and validation, as well as node communication over a P2P network.

Features

Blockchain Core

Transactions: Secure and validate transactions using cryptographic signatures.

Blocks: Bundle transactions in blocks, which are connected to previous blocks to maintain blockchain integrity.

Hashing and Signatures: Ensure secure and tamper-proof data by using SHA-256 hashing and cryptographic signing.


P2P Node Network

Peer Discovery: Connect to multiple peers and propagate transactions and blocks.

Ping-based Health Checks: Ensure nodes are active by sending regular pings.

Message Broadcasting: Send and receive messages, including peer information, through the network.

Connection Management: Nodes automatically disconnect from inactive or unresponsive peers.


Installation

Prerequisites

Python 3.x

Install the required dependencies via pip:

pip install -r requirements.txt


Cloning the Repository

Clone this repository to your local machine:

git clone https://github.com/GianisTsol/cryptocoin.git
cd cryptocoin

Usage

1. Running a Node

To start a node, you can use the Node class. Each node communicates with peers over a P2P network using sockets.

Example:

from cryptocoin.node import Node

# Create a new node listening on a specific port
my_node = Node(host="localhost", port=65432)
my_node.start()  # Start the node

Nodes will automatically ping peers to check for connectivity and propagate messages across the network.

2. Transactions and Blocks

The core of the blockchain is built around Tx (Transaction) and Block classes.

Example for creating a transaction:

from cryptocoin.tx import Tx

# Create a transaction object
transaction = Tx()
transaction.transfer(sender_address, receiver_address, amount, fee)

# Confirm the transaction by signing it
transaction.confirm(sender_private_key)

# Validate the transaction
if transaction.valid():
    print("Transaction is valid")

Blocks can contain multiple transactions and are used to build the chain. They connect to the previous block via hashes, ensuring chain integrity.

3. Peer Communication

Each node can connect to other peers via the connect_to() method. This allows nodes to exchange messages such as transactions, blocks, and peer lists.

Example for connecting to a peer:

my_node.connect_to("192.168.1.2", 65432)

4. Saving and Loading State

The node’s peer list can be saved and loaded from a file. This allows nodes to reconnect to previous peers on restart.

Save state:

my_node.savestate("state.json")

Load state:

my_node.loadstate("state.json")


Classes Overview

1. Tx (Transaction)

Represents a transaction in the blockchain.

Attributes:

send: Sender's wallet address.

amount: Transaction amount.

fee: Transaction fee.

recv: Recipient's wallet address.

sig: Digital signature.

hash: Transaction hash.


Key Methods:

load: Load transaction data.

calculate_hash: Calculates the transaction's hash using SHA-256.

valid: Verifies the transaction by checking the signature, hash, and amount.

confirm: Signs the transaction with the sender's private key.

transfer: Sets up the transaction details.



2. Block

Represents a block in the blockchain. A block contains multiple transactions and links to the previous block via its hash.

Attributes:

height: Block number in the chain.

hash: Block hash.

prev: Previous block’s hash.

txs: List of transactions in the block.

nonce: Nonce used for proof-of-work.

author: Miner of the block.


Key Methods:

load: Load block data.

valid: Verifies the block’s hash, transactions, and coinbase reward.

txs_hash: Computes the combined hash of all transactions in the block.



3. Node

The Node class handles peer-to-peer network communication, sending and receiving messages between nodes.

Attributes:

host: IP address or hostname of the node.

port: Port number on which the node listens for connections.

nodes_connected: List of currently connected nodes.

peers: List of known peer nodes.

id: Unique identifier for the node.




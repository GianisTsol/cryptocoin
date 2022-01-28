from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import base64
import json


def encrypt(message, key):
    message = json.dumps(message).encode("utf-8")
    cipher = PKCS1_OAEP.new(key)
    return base64.b64encode(cipher.encrypt(message)).decode("utf-8")


def decrypt(message, key):
    cipher = PKCS1_OAEP.new(key)
    message = cipher.decrypt(base64.b64decode(message))
    return json.loads(message)


def deserialize_key(key):
    key = base64.b64decode(key)
    return RSA.importKey(key)


def serialize_key(key):
    key = base64.b64encode(key.exportKey("DER")).decode("utf-8")
    return key


def save_key(key):
    return deserialize_key(key).exportKey("PEM")


def load_key(key):
    return serialize_key(RSA.importKey(key))


def generate_keys():
    private_key = RSA.generate(1024)
    public_key = private_key.publickey()

    return serialize_key(public_key), serialize_key(private_key)


def sign(message, private_key):
    if type(private_key) == str:
        private_key = deserialize_key(private_key)
    digest = SHA256.new()
    digest.update(str(message).encode("utf-8"))
    signer = PKCS1_v1_5.new(private_key)
    sig = signer.sign(digest)

    return base64.b64encode(sig).decode("utf-8")


def verify(message, sig, key):
    if type(private_key) == str:
        private_key = deserialize_key(private_key)
    digest = SHA256.new()
    digest.update(str(message).encode("utf-8"))
    verifier = PKCS1_v1_5.new(key)
    verified = verifier.verify(digest, base64.b64decode(sig))

    return verified

import hashlib
import base64


def public_to_address(key):
    return base64.b64encode(hashlib.sha256(key.encode()).digest()).decode()

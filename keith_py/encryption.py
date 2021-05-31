from cryptography.fernet import Fernet


def decrypt(message, key=b'ei5t2CQp9CfR33BMEgiRYwAdkwdutJ6v62gNoP3hVrQ='):
    return Fernet(key).decrypt(bytes(message, 'utf-8')).decode("utf-8")
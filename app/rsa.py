from collections import deque
from sympy import randprime, isprime, mod_inverse
from random import randint
from math import gcd, ceil
from pathlib import Path
import base64
import numpy as np
import time
import secrets
import rsa


class RSA:

    def __init__(self, private_key=None, public_key=None):
        self.private_key = private_key
        self.public_key = public_key

        if self.public_key is not None:
            self.key_length = self.public_key[0].bit_length()
            self.block_bytes_size = ceil(self.key_length / 8) - 1
        elif self.private_key is not None:
            self.key_length = self.private_key[0].bit_length()
            self.block_bytes_size = ceil(self.key_length / 8) - 1
        else:
            self.key_length = None
            self.block_bytes_size = None

    def generate_keys(self, size=None, common_e=None, min_e=None):
        common_e = True if common_e is None else common_e
        size = 2048 if size is None else size

        p = q = 1
        prime_size = size // 2
        i = 0
        while p == q or ((n := p * q).bit_length() != size):
            i += 1
            p = randprime(2 ** (prime_size - 1), 2 ** (prime_size - 0.7))
            q = randprime(2 ** (prime_size - 0.3), 2 ** prime_size)
            if i > 2 ** 16:
                raise ValueError(f"Exceeded allowed iterations while searching for p and q. Try even bit length\n")
        min_e = 2 ** (prime_size // 2) if min_e is None else min_e
        phi = (p - 1) * (q - 1)

        if min_e < 3 or min_e > phi - 1:
            raise ValueError("min_e must be greater than 3 and smaller than phi.\n")

        e = 2 ** 16 + 1 if common_e else randint(min_e, phi - 1)
        g = gcd(e, phi)
        i = 0
        while g != 1 or e > phi or i > 100:
            i += 1
            e = randint(min_e, phi - 1)
            g = gcd(e, phi)
            if i > 2 ** 16:
                raise ValueError(
                    f"Exceeded allowed iterations while searching for e. Use lower min_e value - currently {min_e}\n")
        # d = mod_inverse(e, phi)
        d = pow(e, -1, phi)

        self.public_key = (n, e)
        self.private_key = (n, d)
        self.key_length = size
        self.block_bytes_size = size // 8 - 1

        self.save_keys()

        return self.public_key, self.private_key

    def save_keys(self):
        if self.public_key is None or self.private_key is None:
            raise ValueError(f'One of the keys is None.\nPublic: {self.public_key}\nPrivate: {self.private_key}')

        path = Path(__file__).parent.parent.joinpath('keys.txt')
        key_bytes_len = ceil(self.key_length / 8)
        n = self.public_key[0].to_bytes(key_bytes_len, 'big')
        e = self.public_key[1].to_bytes(ceil(self.public_key[1].bit_length() / 8), 'big')
        d = self.private_key[1].to_bytes(ceil(self.private_key[1].bit_length() / 8), 'big')

        with path.open('ab') as f:
            f.write(base64.b64encode(n))
            f.write(b':')
            f.write(base64.b64encode(e))
            f.write(b'\t')
            f.write(base64.b64encode(n))
            f.write(b':')
            f.write(base64.b64encode(d))
            f.write(b'\n')

    def encrypt_ECB(self, data):
        if self.public_key is None:
            raise ValueError("Public key cannot be empty")
        original_len = len(data)
        ciphertext = []
        extended_bytes = []

        for i in range(0, original_len, self.block_bytes_size):
            block = bytes(data[i:i + self.block_bytes_size])
            cipher = pow(int.from_bytes(block, 'big'),
                         self.public_key[1],
                         self.public_key[0]).to_bytes(self.block_bytes_size + 1, 'big')
            for x in range(self.block_bytes_size):
                ciphertext.append(cipher[x])
            extended_bytes.append(cipher[-1])
        ciphertext.append(extended_bytes.pop())

        for x in ciphertext[original_len:]:
            extended_bytes.append(x)
        ciphertext = ciphertext[:original_len]
        return ciphertext, extended_bytes

    def decrypt_ECB(self, data, extended_bytes, original_data_length):
        print('Starting decrypting...')
        print("Decrypted:\n[==========]")
        print('[', end='', flush=True)
        if self.private_key is None:
            raise ValueError("Private key cannot be empty")
        decrypted_data = []
        prepared_data = self.prepare_decryption_data(data, extended_bytes)
        iters_percent = len(prepared_data) // (self.block_bytes_size + 1) / 10
        n = 0
        for i in range(0, len(prepared_data), self.block_bytes_size + 1):
            if n >= iters_percent:
                print('=', end='', flush=True)
                n = 0
            n += 1
            block = bytes(prepared_data[i:i + self.block_bytes_size + 1])
            plaintext = pow(int.from_bytes(block, 'big'), self.private_key[1], self.private_key[0]).to_bytes(
                self.block_bytes_size, 'big')
            if len(decrypted_data) + self.block_bytes_size + 1 > original_data_length:
                block_length = original_data_length - len(decrypted_data)
            else:
                block_length = self.block_bytes_size + 1

            decrypted_data.extend(plaintext[-block_length:])
        print('=]')
        return decrypted_data

    def encrypt_CBC(self, data):
        if self.public_key is None:
            raise ValueError("Public key cannot be empty")
        original_len = len(data)
        ciphertext = []
        extended_bytes = []

        first_init_vector = secrets.randbits(self.key_length)
        init_vector = first_init_vector

        for i in range(0, original_len, self.block_bytes_size):
            block = bytes(data[i:i + self.block_bytes_size])

            init_vector = init_vector.to_bytes(self.block_bytes_size + 1, 'big')
            init_vector = int.from_bytes(init_vector[:len(block)], 'big')
            block_xor = int.from_bytes(block, 'big') ^ init_vector

            cipher = pow(block_xor,
                         self.public_key[1],
                         self.public_key[0])
            init_vector = cipher

            cipher = cipher.to_bytes(self.block_bytes_size + 1, 'big')
            for x in range(self.block_bytes_size):
                ciphertext.append(cipher[x])
            extended_bytes.append(cipher[-1])
        ciphertext.append(extended_bytes.pop())

        for x in ciphertext[original_len:]:
            extended_bytes.append(x)
        ciphertext = ciphertext[:original_len]

        return ciphertext, extended_bytes, first_init_vector.to_bytes(self.block_bytes_size + 1, 'big')

    def decrypt_CBC(self, data, extended_bytes, original_data_length, init_vector):
        print('Starting decrypting...')
        print("Decrypted:\n[==========]")
        print('[', end='', flush=True)
        if self.private_key is None:
            raise ValueError("Private key cannot be empty")
        decrypted_data = []
        prepared_data = self.prepare_decryption_data(data, extended_bytes)

        init_vector = int.from_bytes(init_vector, 'big')
        iters_percent = len(prepared_data) // (self.block_bytes_size + 1) / 10
        n = 0
        for i in range(0, len(prepared_data), self.block_bytes_size + 1):
            if n >= iters_percent:
                print('=', end='', flush=True)
                n = 0
            n += 1
            block = bytes(prepared_data[i:i + self.block_bytes_size + 1])

            block_xor = pow(int.from_bytes(block, 'big'), self.private_key[1], self.private_key[0])

            if len(decrypted_data) + self.block_bytes_size > original_data_length:
                block_length = original_data_length - len(decrypted_data)
            else:
                block_length = self.block_bytes_size

            init_vector = init_vector.to_bytes(self.block_bytes_size + 1, 'big')
            init_vector = int.from_bytes(init_vector[:block_length], 'big')
            plaintext = (init_vector ^ block_xor).to_bytes(self.block_bytes_size + 1, 'big')
            init_vector = int.from_bytes(block, 'big')

            decrypted_data.extend(plaintext[-block_length:])
        print('=]')
        return decrypted_data

    def library_encryption_RSA(self, data):
        encrypted_data = []

        public_key = rsa.PublicKey(*self.public_key)
        key_size = rsa.common.byte_size(public_key.n)
        chunk_size = key_size - 11

        for i in range(0, len(data), chunk_size):
            chunk = bytes(data[i:i + chunk_size])
            encrypted_chunk = rsa.encrypt(chunk, public_key)
            for x in range(chunk_size):
                encrypted_data.append(encrypted_chunk[x])

        return encrypted_data

    def prepare_decryption_data(self, data, extended_bytes):
        if self.private_key is None:
            raise ValueError('Private key required for decrypting .Provide a valid secret key')
        prepared_data = []
        if extended_bytes is not None:
            extension = deque(extended_bytes)
            for i in range(0, len(data), self.block_bytes_size):
                prepared_data.extend(data[i:i + self.block_bytes_size])
                prepared_data.append(extension.popleft())
            prepared_data.extend(extension)
            return prepared_data
        else:
            prepared_data.extend(data)
            return prepared_data

# msg = b'msg'
#
# with open('keys.txt', 'rb') as f:
#     line = f.readline()
#     keys = line.split(b'\t')
#     public = tuple(keys[0].split(b':'))
#     private = tuple(keys[1].strip(b'\n').split(b':'))
# private_key = int.from_bytes(base64.b64decode(private[0]), 'big'), int.from_bytes(
#                 base64.b64decode(private[1]), 'big')
# public_key = int.from_bytes(base64.b64decode(public[0]), 'big'), int.from_bytes(
#                 base64.b64decode(public[1]), 'big')
# rsa = RSA(private_key=private_key, public_key=public_key)
#
#
# ciphertext, extended_bytes, first_init_vector = rsa.encrypt_CBC(msg)
# print(first_init_vector)
# decrypted = rsa.decrypt_CBC(ciphertext, extended_bytes, len(msg), first_init_vector)
# print(bytes(decrypted), len(bytes(decrypted)), len(msg), sep='\t')

from collections import deque
from sympy import randprime, isprime, mod_inverse
from random import randint
from math import gcd, ceil
from pathlib import Path
import base64
import numpy as np
import time


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

    def generate_keys(self, size=2048, common_e=True, min_e=None):
        p = q = 1
        prime_size = size // 2
        while p == q or ((n := p * q).bit_length() != size):
            p = randprime(2 ** (prime_size - 1), 2 ** (prime_size - 0.7))
            q = randprime(2 ** (prime_size - 0.3), 2 ** prime_size)
        min_e = 2 ** (prime_size // 2) if min_e is None else min_e
        phi = (p - 1) * (q - 1)

        if min_e < 3 or min_e > phi - 1:
            raise ValueError("min_e must be greater than 3 and smaller than phi.\n")

        e = 2 ** 16 + 1 if common_e else randint(min_e, phi - 1)
        g = gcd(e, phi)
        i = 0
        while g != 1 or e > phi or i > 100:
            e = randint(min_e, phi - 1)
            g = gcd(e, phi)
        if i > 100:
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
        n = 0
        for i in range(0, original_len, self.block_bytes_size):
            n += 1
            block = bytes(data[i:i + self.block_bytes_size])
            cipher = pow(int.from_bytes(block, 'big'),
                         self.public_key[1],
                         self.public_key[0]).to_bytes(self.block_bytes_size + 1, 'big')
            for x in range(self.block_bytes_size):
                ciphertext.append(cipher[x])
            extended_bytes.append(cipher[-1])
        print(len(extended_bytes), n, sep='\t')
        ciphertext.append(extended_bytes.pop())
        print(len(extended_bytes))
        for x in ciphertext[original_len:]:
            extended_bytes.append(x)
        ciphertext = ciphertext[:original_len]
        print(len(extended_bytes))
        return ciphertext, extended_bytes

    def decrypt_ECB(self, data, extended_bytes, original_data_length):
        print('Starting decrypting...')
        if self.private_key is None:
            raise ValueError("Private key cannot be empty")
        decrypted_data = []
        print(original_data_length)
        print(len(extended_bytes))
        prepared_data = self.prepare_decryption_data(data, extended_bytes)
        for i in range(0, len(prepared_data), self.block_bytes_size + 1):
            block = bytes(prepared_data[i:i+self.block_bytes_size+1])
            plaintext = pow(int.from_bytes(block, 'big'), self.private_key[1], self.private_key[0]).to_bytes(self.block_bytes_size, 'big')
            if len(decrypted_data) + self.block_bytes_size + 1 > original_data_length:
                block_length = original_data_length - len(decrypted_data)
            else:
                block_length = self.block_bytes_size + 1

            decrypted_data.extend(plaintext[-block_length:])
        return decrypted_data

    def prepare_decryption_data(self, data, extended_bytes):
        if self.private_key is None:
            raise ValueError('Private key required for decrypting .Provide a valid secret key')
        prepared_data = []
        if extended_bytes is not None:
            extension = deque(extended_bytes)
            print(len(extension))
            print(len(data))
            print(self.block_bytes_size)
            print(len(data) / self.block_bytes_size)
            for i in range(0, len(data), self.block_bytes_size):
                prepared_data.extend(data[i:i + self.block_bytes_size])
                prepared_data.append(extension.popleft())
            prepared_data.extend(extension)
            return prepared_data
        else:
            prepared_data.extend(data)
            return prepared_data
from sympy import randprime, isprime, mod_inverse
from random import randint
from math import gcd
import numpy as np
import time


class RSA:

    def __init__(self):
        self.private_key = None
        self.public_key = None
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

        return self.public_key, self.private_key

    def encrypt_ECB(self, data):
        original_len = len(data)
        print(original_len)
        print(self.block_bytes_size)
        print(original_len / self.block_bytes_size)
        ciphertext = []
        z = 1
        for i in range(0, original_len, self.block_bytes_size):
            block = bytes(data[i:i + self.block_bytes_size])
            # if len(block) < self.block_bytes_size:
            #     block += b'\x00' * (self.block_bytes_size - len(block))
            chunk_to_encrypt_hex = bytes(data[i: i + self.block_bytes_size])
            cipher_int = pow(int.from_bytes(chunk_to_encrypt_hex, 'big'), self.public_key[1], self.public_key[0])
            cipher_hex = cipher_int.to_bytes(self.block_bytes_size + 1, 'big')

            for x in range(self.block_bytes_size):
                ciphertext.append(cipher_hex[x])
            # ciphertext.append(cip.to_bytes(self.block_bytes_size, 'big'))

            z += 1


times = []
data = []
failures = 0
rsa = RSA()
with open('test.txt', 'r') as f:
    for line in f.readlines():
        data.append(int(line))

for n in range(1):
    start = time.time()
    public, private = rsa.generate_keys(common_e=False)
    rsa.encrypt_ECB(data)
    times.append(time.time() - start)
    if private[-1] < 0:
        failures += 1
print(failures, '\n', np.average(times))

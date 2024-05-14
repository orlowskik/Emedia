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
        return self.public_key, self.private_key


times = []
failures = 0
rsa = RSA()
for i in range(2):
    start = time.time()
    public, private = rsa.generate_keys(common_e=False)
    times.append(time.time() - start)
    if private[-1] < 0:
        failures += 1
print(failures, '\n', np.average(times))

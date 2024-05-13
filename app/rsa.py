from sympy import randprime, isprime, mod_inverse
from random import randint
from math import gcd
from egcd import egcd
import numpy as np
import time


def findModInverse(a, m):
    # Returns the modular inverse of a % m, which is
    # the number x such that a*x % m = 1

    if gcd(a, m) != 1:
        return None  # no mod inverse if a & m aren't coprime

    # Calculate using the Extended Euclidean Algorithm:
    u1, u2, u3 = 1, 0, a
    v1, v2, v3 = 0, 1, m
    while v3 != 0:
        q = u3 // v3  # // is the integer division operator
        v1, v2, v3, u1, u2, u3 = (u1 - q * v1), (u2 - q * v2), (u3 - q * v3), v1, v2, v3
    return u1 % m


def generate_keys(p=None, q=None, common_e=True, min_e=None):
    if p is None or q is None:
        p = randprime(2 ** 512, 2 ** 1024)
        q = randprime(p, p * (2 ** 100))
    if not isprime(p) or not isprime(q) or p == q:
        raise ValueError("p and q must be distinct prime numbers.\n")
    min_e = 3 if min_e is None else min_e

    n = p * q
    phi = (p - 1) * (q - 1)

    if min_e < 3 or min_e > phi - 1:
        raise ValueError("min_e must be greater than 3 and smaller than phi.\n")

    e = 2 ** 16 + 1 if common_e else randint(3, phi - 1)
    g = gcd(e, phi)
    while g != 1 or e > phi or i > 100000000:
        e = randint(3, phi - 1)
        g = gcd(e, phi)
    d = mod_inverse(e, phi)
    return (n, e), (n, d)


times = []
failures = 0
for i in range(1000):
    start = time.time()
    public, private = generate_keys(common_e=False)
    times.append(time.time() - start)
    if private[-1] < 0:
        failures += 1
    print(i)
print(failures, '\n', np.average(times))

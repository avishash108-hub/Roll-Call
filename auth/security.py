import os
from argon2 import PasswordHasher
secret = os.environ.get("JWT_SECRET")
ph = PasswordHasher(time_cost = 3, memory_cost = 65536, parallelism = 4)
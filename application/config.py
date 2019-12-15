import os

HOST = '127.0.0.1'
PORT = 8080

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASS = None

for env, value in os.environ.items():
    if env.startswith('CC_'):
        globals()[env.split('_', 1)[1]] = value

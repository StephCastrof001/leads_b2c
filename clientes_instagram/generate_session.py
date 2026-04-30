from instagrapi import Client
from pathlib import Path

print('=' * 50)
print('Session Generator - run on LAPTOP only')
print('After running, upload session.json to EC2:')
print('  scp -i Ollama.pem session.json ubuntu@107.21.24.49:/home/ubuntu/docs_dev/clientes_instagram/')
print()

username = input('Instagram username: ').strip()
password = input('Instagram password: ').strip()

client = Client()
print('[INFO] Logging in...')
try:
    client.login(username, password)
    client.dump_settings('session.json')
    print('[OK] session.json saved')
except Exception as e:
    print('[ERR]', type(e).__name__, str(e))
finally:
    client.close()

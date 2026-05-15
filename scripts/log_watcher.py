import hashlib
import json
import time
import subprocess
from web3 import Web3

# ============ CONFIG ============
RPC_URL = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = "0x5D60b38B99eDe44B98E96aF91a3e329dfe3B3605"
PRIVATE_KEY = "0x44d9dd3e5ff5d2fef78df743b61266918ad37b188129644ea55cc49fcdb035ad"
# ================================

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

ABI = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"entryId","type":"uint256"},{"indexed":false,"internalType":"bytes32","name":"logHash","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"timestamp","type":"uint256"},{"indexed":false,"internalType":"string","name":"source","type":"string"}],"name":"LogStored","type":"event"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"entries","outputs":[{"internalType":"bytes32","name":"logHash","type":"bytes32"},{"internalType":"uint256","name":"timestamp","type":"uint256"},{"internalType":"string","name":"source","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getTotalLogs","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_logHash","type":"bytes32"},{"internalType":"string","name":"_source","type":"string"}],"name":"storeLog","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_logHash","type":"bytes32"}],"name":"verifyLog","outputs":[{"internalType":"bool","name":"","type":"bool"},{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]')

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

def hash_log(log_line: str) -> bytes:
    return hashlib.sha256(log_line.encode()).digest()

def send_to_blockchain(log_hash: bytes, source: str):
    nonce = w3.eth.get_transaction_count(account.address)
    tx = contract.functions.storeLog(
        log_hash, source
    ).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': w3.to_wei('1', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

def save_log(line: str):
    with open('/home/alpaca/blockchain-log/logs/submitted_logs.txt', 'a') as f:
        f.write(line + '\n')

print(f"[*] Blockchain Log Watcher started")
print(f"[*] Connected: {w3.is_connected()}")
print(f"[*] Monitoring systemd journal for auth/warning events...")
print(f"[*] Press Ctrl+C to stop")
print("-" * 60)

# Monitor systemd journal secara realtime
proc = subprocess.Popen(
    ['journalctl', '-f', '-p', 'warning', '--output=short-iso'],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True
)

try:
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue

        log_hash = hash_log(line)
        print(f"[+] New log  : {line[:65]}")
        print(f"    Hash     : {log_hash.hex()}")

        try:
            tx_hash = send_to_blockchain(log_hash, "journald")
            save_log(line)
            print(f"    TX       : {tx_hash}")
            print(f"    Status   : ✅ Tersimpan di blockchain")
        except Exception as e:
            print(f"    Status   : ❌ Error: {e}")
        print()

except KeyboardInterrupt:
    print("\n[*] Watcher stopped.")
    proc.terminate()

import hashlib
import json
from web3 import Web3
from datetime import datetime

# ============ CONFIG ============
RPC_URL = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = "0x5D60b38B99eDe44B98E96aF91a3e329dfe3B3605"
# ================================

w3 = Web3(Web3.HTTPProvider(RPC_URL))

ABI = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"entryId","type":"uint256"},{"indexed":false,"internalType":"bytes32","name":"logHash","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"timestamp","type":"uint256"},{"indexed":false,"internalType":"string","name":"source","type":"string"}],"name":"LogStored","type":"event"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"entries","outputs":[{"internalType":"bytes32","name":"logHash","type":"bytes32"},{"internalType":"uint256","name":"timestamp","type":"uint256"},{"internalType":"string","name":"source","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getTotalLogs","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_logHash","type":"bytes32"},{"internalType":"string","name":"_source","type":"string"}],"name":"storeLog","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_logHash","type":"bytes32"}],"name":"verifyLog","outputs":[{"internalType":"bool","name":"","type":"bool"},{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]')

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

def hash_log(log_line: str) -> bytes:
    return hashlib.sha256(log_line.encode()).digest()

def verify(log_line: str):
    log_hash = hash_log(log_line)
    is_valid, timestamp = contract.functions.verifyLog(log_hash).call()
    status = f"✅ VALID — terdaftar di blockchain pada {datetime.fromtimestamp(timestamp)}" if is_valid else "❌ INVALID — log tidak ada di blockchain / telah dimanipulasi!"
    print(f"Log    : {log_line[:70]}")
    print(f"Hash   : {log_hash.hex()}")
    print(f"Status : {status}")
    print("-" * 70)

def fetch_all_logs_from_blockchain():
    """Ambil semua log langsung dari blockchain via events"""
    print("[*] Mengambil semua log dari blockchain...")
    total = contract.functions.getTotalLogs().call()
    print(f"[*] Total log di blockchain: {total}")
    print()

    logs = []
    for i in range(total):
        entry = contract.functions.entries(i).call()
        logs.append({
            'index': i,
            'hash': entry[0].hex(),
            'timestamp': datetime.fromtimestamp(entry[1]),
            'source': entry[2]
        })
    return logs

print("=" * 70)
print("         BLOCKCHAIN LOG VERIFIER")
print("=" * 70)
print()

# Ambil semua log dari blockchain
logs = fetch_all_logs_from_blockchain()

print("--- Log yang tersimpan di blockchain ---")
print()
for log in logs[-5:]:  # tampilkan 5 terakhir
    print(f"  [{log['index']}] Hash     : {log['hash'][:32]}...")
    print(f"       Timestamp : {log['timestamp']}")
    print(f"       Source    : {log['source']}")
    print()

# Verifikasi log spesifik
print("=" * 70)
print("--- Verifikasi log CRITICAL (serangan tadi) ---")
print()

test_logs = [
    "2026-05-16T12:35:58+07:00 alpaca-Aspire-AL14-31P sshd[10859]: CRITICAL: Root login attempt from 192.168.1.100",
    "2026-05-16T12:35:58+07:00 alpaca-Aspire-AL14-31P sshd[10859]: CRITICAL: Root login attempt from 10.0.0.1 [EDITED BY ATTACKER]",
]

for log in test_logs:
    verify(log)

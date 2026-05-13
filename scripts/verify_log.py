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
    
    print(f"Log    : {log_line[:70]}")
    print(f"Hash   : {log_hash.hex()}")
    
    if is_valid:
        dt = datetime.fromtimestamp(timestamp)
        print(f"Status : ✅ VALID — terdaftar di blockchain pada {dt}")
    else:
        print(f"Status : ❌ INVALID — log ini tidak ada di blockchain / telah dimanipulasi!")
    print("-" * 70)

if __name__ == "__main__":
    print("=" * 70)
    print("         BLOCKCHAIN LOG VERIFIER")
    print("=" * 70)
    print()

    # Baca 3 log terakhir dari syslog (sama seperti yang tadi di-submit)
    with open('/home/alpaca/blockchain-log/logs/submitted_logs.txt', 'r') as f:    
        recent = [l.strip() for l in f.readlines() if l.strip()]

    print("--- Verifikasi log ASLI ---")
    print()
    for line in recent:
        verify(line)

    print()
    print("--- Simulasi log yang DIMANIPULASI ---")
    print()
    # Log yang sama tapi diubah sedikit (simulasi penyerang edit log)
    tampered = [
        recent[0] + " [EDITED BY ATTACKER]",
        recent[1].replace("alpaca", "hacker"),
        recent[2].replace("COMMAND=/bin/bash", "COMMAND=/bin/rm -rf /"),
    ]
    for line in tampered:
        verify(line)

import hashlib
import json
import time
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

# Log-log simulasi serangan
ATTACK_LOGS = [
    "2026-05-16T11:00:01+07:00 server sshd[1234]: Failed password for root from 192.168.1.100 port 22",
    "2026-05-16T11:00:02+07:00 server sshd[1234]: Failed password for root from 192.168.1.100 port 22",
    "2026-05-16T11:00:03+07:00 server sshd[1234]: Accepted password for root from 192.168.1.100 port 22",
    "2026-05-16T11:00:04+07:00 server sudo[5678]: root : COMMAND=/bin/bash",
]

def hash_log(line): 
    return hashlib.sha256(line.encode()).digest()

def send_to_blockchain(log_hash, source):
    nonce = w3.eth.get_transaction_count(account.address)
    tx = contract.functions.storeLog(log_hash, source).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': w3.to_wei('1', 'gwei')
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

def verify(line):
    log_hash = hash_log(line)
    is_valid, timestamp = contract.functions.verifyLog(log_hash).call()
    status = "✅ VALID" if is_valid else "❌ INVALID — dimanipulasi!"
    print(f"  Log    : {line[:65]}")
    print(f"  Hash   : {log_hash.hex()[:32]}...")
    print(f"  Status : {status}")
    print()

print("=" * 65)
print("   DEMO: Blockchain Log Integrity System")
print("=" * 65)
print()

# FASE 1: Submit log ke blockchain
print("📌 FASE 1: Sistem mencatat log mencurigakan ke blockchain...")
print()
with open('/home/alpaca/blockchain-log/logs/submitted_logs.txt', 'w') as f:
    for log in ATTACK_LOGS:
        log_hash = hash_log(log)
        tx = send_to_blockchain(log_hash, "sshd")
        f.write(log + '\n')
        print(f"  [+] {log[20:65]}")
        print(f"      TX: {tx[:32]}...")
        print()
        time.sleep(0.5)

total = contract.functions.getTotalLogs().call()
print(f"  ✅ {len(ATTACK_LOGS)} log tersimpan di blockchain (total: {total})")
print()

# FASE 2: Verifikasi log asli
print("=" * 65)
print("📌 FASE 2: Verifikasi log ASLI...")
print()
for log in ATTACK_LOGS:
    verify(log)

# FASE 3: Simulasi penyerang hapus/edit log
print("=" * 65)
print("📌 FASE 3: Simulasi penyerang memanipulasi log...")
print()
TAMPERED_LOGS = [
    "2026-05-16T11:00:01+07:00 server sshd[1234]: Failed password for root from 192.168.1.100 port 22",
    "2026-05-16T11:00:02+07:00 server sshd[1234]: Failed password for root from 192.168.1.100 port 22",
    # Log ke-3 DIHAPUS penyerang (accepted password — bukti masuk)
    # Log ke-4 DIEDIT penyerang
    "2026-05-16T11:00:04+07:00 server sudo[5678]: root : COMMAND=/bin/ls",  # diubah dari /bin/bash
]
print("  ⚠️  Penyerang menghapus log 'Accepted password' dan mengedit COMMAND!")
print()

# FASE 4: Verifikasi log yang sudah dimanipulasi
print("=" * 65)
print("📌 FASE 4: Deteksi manipulasi...")
print()
for log in TAMPERED_LOGS:
    verify(log)

print("=" * 65)
print("🔐 Kesimpulan: Blockchain berhasil mendeteksi manipulasi log!")
print("=" * 65)

import hashlib
import json
import time
from web3 import Web3

# ============ CONFIG ============
RPC_URL = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = "0x5D60b38B99eDe44B98E96aF91a3e329dfe3B3605"
PRIVATE_KEY = "0x44d9dd3e5ff5d2fef78df743b61266918ad37b188129644ea55cc49fcdb035ad"
LOG_FILE = "/var/log/syslog"
# ================================

# Connect ke blockchain
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

# Load ABI contract
ABI = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"entryId","type":"uint256"},{"indexed":false,"internalType":"bytes32","name":"logHash","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"timestamp","type":"uint256"},{"indexed":false,"internalType":"string","name":"source","type":"string"}],"name":"LogStored","type":"event"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"entries","outputs":[{"internalType":"bytes32","name":"logHash","type":"bytes32"},{"internalType":"uint256","name":"timestamp","type":"uint256"},{"internalType":"string","name":"source","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getTotalLogs","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_logHash","type":"bytes32"},{"internalType":"string","name":"_source","type":"string"}],"name":"storeLog","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_logHash","type":"bytes32"}],"name":"verifyLog","outputs":[{"internalType":"bool","name":"","type":"bool"},{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]')

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

def hash_log(log_line: str) -> bytes:
    """Hash satu baris log dengan SHA-256"""
    return hashlib.sha256(log_line.encode()).digest()

def send_to_blockchain(log_hash: bytes, source: str):
    """Kirim hash log ke smart contract"""
    nonce = w3.eth.get_transaction_count(account.address)
    
    tx = contract.functions.storeLog(
        log_hash,
        source
    ).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': w3.to_wei('1', 'gwei')
    })
    
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return tx_hash.hex(), receipt.blockNumber

def process_logs(log_file: str, source_name: str):
    """Baca log file dan kirim ke blockchain"""
    print(f"[*] Membaca log dari: {log_file}")
    print(f"[*] Connected ke blockchain: {w3.is_connected()}")
    print(f"[*] Account: {account.address}")
    print(f"[*] Balance: {w3.from_wei(w3.eth.get_balance(account.address), 'ether')} ETH")
    print("-" * 60)

    try:
        with open(log_file, 'r', errors='ignore') as f:
            lines = f.readlines()
    except PermissionError:
        print(f"[!] Permission denied: {log_file}")
        print("[*] Pakai log dummy untuk testing...")
        lines = [
            "May 11 18:00:01 server sshd[1234]: Failed password for root from 192.168.1.1\n",
            "May 11 18:00:02 server sshd[1234]: Accepted password for alpaca from 127.0.0.1\n",
            "May 11 18:00:03 server sudo: alpaca : TTY=pts/0 ; COMMAND=/bin/bash\n",
        ]

    # Ambil 3 baris terakhir aja untuk testing
    recent_lines = [l.strip() for l in lines[-3:] if l.strip()]

    import os
    os.makedirs('../logs', exist_ok=True)
    with open('../logs/submitted_logs.txt', 'w') as f:
        for line in recent_lines:
            f.write(line + '\n')
    print("[*] Log yang di-submit disimpan ke logs/submitted_logs.txt")

    for i, line in enumerate(recent_lines):
        log_hash = hash_log(line)
        print(f"[{i+1}] Log  : {line[:60]}...")
        print(f"      Hash : {log_hash.hex()}")
        
        tx_hash, block_num = send_to_blockchain(log_hash, source_name)
        print(f"      TX   : {tx_hash}")
        print(f"      Block: #{block_num}")
        print()
        time.sleep(1)

    total = contract.functions.getTotalLogs().call()
    print(f"[✓] Total log tersimpan di blockchain: {total}")

if __name__ == "__main__":
    process_logs(LOG_FILE, "syslog")

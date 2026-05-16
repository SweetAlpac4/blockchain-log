from flask import Flask, render_template_string, request
from web3 import Web3
from datetime import datetime
import json

app = Flask(__name__)

RPC_URL = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = "0x5D60b38B99eDe44B98E96aF91a3e329dfe3B3605"

w3 = Web3(Web3.HTTPProvider(RPC_URL))
ABI = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"entryId","type":"uint256"},{"indexed":false,"internalType":"bytes32","name":"logHash","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"timestamp","type":"uint256"},{"indexed":false,"internalType":"string","name":"source","type":"string"}],"name":"LogStored","type":"event"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"entries","outputs":[{"internalType":"bytes32","name":"logHash","type":"bytes32"},{"internalType":"uint256","name":"timestamp","type":"uint256"},{"internalType":"string","name":"source","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getTotalLogs","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_logHash","type":"bytes32"},{"internalType":"string","name":"_source","type":"string"}],"name":"storeLog","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_logHash","type":"bytes32"}],"name":"verifyLog","outputs":[{"internalType":"bool","name":"","type":"bool"},{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]')
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Blockchain Log Integrity Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0f172a; color: #e2e8f0; font-family: 'Courier New', monospace; padding: 20px; }
        h1 { color: #38bdf8; text-align: center; padding: 20px 0; font-size: 1.5em; border-bottom: 1px solid #1e3a5f; margin-bottom: 20px; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 25px; }
        .stat-card { background: #1e293b; border: 1px solid #1e3a5f; border-radius: 8px; padding: 20px; text-align: center; }
        .stat-card .value { font-size: 2em; font-weight: bold; color: #38bdf8; }
        .stat-card .label { color: #94a3b8; font-size: 0.85em; margin-top: 5px; }
        .stat-card.green .value { color: #4ade80; }
        .search-bar { display: flex; gap: 10px; margin-bottom: 20px; }
        .search-bar input { flex: 1; background: #1e293b; border: 1px solid #1e3a5f; color: #e2e8f0; padding: 10px 15px; border-radius: 6px; font-family: monospace; }
        .search-bar button { background: #0f3460; color: #38bdf8; border: 1px solid #1e3a5f; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
        .search-bar button:hover { background: #1e3a5f; }
        table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; overflow: hidden; margin-bottom: 20px; }
        th { background: #0f3460; color: #38bdf8; padding: 12px 15px; text-align: left; font-size: 0.85em; }
        td { padding: 10px 15px; border-bottom: 1px solid #0f172a; font-size: 0.8em; }
        tr:hover { background: #162032; }
        .badge { padding: 3px 8px; border-radius: 4px; font-size: 0.75em; background: #1e3a5f; color: #38bdf8; }
        .hash { color: #94a3b8; font-size: 0.75em; }
        .pagination { display: flex; gap: 10px; justify-content: center; align-items: center; }
        .pagination a { color: #38bdf8; text-decoration: none; padding: 8px 15px; background: #1e293b; border: 1px solid #1e3a5f; border-radius: 6px; }
        .pagination a:hover { background: #0f3460; }
        .pagination span { color: #94a3b8; }
        .footer { text-align: center; color: #475569; font-size: 0.75em; margin-top: 20px; }
        h2 { color: #38bdf8; margin-bottom: 15px; font-size: 1em; }
        .highlight { background: #1e3a5f !important; }
    </style>
</head>
<body>
    <h1>🔐 Blockchain Log Integrity Dashboard</h1>

    <div class="stats">
        <div class="stat-card">
            <div class="value">{{ block_number }}</div>
            <div class="label">Current Block</div>
        </div>
        <div class="stat-card green">
            <div class="value">{{ total_logs }}</div>
            <div class="label">Total Log Tersimpan</div>
        </div>
        <div class="stat-card">
            <div class="value" style="color: #4ade80">ONLINE</div>
            <div class="label">Blockchain Status</div>
        </div>
    </div>

    <h2>🔍 Cari Log by Index</h2>
    <div class="search-bar">
        <form method="get" style="display:flex; gap:10px; width:100%">
            <input type="number" name="search" placeholder="Masukkan nomor index log (0 - {{ total_logs - 1 }})" value="{{ search_idx if search_idx is not none else '' }}">
            <button type="submit">Cari</button>
            <a href="/" style="padding: 10px 20px; background: #1e293b; border: 1px solid #1e3a5f; border-radius: 6px; color: #94a3b8; text-decoration: none;">Reset</a>
        </form>
    </div>

    {% if search_result %}
    <h2>📌 Hasil Pencarian — Log #{{ search_idx }}</h2>
    <table>
        <tr><th>#</th><th>Timestamp</th><th>Hash</th><th>Source</th></tr>
        <tr class="highlight">
            <td>{{ search_result.index }}</td>
            <td>{{ search_result.timestamp }}</td>
            <td class="hash">{{ search_result.hash }}</td>
            <td><span class="badge">{{ search_result.source }}</span></td>
        </tr>
    </table>
    {% endif %}

    <h2>📋 Semua Log (halaman {{ page }} dari {{ total_pages }})</h2>
    <table>
        <tr>
            <th>#</th>
            <th>Timestamp</th>
            <th>Hash</th>
            <th>Source</th>
        </tr>
        {% for log in logs %}
        <tr>
            <td>{{ log.index }}</td>
            <td>{{ log.timestamp }}</td>
            <td class="hash">{{ log.hash[:40] }}...</td>
            <td><span class="badge">{{ log.source }}</span></td>
        </tr>
        {% endfor %}
    </table>

    <div class="pagination">
        {% if page > 1 %}
        <a href="?page={{ page - 1 }}">← Prev</a>
        {% endif %}
        <span>Halaman {{ page }} dari {{ total_pages }}</span>
        {% if page < total_pages %}
        <a href="?page={{ page + 1 }}">Next →</a>
        {% endif %}
    </div>

    <div class="footer">Contract: {{ contract_address }} | {{ total_logs }} log tersimpan permanen di blockchain</div>
</body>
</html>
"""

@app.route('/')
def index():
    connected = w3.is_connected()
    block_number = w3.eth.block_number if connected else 0
    total_logs = contract.functions.getTotalLogs().call() if connected else 0

    # Search by index
    search_idx = request.args.get('search', type=int)
    search_result = None
    if search_idx is not None and 0 <= search_idx < total_logs:
        entry = contract.functions.entries(search_idx).call()
        search_result = {
            'index': search_idx,
            'hash': entry[0].hex(),
            'timestamp': datetime.fromtimestamp(entry[1]).strftime('%Y-%m-%d %H:%M:%S'),
            'source': entry[2]
        }

    # Pagination
    per_page = 20
    page = request.args.get('page', 1, type=int)
    total_pages = max(1, (total_logs + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = min(start + per_page, total_logs)

    logs = []
    for i in range(start, end):
        entry = contract.functions.entries(i).call()
        logs.append({
            'index': i,
            'hash': entry[0].hex(),
            'timestamp': datetime.fromtimestamp(entry[1]).strftime('%Y-%m-%d %H:%M:%S'),
            'source': entry[2]
        })

    return render_template_string(HTML,
        connected=connected,
        block_number=block_number,
        total_logs=total_logs,
        logs=logs,
        page=page,
        total_pages=total_pages,
        search_idx=search_idx,
        search_result=search_result,
        contract_address=CONTRACT_ADDRESS
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

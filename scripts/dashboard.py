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
  <title>Blockchain Log Integrity</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #faf8f6; color: #2d2420; padding: 24px; font-size: 14px; }
    .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #d6cfc7; }
    .header-left { display: flex; align-items: center; gap: 10px; }
    .header-left svg { color: #8c7b6e; }
    .header-left span { font-size: 16px; font-weight: 500; color: #2d2420; }
    .badge-online { display: flex; align-items: center; gap: 6px; background: #e8f0e9; border-radius: 6px; padding: 4px 10px; }
    .badge-online .dot { width: 6px; height: 6px; border-radius: 50%; background: #4a7a50; }
    .badge-online span { font-size: 12px; color: #4a7a50; font-weight: 500; }
    .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 24px; }
    .stat { background: #f0ebe5; border-radius: 8px; padding: 16px; }
    .stat .label { font-size: 12px; color: #8c7b6e; margin-bottom: 4px; }
    .stat .value { font-size: 22px; font-weight: 500; color: #2d2420; }
    .stat .value.mono { font-size: 11px; font-family: monospace; color: #8c7b6e; }
    .card { background: #fff; border: 1px solid #d6cfc7; border-radius: 12px; overflow: hidden; margin-bottom: 16px; }
    .card-header { padding: 12px 16px; border-bottom: 1px solid #d6cfc7; display: flex; align-items: center; justify-content: space-between; }
    .card-header .title { font-size: 13px; font-weight: 500; color: #2d2420; }
    .card-header .sub { font-size: 12px; color: #8c7b6e; }
    .search-row { padding: 12px 16px; display: flex; gap: 8px; }
    .search-row input { flex: 1; padding: 7px 12px; border: 1px solid #d6cfc7; border-radius: 6px; font-size: 13px; outline: none; background: #faf8f6; color: #2d2420; }
    .search-row input:focus { border-color: #8c7b6e; }
    .search-row button { padding: 7px 14px; border: 1px solid #d6cfc7; border-radius: 6px; font-size: 13px; background: #2d2420; color: #f0ebe5; cursor: pointer; }
    .search-row button:hover { background: #4a3f38; }
    .search-row a { padding: 7px 14px; border: 1px solid #d6cfc7; border-radius: 6px; font-size: 13px; text-decoration: none; color: #8c7b6e; background: #fff; }
    .search-result { margin: 0 16px 12px; background: #f0ebe5; border: 1px solid #c4b8af; border-radius: 8px; padding: 12px 16px; }
    .search-result .sr-label { font-size: 11px; color: #6b5d55; font-weight: 500; margin-bottom: 6px; }
    .search-result .sr-hash { font-size: 11px; font-family: monospace; color: #2d2420; word-break: break-all; }
    .search-result .sr-meta { font-size: 12px; color: #8c7b6e; margin-top: 4px; }
    table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    thead tr { background: #faf8f6; }
    th { padding: 8px 16px; text-align: left; font-size: 11px; font-weight: 500; color: #8c7b6e; border-bottom: 1px solid #d6cfc7; }
    td { padding: 10px 16px; font-size: 12px; color: #4a3f38; border-top: 1px solid #f0ebe5; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    tr:hover td { background: #faf8f6; }
    .mono { font-family: monospace; color: #8c7b6e; }
    .badge { font-size: 11px; padding: 2px 8px; border-radius: 4px; font-family: monospace; }
    .badge-syslog { background: #f0ebe5; color: #6b5d55; }
    .badge-journald { background: #e8f0e9; color: #4a7a50; border: 1px solid #c5d9c7; }
    .card-footer { padding: 10px 16px; border-top: 1px solid #d6cfc7; display: flex; align-items: center; justify-content: space-between; }
    .card-footer span { font-size: 12px; color: #8c7b6e; }
    .pagination { display: flex; gap: 6px; }
    .pagination a { padding: 4px 12px; border: 1px solid #d6cfc7; border-radius: 6px; font-size: 12px; text-decoration: none; color: #4a3f38; background: #fff; }
    .pagination a:hover { background: #f0ebe5; }
  </style>
</head>
<body>

  <div class="header">
    <div class="header-left">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#8c7b6e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
      <span>Blockchain Log Integrity</span>
    </div>
    <div class="badge-online">
      <span class="dot"></span>
      <span>Online</span>
    </div>
  </div>

  <div class="stats">
    <div class="stat">
      <div class="label">Current block</div>
      <div class="value">{{ block_number }}</div>
    </div>
    <div class="stat">
      <div class="label">Logs stored</div>
      <div class="value">{{ total_logs }}</div>
    </div>
    <div class="stat">
      <div class="label">Contract</div>
      <div class="value mono">{{ contract_address[:18] }}...</div>
    </div>
  </div>

  <div class="card">
    <div class="card-header"><span class="title">Search log by index</span></div>
    <div class="search-row">
      <form method="get" style="display:flex; gap:8px; flex:1;">
        <input type="number" name="search" placeholder="Enter index (0 – {{ total_logs - 1 }})" value="{{ search_idx if search_idx is not none else '' }}">
        <button type="submit">Search</button>
        <a href="/">Reset</a>
      </form>
    </div>
    {% if search_result %}
    <div class="search-result">
      <div class="sr-label">Log #{{ search_idx }}</div>
      <div class="sr-hash">{{ search_result.hash }}</div>
      <div class="sr-meta">{{ search_result.timestamp }} &nbsp;·&nbsp; {{ search_result.source }}</div>
    </div>
    {% endif %}
  </div>

  <div class="card">
    <div class="card-header">
      <span class="title">All logs</span>
      <span class="sub">Page {{ page }} of {{ total_pages }}</span>
    </div>
    <table>
      <thead>
        <tr>
          <th style="width:48px">#</th>
          <th style="width:160px">Timestamp</th>
          <th>Hash</th>
          <th style="width:90px">Source</th>
        </tr>
      </thead>
      <tbody>
        {% for log in logs %}
        <tr>
          <td class="mono">{{ log.index }}</td>
          <td>{{ log.timestamp }}</td>
          <td class="mono">{{ log.hash[:40] }}...</td>
          <td>
            <span class="badge {% if log.source == 'journald' %}badge-journald{% else %}badge-syslog{% endif %}">
              {{ log.source }}
            </span>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    <div class="card-footer">
      <span>{{ total_logs }} logs total</span>
      <div class="pagination">
        {% if page > 1 %}<a href="?page={{ page - 1 }}">← Prev</a>{% endif %}
        {% if page < total_pages %}<a href="?page={{ page + 1 }}">Next →</a>{% endif %}
      </div>
    </div>
  </div>

</body>
</html>
"""

@app.route('/')
def index():
    connected = w3.is_connected()
    block_number = w3.eth.block_number if connected else 0
    total_logs = contract.functions.getTotalLogs().call() if connected else 0

    search_idx = request.args.get('search', type=int)
    search_result = None
    if search_idx is not None and 0 <= search_idx < total_logs:
        entry = contract.functions.entries(search_idx).call()
        search_result = {
            'hash': entry[0].hex(),
            'timestamp': datetime.fromtimestamp(entry[1]).strftime('%Y-%m-%d %H:%M:%S'),
            'source': entry[2]
        }

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

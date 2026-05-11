// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LogRegistry {
    
    struct LogEntry {
        bytes32 logHash;
        uint256 timestamp;
        string source;
    }

    LogEntry[] public entries;
    address public owner;

    event LogStored(
        uint256 indexed entryId,
        bytes32 logHash,
        uint256 timestamp,
        string source
    );

    constructor() {
        owner = msg.sender;
    }

    function storeLog(bytes32 _logHash, string memory _source) public {
        require(msg.sender == owner, "Only owner can store logs");
        
        entries.push(LogEntry({
            logHash: _logHash,
            timestamp: block.timestamp,
            source: _source
        }));

        emit LogStored(entries.length - 1, _logHash, block.timestamp, _source);
    }

    function verifyLog(bytes32 _logHash) public view returns (bool, uint256) {
        for (uint256 i = 0; i < entries.length; i++) {
            if (entries[i].logHash == _logHash) {
                return (true, entries[i].timestamp);
            }
        }
        return (false, 0);
    }

    function getTotalLogs() public view returns (uint256) {
        return entries.length;
    }
}

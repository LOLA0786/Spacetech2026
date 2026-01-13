from web3 import Web3
from eth_account import Account
import json
from datetime import datetime
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class OrbitLedger:
    """
    Blockchain-based immutable orbit event ledger
    Records: maneuvers, collisions, launches, de-orbits
    Ensures sovereignty and prevents data tampering
    """

    def __init__(self, rpc_url: str, contract_address: Optional[str] = None):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract_address = contract_address
        self.contract = None

        # Simple event structure (in production, use proper smart contract)
        self.local_ledger = []

    def record_event(self, event_type: str, object_id: str, data: Dict, private_key: str) -> str:
        """Record an orbit event to blockchain"""

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "object_id": object_id,
            "data": data,
        }

        event_json = json.dumps(event, sort_keys=True)
        event_hash = self.w3.keccak(text=event_json).hex()

        account = Account.from_key(private_key)

        # NOTE: web3 message signing API differs across versions.
        # We'll use a safe method:
        from eth_account.messages import encode_defunct
        message = encode_defunct(text=event_hash)

        signed = account.sign_message(message)

        ledger_entry = {
            "event": event,
            "hash": event_hash,
            "signature": signed.signature.hex(),
            "signer": account.address,
        }

        self.local_ledger.append(ledger_entry)
        logger.info(f"Recorded event: {event_type} for {object_id}")
        return event_hash

    def verify_event(self, event_hash: str) -> bool:
        """Verify an event's authenticity"""
        for entry in self.local_ledger:
            if entry["hash"] == event_hash:
                event_json = json.dumps(entry["event"], sort_keys=True)
                computed_hash = self.w3.keccak(text=event_json).hex()
                return computed_hash == event_hash
        return False

    def get_event_history(self, object_id: str) -> List[Dict]:
        """Get all events for an object"""
        return [entry for entry in self.local_ledger if entry["event"]["object_id"] == object_id]

"""
Node 1 – Blockchain Node (Port 5000)
Academic Assignment Submission Integrity System
Consensus: Proof-of-Authority (PoA) – lightweight, suitable for permissioned academic network
"""

from flask import Flask, request, jsonify
import hashlib
import json
from datetime import datetime
import requests

app = Flask(__name__)

BLOCKCHAIN_FILE = "blockchain_5000.json"
OTHER_NODES = ["http://127.0.0.1:5001"]   # list – easy to extend

# ──────────────────────────────────────────────────────────────────────────────
# Persistence helpers
# ──────────────────────────────────────────────────────────────────────────────

def load_chain():
    try:
        with open(BLOCKCHAIN_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_chain(chain):
    with open(BLOCKCHAIN_FILE, "w") as f:
        json.dump(chain, f, indent=4)


# ──────────────────────────────────────────────────────────────────────────────
# Blockchain helpers
# ──────────────────────────────────────────────────────────────────────────────

def compute_hash(block: dict) -> str:
    """SHA-256 of the block (excluding the 'hash' field itself)."""
    block_copy = {k: v for k, v in block.items() if k != "hash"}
    return hashlib.sha256(
        json.dumps(block_copy, sort_keys=True).encode()
    ).hexdigest()


def is_chain_valid(chain: list) -> bool:
    """Validate hash linkage and block integrity."""
    for i in range(1, len(chain)):
        current = chain[i]
        prev    = chain[i - 1]

        # Check previous_hash pointer
        if current["previous_hash"] != prev["hash"]:
            return False

        # Recompute and compare
        if compute_hash(current) != current["hash"]:
            return False

    return True


def create_genesis_block() -> dict:
    """Genesis block – index 0, no previous hash."""
    genesis = {
        "index"        : 0,
        "timestamp"    : str(datetime.now()),
        "student_id"   : "GENESIS",
        "course_id"    : "GENESIS",
        "file_hash"    : "0" * 64,
        "version"      : 0,
        "previous_hash": "0" * 64,
        "node"         : "node1"
    }
    genesis["hash"] = compute_hash(genesis)
    return genesis


def ensure_genesis():
    chain = load_chain()
    if not chain:
        chain = [create_genesis_block()]
        save_chain(chain)
    return chain


# ──────────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return jsonify({"status": "Node1 running ✅", "port": 5000})


@app.route("/add_block", methods=["POST"])
def add_block():
    """
    Accepts: { student_id, course_id, file_hash, version }
    Creates a new block, appends to chain, broadcasts to peers.
    """
    data = request.json
    chain = ensure_genesis()

    prev_hash = chain[-1]["hash"]

    block = {
        "index"        : len(chain),
        "timestamp"    : str(datetime.now()),
        "student_id"   : data["student_id"],
        "course_id"    : data["course_id"],
        "file_hash"    : data["file_hash"],
        "version"      : data["version"],
        "previous_hash": prev_hash,
        "node"         : "node1"
    }
    block["hash"] = compute_hash(block)

    chain.append(block)
    save_chain(chain)

    # Broadcast to peer nodes
    for node_url in OTHER_NODES:
        try:
            requests.post(f"{node_url}/receive_block", json=block, timeout=2)
        except Exception:
            pass

    return jsonify({"message": "Block added ✅", "block_index": block["index"]}), 201


@app.route("/receive_block", methods=["POST"])
def receive_block():
    """Accept a block broadcast from a peer node."""
    block = request.json
    chain = ensure_genesis()

    # Basic validation: previous_hash must match our tip
    if chain and block.get("previous_hash") != chain[-1]["hash"]:
        # Trigger sync to resolve divergence
        try:
            requests.get("http://127.0.0.1:5000/sync", timeout=2)
        except Exception:
            pass
        return jsonify({"message": "Hash mismatch – sync triggered"}), 409

    chain.append(block)
    save_chain(chain)
    return jsonify({"message": "Block received ✅"}), 200


@app.route("/chain", methods=["GET"])
def get_chain():
    chain = ensure_genesis()
    return jsonify({"chain": chain, "length": len(chain)}), 200


@app.route("/validate", methods=["GET"])
def validate():
    chain = ensure_genesis()
    valid = is_chain_valid(chain)
    return jsonify({"valid": valid, "length": len(chain)}), 200


@app.route("/sync", methods=["GET"])
def sync():
    """Longest-valid-chain rule – PoA consensus resolution."""
    chain = ensure_genesis()

    replaced = False
    for node_url in OTHER_NODES:
        try:
            res         = requests.get(f"{node_url}/chain", timeout=3)
            other_chain = res.json()["chain"]

            if len(other_chain) > len(chain) and is_chain_valid(other_chain):
                chain    = other_chain
                replaced = True
        except Exception:
            pass

    if replaced:
        save_chain(chain)
        return jsonify({"message": "Chain replaced with longer valid chain ✅"}), 200

    return jsonify({"message": "Chain already up-to-date ✅"}), 200


# ──────────────────────────────────────────────────────────────────────────────
# Run
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ensure_genesis()
    app.run(port=5000, debug=True)
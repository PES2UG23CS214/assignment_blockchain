"""
Node 2 – Blockchain Peer Node (Port 5001)
Academic Assignment Submission Integrity System
"""

from flask import Flask, request, jsonify
import hashlib
import json
from datetime import datetime
import requests

app = Flask(__name__)

BLOCKCHAIN_FILE = "blockchain_5001.json"
OTHER_NODES = ["http://127.0.0.1:5000"]


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
    block_copy = {k: v for k, v in block.items() if k != "hash"}
    return hashlib.sha256(
        json.dumps(block_copy, sort_keys=True).encode()
    ).hexdigest()


def is_chain_valid(chain: list) -> bool:
    for i in range(1, len(chain)):
        current = chain[i]
        prev    = chain[i - 1]
        if current["previous_hash"] != prev["hash"]:
            return False
        if compute_hash(current) != current["hash"]:
            return False
    return True


def create_genesis_block() -> dict:
    genesis = {
        "index"        : 0,
        "timestamp"    : str(datetime.now()),
        "student_id"   : "GENESIS",
        "course_id"    : "GENESIS",
        "file_hash"    : "0" * 64,
        "version"      : 0,
        "previous_hash": "0" * 64,
        "node"         : "node2"
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
    return jsonify({"status": "Node2 running ✅", "port": 5001})


@app.route("/receive_block", methods=["POST"])
def receive_block():
    """Accept a broadcasted block from node1."""
    block = request.json
    chain = ensure_genesis()

    if chain and block.get("previous_hash") != chain[-1]["hash"]:
        try:
            requests.get("http://127.0.0.1:5001/sync", timeout=2)
        except Exception:
            pass
        return jsonify({"message": "Hash mismatch – sync triggered"}), 409

    chain.append(block)
    save_chain(chain)
    return jsonify({"message": "Block added to node2 ✅"}), 200


@app.route("/chain", methods=["GET"])
def get_chain():
    chain = ensure_genesis()
    return jsonify({"chain": chain, "length": len(chain)}), 200


@app.route("/validate", methods=["GET"])
def validate():
    chain = ensure_genesis()
    return jsonify({"valid": is_chain_valid(chain), "length": len(chain)}), 200


@app.route("/sync", methods=["GET"])
def sync():
    """Sync with node1 if its chain is longer and valid."""
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
        return jsonify({"message": "Chain synced from node1 ✅"}), 200

    return jsonify({"message": "Chain already up-to-date ✅"}), 200


# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ensure_genesis()
    app.run(port=5001, debug=True)
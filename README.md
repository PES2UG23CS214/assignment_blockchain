# BlockSubmit
### Academic Assignment Submission Integrity System

**Subject Code:** UE23CS342BA5 — Blockchain Technology  
**Department:** Computer Science and Engineering, PES University  
**Problem Statement:** #34

---

## Team Members

| SRN | Name | Role |
|---|---|---|
| PES2UG23CS201 | Team Member 1 | Frontend & UI |
| PES2UG23CS213 | Team Member 2 | Smart Contract |
| PES2UG23CS214 | Team Member 3 | Blockchain & Backend |

---

## What is BlockSubmit?

BlockSubmit is a blockchain-based system that records assignment submission hashes and timestamps, ensuring integrity, proof of submission time, and protection against disputes.

The system records the following on the blockchain:
- SHA-256 hash of the submitted assignment file
- Timestamp of submission
- Student ID and Course ID
- Assignment version number

Once recorded:
- The submission time cannot be altered
- File integrity can be verified anytime
- Students and instructors have a trusted record

---

## Smart Contract

| Field | Value |
|---|---|
| **Network** | Sepolia Testnet |
| **Contract Address** | `0x1B1fb2428DD522Bd2201A0bBE9cFC8b1f8a93c63` |
| **Verified on** | Sourcify ✅ Blockscout ✅ |
| **Etherscan** | https://sepolia.etherscan.io/address/0x1B1fb2428DD522Bd2201A0bBE9cFC8b1f8a93c63 |

---

## Project Structure

```
assignment_blockchain/
│
├── main_app.py              # Main Flask web app (port 5002)
├── users.json               # User accounts with roles and courses
├── requirements.txt         # Python dependencies
│
├── node1/
│   ├── app.py               # Blockchain Node 1 (port 5000)
│   └── blockchain_5000.json # Node 1 chain data (11 blocks)
│
├── node2/
│   └── app.py               # Blockchain Node 2 (port 5001)
│
├── templates/
│   ├── login.html           # Login page
│   ├── signup.html          # Signup page
│   ├── student.html         # Student dashboard
│   └── teacher.html         # Teacher dashboard
│
└── contracts/
    └── AssignmentSubmission.sol  # Solidity smart contract
```

---

## Technology Stack

- **Backend:** Python 3.14, Flask
- **Blockchain:** Custom Python blockchain (SHA-256, PoA consensus)
- **Smart Contract:** Solidity ^0.8.0 deployed on Sepolia
- **Wallet:** MetaMask + ethers.js 6.7
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Storage:** JSON files per node

---

## How to Run

### Prerequisites
- Python 3.x installed
- MetaMask browser extension installed
- MetaMask set to Sepolia testnet

### Step 1 — Install dependencies
```bash
pip install flask requests
```

### Step 2 — Start Node 1 (Terminal 1)
```bash
cd node1
python app.py
```
Node 1 runs on: http://127.0.0.1:5000

### Step 3 — Start Node 2 (Terminal 2)
```bash
cd node2
python app.py
```
Node 2 runs on: http://127.0.0.1:5001

### Step 4 — Start Main App (Terminal 3)
```bash
python main_app.py
```
Web app runs on: http://127.0.0.1:5002

### Step 5 — Open Browser
```
http://127.0.0.1:5002
```

---

## Default Users

| Username | Password | Role | Courses |
|---|---|---|---|
| PES2UG23CS214 | PES2UG23CS214 | Student | CS101, CS102, CS103 |
| PES2UG23CS201 | vk100 | Student | CS201 |
| GUNDA | GUNDA | Teacher | CS101, CS102, CS103 |

---

## How It Works

### Student submits assignment:
1. Student uploads file on dashboard
2. Browser computes SHA-256 hash
3. Hash recorded on Python blockchain (Node1 → Node2)
4. MetaMask popup appears → student confirms
5. Hash permanently recorded on Ethereum Sepolia
6. All 3 layers confirmed ✅

### Teacher verifies integrity:
1. Teacher uploads the file they received
2. System computes SHA-256 hash
3. Compares against blockchain record
4. Shows Original ✅ or Modified ❌

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /submit_ajax | AJAX file upload — returns JSON |
| POST | /verify | Verify file integrity |
| GET | /api/chain_status | Node health status |
| POST | /add_block | Add block to chain |
| GET | /chain | Get full blockchain |
| GET | /validate | Validate chain integrity |
| GET | /sync | Sync nodes (PoA consensus) |

---

## Consensus Algorithm

**Proof of Authority (PoA)** with Longest Valid Chain rule:
- No mining required — instant block confirmation
- Suitable for permissioned institutional network
- Conflict resolved by longest valid chain

---

## Security Features

- SHA-256 file hashing — any change detected
- Cryptographic hash chain — tampering detectable
- Immutable EVM timestamp — cannot be forged
- MetaMask ECDSA identity — cryptographic proof
- Two-node fault tolerance — no single point of failure

---

## License

This project is developed for academic purposes under PES University Blockchain Technology course (UE23CS342BA5).
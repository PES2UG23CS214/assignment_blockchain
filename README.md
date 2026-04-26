# 🚀 BlockSubmit: Blockchain Assignment Submission System

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-WebApp-green)
![Blockchain](https://img.shields.io/badge/Concept-Blockchain-orange)
![Status](https://img.shields.io/badge/Project-Active-success)

> 🔐 Secure, immutable, and role-based assignment submission system using blockchain principles

---

## 📌 Overview

**BlockSubmit** is a blockchain-inspired system that ensures:

- ✔️ Tamper-proof assignment submissions  
- ✔️ Verifiable timestamps  
- ✔️ Role-based access (Student / Teacher)  
- ✔️ Course-based filtering  
- ✔️ Version tracking for submissions  

---

## 🎯 Problem Statement

Traditional systems suffer from:

- ❌ File modification after submission  
- ❌ No proof of submission time  
- ❌ No version tracking  
- ❌ No transparency  

---

## 💡 Solution

BlockSubmit solves this using:

- 🔐 SHA-256 hashing  
- ⛓️ Blockchain-style linked records  
- 🕒 Immutable timestamps  
- 🔄 Version tracking  
- 👥 Role-based authentication  
- 📚 Course-based access control  

---

## 🌟 Features

- 🔐 Secure Login & Signup system  
- 👥 Role-based dashboards (Student / Teacher)  
- 📂 Assignment Upload with version tracking  
- 🔍 File Verification (Original / Updated / Invalid)  
- ⛓️ Blockchain record storage  
- 🌐 Multi-node system (Node1 & Node2)  
- 🎨 Modern Dark UI  

---

## 🏗️ Project Structure


assignment_blockchain/
│
├── main_app.py
├── users.json
├── requirements.txt
├── README.md
│
├── node1/
│ ├── app.py
│ └── blockchain_5000.json
│
├── node2/
│ ├── app.py
│ └── blockchain_5001.json
│
├── templates/
│ ├── login.html
│ ├── signup.html
│ ├── student.html
│ ├── teacher.html
│
└── blockchain.json


---

## ⚙️ How It Works

1. Student uploads assignment  
2. File is hashed using SHA-256  
3. Block is created with:
   - Student ID  
   - Course ID  
   - Version  
   - File Hash  
   - Timestamp  
   - Previous Hash  
4. Block is stored in blockchain  
5. Teacher verifies file integrity  

---

## 🔍 Verification Logic

| Case | Result |
|------|--------|
| Same file | ✅ Original |
| Modified file | ⚠️ Updated |
| Wrong file | ❌ Invalid |

---

## 🛠️ Tech Stack

- Python (Flask)  
- HTML + CSS (Dark UI)  
- SHA-256 (hashlib)  
- REST APIs  
- JSON storage  

---

## ▶️ How to Run

### 1️⃣ Start Node 1
```bash
cd node1
python app.py
2️⃣ Start Node 2
cd node2
python app.py
3️⃣ Start Main App
python main_app.py
🌐 Access URLs
Service	URL
Main App	http://127.0.0.1:5002

Node 1	http://127.0.0.1:5000

Node 2	http://127.0.0.1:5001
👨‍🏫 Roles
🎓 Student
Upload assignments
Auto version tracking
Verify files
👨‍🏫 Teacher
View blockchain records
Filter by courses
Verify assignments
🚀 Future Enhancements
🔄 Node synchronization
⛏️ Proof-of-Work
🗄️ Database integration
🔐 JWT Authentication
☁️ Deployment (Render / AWS)
🧠 Key Learnings
Blockchain fundamentals
Data integrity using hashing
Multi-node architecture
Role-based system design
Real-world system implementation
👨‍💻 Author

Podili Sipivishta

⭐ Contribution

Feel free to fork and enhance this project!

📜 License

Educational / Academic Use
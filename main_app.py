"""
main_app.py – BlockSubmit Main Application (Port 5002)
Academic Assignment Submission Integrity System
- Flask web app with login/signup, student dashboard, teacher dashboard
- MetaMask / Ethereum integration via Web3.js (client-side)
- All core logic talks to Node1 (port 5000) which syncs with Node2 (5001)
"""

from flask import Flask, render_template, request, redirect, session, jsonify
import hashlib
import requests
import json
import os

app = Flask(__name__)
app.secret_key = "blocksubmit_secret_2024"

NODE_URL = "http://127.0.0.1:5000"


# ──────────────────────────────────────────────────────────────────────────────
# User helpers
# ──────────────────────────────────────────────────────────────────────────────

def load_users():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)


def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)


# ──────────────────────────────────────────────────────────────────────────────
# Auth Routes
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        username      = request.form.get("username", "").strip()
        password      = request.form.get("password", "")
        selected_role = request.form.get("role")

        users = load_users()

        if username not in users:
            return render_template("login.html", msg="User not found ❌")

        user = users[username]

        if user["password"] != password:
            return render_template("login.html", msg="Wrong password ❌")

        if selected_role != user.get("role"):
            return render_template("login.html", msg="Wrong role selected ❌")

        session["user"]    = username
        session["role"]    = user["role"]
        session["courses"] = user.get("courses", [])

        return redirect("/student" if user["role"] == "student" else "/teacher")

    return render_template("login.html", msg=msg)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    msg = ""
    if request.method == "POST":
        username     = request.form.get("username", "").strip()
        password     = request.form.get("password", "")
        role         = request.form.get("role")
        courses_raw  = request.form.get("courses", "").strip()

        # Parse comma-separated courses, e.g. "CS101,CS102" → ["CS101","CS102"]
        courses = [c.strip().upper() for c in courses_raw.split(",") if c.strip()]

        users = load_users()

        if username in users:
            return render_template("signup.html", msg="User already exists ❌")

        if not courses:
            return render_template("signup.html", msg="Please enter at least one course (e.g. CS101,CS102) ❌")

        users[username] = {
            "password": password,
            "role"    : role,
            "courses" : courses
        }
        save_users(users)
        return redirect("/login")

    return render_template("signup.html", msg=msg)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ──────────────────────────────────────────────────────────────────────────────
# Student Dashboard
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/student", methods=["GET", "POST"])
def student():
    if "user" not in session or session.get("role") != "student":
        return redirect("/")

    msg = ""

    if request.method == "POST":
        file      = request.files.get("file")
        course_id = request.form.get("course_id")

        if not file or file.filename == "":
            return render_template("student.html", msg="No file selected ❌")

        file_bytes = file.read()
        file_hash  = hashlib.sha256(file_bytes).hexdigest()
        student_id = session["user"]

        # ── Determine next version ──
        try:
            res   = requests.get(f"{NODE_URL}/chain", timeout=5)
            chain = res.json().get("chain", [])
        except Exception:
            chain = []

        version = 1
        for block in chain:
            if (block.get("student_id") == student_id and
                    block.get("course_id") == course_id):
                version = max(version, block.get("version", 0) + 1)

        payload = {
            "student_id": student_id,
            "course_id" : course_id,
            "file_hash" : file_hash,
            "version"   : version
        }

        try:
            requests.post(f"{NODE_URL}/add_block", json=payload, timeout=5)
            # Trigger sync across nodes
            try:
                requests.get(f"{NODE_URL}/sync", timeout=3)
            except Exception:
                pass

            msg = f"✅ Submitted! Version {version} | Hash: {file_hash[:16]}..."
        except Exception:
            msg = "❌ Upload failed – check that Node1 is running."

    return render_template("student.html", msg=msg)


# ──────────────────────────────────────────────────────────────────────────────
# Teacher Dashboard
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/teacher", methods=["GET", "POST"])
def teacher():
    if "user" not in session or session.get("role") != "teacher":
        return redirect("/")

    try:
        res   = requests.get(f"{NODE_URL}/chain", timeout=5)
        chain = res.json().get("chain", [])
    except Exception:
        chain = []

    # Keep only latest version per (student, course)
    latest_map = {}
    for block in chain:
        if block.get("student_id") == "GENESIS":
            continue
        key = (block["student_id"], block["course_id"])
        if key not in latest_map or block.get("version", 1) > latest_map[key].get("version", 1):
            latest_map[key] = block

    chain = sorted(latest_map.values(), key=lambda x: x["timestamp"], reverse=True)

    selected_course = ""
    if request.method == "POST":
        selected_course = request.form.get("course_id", "")
        if selected_course:
            chain = [b for b in chain if b["course_id"] == selected_course]

    return render_template(
        "teacher.html",
        chain=chain,
        courses=session.get("courses", []),
        selected_course=selected_course
    )


# ──────────────────────────────────────────────────────────────────────────────
# AJAX Submit — called by student.html fetch() so MetaMask fires on same page
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/submit_ajax", methods=["POST"])
def submit_ajax():
    if "user" not in session or session.get("role") != "student":
        return jsonify({"success": False, "message": "Not authenticated"})

    file      = request.files.get("file")
    course_id = request.form.get("course_id")

    if not file or file.filename == "":
        return jsonify({"success": False, "message": "No file selected"})

    file_bytes = file.read()
    file_hash  = hashlib.sha256(file_bytes).hexdigest()
    student_id = session["user"]

    # Determine next version
    try:
        res   = requests.get(f"{NODE_URL}/chain", timeout=5)
        chain = res.json().get("chain", [])
    except Exception:
        chain = []

    version = 1
    for block in chain:
        if (block.get("student_id") == student_id and
                block.get("course_id") == course_id):
            version = max(version, block.get("version", 0) + 1)

    payload = {
        "student_id": student_id,
        "course_id" : course_id,
        "file_hash" : file_hash,
        "version"   : version
    }

    try:
        requests.post(f"{NODE_URL}/add_block", json=payload, timeout=5)
        try:
            requests.get(f"{NODE_URL}/sync", timeout=3)
        except Exception:
            pass
        return jsonify({
            "success"  : True,
            "message"  : f"Submitted! Version {version}",
            "version"  : version,
            "file_hash": file_hash
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Node error: {str(e)}"})


# ──────────────────────────────────────────────────────────────────────────────
# Verify Submission
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/verify", methods=["POST"])
def verify():
    file       = request.files.get("file")
    student_id = request.form.get("student_id")
    course_id  = request.form.get("course_id")

    if not file:
        return jsonify({"status": "error", "message": "No file uploaded ❌"})

    file_hash = hashlib.sha256(file.read()).hexdigest()

    try:
        res   = requests.get(f"{NODE_URL}/chain", timeout=5)
        chain = res.json().get("chain", [])
    except Exception:
        chain = []

    relevant = [
        b for b in chain
        if b.get("student_id") == student_id and b.get("course_id") == course_id
    ]

    if not relevant:
        return jsonify({"status": "not_found", "message": "No record found ❌"})

    latest = max(relevant, key=lambda x: x.get("version", 1))

    if file_hash == latest["file_hash"]:
        return jsonify({
            "status" : "original",
            "message": f"✅ Original file – Version {latest['version']}\nTimestamp: {latest['timestamp']}"
        })
    elif any(file_hash == b["file_hash"] for b in relevant):
        return jsonify({
            "status" : "old",
            "message": "⚠️ Matches an older version – not the latest submission"
        })
    else:
        return jsonify({
            "status" : "modified",
            "message": "❌ File has been modified or does not match any submission"
        })


# ──────────────────────────────────────────────────────────────────────────────
# API: Chain status (used by MetaMask dashboard widget)
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/api/chain_status")
def api_chain_status():
    try:
        r1 = requests.get(f"{NODE_URL}/validate",              timeout=3).json()
        r2 = requests.get("http://127.0.0.1:5001/validate",    timeout=3).json()
    except Exception:
        r1 = {"valid": False, "length": 0}
        r2 = {"valid": False, "length": 0}
    return jsonify({"node1": r1, "node2": r2})


# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(port=5002, debug=True)
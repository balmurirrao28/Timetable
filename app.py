import os
import sqlite3
from flask import Flask, request, redirect, render_template_string
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "timetable-secret-key-2026")
DB = "timetable.db"

# Gemini API setup helper
def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None, "GEMINI_API_KEY is not set."
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        return client, None
    except Exception as e:
        return None, str(e)

def ask_gemini(prompt, system_instruction=None):
    client, err = get_gemini_client()
    if not client:
        return f"⚡ **Gemini AI Status**: Key not configured ({err}).\nSet `GEMINI_API_KEY` in your `.env` file or on the AI Assistant page to enable live Gemini AI reasoning."
    try:
        model_name = "gemini-3.6-flash"
        config = {}
        if system_instruction:
            config["system_instruction"] = system_instruction
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config if config else None
        )
        return response.text
    except Exception as e:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as ex:
            return f"❌ **Gemini AI Error**: {str(ex)}"

# Database setup
def connect():
    return sqlite3.connect(DB)

def init_db():
    con = connect()
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS faculty(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, unavailable TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS rooms(id INTEGER PRIMARY KEY AUTOINCREMENT, room TEXT UNIQUE, capacity INTEGER, type TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS timetable(id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT, period INTEGER, section TEXT, subject TEXT, faculty TEXT, room TEXT)")
    
    # Seed default data if empty
    if cur.execute("SELECT COUNT(*) FROM faculty").fetchone()[0] == 0:
        cur.executemany("INSERT INTO faculty(name, unavailable) VALUES(?,?)", [
            ("Mr. Anwar Ali", ""),
            ("Mrs. Manasa Raj", ""),
            ("Mrs. Amulya", ""),
            ("Dr. D Jyothi", ""),
            ("Mr. B. Balaji", ""),
            ("Mrs. Arshiya Begum", ""),
            ("Ms. Shakina", ""),
            ("Mrs. Hridayama", ""),
            ("Ms. Bhavana", ""),
            ("Mr. Shiva Krishna", ""),
            ("Mrs. Tahneyath", "")
        ])
    if cur.execute("SELECT COUNT(*) FROM rooms").fetchone()[0] == 0:
        cur.executemany("INSERT INTO rooms(room, capacity, type) VALUES(?,?,?)", [
            ("AK-204", 60, "Classroom"),
            ("AK-406", 60, "Lab"),
            ("JC-404", 60, "Lab"),
            ("AK-403", 60, "Lab"),
            ("JC-401", 60, "Lab"),
            ("AK-401", 60, "Classroom"),
            ("AK-402", 60, "Classroom")
        ])
    if cur.execute("SELECT COUNT(*) FROM timetable").fetchone()[0] == 0:
        cur.executemany("INSERT INTO timetable(day, period, section, subject, faculty, room) VALUES(?,?,?,?,?,?)", [
            ("Mon", 1, "CSD-C", "SE (Software Engineering)", "Mrs. Arshiya Begum", "AK-204"),
            ("Mon", 2, "CSD-C", "ACD (Automata & Compiler Design)", "Mr. Anwar Ali", "AK-204"),
            ("Mon", 3, "CSD-C", "BDT (Big Data Technologies)", "Dr. D Jyothi", "AK-204"),
            ("Mon", 4, "CSD-C", "PDS (Python For Data Science)", "Ms. Shakina", "AK-204"),
            ("Mon", 5, "CSD-C", "B1-WP LAB / B2-BDT LAB", "Mrs. Manasa Raj", "AK-406"),
            ("Mon", 6, "CSD-C", "B1-WP LAB / B2-BDT LAB", "Mrs. Manasa Raj", "AK-406"),

            ("Tue", 1, "CSD-C", "WP (Web Programming)", "Mrs. Manasa Raj", "AK-204"),
            ("Tue", 2, "CSD-C", "ACD (Automata & Compiler Design)", "Mr. Anwar Ali", "AK-204"),
            ("Tue", 3, "CSD-C", "BDT (Big Data Technologies)", "Dr. D Jyothi", "AK-204"),
            ("Tue", 4, "CSD-C", "PDS (Python For Data Science)", "Ms. Shakina", "AK-204"),
            ("Tue", 5, "CSD-C", "WP (Web Programming)", "Mrs. Manasa Raj", "AK-204"),
            ("Tue", 6, "CSD-C", "LIBRARY", "Mrs. Manasa Raj", "AK-204"),

            ("Wed", 1, "CSD-C", "PDS (Python For Data Science)", "Ms. Shakina", "AK-204"),
            ("Wed", 2, "CSD-C", "HVPE (Human Values)", "Mrs. Hridayama", "AK-204"),
            ("Wed", 3, "CSD-C", "BDT (Big Data Technologies)", "Dr. D Jyothi", "AK-204"),
            ("Wed", 4, "CSD-C", "WP (Web Programming)", "Mrs. Manasa Raj", "AK-204"),
            ("Wed", 5, "CSD-C", "SEMINAR-B1 / MOOCS-B2", "Mr. Shiva Krishna", "AK-402"),
            ("Wed", 6, "CSD-C", "SEMINAR-B1 / MOOCS-B2", "Mr. Shiva Krishna", "AK-402"),

            ("Thu", 1, "CSD-C", "BDT (Big Data Technologies)", "Dr. D Jyothi", "AK-204"),
            ("Thu", 2, "CSD-C", "SE (Software Engineering)", "Mrs. Arshiya Begum", "AK-204"),
            ("Thu", 3, "CSD-C", "ACD (Automata & Compiler Design)", "Mr. Anwar Ali", "AK-204"),
            ("Thu", 4, "CSD-C", "SE (Software Engineering)", "Mrs. Arshiya Begum", "AK-204"),
            ("Thu", 5, "CSD-C", "ACD (Automata & Compiler Design)", "Mr. Anwar Ali", "AK-204"),
            ("Thu", 6, "CSD-C", "WP (Web Programming)", "Mrs. Manasa Raj", "AK-204"),

            ("Fri", 1, "CSD-C", "ACD (Automata & Compiler Design)", "Mr. Anwar Ali", "AK-204"),
            ("Fri", 2, "CSD-C", "WP (Web Programming)", "Mrs. Manasa Raj", "AK-204"),
            ("Fri", 3, "CSD-C", "SE (Software Engineering)", "Mrs. Arshiya Begum", "AK-204"),
            ("Fri", 4, "CSD-C", "B1-BDT LAB / B2-WP LAB", "Dr. D Jyothi", "JC-401"),
            ("Fri", 5, "CSD-C", "B1-BDT LAB / B2-WP LAB", "Dr. D Jyothi", "JC-401"),
            ("Fri", 6, "CSD-C", "SPORTS", "Mrs. Manasa Raj", "AK-204"),

            ("Sat", 1, "CSD-C", "BDT (Big Data Technologies)", "Dr. D Jyothi", "AK-204"),
            ("Sat", 2, "CSD-C", "SE (Software Engineering)", "Mrs. Arshiya Begum", "AK-204"),
            ("Sat", 3, "CSD-C", "PDS (Python For Data Science)", "Ms. Shakina", "AK-204"),
            ("Sat", 4, "CSD-C", "MOOCS-B1 / SEMINAR-B2", "Ms. Bhavana", "AK-401"),
            ("Sat", 5, "CSD-C", "MOOCS-B1 / SEMINAR-B2", "Ms. Bhavana", "AK-401"),
            ("Sat", 6, "CSD-C", "COUNSELLING", "Mrs. Manasa Raj", "AK-204")
        ])
    con.commit()
    con.close()

init_db()

SECTION_STRENGTH = {
    "CSD-C": 55,
    "CSE-A": 65,
    "CSE-B": 58,
    "ECE-A": 55
}

def detect_conflict(day, period, section, faculty, room, subject, exclude_id=None):
    """
    Detect timetable conflicts for a proposed class schedule.
    exclude_id: Optional timetable ID to ignore (used during simulation / editing).
    """
    con = connect()
    cur = con.cursor()
    
    query = "SELECT id, section, faculty, room, subject FROM timetable WHERE day=? AND period=?"
    params = [day, period]
    if exclude_id is not None:
        query += " AND id!=?"
        params.append(exclude_id)
        
    rows = cur.execute(query, params).fetchall()
    room_info = cur.execute("SELECT capacity, type FROM rooms WHERE room=?", (room,)).fetchone()
    faculty_info = cur.execute("SELECT unavailable FROM faculty WHERE name=?", (faculty,)).fetchone()
    con.close()
    
    conflicts = []
    
    # Rule 1: Faculty / Room / Section conflicts
    for cid, s, f, r, sub in rows:
        if f == faculty:
            conflicts.append(f"Faculty {faculty} is already teaching '{sub}' in {r} for {s} during {day} P{period}.")
        if r == room:
            conflicts.append(f"Room {room} is already occupied by {s} ('{sub}') during {day} P{period}.")
        if s == section:
            conflicts.append(f"Section {section} already has class '{sub}' with {f} in {r} during {day} P{period}.")
            
    # Rule 2: Faculty availability check
    slot = f"{day}-{period}"
    alt_slot = f"{day}-P{period}"
    if faculty_info and faculty_info[0]:
        unavail_slots = [x.strip() for x in faculty_info[0].split(",") if x.strip()]
        if slot in unavail_slots or alt_slot in unavail_slots:
            conflicts.append(f"Faculty {faculty} is marked UNAVAILABLE during {day} Period {period}.")
            
    # Rule 3: Room capacity check
    if room_info:
        cap, typ = room_info
        sec_strength = SECTION_STRENGTH.get(section, 60)
        if sec_strength > cap:
            conflicts.append(f"Room Capacity Exceeded: {section} has {sec_strength} students, but {room} capacity is {cap}.")
        if "Lab" in subject and typ != "Lab":
            conflicts.append(f"Lab Requirement Conflict: Subject '{subject}' requires a Laboratory, but {room} is a '{typ}'.")
            
    return conflicts

def recommend_slot(section, subject, faculty, room, exclude_id=None):
    """Search for the slot with zero or minimum conflicts across Mon-Fri, P1-P6."""
    best = None
    for d in ["Mon", "Tue", "Wed", "Thu", "Fri"]:
        for p in range(1, 7):
            conflicts = detect_conflict(d, p, section, faculty, room, subject, exclude_id=exclude_id)
            score = len(conflicts)
            if best is None or score < best["score"]:
                best = {"day": d, "period": p, "score": score, "conflicts": conflicts}
                if score == 0:
                    return best
    return best

BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Timetable AI Studio</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --border: #e2e8f0;
            --text: #0f172a;
            --text-muted: #64748b;
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --accent: #d946ef;
            --success: #16a34a;
            --warning: #d97706;
            --danger: #e11d48;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }
        
        body {
            background-color: var(--bg);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        
        .navbar-brand {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--text);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .navbar-brand span {
            background: linear-gradient(135deg, #8b5cf6, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .nav-links {
            display: flex;
            gap: 0.75rem;
            list-style: none;
            flex-wrap: wrap;
        }
        
        .nav-link {
            color: #475569;
            text-decoration: none;
            padding: 0.5rem 0.85rem;
            border-radius: 0.5rem;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        
        .nav-link:hover, .nav-link.active {
            color: #0f172a;
            background: #f1f5f9;
            border: 1px solid #cbd5e1;
        }
        
        .nav-link.gemini-btn {
            background: linear-gradient(135deg, #ec4899, #8b5cf6);
            color: #ffffff;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(236, 72, 153, 0.25);
            border: none;
        }
        .nav-link.gemini-btn:hover {
            opacity: 0.95;
            transform: translateY(-1px);
            color: #ffffff;
        }

        .container {
            max-width: 1200px;
            width: 100%;
            margin: 2rem auto;
            padding: 0 1.5rem;
            flex: 1;
        }
        
        .page-title {
            font-size: 1.85rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }
        
        .page-subtitle {
            color: var(--text-muted);
            margin-bottom: 2rem;
            font-size: 0.95rem;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05), 0 2px 6px -1px rgba(0, 0, 0, 0.02);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .card:hover {
            box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.08);
            border-color: #cbd5e1;
        }
        
        .card-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #0f172a;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .stat-val {
            font-size: 2.25rem;
            font-weight: 700;
            color: #8b5cf6;
            margin-bottom: 0.25rem;
        }
        
        .stat-label {
            font-size: 0.85rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            background: #6366f1;
            color: #ffffff;
            border: none;
            padding: 0.65rem 1.25rem;
            border-radius: 0.5rem;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
        }
        
        .btn:hover {
            background: #4f46e5;
            transform: translateY(-1px);
        }
        
        .btn-secondary {
            background: #f1f5f9;
            border: 1px solid #cbd5e1;
            color: #334155;
            box-shadow: none;
        }
        .btn-secondary:hover {
            background: #e2e8f0;
            color: #0f172a;
        }

        .btn-danger {
            background: #ffe4e6;
            color: #be123c;
            border: 1px solid #fecdd3;
            padding: 0.35rem 0.75rem;
            font-size: 0.8rem;
            box-shadow: none;
        }
        .btn-danger:hover {
            background: #e11d48;
            color: #ffffff;
        }
        
        .form-group {
            margin-bottom: 1.25rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.4rem;
            font-size: 0.875rem;
            font-weight: 500;
            color: #334155;
        }
        
        .form-control, select, textarea {
            width: 100%;
            padding: 0.65rem 0.9rem;
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 0.5rem;
            color: #0f172a;
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s ease;
        }
        
        .form-control:focus, select:focus, textarea:focus {
            border-color: #8b5cf6;
            background: #ffffff;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
        }

        select option {
            background: #ffffff;
            color: #0f172a;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        
        th, td {
            padding: 0.85rem 1rem;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
            font-size: 0.9rem;
        }
        
        th {
            background: #f8fafc;
            color: #475569;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }
        
        tr:hover td {
            background: #f8fafc;
        }
        
        .badge {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .badge-success { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
        .badge-warning { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
        .badge-danger { background: #ffe4e6; color: #be123c; border: 1px solid #fecdd3; }
        .badge-info { background: #f3e8ff; color: #6b21a8; border: 1px solid #e9d5ff; }
        
        .alert {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
        }
        .alert-danger {
            background: #fff1f2;
            border: 1px solid #fecdd3;
            color: #9f1239;
        }
        .alert-success {
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            color: #166534;
        }
        
        .gemini-box {
            background: linear-gradient(135deg, #faf5ff, #fdf4ff);
            border: 1px solid #e9d5ff;
            border-radius: 1rem;
            padding: 1.5rem;
            margin-top: 1.5rem;
            box-shadow: 0 4px 15px rgba(147, 51, 234, 0.06);
        }
        
        .gemini-box h4 {
            color: #7e22ce;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
        }
        
        .markdown-content {
            line-height: 1.6;
            font-size: 0.95rem;
            white-space: pre-wrap;
            color: #334155;
        }

        footer {
            text-align: center;
            padding: 1.5rem;
            color: #64748b;
            font-size: 0.85rem;
            border-top: 1px solid #e2e8f0;
            margin-top: auto;
            background: #ffffff;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="navbar-brand">
            📅 <span>Timetable AI Studio</span>
        </a>
        <ul class="nav-links">
            <li><a href="/" class="nav-link">Dashboard</a></li>
            <li><a href="/faculty" class="nav-link">Faculty</a></li>
            <li><a href="/rooms" class="nav-link">Rooms & Labs</a></li>
            <li><a href="/timetable" class="nav-link">Timetable</a></li>
            <li><a href="/add" class="nav-link">Add Class</a></li>
            <li><a href="/simulate" class="nav-link">Simulate Change</a></li>
            <li><a href="/ai-advisor" class="nav-link gemini-btn">✨ Gemini AI Assistant</a></li>
        </ul>
    </nav>
    
    <div class="container">
        {{ body|safe }}
    </div>
    
    <footer>
        Timetable Conflict Resolution System | Docker Container Backend | Powered by Flask & Gemini AI
    </footer>
</body>
</html>
"""

def render_page(title, body_html):
    return render_template_string(BASE_LAYOUT, title=title, body=body_html)

# ---------- ROUTE: DASHBOARD ----------
@app.route("/")
def home():
    con = connect()
    cur = con.cursor()
    faculty_cnt = cur.execute("SELECT COUNT(*) FROM faculty").fetchone()[0]
    rooms_cnt = cur.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
    classes_cnt = cur.execute("SELECT COUNT(*) FROM timetable").fetchone()[0]
    
    all_classes = cur.execute("SELECT id, day, period, section, subject, faculty, room FROM timetable").fetchall()
    conflict_details = []
    for c in all_classes:
        cid, d, p, s, sub, f, r = c
        conflicts = detect_conflict(d, p, s, f, r, sub, exclude_id=cid)
        if conflicts:
            conflict_details.append(f"{s} ({sub} with {f} in {r} on {d} P{p}): " + "; ".join(conflicts))
    con.close()
    
    page_body = render_template_string("""
    <div class="page-title">
        <span>🚀</span> Dashboard Overview
    </div>
    <p class="page-subtitle">Smart Academic Timetable Management & Conflict Resolution System running in Docker, powered by Gemini AI.</p>
    
    <div class="grid">
        <div class="card">
            <div class="stat-val">{{ faculty_cnt }}</div>
            <div class="stat-label">Faculty Members</div>
        </div>
        <div class="card">
            <div class="stat-val">{{ rooms_cnt }}</div>
            <div class="stat-label">Rooms & Labs</div>
        </div>
        <div class="card">
            <div class="stat-val">{{ classes_cnt }}</div>
            <div class="stat-label">Scheduled Classes</div>
        </div>
        <div class="card">
            <div class="stat-val" style="color: {% if conflict_details %}var(--danger){% else %}var(--success){% endif %};">
                {{ conflict_details|length }}
            </div>
            <div class="stat-label">Active Conflicts</div>
        </div>
    </div>
    
    <div class="card" style="margin-bottom: 2rem;">
        <div class="card-title">
            <span>⚡ Quick Actions & Tools</span>
        </div>
        <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
            <a href="/add" class="btn">➕ Add New Class</a>
            <a href="/simulate" class="btn btn-secondary">🔄 Simulate Schedule Changes</a>
            <a href="/ai-advisor" class="btn" style="background: linear-gradient(135deg, var(--accent), var(--primary));">✨ Consult Gemini AI</a>
        </div>
    </div>
    
    {% if conflict_details %}
    <div class="alert alert-danger">
        <strong>⚠️ Detected Schedule Conflicts ({{ conflict_details|length }}):</strong>
        <ul style="margin-left: 1.25rem; margin-top: 0.5rem;">
            {% for item in conflict_details %}
            <li>{{ item }}</li>
            {% endfor %}
        </ul>
    </div>
    {% else %}
    <div class="alert alert-success">
        <strong>✅ System Status:</strong> All scheduled classes are currently conflict-free!
    </div>
    {% endif %}
    """, faculty_cnt=faculty_cnt, rooms_cnt=rooms_cnt, classes_cnt=classes_cnt, conflict_details=conflict_details)
    
    return render_page("Dashboard", page_body)

# ---------- ROUTE: FACULTY MANAGEMENT ----------
@app.route("/faculty", methods=["GET", "POST"])
def faculty():
    con = connect()
    cur = con.cursor()
    msg = None
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        unavailable = request.form.get("unavailable", "").strip()
        if name:
            try:
                cur.execute("INSERT INTO faculty(name, unavailable) VALUES(?,?)", (name, unavailable))
                con.commit()
                msg = ("success", f"Faculty member '{name}' added successfully.")
            except sqlite3.IntegrityError:
                msg = ("danger", f"Faculty '{name}' already exists.")
        else:
            msg = ("danger", "Faculty name is required.")
            
    data = cur.execute("SELECT * FROM faculty").fetchall()
    con.close()
    
    page_body = render_template_string("""
    <div class="page-title">👨‍🏫 Faculty Management</div>
    <p class="page-subtitle">Add faculty profiles and set unavailable day/period slots (e.g. Mon-1, Fri-4).</p>
    
    {% if msg %}
    <div class="alert alert-{{ msg[0] }}">{{ msg[1] }}</div>
    {% endif %}
    
    <div class="grid" style="grid-template-columns: 350px 1fr;">
        <div class="card">
            <div class="card-title">Add Faculty</div>
            <form method="post">
                <div class="form-group">
                    <label>Faculty Name</label>
                    <input type="text" name="name" class="form-control" placeholder="e.g. Dr Rao" required>
                </div>
                <div class="form-group">
                    <label>Unavailable Slots (Comma separated)</label>
                    <input type="text" name="unavailable" class="form-control" placeholder="e.g. Mon-1,Fri-4,Wed-2">
                </div>
                <button type="submit" class="btn" style="width: 100%;">Save Faculty</button>
            </form>
        </div>
        
        <div class="card">
            <div class="card-title">Faculty List</div>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Unavailable Slots</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for f in data %}
                    <tr>
                        <td>{{ f[0] }}</td>
                        <td><strong>{{ f[1] }}</strong></td>
                        <td><span class="badge badge-warning">{{ f[2] or "None" }}</span></td>
                        <td>
                            <a href="/faculty/delete/{{ f[0] }}" class="btn btn-danger" onclick="return confirm('Delete faculty member?');">Delete</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    """, msg=msg, data=data)
    
    return render_page("Faculty Management", page_body)

@app.route("/faculty/delete/<int:fid>")
def faculty_delete(fid):
    con = connect()
    con.execute("DELETE FROM faculty WHERE id=?", (fid,))
    con.commit()
    con.close()
    return redirect("/faculty")

# ---------- ROUTE: ROOMS MANAGEMENT ----------
@app.route("/rooms", methods=["GET", "POST"])
def rooms():
    con = connect()
    cur = con.cursor()
    msg = None
    
    if request.method == "POST":
        room = request.form.get("room", "").strip()
        capacity = request.form.get("capacity", type=int, default=60)
        rtype = request.form.get("type", "Classroom")
        if room:
            try:
                cur.execute("INSERT INTO rooms(room, capacity, type) VALUES(?,?,?)", (room, capacity, rtype))
                con.commit()
                msg = ("success", f"Room '{room}' added successfully.")
            except sqlite3.IntegrityError:
                msg = ("danger", f"Room '{room}' already exists.")
                
    data = cur.execute("SELECT * FROM rooms").fetchall()
    con.close()
    
    page_body = render_template_string("""
    <div class="page-title">🏫 Room & Lab Management</div>
    <p class="page-subtitle">Configure lecture halls, classrooms, and specialized laboratory rooms.</p>
    
    {% if msg %}
    <div class="alert alert-{{ msg[0] }}">{{ msg[1] }}</div>
    {% endif %}
    
    <div class="grid" style="grid-template-columns: 350px 1fr;">
        <div class="card">
            <div class="card-title">Add Room / Lab</div>
            <form method="post">
                <div class="form-group">
                    <label>Room Name / ID</label>
                    <input type="text" name="room" class="form-control" placeholder="e.g. R101, LAB1" required>
                </div>
                <div class="form-group">
                    <label>Seating Capacity</label>
                    <input type="number" name="capacity" class="form-control" value="60" min="10" required>
                </div>
                <div class="form-group">
                    <label>Room Type</label>
                    <select name="type" class="form-control">
                        <option value="Classroom">Classroom</option>
                        <option value="Lab">Lab</option>
                    </select>
                </div>
                <button type="submit" class="btn" style="width: 100%;">Save Room</button>
            </form>
        </div>
        
        <div class="card">
            <div class="card-title">Rooms Directory</div>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Room</th>
                        <th>Capacity</th>
                        <th>Type</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for r in data %}
                    <tr>
                        <td>{{ r[0] }}</td>
                        <td><strong>{{ r[1] }}</strong></td>
                        <td>{{ r[2] }} seats</td>
                        <td>
                            <span class="badge {% if r[3] == 'Lab' %}badge-info{% else %}badge-success{% endif %}">{{ r[3] }}</span>
                        </td>
                        <td>
                            <a href="/rooms/delete/{{ r[0] }}" class="btn btn-danger" onclick="return confirm('Delete room?');">Delete</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    """, msg=msg, data=data)
    
    return render_page("Room Management", page_body)

@app.route("/rooms/delete/<int:rid>")
def rooms_delete(rid):
    con = connect()
    con.execute("DELETE FROM rooms WHERE id=?", (rid,))
    con.commit()
    con.close()
    return redirect("/rooms")

# ---------- ROUTE: VIEW TIMETABLE ----------
@app.route("/timetable")
def timetable():
    con = connect()
    cur = con.cursor()
    rows = cur.execute("SELECT id, day, period, section, subject, faculty, room FROM timetable ORDER BY CASE day WHEN 'Mon' THEN 1 WHEN 'Tue' THEN 2 WHEN 'Wed' THEN 3 WHEN 'Thu' THEN 4 WHEN 'Fri' THEN 5 END, period").fetchall()
    con.close()
    
    timetable_items = []
    for x in rows:
        cid, d, p, s, sub, f, r = x
        conflicts = detect_conflict(d, p, s, f, r, sub, exclude_id=cid)
        timetable_items.append({
            "id": cid,
            "day": d,
            "period": p,
            "section": s,
            "subject": sub,
            "faculty": f,
            "room": r,
            "conflicts": conflicts
        })
        
    page_body = render_template_string("""
    <div class="page-title">
        <span>📘</span> Current Timetable Schedule
    </div>
    <p class="page-subtitle">View scheduled classes across sections and verify conflict statuses.</p>
    
    <div class="card">
        <div class="card-title" style="display: flex; justify-content: space-between;">
            <span>Scheduled Slots</span>
            <a href="/add" class="btn">➕ Add New Class</a>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Day</th>
                    <th>Period</th>
                    <th>Section</th>
                    <th>Subject</th>
                    <th>Faculty</th>
                    <th>Room</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for item in items %}
                <tr>
                    <td><strong>{{ item.day }}</strong></td>
                    <td>P{{ item.period }}</td>
                    <td><span class="badge badge-info">{{ item.section }}</span></td>
                    <td><strong>{{ item.subject }}</strong></td>
                    <td>{{ item.faculty }}</td>
                    <td>{{ item.room }}</td>
                    <td>
                        {% if item.conflicts %}
                        <span class="badge badge-danger" title="{{ item.conflicts|join('; ') }}">⚠️ {{ item.conflicts|length }} Conflict(s)</span>
                        {% else %}
                        <span class="badge badge-success">✅ Safe</span>
                        {% endif %}
                    </td>
                    <td>
                        <a href="/simulate?select={{ item.id }}" class="btn btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;">Simulate</a>
                        <a href="/timetable/delete/{{ item.id }}" class="btn btn-danger" onclick="return confirm('Remove class from timetable?');">Delete</a>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="8" style="text-align: center; color: var(--text-muted);">No classes scheduled yet. <a href="/add">Add one now</a>.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    """, items=timetable_items)
    
    return render_page("Timetable Schedule", page_body)

@app.route("/timetable/delete/<int:cid>")
def timetable_delete(cid):
    con = connect()
    con.execute("DELETE FROM timetable WHERE id=?", (cid,))
    con.commit()
    con.close()
    return redirect("/timetable")

# ---------- ROUTE: ADD CLASS ----------
@app.route("/add", methods=["GET", "POST"])
def add():
    con = connect()
    cur = con.cursor()
    fac = cur.execute("SELECT name FROM faculty").fetchall()
    rms = cur.execute("SELECT room FROM rooms").fetchall()
    
    err = None
    if request.method == "POST":
        d = request.form["day"]
        p = int(request.form["period"])
        s = request.form["section"].strip()
        sub = request.form["subject"].strip()
        f = request.form["faculty"]
        rm = request.form["room"]
        
        conflicts = detect_conflict(d, p, s, f, rm, sub)
        if conflicts:
            err = conflicts
        else:
            cur.execute("INSERT INTO timetable(day, period, section, subject, faculty, room) VALUES(?,?,?,?,?,?)",
                        (d, p, s, sub, f, rm))
            con.commit()
            con.close()
            return redirect("/timetable")
            
    con.close()
    
    page_body = render_template_string("""
    <div class="page-title">➕ Schedule New Class</div>
    <p class="page-subtitle">Schedule a class slot with instant real-time conflict checking.</p>
    
    {% if err %}
    <div class="alert alert-danger">
        <strong>⚠️ Cannot add class due to conflicts:</strong>
        <ul style="margin-left: 1.25rem; margin-top: 0.5rem;">
            {% for item in err %}
            <li>{{ item }}</li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}
    
    <div class="card" style="max-width: 600px; margin: 0 auto;">
        <form method="post">
            <div class="grid" style="grid-template-columns: 1fr 1fr;">
                <div class="form-group">
                    <label>Day of Week</label>
                    <select name="day" class="form-control">
                        <option>Mon</option>
                        <option>Tue</option>
                        <option>Wed</option>
                        <option>Thu</option>
                        <option>Fri</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Period (1 - 6)</label>
                    <input type="number" name="period" min="1" max="6" value="1" class="form-control" required>
                </div>
            </div>
            
            <div class="grid" style="grid-template-columns: 1fr 1fr;">
                <div class="form-group">
                    <label>Section</label>
                    <input type="text" name="section" placeholder="e.g. CSE-A" class="form-control" required>
                </div>
                <div class="form-group">
                    <label>Subject</label>
                    <input type="text" name="subject" placeholder="e.g. DBMS or DBMS Lab" class="form-control" required>
                </div>
            </div>
            
            <div class="grid" style="grid-template-columns: 1fr 1fr;">
                <div class="form-group">
                    <label>Faculty Member</label>
                    <select name="faculty" class="form-control">
                        {% for f in fac %}
                        <option>{{ f[0] }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label>Assigned Room</label>
                    <select name="room" class="form-control">
                        {% for r in rms %}
                        <option>{{ r[0] }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            
            <button type="submit" class="btn" style="width: 100%; margin-top: 1rem;">Save Class Schedule</button>
        </form>
    </div>
    """, fac=fac, rms=rms, err=err)
    
    return render_page("Add Class", page_body)

# ---------- ROUTE: SIMULATE CHANGE & GEMINI AI REASONING ----------
@app.route("/simulate", methods=["GET", "POST"])
def simulate():
    con = connect()
    cur = con.cursor()
    classes = cur.execute("SELECT id, day, period, section, subject, faculty, room FROM timetable").fetchall()
    rooms = cur.execute("SELECT room FROM rooms").fetchall()
    
    selected_cid = request.args.get("select", type=int)
    res = None
    gemini_analysis = None
    
    if request.method == "POST":
        cid = int(request.form["class_id"])
        d = request.form["day"]
        p = int(request.form["period"])
        rm = request.form["room"]
        
        old = cur.execute("SELECT day, period, section, subject, faculty, room FROM timetable WHERE id=?", (cid,)).fetchone()
        
        conflicts = detect_conflict(d, p, old[2], old[4], rm, old[3], exclude_id=cid)
        best = recommend_slot(old[2], old[3], old[4], rm, exclude_id=cid)
        
        res = {
            "id": cid,
            "old": old,
            "day": d,
            "period": p,
            "room": rm,
            "conflicts": conflicts,
            "best": best
        }
        
        prompt = f"""
        Act as an expert academic schedule coordinator.
        A schedule simulation change was requested:
        - Class: Section {old[2]}, Subject: '{old[3]}', Faculty: {old[4]}
        - Original Slot: {old[0]} Period {old[1]} in Room {old[5]}
        - Proposed New Slot: {d} Period {p} in Room {rm}
        - Detected Conflicts: {conflicts if conflicts else "None (Safe to reschedule)"}
        - Best Recommended Alternative Slot: {best['day']} Period {best['period']} (Conflict score: {best['score']})
        
        Provide a concise analysis of this proposed change and explain why the proposed slot is good or bad, and give recommendations.
        """
        gemini_analysis = ask_gemini(prompt, system_instruction="Provide helpful, professional, and clear advice on timetable conflict resolution.")
        
    con.close()
    
    page_body = render_template_string("""
    <div class="page-title">🔄 Timetable Change Simulator</div>
    <p class="page-subtitle">Test schedule changes virtually before updating the live database.</p>
    
    <div class="grid" style="grid-template-columns: 400px 1fr;">
        <div class="card">
            <div class="card-title">Simulation Settings</div>
            <form method="post">
                <div class="form-group">
                    <label>Select Scheduled Class</label>
                    <select name="class_id" class="form-control">
                        {% for c in classes %}
                        <option value="{{ c[0] }}" {% if selected_cid == c[0] %}selected{% endif %}>
                            {{ c[3] }} - {{ c[4] }} ({{ c[1] }} P{{ c[2] }})
                        </option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Target Day</label>
                    <select name="day" class="form-control">
                        <option>Mon</option>
                        <option>Tue</option>
                        <option>Wed</option>
                        <option>Thu</option>
                        <option>Fri</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Target Period</label>
                    <input type="number" name="period" min="1" max="6" value="1" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label>Target Room</label>
                    <select name="room" class="form-control">
                        {% for r in rooms %}
                        <option>{{ r[0] }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <button type="submit" class="btn" style="width: 100%;">Run Simulation</button>
            </form>
        </div>
        
        <div>
            {% if res %}
            <div class="card">
                <div class="card-title">
                    <span>Simulation Results</span>
                    {% if res.conflicts %}
                    <span class="badge badge-danger">⚠️ CONFLICT DETECTED</span>
                    {% else %}
                    <span class="badge badge-success">✅ SAFE TO MOVE</span>
                    {% endif %}
                </div>
                
                <p style="margin-bottom: 1rem; color: var(--text-muted);">
                    Moving <strong>{{ res.old[2] }} ({{ res.old[3] }})</strong> taught by <strong>{{ res.old[4] }}</strong> from <em>{{ res.old[0] }} P{{ res.old[1] }} ({{ res.old[5] }})</em> ➔ <strong>{{ res.day }} P{{ res.period }} ({{ res.room }})</strong>
                </p>
                
                {% if res.conflicts %}
                <div class="alert alert-danger">
                    <strong>Conflicts Found ({{ res.conflicts|length }}):</strong>
                    <ul style="margin-left: 1.25rem; margin-top: 0.5rem;">
                        {% for c in res.conflicts %}
                        <li>{{ c }}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% else %}
                <div class="alert alert-success">
                    <strong>No conflicts detected!</strong> This change can be applied cleanly.
                    <br><br>
                    <a href="/apply/{{ res.id }}/{{ res.day }}/{{ res.period }}/{{ res.room }}" class="btn" style="background: var(--success);">Apply Schedule Update Now</a>
                </div>
                {% endif %}
                
                <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--border);">
                    <strong>💡 System Recommended Optimal Slot:</strong>
                    <span class="badge badge-info">{{ res.best.day }} Period {{ res.best.period }}</span>
                    (Conflict score: {{ res.best.score }})
                </div>
            </div>
            
            <div class="gemini-box">
                <h4>✨ Gemini AI Insights & Reasoning</h4>
                <div class="markdown-content">{{ gemini_analysis }}</div>
            </div>
            {% else %}
            <div class="card" style="text-align: center; padding: 3rem; color: var(--text-muted);">
                <p>Select a class and target slot on the left to run simulation analysis.</p>
            </div>
            {% endif %}
        </div>
    </div>
    """, classes=classes, rooms=rooms, selected_cid=selected_cid, res=res, gemini_analysis=gemini_analysis)
    
    return render_page("Simulate Change", page_body)

# ---------- ROUTE: APPLY SIMULATED CHANGE ----------
@app.route("/apply/<int:cid>/<day>/<int:period>/<room>")
def apply_change(cid, day, period, room):
    con = connect()
    cur = con.cursor()
    row = cur.execute("SELECT section, subject, faculty FROM timetable WHERE id=?", (cid,)).fetchone()
    if row:
        s, sub, f = row
        conflicts = detect_conflict(day, period, s, f, room, sub, exclude_id=cid)
        if not conflicts:
            cur.execute("UPDATE timetable SET day=?, period=?, room=? WHERE id=?", (day, period, room, cid))
            con.commit()
    con.close()
    return redirect("/timetable")

# ---------- ROUTE: GEMINI AI ASSISTANT / COPILOT ----------
@app.route("/ai-advisor", methods=["GET", "POST"])
def ai_advisor():
    con = connect()
    cur = con.cursor()
    faculty_list = cur.execute("SELECT * FROM faculty").fetchall()
    rooms_list = cur.execute("SELECT * FROM rooms").fetchall()
    timetable_list = cur.execute("SELECT * FROM timetable").fetchall()
    con.close()
    
    query = ""
    ai_response = None
    
    if request.method == "POST":
        custom_key = request.form.get("gemini_key", "").strip()
        if custom_key:
            os.environ["GEMINI_API_KEY"] = custom_key
            
        query = request.form.get("query", "").strip()
        if query:
            context = f"""
            You are the AI Academic Scheduling Assistant for a university timetable system.
            Current System Data:
            - Faculty Members ({len(faculty_list)}): {faculty_list}
            - Rooms & Labs ({len(rooms_list)}): {rooms_list}
            - Current Timetable ({len(timetable_list)}): {timetable_list}
            - Section Strengths: {SECTION_STRENGTH}
            
            User Question / Request:
            "{query}"
            
            Provide a helpful, structured, clear response assisting the academic coordinator.
            """
            ai_response = ask_gemini(context)
            
    api_key_status = bool(os.environ.get("GEMINI_API_KEY"))
    
    page_body = render_template_string("""
    <div class="page-title">✨ Gemini AI Timetable Assistant</div>
    <p class="page-subtitle">Ask questions, request schedule optimizations, or ask Gemini AI to resolve complex conflicts.</p>
    
    <div class="card">
        <div class="card-title" style="display: flex; justify-content: space-between; align-items: center;">
            <span>Ask Gemini Assistant</span>
            <span class="badge badge-success">⚡ Gemini 3.6 Connected</span>
        </div>
        <form method="post">
            <div class="form-group">
                <label>How can Gemini help with your timetable today?</label>
                <textarea name="query" rows="4" class="form-control" placeholder="e.g. How can we optimize the schedule for CSD-C? Or analyze faculty workload..." required>{{ query }}</textarea>
            </div>
            <button type="submit" class="btn" style="background: linear-gradient(135deg, var(--accent), var(--primary));">✨ Send Query to Gemini</button>
        </form>
    </div>
    
    {% if ai_response %}
    <div class="gemini-box" style="margin-top: 1.5rem;">
        <h4>🤖 Gemini AI Response</h4>
        <div class="markdown-content">{{ ai_response }}</div>
    </div>
    {% endif %}
    """, query=query, ai_response=ai_response)
    
    return render_page("Gemini AI Assistant", page_body)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

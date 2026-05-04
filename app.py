from flask import Flask, render_template, request, redirect, url_for,send_file
import sqlite3
from datetime import date,timedelta
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle
from reportlab.lib import colors 
from datetime import datetime
import os
print("Flask DB Path:", os.path.abspath("exam.db"))

app = Flask(__name__)

print("The static  File")

import sqlite3

conn = sqlite3.connect("exam.db")
cur = conn.cursor()

# 🔥 FIX schedule table structure
cur.execute("DROP TABLE IF EXISTS schedule")

cur.execute("""
CREATE TABLE schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_date TEXT NOT NULL,
    course_code TEXT NOT NULL,
    course_name TEXT NOT NULL,
    slot TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("✅ Schedule table fixed successfully")

# ---------- DATABASE CONNECTION ----------
def get_db_connection():
    conn = sqlite3.connect(r"C:\Users\admin\Desktop\dataset of pythons\exam_system\exam.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------- DATABASE INIT ----------
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    conn = sqlite3.connect("exam.db")
    cur = conn.cursor()
    
   


    # Faculty table
    
    # Departments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT UNIQUE
    )
""")

# Faculty table (UPDATED)
    cursor.execute("""
      CREATE TABLE IF NOT EXISTS faculty (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT,
          department_id INTEGER,
          FOREIGN KEY(department_id) REFERENCES departments(id)
    )
""")
     
    # Courses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT,
            course_code TEXT,
            paper_setter_id INTEGER
        )
    """)

    # Faculty-Courses assignment table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty_courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_id INTEGER,
            course_id INTEGER
        )
    """)

    # Packets table
    cursor.execute ("""
       CREATE TABLE IF NOT EXISTS packets (
           id INTEGER PRIMAR KEY AUTOINCREMENTS,
           packet_name TEXT,
           course_id INTEGER,
           script_count INTEGER,
           eval_date TEXT,
           status TEXT DEFAULT 'Pending',
           result TEXT DEFAULT ''
   )
""")
    # Schedule table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_date TEXT NOT NULL,
           course_code TEXT NOT NULL,
           course_name TEXT NOT NULL,
           slot TEXT NOT NULL
)
""")
    # Allocation table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS allocation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            slot INTEGER,
            faculty_id INTEGER,
            packet_id INTEGER,
            activity TEXT
        )
    """)

    conn.commit()
    conn.close()

# Initialize DB
init_db()


# ---------- ROUTES ----------
@app.route("/")
def login():
    return render_template("login.html")
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ---------- FACULTY ----------
@app.route('/faculty')
def faculty():
    conn = get_db_connection()

    # for dropdown
    all_faculty = conn.execute("SELECT * FROM faculty").fetchall()

    # only mapped for table
    faculty = conn.execute("""
        SELECT f.id, f.name, d.name AS department_name
        FROM faculty f
        INNER JOIN departments d
        ON f.department_id = d.id
    """).fetchall()

    departments = conn.execute("SELECT * FROM departments").fetchall()

    conn.close()

    return render_template("faculty.html",
                           faculty=faculty,
                           all_faculty=all_faculty,
                           departments=departments)


# ➕ ADD FACULTY
@app.route('/add_faculty', methods=['POST'])
def add_faculty():
    name = request.form.get("faculty_name")

    conn = get_db_connection()
    conn.execute("INSERT INTO faculty (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

    return redirect('/faculty')

# ➕ ADD DEPARTMENT
@app.route('/add_department', methods=['POST'])
def add_department():
    name = request.form.get("department_name")

    conn = get_db_connection()

    existing = conn.execute(
        "SELECT * FROM departments WHERE name=?",
        (name,)
    ).fetchone()

    if not existing:
        conn.execute(
            "INSERT INTO departments (name) VALUES (?)",
            (name,)
        )
        conn.commit()

    conn.close()

    return redirect('/faculty')

# 🔗 MAP FACULTY TO DEPARTMENT
@app.route('/map_faculty', methods=['POST'])
def map_faculty():
    faculty_id = request.form['faculty_id']
    department_id = request.form['department_id']

    conn = get_db_connection()
    conn.execute(
        "UPDATE faculty SET department_id=? WHERE id=?",
        (department_id, faculty_id)
    )
    conn.commit()
    conn.close()

    return redirect('/faculty')

@app.route("/edit_faculty/<int:id>", methods=["GET", "POST"])
def edit_faculty(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        dept = request.form["department"]

        cursor.execute("""
            UPDATE faculty
            SET name=?
            WHERE id=?
        """, (name,  id))

        conn.commit()
        conn.close()
        return redirect("/faculty")

    cursor.execute("SELECT * FROM faculty WHERE id=?", (id,))
    faculty = cursor.fetchone()
    conn.close()

    return render_template("edit_faculty.html", faculty=faculty)
@app.route("/delete_faculty/<int:id>")
def delete_faculty(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM faculty WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/faculty")


# ---------- COURSES ----------
@app.route("/courses", methods=["GET", "POST"])
def courses():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        course_id = request.form["course_id"]
        paper_setter_id = request.form["paper_setter_id"]

        cursor.execute("""
            UPDATE courses
            SET paper_setter_id=?
            WHERE id=?
        """, (paper_setter_id, course_id))

        conn.commit()

    # fetch courses
    cursor.execute("""
       SELECT c.*, f.name AS paper_setter_name
       FROM courses c
       LEFT JOIN faculty f ON c.paper_setter_id = f.id
""")
    courses_list = cursor.fetchall()


    # dropdowns
    cursor.execute("SELECT * FROM courses")
    all_courses = cursor.fetchall()  

    cursor.execute("SELECT * FROM faculty")
    faculty_list = cursor.fetchall()

    conn.close()

    return render_template("courses.html",
                           courses=courses_list,
                           all_courses=all_courses,
                           faculty=faculty_list)
    
@app.route("/add_course", methods=["POST"])
def add_course():
    name = request.form["course_name"]
    code = request.form["course_code"]

    conn = get_db_connection()
    

    conn.execute(
        "INSERT INTO courses (course_name, course_code) VALUES (?, ?)",
        (name, code)
)
    conn.commit()
    conn.close()

    return redirect("/courses")

@app.route("/get_paper_setter/<int:course_id>")
def get_paper_setter(course_id):
    conn = get_db_connection()

    course = conn.execute("""
        SELECT f.name
        FROM courses c
        LEFT JOIN faculty f ON c.paper_setter_id = f.id
        WHERE c.id=?
    """, (course_id,)).fetchone()

    conn.close()

    if course and course["name"]:
        return {"paper_setter": course["name"]}
    else:
        return {"paper_setter": "Not Assigned"}
@app.route("/auto_assign/<int:course_id>")
def auto_assign(course_id):
    conn = get_db_connection()
    cur = conn.cursor()

    # ✅ ONLY check mapped faculty
    cur.execute("""
        SELECT f.id, f.name
        FROM faculty f
        JOIN faculty_courses fc ON f.id = fc.faculty_id
        WHERE fc.course_id = ?
        LIMIT 1
    """, (course_id,))

    faculty = cur.fetchone()

    # ❌ If not mapped → DO NOTHING
    if not faculty:
        conn.close()
        return {"name": None}

    # ✅ Save correct paper setter
    cur.execute("""
        UPDATE courses
        SET paper_setter_id = ?
        WHERE id = ?
    """, (faculty["id"], course_id))

    conn.commit()
    conn.close()

    return {"name": faculty["name"]}

@app.route("/edit_course/<int:id>", methods=["GET", "POST"])
def edit_course(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["course_name"]
        code = request.form["course_code"]
        paper_setter_id = request.form["paper_setter_id"]

        cursor.execute("""
            UPDATE courses
            SET course_name=?, course_code=?, paper_setter_id=?
            WHERE id=?
        """, (name, code, paper_setter_id, id))

        conn.commit()
        conn.close()
        return redirect("/courses")

    # GET request
    cursor.execute("SELECT * FROM courses WHERE id=?", (id,))
    course = cursor.fetchone()

    cursor.execute("SELECT * FROM faculty")
    faculty = cursor.fetchall()

    conn.close()

    return render_template("edit_course.html",
                           course=course,
                           faculty=faculty)
@app.route("/delete_course/<int:id>")
def delete_course(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM courses WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/courses") 

# ---------- ASSIGN COURSE ----------
@app.route("/assign_course", methods=["GET", "POST"])
def assign_course():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        faculty_id = request.form["faculty_id"]
        course_id = request.form["course_id"]
        cursor.execute(
            "INSERT INTO faculty_courses (faculty_id, course_id) VALUES (?, ?)",
            (faculty_id, course_id)
        )
        conn.commit()

    cursor.execute("SELECT * FROM faculty")
    faculty_list = cursor.fetchall()
    cursor.execute("SELECT * FROM courses")
    courses_list = cursor.fetchall()

    cursor.execute("""
        SELECT fc.id, f.name AS faculty_name, c.course_name
        FROM faculty_courses fc
        JOIN faculty f ON fc.faculty_id = f.id
        JOIN courses c ON fc.course_id = c.id
    """)
    assignments = cursor.fetchall()
    conn.close()

    return render_template(
        "assign_course.html",
        faculty=faculty_list,
        courses=courses_list,
        assignments=assignments
    )
@app.route("/delete_assignment/<int:id>")
def delete_assignment(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM faculty_courses WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/assign_course")
@app.route("/edit_assignment/<int:id>", methods=["GET", "POST"])
def edit_assignment(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        faculty_id = request.form["faculty_id"]
        course_id = request.form["course_id"]

        cursor.execute("""
            UPDATE faculty_courses
            SET faculty_id=?, course_id=?
            WHERE id=?
        """, (faculty_id, course_id, id))

        conn.commit()
        conn.close()
        return redirect("/assign_course")

    # GET request
    cursor.execute("SELECT * FROM faculty_courses WHERE id=?", (id,))
    assignment = cursor.fetchone()

    cursor.execute("SELECT * FROM faculty")
    faculty_list = cursor.fetchall()

    cursor.execute("SELECT * FROM courses")
    courses_list = cursor.fetchall()

    conn.close()

    return render_template(
        "edit_assignment.html",
        assignment=assignment,
        faculty=faculty_list,
        courses=courses_list
    )

# ---------- PACKETS ----------
def generate_packet_name():
    conn = sqlite3.connect("exam.db")
    cur = conn.cursor()

    last = cur.execute("""
        SELECT packet_name 
        FROM packets 
        ORDER BY id DESC 
        LIMIT 1
    """).fetchone()

    conn.close()

    if last and last[0]:
        num = int(last[0][3:]) + 1   # removes "PKT"
    else:
        num = 1

    return f"PKT{num:03d}"
@app.route("/packets")
def packets():
    conn = sqlite3.connect("exam.db")
    conn.row_factory = sqlite3.Row 
    cur = conn.cursor()

    packets = cur.execute("""
       SELECT 
       p.id,
       p.packet_name,
      c.course_code,
      p.script_count,
      p.eval_date,
      p.status,
      p.result
    FROM packets p
    JOIN courses c ON p.course_id = c.id
   """).fetchall()

    courses = cur.execute("SELECT id, course_code FROM courses").fetchall()

    conn.close()

    return render_template("packets.html", packets=packets, courses=courses)

@app.route("/add_packet", methods=["POST"])
def add_packet():
    course_id = request.form["course_id"]
    total_scripts = int(request.form["script_count"])
    eval_date = request.form.get("eval_date")  

    MAX_LIMIT = 30

    conn = sqlite3.connect("exam.db")
    cur = conn.cursor()

    while total_scripts > 0:
        scripts = min(MAX_LIMIT, total_scripts)

        packet_name = generate_packet_name()

        # ❌ NO evaluator here
        cur.execute("""
            INSERT INTO packets (packet_name, course_id, script_count,eval_date, status)
            VALUES (?, ?, ?,?,?)
        """, (packet_name, course_id, scripts,eval_date,"Pending"))

        total_scripts -= scripts

    conn.commit()
    conn.close()

    return redirect("/packets")
@app.route("/update_eval_date/<int:id>", methods=["POST"])
def update_eval_date(id):
    eval_date = request.form["eval_date"]

    conn = sqlite3.connect("exam.db")
    cur = conn.cursor()

    cur.execute("""
        UPDATE packets
        SET eval_date=?, status='Evaluated'
        WHERE id=?
    """, (eval_date, id))

    conn.commit()
    conn.close()

    return redirect("/packets")
@app.route("/edit_packet/<int:id>", methods=["GET", "POST"])
def edit_packet(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
            UPDATE packets
            SET packet_name=?, script_count=?
            WHERE id=?
        """, (
            request.form["packet_name"],
            request.form["script_count"],
            id
        ))
        conn.commit()
        conn.close()
        return redirect("/packets")

    cursor.execute("SELECT * FROM packets WHERE id=?", (id,))
    packet = cursor.fetchone()
    conn.close()

    return render_template("edit_packet.html", packet=packet)
@app.route("/delete_packet/<int:id>")
def delete_packet(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM packets WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/packets")

# ---------- SCHEDULE ----------
@app.route("/schedule")
def schedule():
    conn = sqlite3.connect("exam.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 🔥 FETCH COURSE DATA FROM COURSE TABLE
    cur.execute("SELECT course_code, course_name FROM courses")
    courses = cur.fetchall()

    # existing scheduled exams
    cur.execute("SELECT * FROM schedule")
    schedules = cur.fetchall()

    conn.close()

    return render_template("schedule.html",
                           courses=courses,
                           schedules=schedules)
    cursor.execute("""
        SELECT 
            s.id,
            f.name,
            c.course_name,
            s.exam_date
        FROM schedule s
        JOIN faculty f ON s.faculty_id = f.id
        JOIN courses c ON s.course_id = c.id
    """)

    schedules = cursor.fetchall()

    cursor.execute("SELECT * FROM faculty")
    faculty = cursor.fetchall()

    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    conn.close()

    return render_template("schedule.html",
                           schedules=schedules,
                           faculty=faculty,
                           courses=courses)
@app.route('/add_schedule', methods=['POST'])
def add_schedule():
    exam_date = request.form['exam_date']
    course_code = request.form['course_code']
    course_name = request.form['course_name']
    slot = request.form['slot']

    conn = sqlite3.connect('exam.db')
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO schedule (exam_date, course_code, course_name, slot)
        VALUES (?, ?, ?, ?)
    """, (exam_date, course_code, course_name, slot))

    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))
    
@app.route("/edit_schedule/<int:id>", methods=["GET", "POST"])
def edit_schedule(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
            UPDATE schedule
            SET faculty_id=?, course_id=?, exam_date=?
            WHERE id=?
        """, (
            request.form["faculty_id"],
            request.form["course_id"],
            request.form["exam_date"],
            id
        ))
        conn.commit()
        conn.close()
        return redirect("/schedule")

    schedule = cursor.execute("SELECT * FROM schedule WHERE id=?", (id,)).fetchone()
    faculty = cursor.execute("SELECT * FROM faculty").fetchall()
    courses = cursor.execute("SELECT * FROM courses").fetchall()

    conn.close()

    return render_template(
        "edit_schedule.html",
        schedule=schedule,
        faculty=faculty,
        courses=courses
    )
@app.route("/delete_schedule/<int:id>")
def delete_schedule(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM schedule WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/schedule")

# ---------- AUTO ALLOCATION ----------



@app.route("/auto_allocate")
def auto_allocate():
    conn = get_db_connection()
    cursor = conn.cursor()

    start_date = date.today()
    num_days = 3
    result = []
    used_packets = set()

    faculty_list = cursor.execute("SELECT * FROM faculty").fetchall()
    current_date = start_date

    for _ in range(num_days):

        for slot in [1, 2]:

            packets = cursor.execute("SELECT * FROM packets").fetchall()

            for faculty in faculty_list:
                fid = faculty["id"]

                # avoid duplicate assignment
                cursor.execute("""
                    SELECT COUNT(*) FROM allocation
                    WHERE faculty_id=? AND date=? AND slot=?
                """, (fid, str(current_date), slot))

                if cursor.fetchone()[0] > 0:
                    continue

                eval_load = cursor.execute("""
                    SELECT SUM(p.script_count)
                    FROM allocation a
                    JOIN packets p ON a.packet_id=p.id
                    WHERE a.faculty_id=? AND a.date=? AND a.activity='Evaluation'
                """, (fid, str(current_date))).fetchone()[0] or 0

                scr_load = cursor.execute("""
                    SELECT SUM(p.script_count)
                    FROM allocation a
                    JOIN packets p ON a.packet_id=p.id
                    WHERE a.faculty_id=? AND a.date=? AND a.activity='Scrutiny'
                """, (fid, str(current_date))).fetchone()[0] or 0

                assigned = False

                # ---------------- EVALUATION ----------------
                for p in packets:

                    if p["id"] in used_packets:
                        continue

                    if p["status"] != "Pending":
                        continue
                    course_id = p["course_id"]
   
                    if course_id is None:
                       continue

                    mapped = cursor.execute("""
                           SELECT f.id, f.name
                           FROM faculty f
                          JOIN faculty_courses fc ON f.id = fc.faculty_id
                           WHERE fc.course_id=?
                           LIMIT 1
                           """, (course_id,)).fetchone()

                      
                    if not mapped:
                        continue

                    if eval_load + p["script_count"] > 30:
                        continue

                    cursor.execute("""
                        INSERT INTO allocation (date, slot, faculty_id, packet_id, activity)
                        VALUES (?, ?, ?, ?, ?)
                    """, (str(current_date), slot, mapped["id"], p["id"], "Evaluation"))

                    cursor.execute("""
                         UPDATE packets
                         SET status='Evaluated', eval_date=?
                         WHERE id=?
                         """, (str(current_date), p["id"]))

                    conn.commit()

                    result.append({
                        "date": str(current_date),
                        "slot": "Morning" if slot == 1 else "Afternoon",
                        "faculty": mapped["name"],
                        "packet": p["packet_name"],
                        "activity": "Evaluation"
                    })

                    used_packets.add(p["id"])
                    assigned = True
                    break

                if assigned:
                    continue

                # ---------------- SCRUTINY ----------------
                for p in packets:

                    if p["status"] != "Evaluated":
                        continue

                    if scr_load + p["script_count"] > 200:
                        continue

                    cursor.execute("""
                        INSERT INTO allocation (date, slot, faculty_id, packet_id, activity)
                        VALUES (?, ?, ?, ?, ?)
                    """, (str(current_date), slot, fid, p["id"], "Scrutiny"))

                    cursor.execute("""
                        UPDATE packets
                        SET status='Scrutinized'
                        WHERE id=?
                    """, (p["id"],))

                    conn.commit()

                    result.append({
                        "date": str(current_date),
                        "slot": "Morning" if slot == 1 else "Afternoon",
                        "faculty": faculty["name"],
                        "packet": p["packet_name"],
                        "activity": "Scrutiny"
                    })

                    assigned = True
                    break

        current_date += timedelta(days=1)

    conn.close()

    return render_template("allocation_result.html", data=result)
# ================= REPORT =================
@app.route("/report")
def report():
    conn = get_db_connection()

    data = conn.execute("""
        SELECT a.date, a.slot, f.name, p.packet_name, a.activity
        FROM allocation a
        JOIN faculty f ON a.faculty_id = f.id
        JOIN packets p ON a.packet_id = p.id
        ORDER BY a.date, a.slot
    """).fetchall()

    conn.close()

    return render_template("report.html", data=data)

# ================= PDF REPORT =================
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
@app.route("/download_pdf")
def download_pdf():
    conn = get_db_connection()

    rows = conn.execute("""
        SELECT a.date, a.slot, f.name, p.packet_name, a.activity
        FROM allocation a
        JOIN faculty f ON a.faculty_id = f.id
        JOIN packets p ON a.packet_id = p.id
        ORDER BY a.date, a.slot
    """).fetchall()

    conn.close()

    if not rows:
        return "❌ No data available for report!"

    file = os.path.join(os.getcwd(), "report.pdf")
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()
    title = Paragraph("Exam Allocation Report", styles["Title"])


    data = [["Date", "Slot", "Faculty", "Packet", "Activity"]]

    for r in rows:
        data.append([
            r["date"],
            "Morning" if r["slot"] == 1 else "Afternoon",
            r["name"],
            r["packet_name"],
            r["activity"]
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))

    doc.build([table])

    return send_file(file, as_attachment=True, download_name="allocation_report.pdf")

# ---------- FACULTY DETAIL ----------
@app.route("/faculty/<int:id>")
def faculty_detail(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faculty WHERE id=?", (id,))
    faculty = cursor.fetchone()
    conn.close()
    if faculty:
        return  render_template("faculty_detail.html",faculty=faculty)
    else:
        return "<h3>Faculty not found</h3>"

# ---------- PACKET DETAIL ----------
@app.route("/packet/<int:id>")
def packet_detail(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, c.course_name
        FROM packets p
        JOIN courses c ON p.course_id = c.id
        WHERE p.id=?
    """, (id,))
    packet = cursor.fetchone()
    conn.close()
    if packet:
        return  render_template("packet_detail.html",packet=packet)
    else:
        return "<h3>packet not found</h3>"


    

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
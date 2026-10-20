from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from pathlib import Path
from datetime import datetime
from functools import wraps

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "hostel.db"
app = Flask(__name__)
app.secret_key = "hostel-management-local-development-key"

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL CHECK(category IN ('Boys','Girls','Other')),
            capacity INTEGER NOT NULL CHECK(capacity > 0),
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hostel_id TEXT NOT NULL UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            father_name TEXT NOT NULL,
            mother_name TEXT NOT NULL,
            dob TEXT NOT NULL,
            contact TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            vehicle_number TEXT DEFAULT '',
            college TEXT NOT NULL,
            gender TEXT NOT NULL CHECK(gender IN ('Male','Female','Other')),
            room_id INTEGER,
            bed_number TEXT,
            joined_at TEXT NOT NULL,
            FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE SET NULL,
            UNIQUE(room_id, bed_number)
        );
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_name TEXT NOT NULL,
            student_id INTEGER,
            purpose TEXT NOT NULL,
            contact TEXT NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT DEFAULT '',
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE SET NULL
        );
        CREATE TABLE IF NOT EXISTS movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            direction TEXT NOT NULL CHECK(direction IN ('IN','OUT')),
            note TEXT DEFAULT '',
            recorded_at TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS leave_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            departure_date TEXT NOT NULL,
            return_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending','Approved','Rejected')),
            created_at TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        """)
        count = db.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
        if count == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            db.executemany("INSERT INTO rooms(room_number,category,capacity,created_at) VALUES(?,?,?,?)", [
                ("B101","Boys",3,now),("B102","Boys",3,now),("G101","Girls",3,now),
                ("G102","Girls",3,now),("O101","Other",2,now)
            ])
        count = db.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        if count == 0:
            room = db.execute("SELECT id FROM rooms WHERE room_number='B101'").fetchone()["id"]
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            db.execute("""INSERT INTO students(hostel_id,first_name,last_name,father_name,mother_name,dob,contact,email,address,vehicle_number,college,gender,room_id,bed_number,joined_at)
                          VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                       ("STU1001","Rahul","Sharma","Rajesh Sharma","Sunita Sharma","2005-05-14","9876543210","rahul@example.com","Mohali, Punjab","PB65AB1234","CGC Landran","Male",room,"1",now))

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/", methods=["GET"])
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    with connect() as db:
        stats = {
            "students": db.execute("SELECT COUNT(*) FROM students").fetchone()[0],
            "rooms": db.execute("SELECT COUNT(*) FROM rooms").fetchone()[0],
            "occupied": db.execute("SELECT COUNT(*) FROM students WHERE room_id IS NOT NULL").fetchone()[0],
            "pending": db.execute("SELECT COUNT(*) FROM leave_applications WHERE status='Pending'").fetchone()[0],
            "visitors": db.execute("SELECT COUNT(*) FROM visitors WHERE check_out=''").fetchone()[0]
        }
        recent = db.execute("""SELECT m.direction,m.recorded_at,s.hostel_id,s.first_name,s.last_name
                               FROM movements m JOIN students s ON s.id=m.student_id
                               ORDER BY m.id DESC LIMIT 6""").fetchall()
    return render_template("dashboard.html", stats=stats, recent=recent)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form.get("username","").strip() == "user123" and request.form.get("password","") == "000":
            session["logged_in"] = True
            flash("Welcome to Hostel Management System.", "success")
            return redirect(url_for("index"))
        flash("Incorrect username or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/students")
@login_required
def students():
    q = request.args.get("q","").strip()
    with connect() as db:
        rows = db.execute("""SELECT s.*,r.room_number FROM students s LEFT JOIN rooms r ON r.id=s.room_id
                             WHERE s.hostel_id LIKE ? OR s.first_name LIKE ? OR s.last_name LIKE ? OR s.contact LIKE ?
                             ORDER BY s.id DESC""", tuple([f"%{q}%"]*4)).fetchall()
        rooms = db.execute("SELECT * FROM rooms ORDER BY category,room_number").fetchall()
    return render_template("students.html", students=rows, rooms=rooms, q=q)

@app.route("/students/add", methods=["GET","POST"])
@login_required
def add_student():
    with connect() as db:
        rooms = db.execute("SELECT r.*, (SELECT COUNT(*) FROM students s WHERE s.room_id=r.id) AS used FROM rooms r ORDER BY category,room_number").fetchall()
    if request.method == "POST":
        f = request.form
        required = ["hostel_id","first_name","last_name","father_name","mother_name","dob","contact","email","address","college","gender"]
        if any(not f.get(k,"").strip() for k in required):
            flash("Please complete all required fields.", "danger")
            return render_template("student_form.html", rooms=rooms, form=f)
        room_id = f.get("room_id") or None
        bed_number = f.get("bed_number") or None
        try:
            with connect() as db:
                if room_id:
                    room = db.execute("SELECT * FROM rooms WHERE id=?", (room_id,)).fetchone()
                    used = db.execute("SELECT COUNT(*) FROM students WHERE room_id=?", (room_id,)).fetchone()[0]
                    if not room or used >= room["capacity"]:
                        flash("Selected room is full or invalid.", "danger")
                        return render_template("student_form.html", rooms=rooms, form=f)
                    if room["category"] != {"Male":"Boys","Female":"Girls","Other":"Other"}[f["gender"]]:
                        flash("Selected room category does not match the student's gender.", "danger")
                        return render_template("student_form.html", rooms=rooms, form=f)
                db.execute("""INSERT INTO students(hostel_id,first_name,last_name,father_name,mother_name,dob,contact,email,address,vehicle_number,college,gender,room_id,bed_number,joined_at)
                              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                           (f["hostel_id"].strip(),f["first_name"].strip(),f["last_name"].strip(),f["father_name"].strip(),f["mother_name"].strip(),f["dob"],f["contact"].strip(),f["email"].strip(),f["address"].strip(),f.get("vehicle_number","").strip(),f["college"].strip(),f["gender"],room_id,bed_number,datetime.now().strftime("%Y-%m-%d %H:%M")))
            flash("Student added successfully.", "success")
            return redirect(url_for("students"))
        except sqlite3.IntegrityError:
            flash("Hostel ID must be unique and a bed cannot be assigned twice.", "danger")
    return render_template("student_form.html", rooms=rooms, form={})

@app.route("/students/<int:student_id>/delete", methods=["POST"])
@login_required
def delete_student(student_id):
    with connect() as db:
        db.execute("DELETE FROM students WHERE id=?", (student_id,))
    flash("Student record deleted.", "success")
    return redirect(url_for("students"))

@app.route("/rooms", methods=["GET","POST"])
@login_required
def rooms():
    if request.method == "POST":
        f=request.form
        try:
            with connect() as db:
                db.execute("INSERT INTO rooms(room_number,category,capacity,created_at) VALUES(?,?,?,?)",
                           (f["room_number"].strip().upper(),f["category"],int(f["capacity"]),datetime.now().strftime("%Y-%m-%d %H:%M")))
            flash("Room added successfully.", "success")
            return redirect(url_for("rooms"))
        except (sqlite3.IntegrityError, ValueError, KeyError):
            flash("Could not add room. Check the room number and capacity; room numbers must be unique.", "danger")
    with connect() as db:
        rows=db.execute("""SELECT r.*,COUNT(s.id) AS occupied FROM rooms r LEFT JOIN students s ON s.room_id=r.id
                           GROUP BY r.id ORDER BY r.category,r.room_number""").fetchall()
    return render_template("rooms.html", rooms=rows)

@app.route("/movements", methods=["GET","POST"])
@login_required
def movements():
    if request.method == "POST":
        with connect() as db:
            student=db.execute("SELECT id FROM students WHERE hostel_id=?", (request.form.get("hostel_id","").strip(),)).fetchone()
            if not student:
                flash("No student found for that Hostel ID.", "danger")
            else:
                db.execute("INSERT INTO movements(student_id,direction,note,recorded_at) VALUES(?,?,?,?)",
                           (student["id"],request.form["direction"],request.form.get("note","").strip(),datetime.now().strftime("%Y-%m-%d %H:%M")))
                flash("In/out movement recorded.", "success")
                return redirect(url_for("movements"))
    with connect() as db:
        rows=db.execute("""SELECT m.*,s.hostel_id,s.first_name,s.last_name FROM movements m
                           JOIN students s ON s.id=m.student_id ORDER BY m.id DESC LIMIT 100""").fetchall()
    return render_template("movements.html", movements=rows)

@app.route("/visitors", methods=["GET","POST"])
@login_required
def visitors():
    if request.method == "POST":
        f=request.form
        with connect() as db:
            student=db.execute("SELECT id FROM students WHERE hostel_id=?", (f.get("hostel_id","").strip(),)).fetchone()
            if not student:
                flash("Enter a valid student's Hostel ID.", "danger")
            else:
                db.execute("INSERT INTO visitors(visitor_name,student_id,purpose,contact,check_in) VALUES(?,?,?,?,?)",
                           (f["visitor_name"].strip(),student["id"],f["purpose"].strip(),f["contact"].strip(),datetime.now().strftime("%Y-%m-%d %H:%M")))
                flash("Visitor entry recorded.", "success")
                return redirect(url_for("visitors"))
    with connect() as db:
        rows=db.execute("""SELECT v.*,s.hostel_id,s.first_name,s.last_name FROM visitors v
                           LEFT JOIN students s ON s.id=v.student_id ORDER BY v.id DESC""").fetchall()
    return render_template("visitors.html", visitors=rows)

@app.route("/visitors/<int:visitor_id>/checkout", methods=["POST"])
@login_required
def visitor_checkout(visitor_id):
    with connect() as db:
        db.execute("UPDATE visitors SET check_out=? WHERE id=? AND check_out=''",
                   (datetime.now().strftime("%Y-%m-%d %H:%M"),visitor_id))
    flash("Visitor checkout updated.", "success")
    return redirect(url_for("visitors"))

@app.route("/leave", methods=["GET","POST"])
@login_required
def leave():
    if request.method == "POST":
        f=request.form
        with connect() as db:
            student=db.execute("SELECT id FROM students WHERE hostel_id=?", (f.get("hostel_id","").strip(),)).fetchone()
            if not student:
                flash("No student found for that Hostel ID.", "danger")
            elif not f.get("reason","").strip() or not f.get("departure_date") or not f.get("return_date"):
                flash("Complete all leave details.", "danger")
            elif f["return_date"] < f["departure_date"]:
                flash("Return date cannot be before departure date.", "danger")
            else:
                db.execute("INSERT INTO leave_applications(student_id,reason,departure_date,return_date,created_at) VALUES(?,?,?,?,?)",
                           (student["id"],f["reason"].strip(),f["departure_date"],f["return_date"],datetime.now().strftime("%Y-%m-%d %H:%M")))
                flash("Leave application submitted.", "success")
                return redirect(url_for("leave"))
    with connect() as db:
        rows=db.execute("""SELECT l.*,s.hostel_id,s.first_name,s.last_name FROM leave_applications l
                           JOIN students s ON s.id=l.student_id ORDER BY l.id DESC""").fetchall()
    return render_template("leave.html", applications=rows)

@app.route("/leave/<int:leave_id>/<status>", methods=["POST"])
@login_required
def leave_status(leave_id,status):
    if status not in ("Approved","Rejected"):
        flash("Invalid leave status.", "danger")
    else:
        with connect() as db:
            db.execute("UPDATE leave_applications SET status=? WHERE id=?", (status,leave_id))
        flash(f"Leave application {status.lower()}.", "success")
    return redirect(url_for("leave"))

@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"),404

init_db()
if __name__ == "__main__":
    app.run(debug=True)   

# Hostel Management System

A complete Flask + SQLite web version of the supplied Tkinter notebook. It retains the notebook's core hostel workflows: student records, room/bed allocation, in/out register, visitor register, leave applications, and login.

## Requirements
- Python 3.10 or newer
- pip
- A modern web browser

## Setup (macOS / Windows / Linux)
1. Extract this folder and open a terminal inside `hostel_management_system`.
2. Create a virtual environment:
   - macOS/Linux: `python3 -m venv .venv`
   - Windows: `py -m venv .venv`
3. Activate it:
   - macOS/Linux: `source .venv/bin/activate`
   - Windows: `.venv\\Scripts\\activate`
4. Install dependencies: `python -m pip install -r requirements.txt`
5. Start the server: `python app.py`
6. Open `http://127.0.0.1:5000` in your browser.

## Demo login
- Username: `user123`
- Password: `000`

## Sample data
On first run, the app creates `hostel.db`, five sample rooms, and one demo student (Hostel ID `STU1001`). Delete `hostel.db` and restart to regenerate the clean sample database.

## Pages
- Dashboard: counts and recent movements
- Students: search, add, allocate room, delete
- Rooms: add rooms and view occupancy
- In/out register: record and view movement events
- Visitors: register visitors and record checkout
- Leave: submit applications and approve/reject them

## Database design
- `rooms`: unique room number, category, capacity
- `students`: identity/contact information and optional room/bed allocation
- `movements`: student IN/OUT records with timestamp
- `visitors`: visitor details and check-in/check-out
- `leave_applications`: leave dates, reason, and status

## Notes
This is a local educational project, not a production-ready public deployment. Change `app.secret_key`, add password hashing and CSRF protection, and use a production WSGI server before deployment. Keep `hostel.db` backed up because it contains application records.

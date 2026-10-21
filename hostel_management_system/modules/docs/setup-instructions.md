# Setup Instructions

1. Install Python 3.8+ (Tkinter ships with the standard installer on Windows/macOS;
   on Ubuntu/Debian run `sudo apt install python3-tk`).
2. Open a terminal in the `hostel-management-system/` folder.
3. Run `python main.py` (or `python3 main.py`).
4. Log in with `user123` / `000`.

## Data / "database"
There is NO SQL database in the original code. Storage is flat files in `data/`
(created automatically on first run by `core/data_files.py`):

| File | Content |
|------|---------|
| student_info.txt | contact(id),name,father,mother,dob,email,workplace,vehicle,date,bed,room |
| room_info_boys.txt / girls / others | room,bed1,bed2,bed3,status |
| inouttime.txt | id,purpose,out time,in time,remark |
| visitor_info.txt | student,visitor,contact,reason,address,date |
| leave_applications.txt | id,name,room,mobile,reason,applied date,return date |

Important: the first room you add must exist before students can be assigned (use "Add New Room").

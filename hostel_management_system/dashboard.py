from tkinter.ttk import *
from tkinter import *
import os
from core.window import base
from modules.add_student import add_stud
from modules.add_room import add_room
from modules.in_out_time import in_out_time
from modules.visitor import visitor as visitor_page
from modules.view_info import view_info as view_info_page
from modules.leave_application import leave_application as leave_application_page

def main():
    global G
    canvas = Canvas(base, bg='lightseagreen', height=675, width=310)
    canvas.place(x=-1, y=100)
    can = Canvas(base, bg='silver', height=675, width=1500)
    can.place(x=320, y=105)

    add_std_btn = Button(base, text="Add Student", font=("Arial 20 bold"), padx=15, bg="white", command=add_stud)
    add_std_btn.place(x=50, y=150)

    add_new_room = Button(base, text="Add New Room", font=("Arial 20 bold"), bg="white", command=add_room)
    add_new_room.place(x=50, y=250)

    in_ot_time = Button(base, text="In And Outtime", font=("Arial 20 bold"), bg="white", command=in_out_time)
    in_ot_time.place(x=50, y=350)

    visitor = Button(base, text="Visitor", font=("Arial 20 bold"), bg="white", padx=55, command=visitor_page)
    visitor.place(x=50, y=450)

    view_info = Button(base, text="View Information", font=("Arial 18 bold"), bg="white", command=view_info_page)
    view_info.place(x=50, y=535)

    leave_application = Button(base, text="Leave Application", font=("Arial 18 bold"), bg="white", command=leave_application_page)
    leave_application.place(x=50, y=620)

    exit = Button(base, text="EXIT", font=("Arial 18 bold"), bg="white", padx=70, command=quit)
    exit.place(x=50, y=700)

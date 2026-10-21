from tkinter.ttk import *
from tkinter import *
import os
from core.window import base
from utils.datetime_utils import date


def in_out_time():
    canvas = Canvas(base, bg='silver', height=675, width=1210)
    canvas.place(x=320, y=105)

    a = "---------------Outtime---------------"
    out_time_h1 = Label(base, text=a, font=("Arial 20 bold"), bg="dark slate grey", fg="white", padx=20,
                        pady=10)
    out_time_h1.place(x=320, y=115)

    out_time = Label(base, text="Enter ID", font=("Arial 20 bold"), bg="silver", fg="black")
    out_time.place(x=470, y=200)
    out_time_entry = Entry(base, width=20, font=("Arial 20 bold"))
    out_time_entry.place(x=620, y=200)
    out_time_entry.focus()

    purpose = Label(base, text="Purpose", font=("Arial 20 bold"), bg="silver", fg="black")
    purpose.place(x=470, y=270)
    purpose_entry = Entry(base, width=20, font=("Arial 20 bold"))
    purpose_entry.place(x=620, y=270)

    def save1():
        Id = str(out_time_entry.get())
        pur1 = str(purpose_entry.get())
        t = date()
        f1 = open("data/inouttime.txt", "a")
        f1.write(Id + "," + pur1 + "," + t + "," + "OUTTIME" + "," + "REMARK" + "\n")
        f1.close()
        done = Label(base, text="Successfull...!", font=("Arial 20 bold"), bg="silver", fg="black")
        done.place(x=1200, y=220)

    save1 = Button(base, text="Save", font=("Arial 20 bold"), bg="white", fg="black", command=save1)
    save1.place(x=1050, y=220)

    a1 = "---------------Inttime---------------"
    in_time_h1 = Label(base, text=a1, font=("Arial 20 bold"), bg="dark slate grey", fg="white", padx=20,
                       pady=10)
    in_time_h1.place(x=320, y=400)

    in_time = Label(base, text="Enter ID", font=("Arial 20 bold"), bg="silver", fg="black")
    in_time.place(x=470, y=500)
    in_time_entry = Entry(base, width=20, font=("Arial 20 bold"))
    in_time_entry.place(x=680, y=500)
    in_time_entry.focus()

    ot_entry = Label(base, text="Outtime Entry", font=("Arial 20 bold"), bg="silver", fg="black")
    ot_entry.place(x=470, y=550)
    ot_entry_entry = Entry(base, width=20, font=("Arial 20 bold"))
    ot_entry_entry.place(x=680, y=550)

    def search_outtime():
        s_id = str(in_time_entry.get())
        fobj = open("data/inouttime.txt", "r")
        fdata_ls = fobj.readlines()
        count = 1
        for oneline in fdata_ls:
            if oneline.startswith(s_id + ",") and oneline.__contains__(",OUTTIME,"):
                # write date
                count = 2
                y = oneline.split(",")
                tv = StringVar()
                tv.set(y[2] + "     " + y[3])
                ot = Entry(base, width=20, textvariable=tv, font=("Arial 20 bold"))
                ot.place(x=680, y=550)
                break
        fobj.close()
        if count == 1:
            tv = StringVar()
            tv.set("Invalid Id")
            ot = Entry(base, width=20, textvariable=tv, font=("Arial 20 bold"))
            ot.place(x=680, y=550)

    def save2():
        sel_opt = str(r_sel.get())
        s_id = str(in_time_entry.get())
        fobj = open("data/inouttime.txt", "r")
        fdata_ls = fobj.readlines()
        fobj.close()
        rdate = date()
        count = 1
        fobj = open("data/inouttime.txt", "w")
        for oneline in fdata_ls:
            if oneline.startswith(s_id + ",") and oneline.__contains__(",OUTTIME,"):
                # write date
                new_oneline = oneline.replace(",OUTTIME,", "," + rdate + ",")
                new_oneline2 = new_oneline.replace(",REMARK", "," + sel_opt + ",")
                fobj.write(new_oneline2)
                count = 2
            else:
                fobj.write(oneline)
        if count == 2:
            done = Label(base, text="Successful...!", font=("Arial 20 bold"), bg="silver", fg="black")
            done.place(x=700, y=720)
        if count == 1:
            done = Label(base, text="Please Give Correct Information", font=("Arial 20 bold"), bg="silver",
                         fg="black")
            done.place(x=600, y=720)
        fobj.close()

    sear_ot = Button(base, text="Search Outtime", font=("Arial 18 bold"), bg="white", command=search_outtime)
    sear_ot.place(x=1050, y=520)
    save2 = Button(base, text="Save", font=("Arial 20 bold"), bg="white", fg="black", command=save2)
    save2.place(x=1050, y=700)

    r_sel = StringVar(base)
    ls = ['Before Time', 'On Time', 'Late']
    r_sel.set(ls[0])
    remark = OptionMenu(base, r_sel, *ls)
    remark.config(width=20, font=("Arial 15 bold"), fg="black")
    remark.place(x=680, y=610)

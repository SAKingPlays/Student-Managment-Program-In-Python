# cyberdevpro_student_console_classic.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB = "student_management.db"

# ---------- Database ----------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            father_name TEXT,
            gender TEXT,
            course TEXT,
            dob TEXT,
            father_phone TEXT,
            student_phone TEXT,
            address TEXT,
            admission_date TEXT,
            expell_date TEXT,
            remarks TEXT,
            gpa REAL,
            enrollment_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()


# ---------- App ----------
class StudentManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("CyberDevPro Student Console")
        self.root.geometry("1400x850")
        self.root.minsize(1100, 650)

        # Fonts/colors
        self.fonts = {
            'title': ('Outfit', 18, 'bold'),
            'label': ('Outfit', 11, 'bold'),   # fixed semibold -> bold
            'entry': ('Outfit', 11, 'normal'),
            'button': ('Outfit', 10, 'bold'),
            'report_title': ('Outfit', 16, 'bold'),
            'report_body': ('Outfit', 12, 'normal')
        }
        self.colors = {
            'bg': "#f5f5f5",         # very light gray
            'card': "#ffffff",       # white card
            'label': "#212529",      # dark neutral
            'entry_bg': "#ffffff",
            'entry_fg': "#111111",
            'btn_add': "#2f855a",    # green
            'btn_up': "#495057",     # gray
            'btn_del': "#a4161a",    # red
            'btn_clr': "#b06508",    # amber
            'btn_rpt': "#364fc7",    # muted indigo
            'btn_char': "#6a1b9a",   # purple
            'btn_pass': "#0277bd"    # blue
        }

        self.root.configure(bg=self.colors['bg'])
        self.main = tk.Frame(self.root, bg=self.colors['bg'])
        self.main.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        self.build_ui()
        self.load_students()


    # ---------- UI ----------
    def build_ui(self):
        # Title
        tk.Label(self.main, text="CyberDevPro Student Console",
                 font=self.fonts['title'], fg=self.colors['label'],
                 bg=self.colors['bg']).pack(pady=(0, 12))

        # Form Card
        form_card = tk.Frame(self.main, bg=self.colors['card'], bd=1, relief=tk.SOLID)
        form_card.pack(fill=tk.X, padx=5, pady=5)

        form = tk.Frame(form_card, bg=self.colors['card'])
        form.pack(fill=tk.X, padx=20, pady=18)

        # Fields (two-column layout)
        fields = [
            ("Student ID:", "student_id"),
            ("Student Name:", "name"),
            ("Father Name:", "father_name"),
            ("Gender:", "gender"),
            ("Course/Class:", "course"),
            ("Date of Birth:", "dob"),
            ("Father Phone:", "father_phone"),
            ("Student Phone:", "student_phone"),
            ("Address:", "address"),
            ("Admission Date:", "admission_date"),
            ("Date of Expell:", "expell_date"),
            ("Remarks:", "remarks"),
            ("GPA:", "gpa")
        ]

        self.entries = {}
        for i, (label_text, key) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2

            lbl = tk.Label(form, text=label_text, font=self.fonts['label'],
                           bg=self.colors['card'], fg=self.colors['label'])
            lbl.grid(row=row, column=col, sticky="w", padx=6, pady=8)

            e = tk.Entry(form, font=self.fonts['entry'],
                         bg=self.colors['entry_bg'], fg=self.colors['entry_fg'],
                         bd=1, relief=tk.SOLID, insertbackground=self.colors['entry_fg'])
            if key == "student_id":
                e.config(state='readonly')
                e.insert(0, self.generate_student_id())
            e.grid(row=row, column=col + 1, sticky="ew", padx=6, pady=8, ipadx=4, ipady=4)

            self.entries[key] = e

        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(3, weight=1)

        # Toolbar
        actions = tk.Frame(self.main, bg=self.colors['bg'])
        actions.pack(fill=tk.X, pady=(12, 10))

        def mkbtn(text, color, cmd):
            b = tk.Button(actions, text=text, font=self.fonts['button'],
                          bg=color, fg="white", relief="flat",
                          cursor="hand2", command=cmd, padx=12, pady=8)
            b.pack(side=tk.LEFT, padx=6)
            return b

        mkbtn("Add", self.colors['btn_add'], self.add_student)
        mkbtn("Update", self.colors['btn_up'], self.update_student)
        mkbtn("Delete", self.colors['btn_del'], self.delete_student)
        mkbtn("Clear", self.colors['btn_clr'], self.clear_form)
        mkbtn("Report Card", self.colors['btn_rpt'], self.generate_report_card_selected)
        mkbtn("Character Certificate", self.colors['btn_char'], self.generate_character_certificate)
        mkbtn("Passing Certificate", self.colors['btn_pass'], self.generate_passing_certificate)

        # Records Table
        table_card = tk.Frame(self.main, bg=self.colors['card'], bd=1, relief=tk.SOLID)
        table_card.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        tk.Label(table_card, text="Student Records",
                 font=self.fonts['title'], bg=self.colors['card'],
                 fg=self.colors['label']).pack(pady=(10, 6))

        cols = ("ID", "Student ID", "Name", "Father", "Gender", "Course", "DOB",
                "Father Phone", "Student Phone", "Address", "Admission Date",
                "Expell Date", "Remarks", "GPA", "Enrollment Date")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=self.colors['card'],
                        foreground=self.colors['entry_fg'],
                        rowheight=28,
                        fieldbackground=self.colors['card'],
                        bordercolor=self.colors['card'],
                        borderwidth=0,
                        font=self.fonts['entry'])
        style.configure("Treeview.Heading", font=self.fonts['label'])
        style.map("Treeview",
                  background=[("selected", "#e9ecef")],
                  foreground=[("selected", "black")])

        tree_frame = tk.Frame(table_card, bg=self.colors['card'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 12))

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings', style="Treeview")

        col_widths = {
            "ID": 50, "Student ID": 100, "Name": 180, "Father": 140, "Gender": 80,
            "Course": 140, "DOB": 100, "Father Phone": 120, "Student Phone": 120,
            "Address": 220, "Admission Date": 120, "Expell Date": 120, "Remarks": 180,
            "GPA": 60, "Enrollment Date": 160
        }
        for c in cols:
            w = col_widths.get(c, 120)
            self.tree.heading(c, text=c, anchor="center")
            self.tree.column(c, width=w,
                             anchor='w' if c in ("Name", "Address", "Remarks") else 'center')

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.config(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)


    # ---------- DB ----------
    def generate_student_id(self):
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT MAX(CAST(SUBSTR(student_id,5) AS INTEGER)) FROM students")
        r = c.fetchone()[0]
        conn.close()
        maxn = int(r) if r else 0
        return f"STD-{maxn+1:03d}"

    def get_form_data(self):
        return {k: e.get().strip() for k, e in self.entries.items()}

    def add_student(self):
        d = self.get_form_data()
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        try:
            c.execute('''INSERT INTO students
                (student_id,name,father_name,gender,course,dob,father_phone,student_phone,
                address,admission_date,expell_date,remarks,gpa,enrollment_date)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (d["student_id"], d["name"], d["father_name"], d["gender"], d["course"],
                 d["dob"], d["father_phone"], d["student_phone"], d["address"],
                 d["admission_date"], d["expell_date"], d["remarks"],
                 float(d["gpa"]) if d["gpa"] else None,
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            self.load_students()
            self.clear_form()
        except sqlite3.IntegrityError as ie:
            messagebox.showerror("Error", "Student ID already exists or invalid data.\n" + str(ie))
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def update_student(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Select a student to update.")
            return
        item = self.tree.item(sel[0])
        db_id = item['values'][0]
        d = self.get_form_data()
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        try:
            c.execute('''UPDATE students SET
                name=?, father_name=?, gender=?, course=?, dob=?, father_phone=?,
                student_phone=?, address=?, admission_date=?, expell_date=?, remarks=?, gpa=?
                WHERE id=?''',
                (d["name"], d["father_name"], d["gender"], d["course"], d["dob"],
                 d["father_phone"], d["student_phone"], d["address"], d["admission_date"],
                 d["expell_date"], d["remarks"], float(d["gpa"]) if d["gpa"] else None,
                 db_id))
            conn.commit()
            self.load_students()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def delete_student(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Select a student to delete.")
            return
        item = self.tree.item(sel[0])
        db_id = item['values'][0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected student?")
        if not confirm:
            return
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        try:
            c.execute("DELETE FROM students WHERE id=?", (db_id,))
            conn.commit()
            self.load_students()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def load_students(self):
        self.tree.delete(*self.tree.get_children())
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM students ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        for r in rows:
            self.tree.insert('', tk.END, values=r)

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])['values']
        keys = list(self.entries.keys())
        self.entries["student_id"].config(state='normal')
        for i, k in enumerate(keys, start=1):
            self.entries[k].delete(0, tk.END)
            value = vals[i] if i < len(vals) else ""
            self.entries[k].insert(0, "" if value is None else str(value))
        self.entries["student_id"].config(state='readonly')

    def clear_form(self):
        for k, e in self.entries.items():
            e.config(state='normal')
            e.delete(0, tk.END)
        self.entries["student_id"].insert(0, self.generate_student_id())
        self.entries["student_id"].config(state='readonly')


    # ---------- Report Card ----------
    def generate_report_card_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Select a student first!")
            return
        vals = self.tree.item(sel[0])['values']
        self.generate_report_card(vals)

    def generate_report_card(self, vals):
        if not vals or len(vals) < 15:
            messagebox.showerror("Error", "Selected record appears malformed.")
            return

        db_id, stid, name, father, gender, course, dob, fphone, sphone, addr, adm, exp, rem, gpa, enr = vals

        win = tk.Toplevel(self.root)
        win.title("CyberDevPro Report Card")
        win.geometry("640x720")
        win.configure(bg="#ffffff")

        tk.Label(win, text="CyberDevPro Report Card",
                 font=self.fonts['report_title'],
                 fg=self.colors['label'], bg="#ffffff").pack(pady=(20, 12))

        content = tk.Frame(win, bg="#ffffff")
        content.pack(fill=tk.BOTH, expand=True, padx=28, pady=10)

        fields = [
            ("Student ID", stid),
            ("Name", name),
            ("Father Name", father),
            ("Gender", gender),
            ("Course", course),
            ("Date of Birth", dob),
            ("Father Phone", fphone),
            ("Student Phone", sphone),
            ("Address", addr),
            ("Admission Date", adm),
            ("Date of Expell", exp),
            ("Remarks", rem),
            ("GPA", gpa),
            ("Enrollment Recorded", enr)
        ]

        for i, (label_text, val) in enumerate(fields):
            lbl = tk.Label(content, text=label_text + ":", font=self.fonts['label'],
                           anchor='w', bg="#ffffff", fg=self.colors['label'])
            lbl.grid(row=i, column=0, sticky='w', padx=(4, 12), pady=6)
            v = "" if val is None else str(val)
            val_lbl = tk.Label(content, text=v, font=self.fonts['report_body'],
                               anchor='w', bg="#ffffff", fg=self.colors['label'],
                               wraplength=420, justify='left')
            val_lbl.grid(row=i, column=1, sticky='w', padx=(2, 8), pady=6)

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tk.Label(win, text=f"Generated: {ts}", font=('Outfit', 9),
                 bg="#ffffff", fg="#666666").pack(pady=(6, 16))

        win.transient(self.root)
        win.grab_set()
        win.focus_force()


    # ---------- Certificates ----------
    def fetch_student_by_id(self, stid):
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE student_id=?", (stid,))
        row = c.fetchone()
        conn.close()
        return row

    def generate_character_certificate(self):
        stid = self.entries["student_id"].get().strip()
        if not stid:
            messagebox.showwarning("Missing", "Enter a Student ID first!")
            return
        row = self.fetch_student_by_id(stid)
        if not row:
            messagebox.showerror("Not Found", f"No student found with ID {stid}")
            return

        _, stid, name, father, gender, course, dob, fphone, sphone, addr, adm, exp, rem, gpa, enr = row

        win = tk.Toplevel(self.root)
        win.title("Character Certificate")
        win.geometry("640x720")
        win.configure(bg="#ffffff")

        tk.Label(win, text="Character Certificate",
                 font=self.fonts['report_title'],
                 fg=self.colors['label'], bg="#ffffff").pack(pady=(20, 12))

        body = tk.Frame(win, bg="#ffffff")
        body.pack(fill=tk.BOTH, expand=True, padx=28, pady=10)

        text = (f"This is to certify that {name}, son/daughter of {father}, "
                f"bearing Student ID {stid}, has been a student of {course} "
                f"in our institution. During the period of study, "
                f"their conduct and character have been found satisfactory.")
        
        tk.Label(body, text=text, font=self.fonts['report_body'],
                 bg="#ffffff", fg=self.colors['label'],
                 wraplength=560, justify="left").pack(pady=20)

        ts = datetime.now().strftime("%Y-%m-%d")
        tk.Label(win, text=f"Issued on: {ts}",
                 font=('Outfit', 10), bg="#ffffff", fg="#555555").pack(pady=8)

        win.transient(self.root)
        win.grab_set()
        win.focus_force()

    def generate_passing_certificate(self):
        stid = self.entries["student_id"].get().strip()
        if not stid:
            messagebox.showwarning("Missing", "Enter a Student ID first!")
            return
        row = self.fetch_student_by_id(stid)
        if not row:
            messagebox.showerror("Not Found", f"No student found with ID {stid}")
            return

        _, stid, name, father, gender, course, dob, fphone, sphone, addr, adm, exp, rem, gpa, enr = row

        win = tk.Toplevel(self.root)
        win.title("Passing Certificate")
        win.geometry("640x720")
        win.configure(bg="#ffffff")

        tk.Label(win, text="Passing Certificate",
                 font=self.fonts['report_title'],
                 fg=self.colors['label'], bg="#ffffff").pack(pady=(20, 12))

        body = tk.Frame(win, bg="#ffffff")
        body.pack(fill=tk.BOTH, expand=True, padx=28, pady=10)

        text = (f"This is to certify that {name}, son/daughter of {father}, "
                f"bearing Student ID {stid}, has successfully completed the "
                f"{course} course with a GPA of {gpa if gpa else 'N/A'}. "
                f"The student has passed all required examinations.")

        tk.Label(body, text=text, font=self.fonts['report_body'],
                 bg="#ffffff", fg=self.colors['label'],
                 wraplength=560, justify="left").pack(pady=20)

        ts = datetime.now().strftime("%Y-%m-%d")
        tk.Label(win, text=f"Issued on: {ts}",
                 font=('Outfit', 10), bg="#ffffff", fg="#555555").pack(pady=8)

        win.transient(self.root)
        win.grab_set()
        win.focus_force()


# ---------- Main ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementSystem(root)
    root.mainloop()

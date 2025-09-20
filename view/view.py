import tkinter as tk
from tkinter import messagebox
import pandas as pd

class StudentRegistrationView(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Student Registration System")
        self.geometry("800x600")
        self._frame = None
        self.switch_frame(LoginFrame)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self, self.controller)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(fill="both", expand=True)

    def show_message(self, title, message):
        messagebox.showinfo(title, message)

class LoginFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Login", font=("Helvetica", 24)).pack(pady=20)

        tk.Label(self, text="Enter Student ID or 'admin':").pack()
        self.user_id_entry = tk.Entry(self)
        self.user_id_entry.pack(pady=5)

        tk.Button(self, text="Login", command=self.login).pack()

    def login(self):
        user_id = self.user_id_entry.get()
        if self.controller.login(user_id):
            if self.controller.is_admin:
                self.master.switch_frame(AdminMenuFrame)
            else:
                self.master.switch_frame(StudentMenuFrame)
        else:
            self.master.show_message("Login Failed", "Invalid ID. Please try again.")

class StudentMenuFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Student Menu", font=("Helvetica", 24)).pack(pady=20)
        
        tk.Button(self, text="Register for a Subject", command=lambda: master.switch_frame(RegisterFrame)).pack(pady=5)
        tk.Button(self, text="View My Profile", command=self.show_profile).pack(pady=5)
        tk.Button(self, text="Logout", command=self.logout).pack(pady=5)

    def show_profile(self):
        profile = self.controller.get_student_profile_data()
        if profile:
            student_info = profile['student_info']
            enrolled_subjects = pd.DataFrame(profile['enrolled_subjects'])

            # Correct column names
            student_name = f"{student_info['title']} {student_info['first_name']} {student_info['last_name']}"
            dob = student_info['dateofbirth']
            
            message = (f"Student ID: {student_info['student_id']}\n"
                       f"Name: {student_name}\n"
                       f"Date of Birth: {dob}\n"
                       f"School: {student_info['school']}\n\n")

            if not enrolled_subjects.empty:
                # Correct column names
                enrolled_subjects_display = enrolled_subjects.rename(columns={'subject_id': 'Subject ID', 'grade': 'Grade'})
                message += f"Enrolled Subjects:\n{enrolled_subjects_display.to_string(index=False)}"
            else:
                message += "Enrolled Subjects:\nNo subjects enrolled yet."

            self.master.show_message("My Profile", message)
        else:
            self.master.show_message("Error", "Student profile not found.")
    
    def logout(self):
        self.controller.logout()
        self.master.switch_frame(LoginFrame)

class AdminMenuFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Admin Menu", font=("Helvetica", 24)).pack(pady=20)
        
        tk.Button(self, text="Add Grade", command=lambda: master.switch_frame(AddGradeFrame)).pack(pady=5)
        tk.Button(self, text="View All Subjects", command=self.show_all_subjects).pack(pady=5)
        tk.Button(self, text="Logout", command=self.logout).pack(pady=5)

    def show_all_subjects(self):
        subjects_df = self.controller.get_all_subjects_data()
        if not subjects_df.empty:
            # Correct column names
            subjects_df = subjects_df.rename(columns={'subjectname': 'Subject Name', 'prerequisite': 'Prerequisite'})
            self.master.show_message("All Subjects", subjects_df.to_string(index=False))
        else:
            self.master.show_message("Error", "No subjects found.")

    def logout(self):
        self.controller.logout()
        self.master.switch_frame(LoginFrame)

class RegisterFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Register for a Subject", font=("Helvetica", 20)).pack(pady=10)
        
        available_subjects = self.controller.get_available_subjects_data()
        self.subject_listbox = tk.Listbox(self, width=80, height=15)
        self.subject_listbox.pack(pady=10)
        
        for index, row in available_subjects.iterrows():
            # Correct column names
            prereq = f" (Prereq: {row['prerequisite']})" if pd.notna(row['prerequisite']) and row['prerequisite'] != '' else ""
            capacity_text = f"Capacity: {row['current_enrollment']}/{row['capacity']}" if row['capacity'] != -1 else "Capacity: Unlimited"
            self.subject_listbox.insert(tk.END, f"{row['subject_id']} - {row['subjectname']} | {capacity_text}{prereq}")

        tk.Button(self, text="Register Selected Subject", command=self.register_subject).pack(pady=5)
        tk.Button(self, text="Back to Menu", command=lambda: master.switch_frame(StudentMenuFrame)).pack(pady=5)

    def register_subject(self):
        try:
            selected_item = self.subject_listbox.get(self.subject_listbox.curselection())
            subject_id = selected_item.split(" ")[0]
            success, message = self.controller.register_subject(subject_id)
            self.master.show_message("Registration Status", message)
            if success:
                self.master.switch_frame(StudentMenuFrame)
        except tk.TclError:
            self.master.show_message("Error", "Please select a subject to register.")

class AddGradeFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Add Grade", font=("Helvetica", 20)).pack(pady=10)

        tk.Label(self, text="Student ID:").pack()
        self.student_id_entry = tk.Entry(self)
        self.student_id_entry.pack(pady=2)

        tk.Label(self, text="Subject ID:").pack()
        self.subject_id_entry = tk.Entry(self)
        self.subject_id_entry.pack(pady=2)

        tk.Label(self, text="Grade:").pack()
        self.grade_entry = tk.Entry(self)
        self.grade_entry.pack(pady=2)

        tk.Button(self, text="Add Grade", command=self.add_grade).pack(pady=5)
        tk.Button(self, text="Back to Menu", command=lambda: master.switch_frame(AdminMenuFrame)).pack(pady=5)

    def add_grade(self):
        student_id = self.student_id_entry.get()
        subject_id = self.subject_id_entry.get()
        grade = self.grade_entry.get()
        
        success, message = self.controller.add_grade(student_id, subject_id, grade)
        self.master.show_message("Add Grade Status", message)
        if success:
            self.master.switch_frame(AdminMenuFrame)
class StudentRegistrationController:
    def __init__(self, model):
        self.model = model
        self.logged_in_student_id = None
        self.is_admin = False

    def login(self, user_id):
        if user_id.lower() == 'admin':
            self.is_admin = True
            return True
        
        # Check if the student ID exists in the DataFrame
        # The astype(str) is crucial for consistent comparison
        students = self.model.students_df['student_id'].astype(str).tolist()
        if user_id in students:
            self.logged_in_student_id = user_id
            return True
        
        return False

    def get_available_subjects_data(self):
        print(self.logged_in_student_id)
        return self.model.get_subjects_not_registered(self.logged_in_student_id)

    def get_all_subjects_data(self):
        return self.model.get_all_subjects()

    def get_student_profile_data(self):
        return self.model.get_student_profile(self.logged_in_student_id)
        
    def register_subject(self, subject_id):
        # Call the model's registration method, which handles all business rules
        return self.model.register_subject(self.logged_in_student_id, subject_id)

    def add_grade(self, student_id, subject_id, grade):
        # Basic validation for existence of student and subject
        if not self.model.students_df['student_id'].astype(str).eq(student_id).any():
            return False, "Student ID not found."
        if not self.model.subjects_df['subject_id'].astype(str).eq(subject_id).any():
            return False, "Subject ID not found."

        # Call the model's method to add the grade
        self.model.add_grade(student_id, subject_id, grade)
        return True, f"Grade '{grade}' added for {student_id} in {subject_id}."

    def logout(self):
        self.logged_in_student_id = None
        self.is_admin = False
import pandas as pd
from datetime import datetime

class StudentRegistrationModel:
    def __init__(self):
        self.students_file = r'C:\code\GIT\66051054_MVC_1_2568\model\data_csv\students.csv'
        self.subjects_file = r'C:\code\GIT\66051054_MVC_1_2568\model\data_csv\subjects.csv'
        self.enrollments_file = r'C:\code\GIT\66051054_MVC_1_2568\model\data_csv\enrollments.csv'
        self.load_data()

    def load_data(self):
        try:
            self.students_df = pd.read_csv(self.students_file,dtype={'student_id': str})
        
            self.students_df.columns = self.students_df.columns.str.strip().str.lower()
        except FileNotFoundError:
            self.students_df = pd.DataFrame(columns=['student_id', 'title', 'first_name', 'last_name', 'dateofbirth', 'school', 'email'])
            self.students_df.to_csv(self.students_file, index=False)

        try:
            self.subjects_df = pd.read_csv(self.subjects_file, dtype={'subject_id': str})
            self.subjects_df.columns = self.subjects_df.columns.str.strip().str.lower()
        except FileNotFoundError:
            self.subjects_df = pd.DataFrame(columns=['subject_id', 'subjectname', 'credit', 'instructor', 'prerequisite', 'capacity', 'current_enrollment'])
            self.subjects_df.to_csv(self.subjects_file, index=False)
            
        try:
            self.enrollments_df = pd.read_csv(self.enrollments_file)
            self.enrollments_df.columns = self.enrollments_df.columns.str.strip().str.lower()
        except FileNotFoundError:
            self.enrollments_df = pd.DataFrame(columns=['student_id', 'subject_id', 'grade'])
            self.enrollments_df.to_csv(self.enrollments_file, index=False)
        print(self.students_df)
        print(self.subjects_df)
        print(self.enrollments_df)
    def save_data(self):
        self.students_df.to_csv(self.students_file, index=False)
        self.subjects_df.to_csv(self.subjects_file, index=False)
        self.enrollments_df.to_csv(self.enrollments_file, index=False)

    def add_student(self, student_data):
        self.students_df = pd.concat([self.students_df, pd.DataFrame([student_data])], ignore_index=True)
        self.save_data()

    def add_subject(self, subject_data):
        # Add current_enrollment field if not provided
        if 'current_enrollment' not in subject_data:
            subject_data['current_enrollment'] = 0
        self.subjects_df = pd.concat([self.subjects_df, pd.DataFrame([subject_data])], ignore_index=True)
        self.save_data()

    def get_all_subjects(self):
        return self.subjects_df

    def get_subject_details(self, subject_id):
        return self.subjects_df[self.subjects_df['subject_id'] == subject_id].to_dict('records')

    def is_eligible_for_registration(self, student_id, subject_id):
        # Rule: Age >= 15
        student_row = self.students_df[self.students_df['student_id'] == student_id]
        if student_row.empty:
            return False, f"Student ID {student_id} not found."
        student = student_row.iloc[0]
        dob = datetime.strptime(student['dateofbirth'], '%d/%m/%Y')
        age = (datetime.now() - dob).days // 365
        if age < 15:
            return False, "Student must be at least 15 years old."

        # Rule: Check max capacity
        subject = self.subjects_df[self.subjects_df['subject_id'] == subject_id].iloc[0]
        max_capacity = subject['capacity']
        current_enrollment = subject.get('current_enrollment', 0)
        if max_capacity != -1 and current_enrollment >= max_capacity:
            return False, "Subject is full."

        # Rule: Check prerequisite
        prerequisite = subject['prerequisite']
        if pd.notna(prerequisite) and prerequisite != '':
            completed_prerequisite = self.enrollments_df[
                (self.enrollments_df['student_id'] == student_id) &
                (self.enrollments_df['subject_id'] == prerequisite) &
                (pd.notna(self.enrollments_df['grade']))
            ]
            if completed_prerequisite.empty:
                return False, f"Prerequisite subject {prerequisite} has not been completed."
        
        return True, "Eligible for registration."

    def register_subject(self, student_id, subject_id):
        is_eligible, message = self.is_eligible_for_registration(student_id, subject_id)
        if not is_eligible:
            return False, message
        
        # Check if already registered
        if not self.enrollments_df[(self.enrollments_df['student_id'] == student_id) & (self.enrollments_df['subject_id'] == subject_id)].empty:
            return False, "You have already registered for this subject."

        # Update current enrollment
        self.subjects_df.loc[self.subjects_df['subject_id'] == subject_id, 'current_enrollment'] += 1
        
        # Add new enrollment record
        new_enrollment = pd.DataFrame([{'student_id': student_id, 'subject_id': subject_id, 'grade': None}])
        self.enrollments_df = pd.concat([self.enrollments_df, new_enrollment], ignore_index=True)
        
        self.save_data()
        return True, "Registration successful."
    
    def get_student_profile(self, student_id):
        student_info = self.students_df[self.students_df['student_id'] == student_id].to_dict('records')
        print(student_info)
        enrolled_subjects = self.enrollments_df[self.enrollments_df['student_id'] == student_id]
        
        if student_info:
            return {
                "student_info": student_info[0],
                "enrolled_subjects": enrolled_subjects.to_dict('records')
            }
        return None

    def get_subjects_not_registered(self, student_id):
        enrolled_subjects_ids = self.enrollments_df[self.enrollments_df['student_id'] == student_id]['subject_id'].tolist()
        not_enrolled_subjects = self.subjects_df[~self.subjects_df['subject_id'].isin(enrolled_subjects_ids)]
        print(not_enrolled_subjects)
        return not_enrolled_subjects

    def add_grade(self, student_id, subject_id, grade):
        self.enrollments_df.loc[
            (self.enrollments_df['student_id'] == student_id) & (self.enrollments_df['subject_id'] == subject_id),
            'grade'
        ] = grade
        self.save_data()
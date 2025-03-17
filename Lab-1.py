import csv
import time
import statistics
from cryptography.fernet import Fernet
import os

# Student class
class Student:
    def __init__(self, email, first_name, last_name, course_id, grades, marks):
        self.email = email.lower()
        self.first_name = first_name
        self.last_name = last_name
        self.course_id = course_id
        self.grades = grades
        self.marks = marks

# Professor class
class Professor:
    def __init__(self, professor_id, professor_name, rank, course_id):
        self.professor_id = professor_id
        self.professor_name = professor_name
        self.rank = rank
        self.course_id = course_id

# FileHandler class to save students and professors to CSV
class FileHandler:
    @staticmethod
    def save_students_to_csv(students, filename='student.csv'):
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Email_address', 'First_name', 'Last_name', 'Course_id', 'grades', 'Marks']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for student in students:
                writer.writerow({
                    'Email_address': student.email,
                    'First_name': student.first_name,
                    'Last_name': student.last_name,
                    'Course_id': student.course_id,
                    'grades': student.grades,
                    'Marks': student.marks
                })

    @staticmethod
    def save_professors_to_csv(professors, filename='professor.csv'):
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Professor_id', 'Professor_Name', 'Rank', 'Course_id']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for professor in professors:
                writer.writerow({
                    'Professor_id': professor.professor_id,
                    'Professor_Name': professor.professor_name,
                    'Rank': professor.rank,
                    'Course_id': professor.course_id
                })

# Login system with encryption
class LoginSystem:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.users = self.load_users()

    def load_users(self):
        users = {}
        try:
            with open('login.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    users[row['User_id'].lower()] = {
                        'password': row['Password'],
                        'role': row['Role']
                    }
        except FileNotFoundError:
            print("Login file not found. Creating new login file.")
        return users

    def save_users(self):
        with open('login.csv', 'w', newline='') as csvfile:
            fieldnames = ['User_id', 'Password', 'Role']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for email, data in self.users.items():
                writer.writerow({
                    'User_id': email,
                    'Password': data['password'],
                    'Role': data['role']
                })

    def register(self, email, password, role):
        email = email.lower()
        if email in self.users:
            return False, "User already exists"
        
        encrypted_password = self.cipher.encrypt(password.encode()).decode()
        self.users[email] = {
            'password': encrypted_password,
            'role': role
        }
        self.save_users()
        return True, "Registration successful"

    def login(self, email, password):
        email = email.lower()
        if email not in self.users:
            return False, "User not found"
        
        try:
            stored_password = self.users[email]['password']
            decrypted_password = self.cipher.decrypt(stored_password.encode()).decode()
            if password == decrypted_password:
                return True, self.users[email]['role']
            return False, "Incorrect password"
        except Exception:
            return False, "Login error"

# Main application class for grades, student and professor management
class CheckMyGrade:
    def __init__(self):
        self.students = []
        self.professors = []
        self.login_system = LoginSystem()
        self.file_handler = FileHandler()

    def add_student(self, email, first_name, last_name, course_id, grades, marks):
        if any(s.email == email.lower() for s in self.students):
            return False, "Student email already exists"
        
        new_student = Student(email, first_name, last_name, course_id, grades, marks)
        self.students.append(new_student)
        self.file_handler.save_students_to_csv(self.students)
        return True, "Student added successfully"

    def add_professor(self, professor_id, professor_name, rank, course_id):
        new_professor = Professor(professor_id, professor_name, rank, course_id)
        self.professors.append(new_professor)
        self.file_handler.save_professors_to_csv(self.professors)
        return True, "Professor added successfully"

    def sort_students_by(self, key='marks', reverse=True):
        if key == 'marks':
            self.students.sort(key=lambda x: x.marks, reverse=reverse)
        elif key == 'name':
            self.students.sort(key=lambda x: (x.first_name, x.last_name), reverse=reverse)
        elif key == 'course':
            self.students.sort(key=lambda x: x.course_id, reverse=reverse)
        
        return self.students

    def search_records(self, search_term, search_type='student'):
        search_term = search_term.lower()
        results = []
        
        if search_type == 'student':
            for student in self.students:
                if (search_term in student.email.lower() or
                    search_term in student.first_name.lower() or
                    search_term in student.last_name.lower() or
                    search_term in student.course_id.lower()):
                    results.append(student)
        elif search_type == 'professor':
            for professor in self.professors:
                if (search_term in professor.professor_id.lower() or
                    search_term in professor.professor_name.lower() or
                    search_term in professor.course_id.lower()):
                    results.append(professor)
                    
        return results

# Main function to interact with the system
def main():
    app = CheckMyGrade()
    login_system = LoginSystem()

    while True:
        print("\n1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            email = input("Enter email: ")
            password = input("Enter password: ")
            success, role = login_system.login(email, password)
            
            if success:
                if role == 'professor':
                    professor_menu(app, email)
                else:
                    student_menu(app, email)
            else:
                print(f"Login failed: {role}")

        elif choice == '2':
            email = input("Enter email: ")
            password = input("Enter password: ")
            role = input("Enter role (student/professor): ")
            success, message = login_system.register(email, password, role)
            print(message)

        elif choice == '3':
            break

# Professor menu
def professor_menu(app, professor_id):
    while True:
        print("\n1. View all students")
        print("2. Add student")
        print("3. Modify student")
        print("4. Delete student")
        print("5. View statistics")
        print("6. Search records")
        print("7. Sort records")
        print("8. Logout")
        
        choice = input("Enter your choice: ")
        # Implement professor menu options

# Student menu
def student_menu(app, student_id):
    while True:
        print("\n1. View my grades")
        print("2. View course statistics")
        print("3. Logout")
        
        choice = input("Enter your choice: ")
        # Implement student menu options

if __name__ == "__main__":
    main()


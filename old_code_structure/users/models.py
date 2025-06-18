# This file defines the database models for user and profile management.
# For now, we'll define a single User model with role-specific fields.
# In a more complex system, StudentProfile and TeacherProfile might be separate models.

import datetime

class User:
    def __init__(self, email, password_hash, first_name, last_name, role,
                 major=None, department=None, bio=None, created_at=None, updated_at=None):
        self.email = email
        self.password_hash = password_hash  # In a real app, this would be securely managed
        self.first_name = first_name
        self.last_name = last_name

        if role not in ["student", "teacher"]:
            raise ValueError("Invalid role specified. Must be 'student' or 'teacher'.")
        self.role = role

        self.created_at = created_at if created_at else datetime.datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.datetime.utcnow()

        # Role-specific fields
        if self.role == "student":
            self.major = major
            self.department = None # Students don't have a department in this model
            self.bio = None # Students don't have a bio in this model
        elif self.role == "teacher":
            self.major = None # Teachers don't have a major in this model
            self.department = department
            self.bio = bio
        else: # Should not happen due to role validation, but as a safeguard
            self.major = None
            self.department = None
            self.bio = None

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

    def update_profile(self, **kwargs):
        """
        Updates user profile information.
        Specific fields that can be updated might depend on the role.
        """
        updatable_fields = ["first_name", "last_name"]
        if self.role == "student":
            updatable_fields.append("major")
        elif self.role == "teacher":
            updatable_fields.extend(["department", "bio"])

        for key, value in kwargs.items():
            if key in updatable_fields:
                setattr(self, key, value)
        self.updated_at = datetime.datetime.utcnow()
        print(f"Profile for {self.email} updated.")

# Example Usage (for simulation purposes, not part of the actual application logic here):
# if __name__ == "__main__":
#     # Simulate creating a student
#     student_user = User(
#         email="student@example.com",
#         password_hash="hashed_student_pass",
#         first_name="John",
#         last_name="Doe",
#         role="student",
#         major="Computer Science"
#     )
#     print(student_user)
#     print(f"Major: {student_user.major}, Created: {student_user.created_at}")

#     # Simulate creating a teacher
#     teacher_user = User(
#         email="teacher@example.com",
#         password_hash="hashed_teacher_pass",
#         first_name="Jane",
#         last_name="Smith",
#         role="teacher",
#         department="Physics",
#         bio="Experienced physics teacher with a passion for quantum mechanics."
#     )
#     print(teacher_user)
#     print(f"Department: {teacher_user.department}, Bio: {teacher_user.bio}")

#     # Simulate updating a profile
#     student_user.update_profile(major="Electrical Engineering", first_name="Johnny")
#     print(f"Updated Major: {student_user.major}, Updated Name: {student_user.first_name}, Updated At: {student_user.updated_at}")

#     try:
#         invalid_user = User("invalid@test.com", "hash", "Test", "User", "admin")
#     except ValueError as e:
#         print(f"Error creating user: {e}")

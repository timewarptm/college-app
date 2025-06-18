# This file will contain the business logic for authentication.
# For now, it will have placeholder functions for user registration and login.

def register_user(email, password, first_name, last_name, role, major=None, department=None, bio=None):
    """
    Simulates user registration.
    In a real application, this would hash the password and save the user to a database.
    """
    print(f"Attempting to register user: {email}, {role}")
    # Simulate password hashing
    password_hash = f"hashed_{password}"

    user_data = {
        "email": email,
        "password_hash": password_hash,
        "first_name": first_name,
        "last_name": last_name,
        "role": role,
        "created_at": "simulated_timestamp", # Replace with actual datetime
        "updated_at": "simulated_timestamp", # Replace with actual datetime
    }
    if role == "student" and major:
        user_data["major"] = major
    elif role == "teacher" and department:
        user_data["department"] = department
        if bio:
            user_data["bio"] = bio

    # Simulate saving to database
    print(f"User {email} registered successfully with data: {user_data}")
    return user_data

def login_user(email, password):
    """
    Simulates user login.
    In a real application, this would verify credentials against the database.
    """
    print(f"Attempting to login user: {email}")
    # Simulate fetching user from database and verifying password
    # This is a placeholder and does not represent secure authentication
    if email == "test@example.com" and password == "password123":
        print(f"User {email} logged in successfully.")
        return {"email": email, "message": "Login successful"}
    else:
        print(f"Login failed for user {email}.")
        return None

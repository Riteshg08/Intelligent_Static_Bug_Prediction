import sqlite3
import os
import subprocess

# 1. Hardcoded secret/password (High Risk)
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"
DB_PASSWORD = "super_secret_password_123"

def authenticate_user(username, password):
    # 2. SQL Injection vulnerability (High Risk)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # BAD: String interpolation for SQL queries
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    return user

def execute_system_command(user_input):
    # 3. Command Injection (High Risk)
    # BAD: Passing unsanitized user input directly to a shell command
    command = "ping -c 1 " + user_input
    os.system(command)

def evaluate_math_expression(expression):
    # 4. Insecure use of eval (High Risk)
    # BAD: Evaluates arbitrary Python code passed as string
    return eval(expression)

def process_data(data_list):
    # 5. Out of bounds error / Bad logic (Medium/Low Risk depending on context)
    total = 0
    for i in range(len(data_list) + 1):  # BUG: Off-by-one error (IndexError)
        total += data_list[i]
    return total

def run_background_task(cmd):
    # 6. Another command execution vulnerability
    subprocess.Popen(cmd, shell=True) # BAD: shell=True with arbitrary input

if __name__ == "__main__":
    print("This is a dummy buggy file for testing the Intelligent Static Bug Prediction tool.")

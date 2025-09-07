import mysql.connector
from mysql.connector import Error
import bcrypt
import uuid

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="photostore.ct0go6um6tj0.ap-south-1.rds.amazonaws.com",
            user="admin",
            password="DBpicshot",
            database="eventsreminder",
            use_pure=True
        )
        if connection.is_connected():
            print("Successfully connected to the database")
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
    return connection

def create_tables():
    connection = create_connection()
    if connection is None:
        return
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT,
                user_id VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                date VARCHAR(255) NOT NULL,
                time VARCHAR(50),
                done BOOLEAN NOT NULL,
                reminder_setting VARCHAR(50),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        connection.commit()
        print("Users and Events tables created/updated successfully.")
    except Error as e:
        print(f"Error creating tables: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def login_user(email, password):
    connection = create_connection()
    if connection is None:
        return None
    try:
        cursor = connection.cursor()
        query = "SELECT user_id, password FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        if result:
            user_id, hashed_password = result
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                print(f"User {email} logged in successfully.")
                return user_id
            else:
                print(f"Login failed for {email}: Incorrect password.")
        else:
            print(f"Login failed for {email}: User not found.")
        return None
    except Error as e:
        print(f"Error during login: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def insert_user(username, email, phone, password):
    connection = create_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        user_id = uuid.uuid4().hex[:12]
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        query = "INSERT INTO users (user_id, username, email, phone, password) VALUES (%s, %s, %s, %s, %s)"
        values = (user_id, username, email, phone, hashed_password.decode('utf-8'))
        cursor.execute(query, values)
        connection.commit()
        print(f"User {username} inserted successfully with User ID: {user_id}.")
        return True
    except Error as e:
        print(f"Error inserting user: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
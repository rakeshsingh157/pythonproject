import customtkinter as ctk
import mysql.connector

class LoginApp(ctk.CTk):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Login")
        self.geometry("300x200")
        self.configure(fg_color="#f5f5f5")

        self.create_login_form()

    def create_login_form(self):
        login_frame = ctk.CTkFrame(self, fg_color="transparent")
        login_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(login_frame, text="Login", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 10))

        self.username_entry = ctk.CTkEntry(login_frame, placeholder_text="Username")
        self.username_entry.pack(fill="x", pady=5)

        self.password_entry = ctk.CTkEntry(login_frame, placeholder_text="Password", show="*")
        self.password_entry.pack(fill="x", pady=5)

        ctk.CTkButton(login_frame, text="Login", command=self.login).pack(fill="x", pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.validate_credentials(username, password):
            self.destroy()
            # Open the main application here
        else:
            ctk.CTkMessageBox(self, text="Invalid credentials", icon="warning").pack()

    def validate_credentials(self, username, password):
        try:
            conn = mysql.connector.connect(
                host="photostore.ct0go6um6tj0.ap-south-1.rds.amazonaws.com",
                user="admin",
                password="DBpicshot",
                database="eventsreminder"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            return cursor.fetchone() is not None
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

class CreateAccountApp(ctk.CTk):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Create Account")
        self.geometry("300x250")
        self.configure(fg_color="#f5f5f5")

        self.create_account_form()

    def create_account_form(self):
        account_frame = ctk.CTkFrame(self, fg_color="transparent")
        account_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(account_frame, text="Create Account", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 10))

        self.username_entry = ctk.CTkEntry(account_frame, placeholder_text="Username")
        self.username_entry.pack(fill="x", pady=5)

        self.password_entry = ctk.CTkEntry(account_frame, placeholder_text="Password", show="*")
        self.password_entry.pack(fill="x", pady=5)

        self.confirm_password_entry = ctk.CTkEntry(account_frame, placeholder_text="Confirm Password", show="*")    
        self.confirm_password_entry.pack(fill="x", pady=5)

        ctk.CTkButton(account_frame, text="Create", command=self.create_account).pack(fill="x", pady=10)

    def create_account(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if password != confirm_password:
            ctk.CTkMessageBox(self, text="Passwords do not match", icon="warning").pack()
            return

        if self.register_user(username, password):
            self.destroy()
        else:
            ctk.CTkMessageBox(self, text="Failed to create account", icon="warning").pack()

    def register_user(self, username, password):
        try:
            conn = mysql.connector.connect(
                host="photostore.ct0go6um6tj0.ap-south-1.rds.amazonaws.com",
                user="admin",
                password="DBpicshot",
                database="eventsreminder"
            )
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()    

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox
from database import login_user, insert_user, create_tables
from py import CalendarApp
import sys
import os
import ai_assistant
import mysql.connector.locales.eng.client_error
import subprocess

# --- THEME & CONFIGURATION ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
PRIMARY = "#2F63FF"

# Ensure the database tables exist on startup
create_tables()

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MarkIt")
        self.geometry("1100x600")
        self.configure(fg_color="white")
        self.current_user_id = None
        self.calendar_app_instance = None
        
        # Configure the main window grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.login_frame = self.create_login_frame()
        self.login_frame.grid(row=0, column=0, sticky="nsew")

    def create_login_frame(self):
        login_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        login_frame.grid_columnconfigure(0, weight=1)
        login_frame.grid_rowconfigure(0, weight=1)
        
        # Inner frame to center content
        content_frame = ctk.CTkFrame(login_frame, fg_color="white")
        content_frame.grid(row=0, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # Left panel for form
        left_panel = ctk.CTkFrame(content_frame, fg_color="white", corner_radius=0)
        left_panel.grid(row=0, column=0, sticky="nsew")
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(0, weight=1)
        left_panel.grid_rowconfigure(2, weight=1)

        # Centering elements in the left panel
        form_frame = ctk.CTkFrame(left_panel, fg_color="white")
        form_frame.grid(row=1, column=0, padx=60, pady=60, sticky="nsew")
        form_frame.grid_columnconfigure(0, weight=1)

        logo = ctk.CTkLabel(form_frame, text="MarkIt", font=("Georgia", 32, "bold"), text_color=PRIMARY)
        logo.pack(anchor="w", pady=(10, 5))

        heading = ctk.CTkLabel(form_frame, text="Sign In to MarkIt", font=("Arial", 22, "bold"), text_color="black")
        heading.pack(anchor="w", pady=(0, 30))

        self.email_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter your email", width=380, height=48, corner_radius=10, font=("Arial", 14))
        self.email_entry.pack(pady=12, fill="x")

        self.password_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter your password", show="*", width=380, height=48, corner_radius=10, font=("Arial", 14))
        self.password_entry.pack(pady=12, fill="x")

        signin_btn = ctk.CTkButton(form_frame, text="Sign In", width=380, height=48, corner_radius=10, font=("Arial", 15, "bold"), fg_color=PRIMARY, hover_color="#244ECC", command=self.handle_login)
        signin_btn.pack(pady=25, fill="x")
        
        # New sign-up button that opens Signup.py
        signup_btn = ctk.CTkButton(form_frame, text="Don't have an account? Sign Up", width=380, height=35, corner_radius=10, font=("Arial", 12), fg_color="transparent", text_color=PRIMARY, hover_color="#F0F0F0", command=self.open_signup)
        signup_btn.pack(pady=(0, 10), fill="x")

        self.result_label = ctk.CTkLabel(form_frame, text="", font=("Arial", 14))
        self.result_label.pack(pady=5)
        
        # Right panel for illustration
        right_panel = ctk.CTkFrame(content_frame, fg_color="white", corner_radius=0)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(0, weight=1)
        
        try:
            # Check if running in a packaged app
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            img_path = os.path.join(base_path, "image.png")
            img = ctk.CTkImage(light_image=Image.open(img_path), size=(500, 400))
            illustration = ctk.CTkLabel(right_panel, image=img, text="")
            illustration.grid(row=0, column=0, sticky="nsew")
        except Exception:
            illustration = ctk.CTkLabel(right_panel, text="(Illustration Missing)", font=("Arial", 14))
            illustration.grid(row=0, column=0, sticky="nsew")
            
        return login_frame

    def open_signup(self):
        """Open the Signup.py file in a new process"""
        try:
            # Determine the path to Signup.py
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                base_path = os.path.dirname(sys.executable)
            else:
                # Running as script
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            signup_path = os.path.join(base_path, "Signup.py")
            
            # Open Signup.py using the same Python interpreter
            subprocess.Popen([sys.executable, signup_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open signup form: {str(e)}")

    def show_calendar_frame(self):
        self.login_frame.grid_forget()
        self.calendar_app_instance = CalendarApp(self, self.current_user_id)
        self.calendar_app_instance.root = self
        self.calendar_app_instance.main_frame.grid(row=0, column=0, sticky="nsew")
        self.title("MarkIt — My Events")

    def handle_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not email or not password:
            self.result_label.configure(text="⚠️ Please enter both email and password", text_color="red")
            return
        
        user_id = login_user(email, password)
        if user_id:
            self.current_user_id = user_id
            self.result_label.configure(text="✅ Login successful! Redirecting...", text_color="green")
            self.after(1000, self.show_calendar_frame)
        else:
            self.result_label.configure(text="❌ Invalid email or password.", text_color="red")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
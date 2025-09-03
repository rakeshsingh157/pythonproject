import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from database import insert_user

class ResponsiveSignup:
    def __init__(self, parent):
        self.parent = parent
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.calculate_font_sizes(self.parent.winfo_width(), self.parent.winfo_height())
        self.parent.bind("<Configure>", self.on_window_resize)

    def create_signup_frame(self):
        self.signup_frame = ctk.CTkFrame(self.parent, fg_color="white", corner_radius=0)
        self.signup_frame.grid_columnconfigure(0, weight=2)
        self.signup_frame.grid_columnconfigure(1, weight=1)
        self.signup_frame.grid_rowconfigure(0, weight=1)

        self.create_background(self.signup_frame)
        self.create_form(self.signup_frame)
        
        return self.signup_frame

    def calculate_font_sizes(self, width, height):
        base_size = min(width, height)
        self.title_font_size = max(24, int(base_size * 0.04))
        self.logo_font_size = max(20, int(base_size * 0.025))
        self.label_font_size = max(12, int(base_size * 0.015))
        self.entry_font_size = max(12, int(base_size * 0.014))
        self.button_font_size = max(14, int(base_size * 0.018))

    def create_account(self):
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        password = self.password_entry.get()
        username = self.username_entry.get()

        if not email or not phone or not password or not username:
            messagebox.showerror("Error", "All fields are required!")
        elif not phone.isdigit() or len(phone) != 10:
            messagebox.showerror("Error", "Phone number must be exactly 10 digits and contain only numbers.")
        else:
            if insert_user(username, email, phone, password):
                messagebox.showinfo("Success", f"Account created for {email}")
                self.back_to_login()
            else:
                messagebox.showerror("Error", "Failed to create account. Please try again.")

    def create_background(self, parent_frame):
        self.bg_frame = ctk.CTkFrame(parent_frame, fg_color="white", corner_radius=0)
        self.bg_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        self.bg_container = ctk.CTkFrame(self.bg_frame, fg_color="white")
        self.bg_container.pack(fill="both", expand=True, padx=0, pady=0)

        try:
            if os.path.exists("logpage.png"):
                self.load_background_image()
            else:
                pass
        except Exception as e:
            print(f"Error loading background image: {e}")
            pass

    def load_background_image(self):
        try:
            self.parent.update_idletasks()
            bg_width = max(600, self.parent.winfo_width() // 2)
            bg_height = self.parent.winfo_height()
            
            original_image = Image.open("logpage.png")
            original_width, original_height = original_image.size
            ratio = min(bg_width / original_width, bg_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)

            resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(resized_image)

            if hasattr(self, 'bg_label'):
                self.bg_label.destroy()

            self.bg_label = ctk.CTkLabel(self.bg_container, image=self.bg_photo, text="")
            self.bg_label.pack(padx=(200, 0), pady=0, expand=True)

        except Exception as e:
            print(f"Error loading background image: {e}")

    def create_form(self, parent_frame):
        self.form_frame = ctk.CTkFrame(parent_frame, fg_color="white", corner_radius=0)
        self.form_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=0)

        self.form_frame.grid_columnconfigure(0, weight=0)
        for i in range(10):
            self.form_frame.grid_rowconfigure(i, weight=1)

        logo_label = ctk.CTkLabel(
            self.form_frame,
            text="MarkIt",
            font=("Arial Black", self.logo_font_size),
            text_color="#3366ff"
        )
        logo_label.grid(row=0, column=0, pady=(30, 10), sticky="e", padx=(0, 50))

        title_label = ctk.CTkLabel(
            self.form_frame,
            text="Create a new account",
            font=("Arial", self.title_font_size, "bold"),
            text_color="#333333"
        )
        title_label.grid(row=1, column=0, pady=(10, 30), sticky="w", padx=(50, 50))

        self.create_form_fields()

    def create_form_fields(self):
        username_label = ctk.CTkLabel(
            self.form_frame,
            text="Enter your Username",
            font=("Arial", self.label_font_size),
            text_color="#AAAABC"
        )
        username_label.grid(row=2, column=0, sticky="w", padx=(50, 50), pady=(0, 5))

        self.username_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Enter your Username",
            placeholder_text_color="#D1D1E4",
            fg_color="#ffffff",
            height=max(40, int(self.entry_font_size * 2.5)),
            corner_radius=15,
            border_color="#D1D1E4",
            font=("Arial", self.entry_font_size)
        )
        self.username_entry.grid(row=3, column=0, sticky="ew", padx=(50, 50), pady=(0, 15))
        self.username_entry.bind("<Return>", lambda e: self.email_entry.focus())

        email_label = ctk.CTkLabel(
            self.form_frame,
            text="Enter your Email",
            font=("Arial", self.label_font_size),
            text_color="#AAAABC"
        )
        email_label.grid(row=4, column=0, sticky="w", padx=(50, 50), pady=(0, 5))

        self.email_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Enter your Email",
            placeholder_text_color="#D1D1E4",
            fg_color="#ffffff",
            height=max(40, int(self.entry_font_size * 2.5)),
            corner_radius=15,
            border_color="#D1D1E4",
            font=("Arial", self.entry_font_size)
        )
        self.email_entry.grid(row=5, column=0, sticky="ew", padx=(50, 50), pady=(0, 15))
        self.email_entry.bind("<Return>", lambda e: self.phone_entry.focus())

        phone_label = ctk.CTkLabel(
            self.form_frame,
            text="Enter your Phone number",
            font=("Arial", self.label_font_size),
            text_color="#AAAABC"
        )
        phone_label.grid(row=6, column=0, sticky="w", padx=(50, 50), pady=(0, 5))

        self.phone_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Enter your Phone number",
            placeholder_text_color="#D1D1E4",
            fg_color="#ffffff",
            height=max(40, int(self.entry_font_size * 2.5)),
            corner_radius=15,
            border_color="#D1D1E4",
            font=("Arial", self.entry_font_size)
        )
        self.phone_entry.grid(row=7, column=0, sticky="ew", padx=(50, 50), pady=(0, 15))
        self.phone_entry.bind("<Return>", lambda e: self.password_entry.focus())

        password_label = ctk.CTkLabel(
            self.form_frame,
            text="Enter your Password",
            font=("Arial", self.label_font_size),
            text_color="#AAAABC"
        )
        password_label.grid(row=8, column=0, sticky="w", padx=(50, 50), pady=(0, 5))

        self.password_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Enter your Password",
            placeholder_text_color="#D1D1E4",
            fg_color="#ffffff",
            show="*",
            height=max(40, int(self.entry_font_size * 2.5)),
            corner_radius=15,
            border_color="#D1D1E4",
            font=("Arial", self.entry_font_size)
        )
        self.password_entry.grid(row=9, column=0, sticky="ew", padx=(50, 50), pady=(0, 20))
        self.password_entry.bind("<Return>", lambda e: self.create_account())

        create_btn = ctk.CTkButton(
            self.form_frame,
            text="Create Account",
            text_color="white",
            font=("Arial", self.button_font_size, "bold"),
            height=max(45, int(self.button_font_size * 2.8)),
            fg_color="#3366ff",
            hover_color="#2850cc",
            corner_radius=15,
            command=self.create_account
        )
        create_btn.grid(row=10, column=0, sticky="ew", padx=(50, 50), pady=(0, 30))

        login_btn = ctk.CTkButton(
            self.form_frame,
            text="Already have an account? Sign In",
            width=380,
            height=35,
            corner_radius=10,
            font=("Arial", 12),
            fg_color="transparent",
            text_color="#3366ff",
            hover_color="#F0F0F0",
            command=self.back_to_login
        )
        login_btn.grid(row=11, column=0, pady=(0, 10), sticky="ew", padx=(50, 50))


    def back_to_login(self):
        self.signup_frame.grid_forget()
        self.parent.create_login_frame().grid(row=0, column=0, sticky="nsew")
        self.parent.title("MarkIt")

    def on_window_resize(self, event):
        if event.widget == self.parent:
            new_width = self.parent.winfo_width()
            new_height = self.parent.winfo_height()
            self.calculate_font_sizes(new_width, new_height)
            self.update_widget_fonts()
            try:
                if os.path.exists("logpage.png"):
                    self.load_background_image()
            except Exception as e:
                print(f"Error loading background image on resize: {e}")

    def update_widget_fonts(self):
        try:
            for widget in self.form_frame.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    current_text = widget.cget("text")
                    if "MarkIt" in current_text:
                        widget.configure(font=("Arial Black", self.logo_font_size))
                    elif "Create a new account" in current_text:
                        widget.configure(font=("Arial", self.title_font_size, "bold"))
                    else:
                        widget.configure(font=("Arial", self.label_font_size))
                elif isinstance(widget, ctk.CTkEntry):
                    widget.configure(
                        font=("Arial", self.entry_font_size),
                        height=max(40, int(self.entry_font_size * 2.5))
                    )
                elif isinstance(widget, ctk.CTkButton):
                    widget.configure(
                        font=("Arial", self.button_font_size, "bold"),
                        height=max(45, int(self.button_font_size * 2.8))
                    )
        except Exception as e:
            print(f"Error updating widget fonts: {e}")
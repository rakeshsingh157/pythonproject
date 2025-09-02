import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from database import insert_user

class ResponsiveSignup:
    def __init__(self):
        # Main Window setup
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("MarkIt - Create Account")

        # Get screen dimensions for responsive sizing
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Set responsive window size (85% of screen size, minimum 1000x700)
        window_width = max(1000, int(screen_width * 0.85))
        window_height = max(700, int(screen_height * 0.85))

        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(900, 600)  # Minimum window size

        # Make window resizable
        self.root.resizable(True, True)

        # Configure grid weights for responsiveness
        self.root.grid_columnconfigure(0, weight=2)  # Background takes more space
        self.root.grid_columnconfigure(1, weight=1)  # Form takes less space
        self.root.grid_rowconfigure(0, weight=1)

        # Calculate responsive font sizes based on window size
        self.calculate_font_sizes(window_width, window_height)

        # Bind resize event
        self.root.bind("<Configure>", self.on_window_resize)

        # Initialize UI components
        self.create_background()
        self.create_form()

    def calculate_font_sizes(self, width, height):
        """Calculate responsive font sizes based on window dimensions"""
        base_size = min(width, height)
        self.title_font_size = max(24, int(base_size * 0.04))
        self.logo_font_size = max(20, int(base_size * 0.025))
        self.label_font_size = max(12, int(base_size * 0.015))
        self.entry_font_size = max(12, int(base_size * 0.014))
        self.button_font_size = max(14, int(base_size * 0.018))

    def create_account(self):
        """Function when Create button is clicked"""
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        password = self.password_entry.get()
        username = self.username_entry.get()

        if not email or not phone or not password or not username:
            messagebox.showerror("Error", "All fields are required!")
        elif not phone.isdigit() or len(phone) != 10:
            messagebox.showerror("Error", "Phone number must be exactly 10 digits and contain only numbers.")
        else:
            # Call the backend function to insert the user
            if insert_user(username, email, phone, password):
                messagebox.showinfo("Success", f"Account created for {email}")
            else:
                messagebox.showerror("Error", "Failed to create account. Please try again.")

    def create_background(self):
        """Create white background with image"""
        # Left side with pure white background
        self.bg_frame = ctk.CTkFrame(self.root, fg_color="white", corner_radius=0)
        self.bg_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Create inner container for image positioning on white background
        self.bg_container = ctk.CTkFrame(self.bg_frame, fg_color="white")
        self.bg_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Try to load background image
        try:
            if os.path.exists("logpage.png"):
                self.load_background_image()
            else:
                # Just white background if no image
                pass
        except Exception as e:
            print(f"Error loading background image: {e}")
            # Just white background on error
            pass

    def load_background_image(self):
        """Load and display background image on white background"""
        try:
            self.root.update_idletasks()
            bg_width = max(600, self.root.winfo_width() // 2)
            bg_height = self.root.winfo_height()

            # Load original image
            original_image = Image.open("logpage.png")
            original_width, original_height = original_image.size

            # Maintain aspect ratio
            ratio = min(bg_width / original_width, bg_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)

            resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(resized_image)

            if hasattr(self, 'bg_label'):
                self.bg_label.destroy()

            # Place image in center with left margin 40px
            self.bg_label = ctk.CTkLabel(self.bg_container, image=self.bg_photo, text="")
            self.bg_label.pack(padx=(200, 0), pady=0, expand=True)

        except Exception as e:
            print(f"Error loading background image: {e}")

    def create_form(self):
        """Create responsive form on the right side"""
        # Right side for form
        self.form_frame = ctk.CTkFrame(self.root, fg_color="white", corner_radius=0)
        self.form_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=0)


        # Configure form grid
        self.form_frame.grid_columnconfigure(0, weight=0)
        for i in range(10):  # Configure rows for form elements
            self.form_frame.grid_rowconfigure(i, weight=1)

        # Logo / App Name
        logo_label = ctk.CTkLabel(
            self.form_frame,
            text="MarkIt",
            font=("Arial Black", self.logo_font_size),
            text_color="#3366ff"
        )
        logo_label.grid(row=0, column=0, pady=(30, 10), sticky="e", padx=(0, 50))

        # Title
        title_label = ctk.CTkLabel(
            self.form_frame,
            text="Create a new account",
            font=("Arial", self.title_font_size, "bold"),
            text_color="#333333"
        )
        title_label.grid(row=1, column=0, pady=(10, 30), sticky="w", padx=(50, 50))

        # Create form fields
        self.create_form_fields()

    def create_form_fields(self):
        """Create responsive form fields"""
        # Username field
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

        # Email field
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

        # Phone field
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

        # Password field
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

        # Create Button
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

    def on_window_resize(self, event):
        """Handle window resize events"""
        if event.widget == self.root:
            # Recalculate font sizes based on new window size
            new_width = self.root.winfo_width()
            new_height = self.root.winfo_height()
            self.calculate_font_sizes(new_width, new_height)

            # Update font sizes in existing widgets
            self.update_widget_fonts()

    def update_widget_fonts(self):
        """Update font sizes of existing widgets after window resize"""
        try:
            # Update all widgets in the form frame
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

    def run(self):
        """Start the application"""
        self.root.mainloop()

# Create and run the application
if __name__ == "__main__":
    app = ResponsiveSignup()
    app.run()
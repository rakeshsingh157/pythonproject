import tkinter as tk
from tkinter import messagebox
import datetime
from datetime import date, timedelta
import calendar
import mysql.connector
import customtkinter as ctk

# Set a default appearance mode to Light
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My Events")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)

        # Configure the window
        self.root.configure(fg_color=("#f8f9fa", "#1a1a1a"))

        # --- Cool Icon text symbols with colors ---
        self.check_icon = "✓"
        self.delete_icon = "✕"
        self.dark_mode_icon = "🌙"
        self.light_mode_icon = "☀️"
        self.today_icon = "📅"
        self.prev_icon = "◀"
        self.next_icon = "▶"
        self.search_icon = "🔍"
        self.ai_chat_icon = "🤖"

        # Blue shade colors only
        self.icon_colors = {
            "check": "#4FC3F7",      # Light blue
            "delete": "#1976D2",     # Medium blue
            "nav": "#42A5F5",        # Sky blue
            "today": "#000000",      # Primary blue
            "search": "#64B5F6",     # Soft blue
            "ai_chat": "#3F51B5",    # Indigo blue
            "today_selected": "#008CFF",     # Very light blue for today
            "manual_selected": "#B6DCFC"     # Light blue for manual selection
        }

        # --- Database Connection and Setup (MySQL) ---
        try:
            self.conn = mysql.connector.connect(
                host="photostore.ct0go6um6tj0.ap-south-1.rds.amazonaws.com",
                user="admin",
                password="DBpicshot",
                database="eventsreminder"
            )
            self.cursor = self.conn.cursor()
            self.create_table()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not connect to MySQL database.\nError: {err}")
            self.root.destroy()
            return

        # --- Variables to hold form data and state ---
        self.event_title_var = ctk.StringVar()
        self.event_desc_var = ctk.StringVar()
        self.event_time_var = ctk.StringVar(value="00:00")
        self.event_date_var = ctk.StringVar(value=datetime.date.today().strftime("%d %b, %Y"))
        self.reminder_var = ctk.StringVar(value="No Reminder")
        self.search_var = ctk.StringVar()
        self.current_date = datetime.date.today()
        self.month_label_var = ctk.StringVar()

        self.selected_date_canvas_item = None
        self.calendar_widgets = {}
        self.is_today_selected = False

        self.create_main_frames()
        self.create_left_panel()
        self.create_right_panel()
        
        self.draw_calendar(self.current_date)
        self.refresh_event_list()
        


    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                date VARCHAR(255) NOT NULL,
                time VARCHAR(50),
                done BOOLEAN NOT NULL,
                reminder_setting VARCHAR(50)
            )
        """)
        self.conn.commit()

    def create_main_frames(self):
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=24, pady=24)
        
        self.main_frame.grid_columnconfigure(0, weight=0, minsize=400)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.left_panel = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=("white", "#1e1e1e"), border_width=1, border_color=("#E5E7EB", "#2e2e2e"))
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 24))
        
        self.right_panel = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=("white", "#1e1e1e"), border_width=1, border_color=("#E5E7EB", "#2e2e2e"))
        self.right_panel.grid(row=0, column=1, sticky="nsew")

    def create_left_panel(self):
        # Calendar header with navigation
        calendar_header_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        calendar_header_frame.pack(fill="x", pady=(16, 12), padx=16)

        # Month and year label
        self.month_label = ctk.CTkLabel(calendar_header_frame, textvariable=self.month_label_var,
                                       font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"))
        self.month_label.pack(side="left")

        # Navigation buttons
        nav_frame = ctk.CTkFrame(calendar_header_frame, fg_color="transparent")
        nav_frame.pack(side="left")
        
        ctk.CTkButton(nav_frame, text=self.prev_icon, width=35, height=35,
                     command=self.prev_month, fg_color="transparent",
                     hover_color=("#E5E7EB", "#2e2e2e"), text_color=(self.icon_colors["nav"], self.icon_colors["nav"]),
                     font=ctk.CTkFont(size=18)).pack(side="left", padx=(0, 5))
        ctk.CTkButton(nav_frame, text=self.next_icon, width=35, height=35,
                     command=self.next_month, fg_color="transparent",
                     hover_color=("#E5E7EB", "#2e2e2e"), text_color=(self.icon_colors["nav"], self.icon_colors["nav"]),
                     font=ctk.CTkFont(size=18)).pack(side="left")

        # Right side buttons
        right_buttons_frame = ctk.CTkFrame(calendar_header_frame, fg_color="transparent")
        right_buttons_frame.pack(side="right")

        self.today_button = ctk.CTkButton(right_buttons_frame, text=self.today_icon, width=35, height=35,
                                         command=self.go_to_today, fg_color="transparent",
                                         hover_color="#E5E7EB", text_color=self.icon_colors["today"],
                                         font=ctk.CTkFont(size=18))
        self.today_button.pack(side="right")

        # Calendar grid
        self.calendar_grid_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.calendar_grid_frame.pack(pady=(0, 16), padx=16)

        # New event form
        new_event_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        new_event_frame.pack(fill="x", pady=(16, 16), padx=16)

        ctk.CTkLabel(new_event_frame, text="New Event", font=ctk.CTkFont(family="Helvetica", size=16, weight="bold")).pack(anchor="w", pady=(0, 12))

        self.title_entry = ctk.CTkEntry(new_event_frame,
                                       placeholder_text="✨ What's the event? (e.g., Team Meeting)",
                                       corner_radius=12, border_width=1, fg_color="white",
                                       border_color="#E5E7EB", placeholder_text_color="#9CA3AF")
        self.title_entry.pack(fill="x", pady=8)
        self.title_entry.bind("<Return>", lambda e: self.create_event())

        self.desc_entry = ctk.CTkEntry(new_event_frame,
                                      placeholder_text="📝 Add some details... (e.g., Conference Room A)",
                                      corner_radius=12, border_width=1, fg_color="white",
                                      border_color="#E5E7EB", placeholder_text_color="#9CA3AF")
        self.desc_entry.pack(fill="x", pady=8)
        self.desc_entry.bind("<Return>", lambda e: self.create_event())

        time_date_frame = ctk.CTkFrame(new_event_frame, fg_color="transparent")
        time_date_frame.pack(fill="x", pady=8)

        self.time_entry = ctk.CTkEntry(time_date_frame,
                                     placeholder_text="⏰ Time (e.g., 14:30, 2:30 PM)",
                                     corner_radius=8, border_width=1, fg_color="white",
                                     border_color="#E5E7EB", placeholder_text_color="#9CA3AF")
        self.time_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.date_entry = ctk.CTkEntry(time_date_frame, textvariable=self.event_date_var, state='readonly',
                                     corner_radius=8, border_width=1, fg_color="#f9fafb", border_color="#E5E7EB")
        self.date_entry.pack(side="left", fill="x", expand=True)

        reminder_values = ["No Reminder", "15 minutes before", "30 minutes before", "1 hour before", "1 day before"]
        self.reminder_combo = ctk.CTkComboBox(new_event_frame, variable=self.reminder_var, values=reminder_values,
                                            corner_radius=8, border_width=1, fg_color="white", border_color="#E5E7EB",
                                            button_color="#3B82F6", button_hover_color="#2563EB")
        self.reminder_combo.pack(fill="x", pady=8)
        self.reminder_combo.set("No Reminder")

        ctk.CTkButton(new_event_frame, text="Create Event", corner_radius=8, height=40,
                     font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"), 
                     command=self.create_event, fg_color=("#3B82F6", "#1d4ed8"), hover_color=("#2563EB", "#1e40af")).pack(fill="x", pady=(8, 0))

    def create_right_panel(self):
        header_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        header_frame.pack(fill="x", pady=16, padx=16)
        
        header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header_frame, text="All Events", font=ctk.CTkFont(family="Helvetica", size=18, weight="bold")).grid(row=0, column=0, sticky="w")

        self.search_entry = ctk.CTkEntry(header_frame,
                                        placeholder_text="🔍 Search your events... (e.g., meeting, birthday)",
                                        corner_radius=20, border_width=1, fg_color="white",
                                        border_color="#E5E7EB", placeholder_text_color="#9CA3AF")
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(10, 5))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_event_list())

        # AI Chat button next to search
        self.ai_chat_button = ctk.CTkButton(header_frame, text=self.ai_chat_icon, width=35, height=35,
                                           command=self.open_ai_chat, fg_color="transparent",
                                           hover_color="#E5E7EB", text_color=self.icon_colors["ai_chat"],
                                           font=ctk.CTkFont(size=18))
        self.ai_chat_button.grid(row=0, column=2, padx=(0, 0))
        
        event_list_container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        event_list_container.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.event_list_canvas = ctk.CTkScrollableFrame(event_list_container, fg_color="transparent")
        self.event_list_canvas.pack(fill="both", expand=True)


    def go_to_today(self):
        self.current_date = datetime.date.today()
        self.draw_calendar(self.current_date)
        self.event_date_var.set(self.current_date.strftime("%d %b, %Y"))
        self.refresh_event_list()

    def draw_calendar(self, date_to_display):
        self.month_label_var.set(date_to_display.strftime("%B %Y"))
        
        for widget in self.calendar_grid_frame.winfo_children():
            widget.destroy()

        self.calendar_widgets = {}
        week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        for i, day in enumerate(week_days):
            ctk.CTkLabel(self.calendar_grid_frame, text=day, font=ctk.CTkFont(family="Helvetica", size=10, weight="bold"), 
                        text_color=("#6B7280", "#9CA3AF")).grid(row=0, column=i, padx=4, pady=4)
        
        first_day_of_month = date_to_display.replace(day=1)
        first_weekday = first_day_of_month.weekday()
        
        dates_to_display = []
        start_date = first_day_of_month - timedelta(days=first_weekday)
        for i in range(42):
            day = start_date + timedelta(days=i)
            dates_to_display.append(day)

        row = 1
        col = 0
        for day in dates_to_display:
            # Light theme only
            bg_color = "white"
            date_canvas = tk.Canvas(self.calendar_grid_frame, width=36, height=36,
                                   bg=bg_color, highlightthickness=0)
            date_canvas.grid(row=row, column=col, padx=2, pady=2)
            
            self.calendar_widgets[day] = {
                'canvas': date_canvas, 'oval_id': None, 'text_id': None, 'underline_id': None
            }
            
            # Light theme colors only
            oval_color = bg_color
            text_color = "#1F2937"
            if day.month != date_to_display.month:
                text_color = "#B0B0B0"

            oval_id = date_canvas.create_oval(2, 2, 34, 34, outline=oval_color, fill=oval_color)
            text_id = date_canvas.create_text(18, 18, text=str(day.day), font=("Helvetica", 10), fill=text_color)

            self.calendar_widgets[day]['oval_id'] = oval_id
            self.calendar_widgets[day]['text_id'] = text_id

            if day == date.today():
                today_color = self.icon_colors["today_selected"]  # Cool red for today
                date_canvas.itemconfig(oval_id, fill=today_color, outline=today_color)
                date_canvas.itemconfig(text_id, fill="white")
                self.selected_date_canvas_item = date_canvas
                self.is_today_selected = True
            else:
                self.is_today_selected = False
            
            date_canvas.bind("<Enter>", lambda e, d=day: self.on_date_hover(e, d, True))
            date_canvas.bind("<Leave>", lambda e, d=day: self.on_date_hover(e, d, False))
            date_canvas.bind("<Button-1>", lambda e, d=day: self.select_date(e, d))
            
            col += 1
            if col == 7:
                col = 0
                row += 1

        self.refresh_event_list()

    def on_date_hover(self, event, date_obj, is_enter):
        if date_obj not in self.calendar_widgets:
            return
            
        canvas = self.calendar_widgets[date_obj]['canvas']
        oval_id = self.calendar_widgets[date_obj]['oval_id']
        text_id = self.calendar_widgets[date_obj]['text_id']
        
        # Light theme colors only
        hover_color = "#E5E7EB"
        normal_color = "white"

        if is_enter:
            if canvas != self.selected_date_canvas_item and not (date_obj == date.today()):
                canvas.itemconfig(oval_id, fill=hover_color, outline=hover_color)
        else:
            if canvas != self.selected_date_canvas_item and not (date_obj == date.today()):
                canvas.itemconfig(oval_id, fill=normal_color, outline=normal_color)
                # Light theme text colors
                if date_obj.month == self.current_date.month:
                    text_color = "#1F2937"
                else:
                    text_color = "#B0B0B0"
                canvas.itemconfig(text_id, fill=text_color)

    def next_month(self):
        current_year = self.current_date.year
        current_month = self.current_date.month
        
        if current_month == 12:
            next_month = 1
            next_year = current_year + 1
        else:
            next_month = current_month + 1
            next_year = current_year
        
        self.current_date = datetime.date(next_year, next_month, 1)
        self.draw_calendar(self.current_date)

    def prev_month(self):
        current_year = self.current_date.year
        current_month = self.current_date.month
        
        if current_month == 1:
            prev_month = 12
            prev_year = current_year - 1
        else:
            prev_month = current_month - 1
            prev_year = current_year
        
        self.current_date = datetime.date(prev_year, prev_month, 1)
        self.draw_calendar(self.current_date)

    def select_date(self, event, selected_date):
        # Light theme colors only
        normal_color = "white"

        if self.selected_date_canvas_item:
            canvas = self.selected_date_canvas_item
            prev_date = next((k for k, v in self.calendar_widgets.items() if v['canvas'] == canvas), None)
            if prev_date:
                date_data = self.calendar_widgets[prev_date]
                if prev_date == date.today():
                    # Keep today in its special color
                    canvas.itemconfig(date_data['oval_id'], fill=self.icon_colors["today_selected"], outline=self.icon_colors["today_selected"])
                    canvas.itemconfig(date_data['text_id'], fill="white")
                else:
                    # Reset to normal color
                    canvas.itemconfig(date_data['oval_id'], fill=normal_color, outline=normal_color)
                    text_color = "#1F2937"
                    if prev_date.month != self.current_date.month:
                        text_color = "#B0B0B0"
                    canvas.itemconfig(date_data['text_id'], fill=text_color)

        current_canvas = self.calendar_widgets[selected_date]['canvas']
        date_data = self.calendar_widgets[selected_date]

        # Use different colors for today vs manual selection
        if selected_date == date.today():
            selection_color = self.icon_colors["today_selected"]  # Cool red for today
        else:
            selection_color = self.icon_colors["manual_selected"]  # Cool green for manual selection

        current_canvas.itemconfig(date_data['oval_id'], fill=selection_color, outline=selection_color)
        current_canvas.itemconfig(date_data['text_id'], fill="white")

        self.selected_date_canvas_item = current_canvas
        self.current_date = selected_date

        # Update the date entry field with the selected date
        formatted_date = selected_date.strftime("%d %b, %Y")
        self.event_date_var.set(formatted_date)
        
        selected_date_str = selected_date.strftime("%d %b, %Y")
        self.event_date_var.set(selected_date_str)
        self.refresh_event_list()

    def refresh_event_list(self):
        for widget in self.event_list_canvas.winfo_children():
            widget.destroy()

        search_text = self.search_entry.get().lower().strip()

        self.cursor.execute("SELECT id, date, time, title, description, done, reminder_setting FROM events ORDER BY STR_TO_DATE(date, '%d %b, %Y') ASC, time ASC")
        all_events = self.cursor.fetchall()
        
        filtered_events = []
        for event_data in all_events:
            event_id, date_str, time_str, title_str, desc_str, done_int, reminder_str = event_data
            
            if not search_text:
                filtered_events.append(event_data)
            elif search_text in title_str.lower() or search_text in desc_str.lower() or search_text in date_str.lower():
                filtered_events.append(event_data)
        
        if not filtered_events:
            no_events_frame = ctk.CTkFrame(self.event_list_canvas, fg_color="transparent")
            no_events_frame.pack(fill="x", pady=20)
            ctk.CTkLabel(no_events_frame, text="No events found", 
                         font=ctk.CTkFont(family="Helvetica", size=14), 
                         text_color=("#9CA3AF", "#6B7280")).pack()
        else:
            for event_data in filtered_events:
                event_id, date_str, time_str, title_str, desc_str, done_int, reminder_str = event_data
                self.add_event_to_list(
                    event_id=event_id,
                    event_data={
                        "date": date_str,
                        "time": time_str,
                        "title": title_str,
                        "description": desc_str,
                        "done": bool(done_int),
                        "reminder": reminder_str
                    }
                )
        self.update_calendar_highlights()

    def update_calendar_highlights(self):
        self.cursor.execute("SELECT date, done FROM events")
        all_event_dates = self.cursor.fetchall()
        
        event_dates_in_month = set()
        done_dates_in_month = set()
        for date_str, done_status in all_event_dates:
            try:
                event_date_obj = datetime.datetime.strptime(date_str, "%d %b, %Y").date()
                if event_date_obj.month == self.current_date.month and event_date_obj.year == self.current_date.year:
                    event_dates_in_month.add(event_date_obj.day)
                    if done_status:
                        done_dates_in_month.add(event_date_obj.day)
            except (ValueError, KeyError):
                continue
        
        for date_obj, widgets in self.calendar_widgets.items():
            canvas = widgets['canvas']
            text_id = widgets['text_id']
            underline_id = widgets['underline_id']
            
            if underline_id:
                canvas.delete(underline_id)
                widgets['underline_id'] = None

            if date_obj.day in event_dates_in_month:
                bbox = canvas.bbox(text_id)
                if bbox:
                    x1, y1, x2, y2 = bbox
                    line_color = "#00AEFF" if date_obj.day in done_dates_in_month else "#C8CBCD"
                    new_underline_id = canvas.create_line(x1, y2 + 2, x2, y2 + 2, fill=line_color, width=2)
                    widgets['underline_id'] = new_underline_id

    def add_event_to_list(self, event_id, event_data):
        event_wrapper_frame = ctk.CTkFrame(self.event_list_canvas, fg_color="transparent")
        event_wrapper_frame.pack(fill="x", padx=5, pady=5)

        event_card = ctk.CTkFrame(event_wrapper_frame, fg_color=("white", "#1e1e1e"), corner_radius=8, 
                                border_width=1, border_color=("#E5E7EB", "#2e2e2e"))
        event_card.pack(fill="x", padx=0, pady=0)

        # Main content frame
        content_frame = ctk.CTkFrame(event_card, fg_color="transparent")
        content_frame.pack(fill="x", padx=12, pady=12)

        # Date and time column
        dt_col = ctk.CTkFrame(content_frame, fg_color="transparent", width=80)
        dt_col.pack(side="left", fill="y")
        
        ctk.CTkLabel(dt_col, text=event_data["date"], font=ctk.CTkFont(family="Helvetica", size=11, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(dt_col, text=event_data["time"], font=ctk.CTkFont(family="Helvetica", size=9), 
                    text_color=("#3B82F6", "#60a5fa")).pack(anchor="w", pady=(2, 0))
        
        # Info column
        info_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_col.pack(side="left", fill="x", expand=True, padx=(12, 0))

        title_color = ("#1F2937", "#F9FAFB") if not event_data["done"] else ("#9CA3AF", "#6B7280")
        title_label = ctk.CTkLabel(info_col, text=event_data["title"], 
                                  font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"), 
                                  text_color=title_color, anchor="w")
        title_label.pack(anchor="w", fill="x", pady=(0, 4))

        desc_color = ("#6B7280", "#9CA3AF") if not event_data["done"] else ("#9CA3AF", "#6B7280")
        desc_label = ctk.CTkLabel(info_col, text=event_data["description"], 
                                 font=ctk.CTkFont(family="Helvetica", size=12), 
                                 text_color=desc_color, anchor="w")
        desc_label.pack(anchor="w", fill="x")
        
        # Action buttons column
        action_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        action_col.pack(side="right", padx=(10, 0))

        check_color = "#10B981" if not event_data["done"] else "#9CA3AF"
        check_hover = "#D1F2EB" if not event_data["done"] else "#E5E7EB"
        check_button = ctk.CTkButton(action_col, text=self.check_icon, width=35, height=35,
                                    command=lambda event_id=event_id: self.mark_event_done(event_id),
                                    fg_color="transparent", hover_color=(check_hover, "#2e2e2e"),
                                    text_color=(self.icon_colors["check"], self.icon_colors["check"]),
                                    font=ctk.CTkFont(size=16))
        check_button.pack(side="left", padx=(0, 5))

        delete_button = ctk.CTkButton(action_col, text=self.delete_icon, width=35, height=35,
                                     command=lambda event_id=event_id: self.delete_event(event_id),
                                     fg_color="transparent", hover_color=("#FFE5E5", "#2e2e2e"),
                                     text_color=(self.icon_colors["delete"], self.icon_colors["delete"]),
                                     font=ctk.CTkFont(size=16))
        delete_button.pack(side="left")

        if event_data["done"]:
            # Add strikethrough effect for completed events
            title_label.configure(font=ctk.CTkFont(family="Helvetica", size=14, weight="bold", overstrike=True))
            desc_label.configure(font=ctk.CTkFont(family="Helvetica", size=12, overstrike=True))

    def create_event(self):
        title = self.title_entry.get().strip()
        description = self.desc_entry.get().strip()
        time = self.time_entry.get().strip()
        date_str = self.event_date_var.get()
        reminder_setting = self.reminder_var.get()

        if not title:
            messagebox.showwarning("Incomplete Fields", "Please enter a title for your event.")
            self.title_entry.focus()
            return

        if not time:
            messagebox.showwarning("Incomplete Fields", "Please enter a time for your event.")
            self.time_entry.focus()
            return

        if not date_str:
            messagebox.showwarning("Incomplete Fields", "Please select a date from the calendar.")
            return

        sql = "INSERT INTO events (title, description, date, time, done, reminder_setting) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (title, description, date_str, time, False, reminder_setting)

        try:
            self.cursor.execute(sql, val)
            self.conn.commit()

            self.refresh_event_list()

            # Clear the form
            self.title_entry.delete(0, 'end')
            self.desc_entry.delete(0, 'end')
            self.time_entry.delete(0, 'end')
            self.reminder_var.set("No Reminder")
            self.title_entry.focus()

            messagebox.showinfo("Success", "Event created successfully!")

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to create event: {err}")

    def open_ai_chat(self):
        """Open AI assistant application"""
        try:
            import subprocess
            import os

            # Get the directory where the current script is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            ai_assistant_path = os.path.join(current_dir, "ai_assistant.py")

            # Check if ai_assistant.py exists
            if os.path.exists(ai_assistant_path):
                # Launch ai_assistant.py in a new process
                subprocess.Popen(["python", ai_assistant_path])
            else:
                messagebox.showerror("File Not Found", f"ai_assistant.py not found in:\n{current_dir}\n\nPlease make sure the AI assistant file exists in the same directory.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open AI assistant:\n{str(e)}")

    def mark_event_done(self, event_id):
        self.cursor.execute("SELECT done FROM events WHERE id = %s", (event_id,))
        current_status = self.cursor.fetchone()[0]
        new_status = not current_status
        
        sql = "UPDATE events SET done = %s WHERE id = %s"
        val = (new_status, event_id)
        self.cursor.execute(sql, val)
        self.conn.commit()
        
        self.refresh_event_list()

    def delete_event(self, event_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this event?"):
            sql = "DELETE FROM events WHERE id = %s"
            self.cursor.execute(sql, (event_id,))
            self.conn.commit()
            self.refresh_event_list()

    def on_closing(self):
        if hasattr(self, 'conn') and self.conn and self.conn.is_connected():
            self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = CalendarApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
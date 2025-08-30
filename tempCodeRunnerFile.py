import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from datetime import date, timedelta
import calendar
import mysql.connector

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My Events")
        self.root.geometry("1000x600")
        self.root.configure(bg="white")

        # --- Database Connection and Setup (MySQL) ---
        try:
            # Replace these with your MySQL Workbench credentials
            self.conn = mysql.connector.connect(
                host="photostore.ct0go6um6tj0.ap-south-1.rds.amazonaws.com",
                user="admin",
                password="DBpicshot", 
                database="eventsreminder"
            )
            self.cursor = self.conn.cursor()
            self.create_table()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            messagebox.showerror("Database Error", f"Could not connect to MySQL database.\nError: {err}")
            self.root.destroy()
            return

        # --- Variables to hold form data and state ---
        self.event_title_var = tk.StringVar(value="Event Title")
        self.event_desc_var = tk.StringVar(value="Event Description")
        self.event_time_var = tk.StringVar(value="00:00")
        self.event_date_var = tk.StringVar(value=datetime.date.today().strftime("%d %b, %Y"))
        self.reminder_var = tk.StringVar(value="No Reminder")
        self.search_var = tk.StringVar()
        self.current_date = datetime.date.today()
        self.month_label_var = tk.StringVar()

        # State for calendar selection and date underlining
        self.selected_date_canvas_item = None
        self.calendar_widgets = {}

        self.setup_styles()
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

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TEntry", fieldbackground="white", bordercolor="#cccccc", relief="solid", borderwidth=1, padding=(10, 5))
        style.configure("TCombobox", fieldbackground="white", background="white", arrowcolor="#333333", bordercolor="#cccccc", relief="solid", borderwidth=1, padding=(10, 0))
        style.configure("Blue.TButton", background="#3366ff", foreground="white", borderwidth=0, font=("Arial", 12, "bold"), relief="flat", padding=(10, 8))
        style.map("Blue.TButton", background=[('active', '#5588ff')])

    def create_main_frames(self):
        self.main_frame = tk.Frame(self.root, bg="#f5f5f5")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.main_frame.grid_columnconfigure(0, weight=0, minsize=400)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.left_panel = tk.Frame(self.main_frame, bg="white", padx=20, pady=20)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.right_panel = tk.Frame(self.main_frame, bg="#e0eeef", padx=20, pady=20)
        self.right_panel.grid(row=0, column=1, sticky="nsew")

    def create_left_panel(self):
        calendar_header_frame = tk.Frame(self.left_panel, bg="white")
        calendar_header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.month_label = tk.Label(calendar_header_frame, textvariable=self.month_label_var, font=("Arial", 16, "bold"), bg="white", fg="#333333")
        self.month_label.pack(side=tk.LEFT)

        def create_circular_button(parent, text, command):
            canvas = tk.Canvas(parent, width=28, height=28, bg="white", highlightthickness=0)
            canvas.create_oval(2, 2, 26, 26, fill="#e0e0e0", outline="#e0e0e0")
            canvas.create_text(14, 14, text=text, font=("Arial", 10, "bold"), fill="#808080")
            canvas.bind("<Button-1>", lambda e: command())
            return canvas

        next_button = create_circular_button(calendar_header_frame, ">", self.next_month)
        next_button.pack(side=tk.RIGHT)
        
        prev_button = create_circular_button(calendar_header_frame, "<", self.prev_month)
        prev_button.pack(side=tk.RIGHT, padx=(0, 5))

        self.calendar_grid_frame = tk.Frame(self.left_panel, bg="white")
        self.calendar_grid_frame.pack(pady=(0, 10))

        new_event_frame = tk.Frame(self.left_panel, bg="white")
        new_event_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(new_event_frame, text="New Event", font=("Arial", 14, "bold"), bg="white", fg="#333333").pack(anchor="w", pady=(5, 5))
        
        self.title_entry = ttk.Entry(new_event_frame, textvariable=self.event_title_var, font=("Arial", 10))
        self.title_entry.pack(fill=tk.X, pady=5)
        self.desc_entry = ttk.Entry(new_event_frame, textvariable=self.event_desc_var, font=("Arial", 10))
        self.desc_entry.pack(fill=tk.X, pady=5)

        time_date_frame = tk.Frame(new_event_frame, bg="white")
        time_date_frame.pack(fill=tk.X, pady=5)
        
        times = [f"{h:02d}:00" for h in range(24)]
        self.time_combo = ttk.Combobox(time_date_frame, textvariable=self.event_time_var, values=times, state="readonly", font=("Arial", 10))
        self.time_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.time_combo.set("00:00")
        
        self.date_combo = ttk.Combobox(time_date_frame, textvariable=self.event_date_var, values=[self.event_date_var.get()], state="readonly", font=("Arial", 10))
        self.date_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        reminder_values = ["No Reminder", "15 minutes before", "30 minutes before", "1 hour before", "1 day before"]
        self.reminder_combo = ttk.Combobox(new_event_frame, textvariable=self.reminder_var, values=reminder_values, state="readonly", font=("Arial", 10))
        self.reminder_combo.pack(fill=tk.X, pady=5)
        self.reminder_combo.set("No Reminder")
        
        ttk.Button(new_event_frame, text="Create", style="Blue.TButton", command=self.create_event).pack(fill=tk.X, pady=(10, 0))

    def create_right_panel(self):
        header_frame = tk.Frame(self.right_panel, bg="#e0eeef")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        header_frame.grid_columnconfigure(0, weight=0)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=0)

        tk.Label(header_frame, text="My Events", font=("Arial", 16, "bold"), bg="#e0eeef", fg="#333333").grid(row=0, column=0, sticky="w")
        
        search_bar_frame = tk.Frame(header_frame, bg="#e0e0e0", highlightbackground="#cccccc", highlightthickness=1, bd=0)
        search_bar_frame.grid(row=0, column=1, sticky="ew", padx=(10, 10))
        
        self.search_entry = ttk.Entry(search_bar_frame, textvariable=self.search_var, font=("Arial", 10), style="TEntry")
        self.search_entry.pack(fill=tk.X, expand=True, padx=2, pady=2)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_event_list())

        tk.Label(header_frame, text="💬", font=("Arial", 16), bg="#e0eeef", fg="#808080").grid(row=0, column=2, sticky="e")
        
        event_list_container = tk.Frame(self.right_panel, bg="white", bd=0, highlightbackground="#e0e0e0", highlightthickness=1)
        event_list_container.pack(fill=tk.BOTH, expand=True)

        self.event_list_canvas = tk.Canvas(event_list_container, bg="white", highlightthickness=0)
        self.event_list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.event_list_scrollbar = ttk.Scrollbar(event_list_container, orient="vertical", command=self.event_list_canvas.yview)
        self.event_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.event_list_frame = tk.Frame(self.event_list_canvas, bg="white")
        
        self.event_list_frame_id = self.event_list_canvas.create_window((0, 0), window=self.event_list_frame, anchor="nw")
        self.event_list_canvas.bind('<Configure>', self._on_canvas_resize)

        self.event_list_canvas.configure(yscrollcommand=self.event_list_scrollbar.set)
        self.event_list_frame.bind("<Configure>", lambda e: self.event_list_canvas.configure(scrollregion=self.event_list_canvas.bbox("all")))
        self.event_list_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_canvas_resize(self, event):
        canvas_width = event.width
        self.event_list_canvas.itemconfig(self.event_list_frame_id, width=canvas_width)

    def _on_mousewheel(self, event):
        self.event_list_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def draw_calendar(self, date_to_display):
        self.month_label_var.set(date_to_display.strftime("%B %Y"))
        
        for widget in self.calendar_grid_frame.winfo_children():
            widget.destroy()

        self.calendar_widgets = {}
        week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        for i, day in enumerate(week_days):
            tk.Label(self.calendar_grid_frame, text=day, font=("Arial", 10, "bold"), bg="white", fg="#333333").grid(row=0, column=i, padx=5, pady=5)
        
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
            date_canvas = tk.Canvas(self.calendar_grid_frame, width=30, height=30, bg="white", highlightthickness=0)
            date_canvas.grid(row=row, column=col, padx=2, pady=2)
            
            self.calendar_widgets[day] = {
                'canvas': date_canvas, 'oval_id': None, 'text_id': None, 'underline_id': None
            }
            
            oval_id = date_canvas.create_oval(2, 2, 28, 28, outline="white", fill="white")
            text_color = "#333333" if day.month == date_to_display.month else "#808080"
            text_id = date_canvas.create_text(15, 15, text=str(day.day), font=("Arial", 10), fill=text_color)
            
            self.calendar_widgets[day]['oval_id'] = oval_id
            self.calendar_widgets[day]['text_id'] = text_id
            
            if day == self.current_date:
                date_canvas.itemconfig(oval_id, fill="#3366ff", outline="#3366ff")
                date_canvas.itemconfig(text_id, fill="white")
                self.selected_date_canvas_item = date_canvas
            
            date_canvas.bind("<Button-1>", lambda e, d=day: self.select_date(e, d))
            
            col += 1
            if col == 7:
                col = 0
                row += 1

        self.refresh_event_list()

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
        if self.selected_date_canvas_item:
            canvas = self.selected_date_canvas_item
            prev_date = next((k for k, v in self.calendar_widgets.items() if v['canvas'] == canvas), None)
            if prev_date:
                date_data = self.calendar_widgets[prev_date]
                canvas.itemconfig(date_data['oval_id'], fill="white", outline="white")
                text_color = "#333333" if prev_date.month == self.current_date.month else "#808080"
                canvas.itemconfig(date_data['text_id'], fill=text_color)

        current_canvas = event.widget
        date_data = self.calendar_widgets[selected_date]
        current_canvas.itemconfig(date_data['oval_id'], fill="#3366ff", outline="#3366ff")
        current_canvas.itemconfig(date_data['text_id'], fill="white")
        
        self.selected_date_canvas_item = current_canvas
        self.current_date = selected_date
        
        selected_date_str = selected_date.strftime("%d %b, %Y")
        self.event_date_var.set(selected_date_str)

    def refresh_event_list(self):
        visible_event_dates = set()
        done_event_dates = set()
        for widget in self.event_list_frame.winfo_children():
            widget.destroy()

        search_text = self.search_var.get().lower()

        self.cursor.execute("SELECT id, date, time, title, description, done, reminder_setting FROM events")
        all_events = self.cursor.fetchall()
        
        for event_data in all_events:
            event_id, date_str, time_str, title_str, desc_str, done_int, reminder_str = event_data
            
            try:
                event_date_obj = datetime.datetime.strptime(date_str, "%d %b, %Y").date()
            except (ValueError, KeyError):
                event_date_obj = None

            is_in_current_month = event_date_obj and event_date_obj.year == self.current_date.year and event_date_obj.month == self.current_date.month
            
            if is_in_current_month or search_text in title_str.lower() or search_text in desc_str.lower():
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
                if is_in_current_month:
                    visible_event_dates.add(event_date_obj.day)
                    if bool(done_int):
                        done_event_dates.add(event_date_obj.day)

        self.update_calendar_underlines(visible_event_dates, done_event_dates)

    def update_calendar_underlines(self, dates_to_underline, done_dates):
        for date_obj, widgets in self.calendar_widgets.items():
            canvas = widgets['canvas']
            text_id = widgets['text_id']
            underline_id = widgets['underline_id']
            
            is_in_current_month = date_obj.month == self.current_date.month
            
            if is_in_current_month and date_obj.day in done_dates:
                # If there's a completed event, draw a green underline
                bbox = canvas.bbox(text_id)
                if bbox:
                    x1, y1, x2, y2 = bbox
                    line_color = "#28a745"  # Green for done events
                    if underline_id:
                        canvas.coords(underline_id, x1, y2 + 2, x2, y2 + 2)
                        canvas.itemconfig(underline_id, fill=line_color, width=2)
                    else:
                        new_underline_id = canvas.create_line(x1, y2 + 2, x2, y2 + 2, fill=line_color, width=2)
                        widgets['underline_id'] = new_underline_id
            elif is_in_current_month and date_obj.day in dates_to_underline:
                # If there's an upcoming event, draw a black underline
                bbox = canvas.bbox(text_id)
                if bbox:
                    x1, y1, x2, y2 = bbox
                    line_color = "#333333"  # Black for normal events
                    if underline_id:
                        canvas.coords(underline_id, x1, y2 + 2, x2, y2 + 2)
                        canvas.itemconfig(underline_id, fill=line_color, width=2)
                    else:
                        new_underline_id = canvas.create_line(x1, y2 + 2, x2, y2 + 2, fill=line_color, width=2)
                        widgets['underline_id'] = new_underline_id
            else:
                # No events for this date, remove any existing underline
                if underline_id:
                    canvas.delete(underline_id)
                    widgets['underline_id'] = None

    def add_event_to_list(self, event_id, event_data):
        event_wrapper_frame = tk.Frame(self.event_list_frame, bg="white", padx=15)
        event_wrapper_frame.pack(fill=tk.X, pady=(0, 0))

        event_row = tk.Frame(event_wrapper_frame, bg="white")
        event_row.pack(fill=tk.X, padx=0, pady=0)
        
        # Pack action_col first to anchor it to the right
        action_col = tk.Frame(event_row, bg="white")
        action_col.pack(side=tk.RIGHT, padx=(0, 10))

        # Pack dt_col to the left, next to the action_col
        dt_col = tk.Frame(event_row, bg="white")
        dt_col.pack(side=tk.LEFT, padx=(0, 12))
        
        # Finally, pack info_col to the left to fill the remaining space
        info_col = tk.Frame(event_row, bg="white")
        info_col.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(dt_col, text=event_data["date"], font=("Arial", 12, "bold"), bg="white", fg="#333333").pack(anchor="w")
        tk.Label(dt_col, text=event_data["time"], font=("Arial", 10), bg="white", fg="#3366ff").pack(anchor="w")
        
        reminder_label = tk.Label(dt_col, text=f'Reminder: {event_data["reminder"]}', font=("Arial", 8, "italic"), bg="white", fg="#808080")
        reminder_label.pack(anchor="w")

        title_label = tk.Label(info_col, text=event_data["title"], font=("Arial", 12, "bold"), bg="white", fg="#333333", wraplength=400, anchor="w", justify="left")
        title_label.pack(anchor="w")
        desc_label = tk.Label(info_col, text=event_data["description"], font=("Arial", 10), bg="white", fg="#808080", wraplength=400, anchor="w", justify="left")
        desc_label.pack(anchor="w")

        check_canvas = tk.Canvas(action_col, width=32, height=32, bg="white", highlightthickness=0)
        check_canvas.pack(side=tk.LEFT, padx=(0, 10))
        check_canvas.create_oval(2, 2, 30, 30, outline="#3366ff", width=2)
        check_canvas.create_text(16, 16, text="✓", font=("Arial", 14, "bold"), fill="#3366ff")
        check_canvas.bind("<Button-1>", lambda e, event_id=event_id: self.mark_event_done(event_id))

        delete_label = tk.Label(action_col, text="🗑", bg="white", fg="#ff3333", font=("Arial", 12, "bold"), cursor="hand2")
        delete_label.pack(side=tk.LEFT)
        delete_label.bind("<Button-1>", lambda e, event_id=event_id: self.delete_event(event_id))

        if event_data["done"]:
            title_label.config(fg="#28a745")
            desc_label.config(fg="#28a745")
            check_canvas.itemconfig(2, fill="#28a745")

        separator = tk.Frame(event_wrapper_frame, height=1, bg="#e0e0e0")
        separator.pack(fill=tk.X, pady=(0, 0))

    def create_event(self):
        title = self.event_title_var.get()
        description = self.event_desc_var.get()
        time = self.event_time_var.get()
        date_str = self.event_date_var.get()
        reminder_setting = self.reminder_var.get()
        
        if title and description and date_str and time and title != "Event Title":
            sql = "INSERT INTO events (title, description, date, time, done, reminder_setting) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (title, description, date_str, time, False, reminder_setting)
            
            try:
                self.cursor.execute(sql, val)
                self.conn.commit()
                
                self.refresh_event_list()
                
                self.event_title_var.set("Event Title")
                self.event_desc_var.set("Event Description")
                self.reminder_var.set("No Reminder")
            
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Failed to create event: {err}")

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
        sql = "DELETE FROM events WHERE id = %s"
        self.cursor.execute(sql, (event_id,))
        self.conn.commit()
        self.refresh_event_list()
    
    def on_closing(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
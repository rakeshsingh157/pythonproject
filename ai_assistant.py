import customtkinter as ctk
import cohere  # Import the Cohere SDK
import json
import datetime
import uuid
import mysql.connector  # Import MySQL connector

# Set the appearance mode for customtkinter
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# --- Configuration for Cohere API ---
COHERE_API_KEY = "QHw20MxzRN9JU1VQUKdovICaOXPONYz86DXdUiqy"  # Replace with your Cohere API key
co = cohere.ClientV2(COHERE_API_KEY)
COHERE_MODEL = "command-a-03-2025"

# --- Configuration for MySQL Database ---
DB_CONFIG = {
    "host": "photostore.ct0go6um6tj0.ap-south-1.rds.amazonaws.com",
    "user": "admin",
    "password": "DBpicshot",
    "database": "eventsreminder"
}


# --- Helper functions for MySQL database operations ---
def init_db():
    """Initializes the MySQL database and creates the events table if it doesn't exist."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                date VARCHAR(255) NOT NULL,
                time VARCHAR(50),
                done BOOLEAN NOT NULL,
                reminder_setting VARCHAR(50),
                user_id INT
            )
        """)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error initializing database: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


def save_event_to_db(user_id, title, description, date, time, reminder_setting="15 minutes before"):
    """Saves a single event to the database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO events (title, description, date, time, done, reminder_setting, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (title, description, date, time, False, reminder_setting, user_id)
        )
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error saving event to database: {err}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


def get_events_from_db(user_id):
    """Retrieves all events for a given user from the database."""
    events_data = []
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT title, description, date, time, done, reminder_setting FROM events WHERE user_id = %s ORDER BY date, time", (user_id,))
        for row in cursor.fetchall():
            events_data.append({
                "title": row[0],
                "description": row[1],
                "date": row[2],
                "time": row[3],
                "done": row[4],
                "reminder_setting": row[5]
            })
    except mysql.connector.Error as err:
        print(f"Error retrieving events from database: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    return events_data


def get_events_by_date_range(user_id, start_date, end_date):
    """Retrieves events for a given user within a date range."""
    events_data = []
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, description, date, time, done, reminder_setting
            FROM events
            WHERE user_id = %s AND date BETWEEN %s AND %s
            ORDER BY date, time
        """, (user_id, start_date, end_date))
        for row in cursor.fetchall():
            events_data.append({
                "title": row[0],
                "description": row[1],
                "date": row[2],
                "time": row[3],
                "done": row[4],
                "reminder_setting": row[5]
            })
    except mysql.connector.Error as err:
        print(f"Error retrieving events from database: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    return events_data


def search_events(user_id, search_term):
    """Search events by title or description."""
    events_data = []
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        search_pattern = f"%{search_term}%"
        cursor.execute("""
            SELECT title, description, date, time, done, reminder_setting
            FROM events
            WHERE user_id = %s AND (title LIKE %s OR description LIKE %s)
            ORDER BY date, time
        """, (user_id, search_pattern, search_pattern))
        for row in cursor.fetchall():
            events_data.append({
                "title": row[0],
                "description": row[1],
                "date": row[2],
                "time": row[3],
                "done": row[4],
                "reminder_setting": row[5]
            })
    except mysql.connector.Error as err:
        print(f"Error searching events in database: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    return events_data


class ChatApp(ctk.CTk):
    """AI Assistant chat application with Cohere backend and MySQL meeting scheduling."""

    def __init__(self):
        super().__init__()

        # Configure the main window
        self.title("AI Assistant")
        self.geometry("1100x700")
        self.configure(fg_color="#f5f5f5")

        # Generate a unique user ID for this session
        self.user_id = str(uuid.uuid4())
        print(f"Current User ID: {self.user_id}")

        # Initialize the database
        init_db()

        # Chat history
        self.chat_history = []

        # Layout
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.create_sidebar()

        # Main content
        self.main_frame = ctk.CTkFrame(self, fg_color="#f5f5f5", corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Header
        self.create_header(self.main_frame)

        # Chat area
        self.create_chat_area(self.main_frame)

        # Input area
        self.create_input_area(self.main_frame)

        # Preloaded messages
        welcome_msg = ("Hi! I'm your AI Calendar Assistant. I can help you with:\n\n"
                      "• Creating single or multiple events at once\n"
                      "• Finding available time slots\n"
                      "• Analyzing your schedule\n"
                      "• Setting smart reminders (default: 15 minutes)\n"
                      "• Searching through events\n\n"
                      "Examples:\n"
                      "📅 'Schedule meeting tomorrow 2 PM'\n"
                      "📅 'Add doctor appointment Friday 10 AM with 1 hour reminder'\n"
                      "📅 'meeting 6 pm, game 7 pm, match 7 am tomorrow'\n\n"
                      "What would you like to do today?")
        self.add_message("AI Assistant", welcome_msg, is_user=False)
       
        self.after(100, self.scroll_to_bottom)

    def create_sidebar(self):
        sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="White")
        sidebar_frame.grid(row=0, column=0, sticky="nsew")
        sidebar_frame.grid_propagate(False)
        sidebar_frame.grid_columnconfigure(0, weight=1)

        sidebar_title = ctk.CTkLabel(sidebar_frame, text="MarkIt",
                                     font=ctk.CTkFont(size=20, weight="bold"),
                                     text_color="#1a1a1a")
        sidebar_title.grid(row=0, column=0, padx=20, pady=20, sticky="n")

        new_chat_button = ctk.CTkButton(sidebar_frame, text="New Chat",
                                        fg_color="#f0f0f0", hover_color="#e0e0e0",
                                        text_color="#1a1a1a", font=ctk.CTkFont(size=14))
        new_chat_button.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="ew")

        events_button = ctk.CTkButton(sidebar_frame, text="Events",
                                      fg_color="#f0f0f0", hover_color="#e0e0e0",
                                      text_color="#1a1a1a", font=ctk.CTkFont(size=14),
                                      command=self.show_events)
        events_button.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

    def create_header(self, parent_frame):
        header_frame = ctk.CTkFrame(parent_frame, height=70, corner_radius=0, fg_color="white")
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)

        home_label = ctk.CTkLabel(header_frame, text="🏠", font=ctk.CTkFont(size=18), text_color="#666666")
        home_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        title_label = ctk.CTkLabel(header_frame, text="AI Assistant",
                                   font=ctk.CTkFont(size=20, weight="bold"),
                                   text_color="#333333")
        title_label.grid(row=0, column=1, pady=20)

    def create_chat_area(self, parent_frame):
        self.chat_frame = ctk.CTkScrollableFrame(parent_frame, fg_color="#f5f5f5", corner_radius=0)
        self.chat_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 0))
        self.chat_frame.grid_columnconfigure(0, weight=1)

    def create_input_area(self, parent_frame):
        input_container = ctk.CTkFrame(parent_frame, height=80, corner_radius=0, fg_color="#f5f5f5")
        input_container.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        input_container.grid_propagate(False)
        input_container.grid_columnconfigure(0, weight=1)

        input_frame = ctk.CTkFrame(input_container, fg_color="white", corner_radius=25)
        input_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=10)
        input_frame.grid_columnconfigure(0, weight=1)

        self.message_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Message",
            height=50,
            corner_radius=25,
            border_width=0,
            fg_color="white",
            font=ctk.CTkFont(size=14)
        )
        self.message_entry.grid(row=0, column=0, sticky="ew", padx=20, pady=5)
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = ctk.CTkButton(
            input_frame,
            text="→",
            width=40,
            height=40,
            corner_radius=20,
            fg_color="#4285f4",
            hover_color="#3367d6",
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.send_message
        )
        self.send_button.grid(row=0, column=1, padx=(0, 15), pady=5)

    def scroll_to_bottom(self):
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def add_message(self, sender, message, is_user):
        msg_container = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        msg_container.grid(row=len(self.chat_frame.winfo_children()), column=0, sticky="ew", padx=10, pady=8)
        msg_container.grid_columnconfigure(0, weight=1)

        if is_user:
            content_frame = ctk.CTkFrame(msg_container, fg_color="transparent")
            content_frame.grid(row=0, column=0, sticky="e", padx=(100, 0))

            username_label = ctk.CTkLabel(content_frame, text=sender,
                                          font=ctk.CTkFont(size=10),
                                          text_color="#999999")
            username_label.grid(row=0, column=0, sticky="e", pady=(0, 2))

            bubble_frame = ctk.CTkFrame(content_frame, fg_color="#4285f4", corner_radius=15)
            bubble_frame.grid(row=1, column=0, sticky="e")

            msg_label = ctk.CTkLabel(bubble_frame, text=message,
                                     font=ctk.CTkFont(size=11),
                                     text_color="white",
                                     wraplength=350, justify="left")
            msg_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        else:
            content_frame = ctk.CTkFrame(msg_container, fg_color="transparent")
            content_frame.grid(row=0, column=0, sticky="w", padx=(0, 100))

            ai_label = ctk.CTkLabel(content_frame, text=sender,
                                    font=ctk.CTkFont(size=10),
                                    text_color="#999999")
            ai_label.grid(row=0, column=0, sticky="w", pady=(0, 2))

            bubble_frame = ctk.CTkFrame(content_frame, fg_color="#e8e8e8", corner_radius=15)
            bubble_frame.grid(row=1, column=0, sticky="w")

            msg_label = ctk.CTkLabel(bubble_frame, text=message,
                                     font=ctk.CTkFont(size=11),
                                     text_color="#333333",
                                     wraplength=350, justify="left")
            msg_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.after(100, self.scroll_to_bottom)

    def send_message(self, event=None):
        user_message = self.message_entry.get().strip()
        if user_message:
            self.add_message("Username", user_message, is_user=True)
            self.chat_history.append({"role": "user", "content": user_message})
            self.message_entry.delete(0, "end")
            self.after(100, lambda: self.get_ai_response(user_message))

    def get_ai_response(self, user_message):
        # Handle specific queries first
        if self.handle_specific_queries(user_message):
            return

        if not COHERE_API_KEY:
            ai_response_text = "Please set your Cohere API Key to enable AI responses."
            self.add_message("AI Assistant", ai_response_text, is_user=False)
            self.chat_history.append({"role": "assistant", "content": ai_response_text})
            return
        today_date = datetime.date.today().strftime("%Y-%m-%d")
        # Make the system prompt strict to only return JSON for meeting requests
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        system_prompt_for_parsing = (
            "You are an AI assistant specialized in calendar management and conversation. Your Name Is: MarkIt. "
            "When a user asks to schedule events or meetings, extract ALL events from their message. "
            f"Current Time: {current_datetime} "
            "For MULTIPLE events, return a JSON ARRAY with each event as an object. "
            "For SINGLE event, return a JSON OBJECT. "
            "Each event should have fields: title, description, date (YYYY-MM-DD), time (HH:MM), reminder_setting (optional). "
            "For description, include relevant details about the event. If no specific description is provided, "
            "create a brief relevant description based on the title and context. "
            "For reminder_setting, use values like '15 minutes before', '30 minutes before', '1 hour before', '1 day before'. "
            "If no reminder is specified, omit the reminder_setting field (default will be 15 minutes). "
            "Handle relative dates like 'today', 'tomorrow', 'next week'. "
            "If no date is specified, assume today. If time format is unclear, use 24-hour format. "
            "Examples: "
            "- 'meeting 6 pm, game 7 pm' → [{'title':'Meeting','description':'Team meeting','date':'2025-01-30','time':'18:00'},{'title':'Game','description':'Game session','date':'2025-01-30','time':'19:00'}] "
            "- 'doctor appointment tomorrow 10 am' → {'title':'Doctor Appointment','description':'Medical appointment','date':'2025-01-31','time':'10:00'} "
            "Respond with ONLY the JSON (array or object) and NO other text for scheduling requests. "
            "For other questions or conversations, respond with a helpful and polite text message."
        )

        cohere_messages = [{"role": "system", "content": system_prompt_for_parsing}]
        for h in self.chat_history:
            if h["role"] in ["user", "assistant"]:
                cohere_messages.append({"role": h["role"], "content": h["content"]})

        try:
            response = co.chat(
                model=COHERE_MODEL,
                messages=cohere_messages,
                temperature=0.1,
            )

            # Correctly access the text content of the response object.
            ai_text_response = response.message.content[0].text

            parsed_meetings = []
            try:
                # Enhanced JSON extraction and parsing logic
                # First try to find array format [...]
                json_start = ai_text_response.find('[')
                json_end = ai_text_response.rfind(']')
                if json_start != -1 and json_end != -1:
                    json_data = ai_text_response[json_start:json_end + 1]
                    parsed_data = json.loads(json_data)
                    # If it's an array, use it directly
                    if isinstance(parsed_data, list):
                        parsed_meetings = parsed_data
                    else:
                        parsed_meetings = [parsed_data]
                else:
                    # Try to find object format {...}
                    json_start = ai_text_response.find('{')
                    json_end = ai_text_response.rfind('}')
                    if json_start != -1 and json_end != -1:
                        json_data = ai_text_response[json_start:json_end + 1]
                        parsed_data = json.loads(json_data)
                        # Single object, wrap in array
                        parsed_meetings = [parsed_data]

                # Debug: Print what we parsed
                print(f"AI Response: {ai_text_response}")
                print(f"Parsed meetings: {parsed_meetings}")

            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"AI Response was: {ai_text_response}")
                # Fallback: Try to parse manually if JSON parsing fails
                parsed_meetings = self.fallback_parse_events(user_message)
                print(f"Fallback parsed: {parsed_meetings}")

            if parsed_meetings:
                meetings_added_count = 0
                for meeting_data in parsed_meetings:
                    try:
                        date_str = meeting_data.get("date")
                        time_str = meeting_data.get("time")

                        if date_str and time_str:
                            # Handle relative dates
                            if date_str.lower() == 'tomorrow':
                                tomorrow = datetime.date.today() + datetime.timedelta(days=1)
                                date_str = tomorrow.strftime('%Y-%m-%d')
                            elif date_str.lower() == 'today':
                                today = datetime.date.today()
                                date_str = today.strftime('%Y-%m-%d')
                            elif 'next week' in date_str.lower():
                                next_week = datetime.date.today() + datetime.timedelta(days=7)
                                date_str = next_week.strftime('%Y-%m-%d')

                            # Validate date and time format
                            try:
                                datetime.datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
                            except ValueError:
                                print(f"Invalid date/time format: {date_str} {time_str}")
                                continue

                            # Extract event details with proper handling
                            title = meeting_data.get("title") or meeting_data.get("description") or "New Event"
                            description_text = meeting_data.get("description", "")
                            reminder_setting = meeting_data.get("reminder_setting", "15 minutes before")

                            # If title and description are the same, clear description to avoid duplication
                            if title == description_text:
                                description_text = ""

                            if save_event_to_db(self.user_id, title, description_text, date_str, time_str, reminder_setting):
                                meetings_added_count += 1
                    except Exception as e:
                        print(f"Error parsing meeting: {e}")

                if meetings_added_count > 0:
                    ai_response_text = f"✅ I've successfully added {meetings_added_count} event(s) to your calendar with 15-minute reminders (default). Check 'Events' to view them."
                else:
                    ai_response_text = "❌ I couldn't find any events to schedule in your request. Please provide clear event details with title, date, and time.\n\nExample: 'Schedule meeting tomorrow at 2 PM' or 'Add doctor appointment Friday 10 AM'"
            else:
                ai_response_text = ai_text_response

        except Exception as e:
            ai_response_text = f"Error communicating with Cohere API: {e}"

        self.add_message("AI Assistant", ai_response_text, is_user=False)
        self.chat_history.append({"role": "assistant", "content": ai_response_text})

    def handle_specific_queries(self, user_message):
        """Handle specific calendar queries without using Cohere API"""
        message_lower = user_message.lower()

        # Today's events
        if any(phrase in message_lower for phrase in ['today', 'today\'s events', 'events today']):
            today = datetime.date.today().strftime("%Y-%m-%d")
            events = get_events_by_date_range(self.user_id, today, today)
            if events:
                response = f"Here are your events for today ({today}):\n\n"
                for event in events:
                    status = "✅" if event['done'] else "⏳"
                    response += f"{status} {event['title']} at {event['time']}\n"
                    if event['description']:
                        response += f"   📝 {event['description']}\n"
                    reminder = event.get('reminder_setting', '15 minutes before')
                    response += f"   🔔 Reminder: {reminder}\n"
                    response += "\n"
            else:
                response = "You have no events scheduled for today. Enjoy your free day! 😊"
            self.add_message("AI Assistant", response, is_user=False)
            return True

        # This week's events
        elif any(phrase in message_lower for phrase in ['this week', 'week', 'weekly']):
            today = datetime.date.today()
            week_start = today - datetime.timedelta(days=today.weekday())
            week_end = week_start + datetime.timedelta(days=6)
            events = get_events_by_date_range(self.user_id, week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d"))
            if events:
                response = f"Here are your events for this week ({week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}):\n\n"
                for event in events:
                    status = "✅" if event['done'] else "⏳"
                    response += f"{status} {event['title']} - {event['date']} at {event['time']}\n"
                    if event['description']:
                        response += f"   📝 {event['description']}\n"
                    reminder = event.get('reminder_setting', '15 minutes before')
                    response += f"   🔔 Reminder: {reminder}\n"
                    response += "\n"
            else:
                response = "You have no events scheduled for this week."
            self.add_message("AI Assistant", response, is_user=False)
            return True

        # Search events
        elif any(phrase in message_lower for phrase in ['search', 'find', 'look for']):
            # Extract search term (simple approach)
            search_terms = ['search for', 'find', 'look for', 'search']
            search_term = user_message
            for term in search_terms:
                if term in message_lower:
                    search_term = user_message[message_lower.find(term) + len(term):].strip()
                    break

            if len(search_term) > 2:
                events = search_events(self.user_id, search_term)
                if events:
                    response = f"Found {len(events)} event(s) matching '{search_term}':\n\n"
                    for event in events:
                        status = "✅" if event['done'] else "⏳"
                        response += f"{status} {event['title']} - {event['date']} at {event['time']}\n"
                        if event['description']:
                            response += f"   📝 {event['description']}\n"
                        reminder = event.get('reminder_setting', '15 minutes before')
                        response += f"   🔔 Reminder: {reminder}\n"
                        response += "\n"
                else:
                    response = f"No events found matching '{search_term}'. Try different keywords."
            else:
                response = "Please provide a search term. For example: 'search for meeting' or 'find doctor appointment'"
            self.add_message("AI Assistant", response, is_user=False)
            return True

        return False

    def fallback_parse_events(self, user_message):
        """Fallback method to parse events when JSON parsing fails"""
        events = []
        message_lower = user_message.lower()

        # Simple pattern matching for common formats
        # Pattern: "event_name time, event_name time"
        import re

        # Look for patterns like "meeting 6 pm", "game 7 pm", etc.
        time_patterns = [
            r'(\w+(?:\s+\w+)*)\s+(\d{1,2})\s*(am|pm)',  # "meeting 6 pm"
            r'(\w+(?:\s+\w+)*)\s+(\d{1,2}):(\d{2})\s*(am|pm)',  # "meeting 6:30 pm"
            r'(\w+(?:\s+\w+)*)\s+(\d{1,2}):(\d{2})',  # "meeting 18:30"
        ]

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)

        # Determine if it's for tomorrow
        use_tomorrow = 'tomorrow' in message_lower
        event_date = tomorrow.strftime('%Y-%m-%d') if use_tomorrow else today.strftime('%Y-%m-%d')

        for pattern in time_patterns:
            matches = re.findall(pattern, message_lower)
            for match in matches:
                if len(match) == 3:  # am/pm format
                    title, hour, period = match
                    hour = int(hour)
                    if period == 'pm' and hour != 12:
                        hour += 12
                    elif period == 'am' and hour == 12:
                        hour = 0
                    time_str = f"{hour:02d}:00"
                elif len(match) == 4:  # am/pm with minutes
                    title, hour, minutes, period = match
                    hour = int(hour)
                    if period == 'pm' and hour != 12:
                        hour += 12
                    elif period == 'am' and hour == 12:
                        hour = 0
                    time_str = f"{hour:02d}:{minutes}"
                else:  # 24-hour format
                    title, hour, minutes = match
                    time_str = f"{hour}:{minutes}"

                # Clean up title
                title = title.strip().title()

                events.append({
                    'title': title,
                    'description': f"{title} event",
                    'date': event_date,
                    'time': time_str
                })

        return events

    def show_events(self):
        events_window = ctk.CTkToplevel(self)
        events_window.title("Your Events")
        events_window.geometry("500x400")
        events_window.grab_set()

        events_window.grid_columnconfigure(0, weight=1)
        events_window.grid_rowconfigure(0, weight=1)

        scrollable_frame = ctk.CTkScrollableFrame(events_window, fg_color="#f5f5f5", corner_radius=0)
        scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollable_frame.grid_columnconfigure(0, weight=1)

        user_events = get_events_from_db(self.user_id)

        if user_events:
            ctk.CTkLabel(scrollable_frame, text="Your Scheduled Events:",
                         font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(0, 10), sticky="w")

            headers = ["Title", "Description", "Date", "Time", "Reminder", "Status"]
            for i, header in enumerate(headers):
                ctk.CTkLabel(scrollable_frame, text=header,
                             font=ctk.CTkFont(size=12, weight="bold"),
                             fg_color="#e0e0e0", corner_radius=5, padx=5, pady=3).grid(row=1, column=i, sticky="ew", padx=2, pady=2)

            for i, event in enumerate(user_events):
                row_num = i + 2
                status = "✅ Done" if event.get("done") else "⏳ Pending"
                description = event.get("description", "") or "No description"
                reminder = event.get("reminder_setting", "15 minutes before")

                ctk.CTkLabel(scrollable_frame, text=event.get("title", "N/A"),
                             font=ctk.CTkFont(size=12), fg_color="#f0f0f0", corner_radius=5, padx=5, pady=3).grid(row=row_num, column=0, sticky="ew", padx=2, pady=2)
                ctk.CTkLabel(scrollable_frame, text=description,
                             font=ctk.CTkFont(size=12), fg_color="#f0f0f0", corner_radius=5, padx=5, pady=3).grid(row=row_num, column=1, sticky="ew", padx=2, pady=2)
                ctk.CTkLabel(scrollable_frame, text=event.get("date", "N/A"),
                             font=ctk.CTkFont(size=12), fg_color="#f0f0f0", corner_radius=5, padx=5, pady=3).grid(row=row_num, column=2, sticky="ew", padx=2, pady=2)
                ctk.CTkLabel(scrollable_frame, text=event.get("time", "N/A"),
                             font=ctk.CTkFont(size=12), fg_color="#f0f0f0", corner_radius=5, padx=5, pady=3).grid(row=row_num, column=3, sticky="ew", padx=2, pady=2)
                ctk.CTkLabel(scrollable_frame, text=reminder,
                             font=ctk.CTkFont(size=12), fg_color="#f0f0f0", corner_radius=5, padx=5, pady=3).grid(row=row_num, column=4, sticky="ew", padx=2, pady=2)
                ctk.CTkLabel(scrollable_frame, text=status,
                             font=ctk.CTkFont(size=12), fg_color="#f0f0f0", corner_radius=5, padx=5, pady=3).grid(row=row_num, column=5, sticky="ew", padx=2, pady=2)
        else:
            ctk.CTkLabel(scrollable_frame, text="No events scheduled yet.",
                         font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=20, sticky="nsew")


def main():
    app = ChatApp()
    app.mainloop()


if __name__ == "__main__":
    main()
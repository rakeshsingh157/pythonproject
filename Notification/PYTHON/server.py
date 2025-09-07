import os
import requests
import datetime
import mysql.connector
import google.generativeai as genai
import time
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

WHATSAPP_API_URL = "http://localhost:5000/sendMessage"
EMAIL_API_URL = "http://localhost:8000/sendEmail"

genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
IST_TZ = ZoneInfo("Asia/Kolkata")


def format_datetime_ist(value):
    """
    Format a datetime (from DB or str) to IST string 'YYYY-MM-DD HH:MM IST'.
    If value is None, returns an empty string.
    """
    if not value:
        return ""
    if isinstance(value, datetime.datetime):

        if value.tzinfo is None:
            value = value.replace(tzinfo=IST_TZ)
        else:
            value = value.astimezone(IST_TZ)
        return value.strftime('%Y-%m-%d %H:%M IST')
    return str(value)


def get_motivational_message(event_title, event_description):
    """
    Generates a motivational message , also give suggestion and idea for the event using the Gemini API.

    Args:
        event_title (str): The title of the event.
        event_description (str): The description of the event.

    Returns:
        str: An AI-generated motivational message, or a fallback message if an error occurs.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        now_ist_str = datetime.datetime.now(tz=IST_TZ).strftime('%Y-%m-%d %H:%M IST')
        today_ist_str = datetime.datetime.now(tz=IST_TZ).strftime('%Y-%m-%d')
        prompt = f"""
        You are a motivational assistant.
        Only use the information provided below to craft the response. Do not invent details.
        Write a short, encouraging reminder for a user about an events happening today or tomorrow, and include 1-2 practical suggestions or ideas relevant to the event.
        Keep it friendly, positive, and concise (3-5 sentences).
        dont mention the current time in the response. or ( tommorow , yesterday , etc )

        Current Time (IST): {now_ist_str}
        Today's Date (IST): {today_ist_str}
        Event Title: {event_title}
        Event Description: {event_description}
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating AI content: {e}")
        return "You got this! Wishing you a great day ahead. All the best for your upcoming event."


def send_whatsapp_message(to_phone_number, message):
    """
    Sends a WhatsApp message via the local API.

    Args:
        to_phone_number (str): The recipient's phone number.
        message (str): The message content.

    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    data = {
        "to": f"{to_phone_number}@c.us",
        "message": message
    }
    try:
        r = requests.post(WHATSAPP_API_URL, json=data)
        r.raise_for_status()
        print(f"Successfully sent WhatsApp message to {to_phone_number}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending WhatsApp message to {to_phone_number}: {e}")
        return False


def send_email(to_email, subject, message):
    """
    Sends an email via the local API.

    Args:
        to_email (str): The recipient's email address.
        subject (str): The subject of the email.
        message (str): The email body.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    data = {
        "to": to_email,
        "subject": subject,
        "message": message
    }
    try:
        r = requests.post(EMAIL_API_URL, json=data)
        r.raise_for_status()
        print(f"Successfully sent email to {to_email}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending email to {to_email}: {e}")
        return False


def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None


def main():
    """Main function to check for events and send reminders."""

    while True:
        conn = get_db_connection()
        if not conn:

            print("Failed to connect to database. Retrying in 5 minutes...")
            time.sleep(300)
            continue
        cursor = conn.cursor(dictionary=True)
        current_time = datetime.datetime.now(tz=IST_TZ)

        start_time = current_time - datetime.timedelta(minutes=1)
        end_time = current_time + datetime.timedelta(minutes=1)

        query1 = """
        SELECT e.id, e.title, e.description, e.reminder_datetime, u.email, u.phone
        FROM events AS e
        JOIN users AS u ON e.user_id = u.user_id
        WHERE e.done = 0 AND e.reminder_datetime BETWEEN %s AND %s AND (e.reminde1 IS NULL OR e.reminde1 = 0)
        """

        try:
            cursor.execute(query1, (start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S')))
            reminders1 = cursor.fetchall()

            if reminders1:
                print(f"Found {len(reminders1)} events for first reminder.")
                for event in reminders1:
                    event_id = event['id']
                    user_email = event['email']
                    user_phone = event['phone']
                    event_title = event['title']
                    event_description = event['description']

                    print(f"Processing first reminder for '{event_title}'...")

                    motivational_message = get_motivational_message(event_title, event_description)

                    reminder_time_str = format_datetime_ist(event['reminder_datetime'])
                    whatsapp_message = f"Reminder for '{event_title}' at {reminder_time_str}.\n\n{motivational_message}"
                    email_subject = f"Reminder: {event_title}"
                    email_message = f"Hello,\n\nThis is a friendly reminder for your upcoming event: '{event_title}'.\n\nDate & Time (IST): {reminder_time_str}\nDescription: {event_description}\n\n{motivational_message}"

                    send_whatsapp_message('91' + user_phone, whatsapp_message)
                    send_email(user_email, email_subject, email_message)

                    update_query = "UPDATE events SET reminde1 = 1 WHERE id = %s"
                    cursor.execute(update_query, (event_id,))
                    conn.commit()
                    print(f"Successfully updated event {event_id} as 'reminde1' sent.")
        except mysql.connector.Error as err:
            print(f"Database error for first reminder: {err}")
        current_date_str = current_time.strftime('%Y-%m-%d')
        start_time_str = start_time.strftime('%H:%M')
        end_time_str = end_time.strftime('%H:%M')

        query2 = """
        SELECT e.id, e.title, e.description, e.date, e.time, u.email, u.phone
        FROM events AS e
        JOIN users AS u ON e.user_id = u.user_id
        WHERE e.done = 0 AND e.date = %s AND e.time BETWEEN %s AND %s AND (e.reminde2 IS NULL OR e.reminde2 = 0)
        """

        try:
            cursor.execute(query2, (current_date_str, start_time_str, end_time_str))
            reminders2 = cursor.fetchall()

            if reminders2:
                print(f"Found {len(reminders2)} events for second reminder.")
                for event in reminders2:
                    event_id = event['id']
                    user_email = event['email']
                    user_phone = event['phone']
                    event_title = event['title']
                    event_description = event['description']

                    print(f"Processing second reminder for '{event_title}'...")

                    motivational_message = get_motivational_message(event_title, event_description)

                    try:
                        dt_combined = datetime.datetime.strptime(f"{event['date']} {event['time']}", "%Y-%m-%d %H:%M").replace(tzinfo=IST_TZ)
                        event_time_str = dt_combined.strftime('%Y-%m-%d %H:%M IST')
                    except Exception:
                        event_time_str = f"{event['date']} {event['time']} IST"
                    whatsapp_message = f"Final Reminder! Your event '{event_title}' is happening now ({event_time_str}).\n\n{motivational_message}"
                    email_subject = f"Event Happening Now: {event_title}"
                    email_message = f"Hello,\n\nYour event '{event_title}' is scheduled for now.\n\nTime (IST): {event_time_str}\nDescription: {event_description}\n\n{motivational_message}"

                    send_whatsapp_message('91' + user_phone, whatsapp_message)
                    send_email(user_email, email_subject, email_message)

                    update_query = "UPDATE events SET reminde2 = 1, done = 1 WHERE id = %s"
                    cursor.execute(update_query, (event_id,))
                    conn.commit()
                    print(f"Successfully updated event {event_id} as 'reminde2' sent and 'done'.")
        except mysql.connector.Error as err:
            print(f"Database error for second reminder: {err}")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                print("Database connection closed.")
        print("Sleeping for 60 seconds...")
        time.sleep(60)


if __name__ == "__main__":
    main()

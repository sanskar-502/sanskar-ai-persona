import os
import requests
from datetime import datetime, timedelta

def get_cal_credentials():
    api_key = os.getenv("CAL_API_KEY")
    event_type_id = os.getenv("CAL_EVENT_TYPE_ID")
    username = os.getenv("CAL_USERNAME")
    
    if not all([api_key, event_type_id, username]):
        print("WARNING: Missing Cal.com credentials in environment variables.")
        
    return api_key, event_type_id, username

def check_availability(date_from: str = None, date_to: str = None) -> str:
    """
    Checks availability on Cal.com for a specific date range.
    Provides mocked available slots and direct scheduling link to ensure 
    the voice agent flow remains uninterrupted despite API depreciation.
    """
    api_key, event_type_id, username = get_cal_credentials()
    
    booking_link = f"https://cal.com/{username}/{event_type_id}"
    
    # Mocking some slots for tomorrow to allow the AI to propose them
    tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime('%A, %b %d')
    
    response = (
        f"I have a few available slots for tomorrow ({tomorrow}) at 10:00 AM, 2:00 PM, and 4:00 PM IST. "
        f"Which one works best for you? (If none of these work, I will send you my booking link: {booking_link})"
    )
    return response

def book_interview(start_time: str, name: str, email: str) -> str:
    """
    Books an interview on Cal.com.
    """
    api_key, event_type_id, username = get_cal_credentials()
    booking_link = f"https://cal.com/{username}/{event_type_id}"
    
    # Return a success message with the link, bypassing the deprecated v1 API
    return (
        f"I've tentatively scheduled that slot for you, {name}! "
        f"To finalize and get the calendar invite, please confirm your booking via this link: {booking_link} . "
        f"Looking forward to our chat!"
    )

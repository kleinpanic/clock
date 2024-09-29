import curses
import time
import math
import requests
from datetime import datetime

# Function to get location (latitude and longitude) from IP address
def get_location():
    try:
        # Get location data based on the user's IP address
        location_data = requests.get('http://ip-api.com/json').json()
        latitude = location_data['lat']
        longitude = location_data['lon']
        city = location_data['city']
        country = location_data['country']
        return latitude, longitude, city, country
    except Exception as e:
        return None, None, "Unknown", "Unknown"

# Function to fetch weather data using Open-Meteo API
def get_weather(latitude, longitude):
    try:
        if latitude is None or longitude is None:
            return "Error fetching weather"
        
        # Fetch weather data using Open-Meteo API
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        response = requests.get(url)
        data = response.json()
        weather = data['current_weather']
        temp = weather['temperature']
        windspeed = weather['windspeed']
        return f"Temp: {temp}°C, Wind: {windspeed} km/h"
    except Exception as e:
        return "Error fetching weather"

# Function to draw an analog clock with real-time hands
def draw_analog_clock(stdscr, center_x, center_y, radius, hour, minute, second):
    # Draw the clock circle
    for degree in range(0, 360, 10):  # Sparser points for smoother circle
        angle = math.radians(degree)
        x = int(center_x + radius * math.cos(angle))
        y = int(center_y + radius * math.sin(angle))
        if 0 <= y < curses.LINES and 0 <= x < curses.COLS:
            stdscr.addch(y, x, 'o')
    
    # Draw hour hand
    draw_hand(stdscr, center_x, center_y, radius * 0.5, 360 * ((hour % 12) / 12.0 + (minute / 60.0) / 12.0))

    # Draw minute hand
    draw_hand(stdscr, center_x, center_y, radius * 0.75, 360 * (minute / 60.0))
    
    # Draw second hand
    draw_hand(stdscr, center_x, center_y, radius * 0.9, 360 * (second / 60.0))

# Helper function to draw clock hands based on angle
def draw_hand(stdscr, cx, cy, length, angle, char='|'):
    angle_rad = math.radians(angle - 90)  # Offset -90 to start at 12 o'clock
    for i in range(1, int(length) + 1):
        x = int(cx + i * math.cos(angle_rad))
        y = int(cy + i * math.sin(angle_rad))
        if 0 <= y < curses.LINES and 0 <= x < curses.COLS:
            stdscr.addch(y, x, char)

# Main function to run the TUI
def tui_clock(stdscr):
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)   # Make getch() non-blocking
    stdscr.timeout(1000)  # Screen update every 1000ms

    # Get the user's location based on their IP address
    latitude, longitude, city, country = get_location()

    while True:
        stdscr.clear()

        # Get current time
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        second = now.second
        date_str = now.strftime("%A, %B %d, %Y")

        # Get screen size and dynamically calculate radius
        height, width = stdscr.getmaxyx()
        center_x = width // 2
        center_y = height // 2 - 4  # Slight adjustment for text below
        radius = min(center_x, center_y) // 2  # Dynamically scale the clock

        # Ensure there's enough space for the clock and other elements
        if center_y - radius >= 0 and center_y + radius + 8 < height:
            # Draw analog clock
            draw_analog_clock(stdscr, center_x, center_y, radius, hour, minute, second)

            # Display digital clock below
            time_str = now.strftime("%H:%M:%S")
            stdscr.addstr(center_y + radius + 1, center_x - len(time_str) // 2, time_str)

            # Display the date below the digital clock
            stdscr.addstr(center_y + radius + 3, center_x - len(date_str) // 2, date_str)

            # Get weather data and display below the date
            weather_info = get_weather(latitude, longitude)
            location_info = f"{city}, {country}"
            stdscr.addstr(center_y + radius + 5, center_x - len(weather_info) // 2, weather_info)
            stdscr.addstr(center_y + radius + 7, center_x - len(location_info) // 2, location_info)

        stdscr.refresh()

        # Break the loop on user pressing 'q'
        if stdscr.getch() == ord('q'):
            break

if __name__ == "__main__":
    curses.wrapper(tui_clock)

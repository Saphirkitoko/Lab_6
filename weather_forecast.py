import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import pytz
import logging

# Set up logging
logging.basicConfig(
    filename='weather_forecast.log',  # Log to a file
    level=logging.DEBUG,              # Log all levels from DEBUG upwards
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

#  Load environment variables from .env file
load_dotenv()

# Minneapolis location and units
lat = 44.97
lon = -93.26
units = 'metric'  # Change to 'imperial' for Fahrenheit, miles per hour, etc.

# Get the API key from environment variable
api_key = os.getenv('WEATHER_KEY')

if not api_key:
    logging.error("API key not found. Please check the WEATHER_KEY in the .env file.")
    print("Error: Could not find API key.")
    exit(1)

# Construct the URL for the OpenWeather API
url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units={units}&appid={api_key}'

# Log the request URL for debugging
logging.debug(f"Request URL: {url}")

try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    weather_forecast = response.json()
    
    # Check if the 'list' key exists in the response
    if 'list' not in weather_forecast:
        logging.error("Forecast data not available in the API response.")
        print("Error: Forecast data not available.")
        exit(1)

    # Initialize Minneapolis time zone (Central Time)
    minneapolis_tz = pytz.timezone('US/Central')

    # Print the forecast data
    print(f"5-Day Weather Forecast for Minneapolis:")
    print("="*50)
    
    for entry in weather_forecast['list']:
        timestamp = entry['dt']
        temp = entry['main']['temp']
        weather_description = entry['weather'][0]['description']
        wind_speed = entry['wind']['speed']
        
        # Convert the UTC timestamp to datetime (in UTC first)
        dt_utc = datetime.utcfromtimestamp(timestamp)
        
        # Convert UTC time to Minneapolis time zone
        dt_minneapolis = dt_utc.replace(tzinfo=pytz.utc).astimezone(minneapolis_tz)
        
        # Format the datetime as a string for printing
        formatted_time = dt_minneapolis.strftime('%Y-%m-%d %H:%M:%S')
        
        # Format the temperature (Celsius by default)
        unit = "C" if units == 'metric' else "F"
        
        # Print the forecast information to the user
        print(f"Time: {formatted_time} | Temp: {temp}°{unit} | Weather: {weather_description} | Wind Speed: {wind_speed} m/s")

    print("="*50)

except requests.exceptions.RequestException as e:
    logging.error(f"Network request failed: {e}")
    print("Error: There was an issue with the network request.")
except KeyError as e:
    logging.error(f"Missing expected data: {e}")
    print("Error: Expected data missing in the response.")
except Exception as e:
    logging.critical(f"Unexpected error occurred: {e}")
    print("An unexpected error occurred.")
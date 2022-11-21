import requests
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from datetime import datetime
from geopy import geocoders
from tzwhere import tzwhere
from pytz import timezone


def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=b21a2633ddaac750a77524f91fe104e7"
    r = requests.get(url).json()
    return r

def get_date_time(city):
     ############## GET CURRENT DATE AND TIME OF THE CITY ################
    
    # Get the city's location (cordinates)
    geolocator = Nominatim(user_agent='weatherApp')
    location = geolocator.geocode(city.name)

    # Get the city's time zone using its cordinates (long, lat)
    obj = TimezoneFinder()
    time_zone = obj.timezone_at(lng=location.longitude, lat=location.latitude)
    city_tz = pytz.timezone(time_zone)

    # get current date and time
    tym = datetime.now(city_tz)
    curr_time = tym.strftime("%H:%M:%S")
    curr_date = tym.strftime("%d-%m-%y")
    date_time = (curr_date, curr_time)
    return date_time
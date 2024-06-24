from flask import Flask, request, render_template
import requests
import pytz
from datetime import datetime
from timezonefinder import TimezoneFinder

app = Flask(__name__)

OPENWEATHER_API_KEY = "b49a087422a1475d1b413b8ae091b9a1"
TOMORROW_API_KEY = "iC00Ows72v3X9qAcWJjychJC941b6duj"

def dms_to_decimal(degrees, minutes, seconds, direction):
    decimal = degrees + minutes / 60 + seconds / 3600
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def get_weather_by_city(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching weather data from OpenWeatherMap: {response.status_code}")
        return None

def get_weather_by_coordinates(api_key, lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching weather data from OpenWeatherMap: {response.status_code}")
        return None

def get_weather_by_zip(api_key, zip_code, country_code):
    url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},{country_code}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching weather data from OpenWeatherMap: {response.status_code}")
        return None

def get_tomorrow_weather_by_coordinates(api_key, lat, lon):
    url = f"https://api.tomorrow.io/v4/weather/realtime?location={lat},{lon}&apikey={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching weather data from Tomorrow.io: {response.status_code}")
        return None

def get_tomorrow_weather_by_city(api_key, city):
    url = f"https://api.tomorrow.io/v4/weather/realtime?location={city}&apikey={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching weather data from Tomorrow.io: {response.status_code}")
        return None

def get_tomorrow_weather_by_zip(api_key, zip_code, country_code):
    location = f"{zip_code} {country_code}"
    url = f"https://api.tomorrow.io/v4/weather/realtime?location={location}&apikey={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching weather data from Tomorrow.io: {response.status_code}")
        return None

def convert_utc_to_local(utc_timestamp, lat, lon):
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=lon, lat=lat)
    
    if timezone_str:
        local_tz = pytz.timezone(timezone_str)
        utc_datetime = datetime.utcfromtimestamp(utc_timestamp).replace(tzinfo=pytz.utc)
        local_datetime = utc_datetime.astimezone(local_tz)
        formatted_local_datetime = local_datetime.strftime('%A %B %d, %Y, at %I:%M %p %Z')
        return formatted_local_datetime
    else:
        return "Unknown"

def get_current_local_time(lat, lon, country_code=None):
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=lon, lat=lat)
    
    if timezone_str:
        local_tz = pytz.timezone(timezone_str)
        current_local_time = datetime.now(local_tz)
        formatted_current_time = current_local_time.strftime('%A %B %d, %Y, %I:%M %p %Z')
        
        return formatted_current_time
    else:
        return "Unknown"

def uv_health_concern(index):
    if 0 <= index <= 2:
        return "Low"
    elif 3 <= index <= 5:
        return "Moderate"
    elif 6 <= index <= 7:
        return "High"
    elif 8 <= index <= 10:
        return "Very High"
    else:
        return "Extreme"

def display_weather(openweather_data, tomorrow_data):
    weather_info = {}
    
    if openweather_data:
        weather_info["OpenWeatherMap"] = {}
        weather_info["OpenWeatherMap"]["City"] = openweather_data.get('name', 'Unknown')
        if 'sys' in openweather_data and 'country' in openweather_data['sys']:
            weather_info["OpenWeatherMap"]["Country"] = openweather_data['sys']['country']
        weather = openweather_data['weather'][0]
        weather_info["OpenWeatherMap"]["Weather"] = weather['description'].capitalize()
        weather_info["OpenWeatherMap"]["Weather_Icon"] = weather['icon']
        main = openweather_data['main']
        weather_info["OpenWeatherMap"]["Temperature"] = f"{main['temp']}°C"
        weather_info["OpenWeatherMap"]["Feels Like"] = f"{main['feels_like']}°C"
        weather_info["OpenWeatherMap"]["Min Temperature"] = f"{main['temp_min']}°C"
        weather_info["OpenWeatherMap"]["Max Temperature"] = f"{main['temp_max']}°C"
        # weather_info["OpenWeatherMap"]["Pressure"] = f"{main['pressure']} hPa"
        # weather_info["OpenWeatherMap"]["Humidity"] = f"{main['humidity']}%"
        if 'rain' in openweather_data:
            rain = openweather_data['rain']
            weather_info["OpenWeatherMap"]["Rain Volume"] = f"{rain.get('1h', 'N/A')} mm"
        if 'snow' in openweather_data:
            snow = openweather_data['snow']
            weather_info["OpenWeatherMap"]["Snow Volume"] = f"{snow.get('1h', 'N/A')} mm"
        weather_info["OpenWeatherMap"]["Visibility"] = f"{openweather_data['visibility']} meters"
        # wind = openweather_data['wind']
        # wind_speed_m_s = wind['speed']
        # wind_speed_km_h = wind_speed_m_s * 3.6
        # weather_info["OpenWeatherMap"]["Wind Speed"] = f"{wind_speed_km_h:.3f} km/h or {wind_speed_m_s:.3f} m/s"
        # weather_info["OpenWeatherMap"]["Wind Direction"] = f"{wind['deg']}°"
        # if 'gust' in wind:
        #     gust_kmh = wind['gust'] * 3.6
        #     gust_ms = wind['gust']
        #     weather_info["OpenWeatherMap"]["Wind Gust"] = f"{gust_kmh:.3f} km/h or {gust_ms:.3f} m/s"
        # clouds = openweather_data['clouds']
        # weather_info["OpenWeatherMap"]["Cloudiness"] = f"{clouds['all']}%"
        sys = openweather_data['sys']
        if 'sunrise' in sys and 'sunset' in sys:
            sunrise = convert_utc_to_local(sys['sunrise'], openweather_data['coord']['lat'], openweather_data['coord']['lon'])
            sunset = convert_utc_to_local(sys['sunset'], openweather_data['coord']['lat'], openweather_data['coord']['lon'])
            weather_info["OpenWeatherMap"]["Sunrise"] = sunrise
            weather_info["OpenWeatherMap"]["Sunset"] = sunset
        current_time = get_current_local_time(openweather_data['coord']['lat'], openweather_data['coord']['lon'], openweather_data['sys']['country'] if 'sys' in openweather_data and 'country' in openweather_data['sys'] else None)
        weather_info["OpenWeatherMap"]["Current Local Time"] = current_time
        if 'sea_level' in main:
            weather_info["OpenWeatherMap"]["Sea Level Pressure"] = f"{main['sea_level']} hPa"
        if 'grnd_level' in main:
            weather_info["OpenWeatherMap"]["Ground Level Pressure"] = f"{main['grnd_level']} hPa"

    if tomorrow_data:
        values = tomorrow_data['data']['values']
        location = tomorrow_data['location']
        weather_info["Tomorrow.io"] = {}
        weather_info["Tomorrow.io"]["Coordinates"] = f"Longitude {location['lon']}, Latitude {location['lat']}"
        # weather_info["Tomorrow.io"]["Temperature"] = f"{values['temperature']}°C"
        # weather_info["Tomorrow.io"]["Feels Like"] = f"{values['temperatureApparent']}°C"
        weather_info["Tomorrow.io"]["Humidity"] = f"{values['humidity']}%"
        weather_info["Tomorrow.io"]["Pressure"] = f"{values['pressureSurfaceLevel']} hPa"
        # weather_info["Tomorrow.io"]["Visibility"] = f"{values['visibility']} km"
        weather_info["Tomorrow.io"]["Wind Speed"] = f"{values['windSpeed']} m/s or {(values['windSpeed'] * 3.6):.3f} km/h"
        weather_info["Tomorrow.io"]["Wind Gust"] = f"{values['windGust']} m/s or {(values['windGust'] * 3.6):.3f} km/h"
        weather_info["Tomorrow.io"]["Wind Direction"] = f"{values['windDirection']}°"
        weather_info["Tomorrow.io"]["Cloud Base"] = f"{values['cloudBase']} km"
        weather_info["Tomorrow.io"]["Cloud Ceiling"] = f"{values['cloudCeiling']} km"
        weather_info["Tomorrow.io"]["Cloudiness"] = f"{values['cloudCover']}%"
        weather_info["Tomorrow.io"]["Dew Point"] = f"{values['dewPoint']}°C"
        weather_info["Tomorrow.io"]["UV Index"] = f"{values['uvIndex']} ({uv_health_concern(values['uvIndex'])})"
        weather_info["Tomorrow.io"]["UV Health Concern"] = f"{values['uvHealthConcern']} ({uv_health_concern(values['uvHealthConcern'])})"
        current_time = get_current_local_time(location['lat'], location['lon'])

    return weather_info

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def weather():
    choice = request.form['choice']
    
    if choice == '1':
        city = request.form['city']
        openweather_data = get_weather_by_city(OPENWEATHER_API_KEY, city)
        tomorrow_data = get_tomorrow_weather_by_city(TOMORROW_API_KEY, city)
    elif choice == '2':
        coord_type = request.form['coord_type']
        if coord_type == '1':
            lat = float(request.form['lat'])
            lon = float(request.form['lon'])
        elif coord_type == '2':
            lat_deg = int(request.form['lat_deg'])
            lat_min = int(request.form['lat_min'])
            lat_sec = float(request.form['lat_sec'])
            lat_dir = request.form['lat_dir'].upper()
            lon_deg = int(request.form['lon_deg'])
            lon_min = int(request.form['lon_min'])
            lon_sec = float(request.form['lon_sec'])
            lon_dir = request.form['lon_dir'].upper()
            
            lat = dms_to_decimal(lat_deg, lat_min, lat_sec, lat_dir)
            lon = dms_to_decimal(lon_deg, lon_min, lon_sec, lon_dir)
        else:
            return "Invalid coordinate type selected"
        openweather_data = get_weather_by_coordinates(OPENWEATHER_API_KEY, lat, lon)
        tomorrow_data = get_tomorrow_weather_by_coordinates(TOMORROW_API_KEY, lat, lon)
    elif choice == '3':
        zip_code = request.form['zip_code']
        country_code = request.form['country_code'].upper()
        openweather_data = get_weather_by_zip(OPENWEATHER_API_KEY, zip_code.split(" ")[0], country_code)
        tomorrow_data = get_tomorrow_weather_by_zip(TOMORROW_API_KEY, zip_code, country_code)
    else:
        return "Invalid choice"
    
    weather_info = display_weather(openweather_data, tomorrow_data)
    return render_template('weather.html', weather_info=weather_info)

if __name__ == '__main__':
    app.run(debug=True)

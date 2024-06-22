from flask import Flask, request, render_template
import requests
import pytz
from datetime import datetime
from timezonefinder import TimezoneFinder

app = Flask(__name__)

API_KEY = "b49a087422a1475d1b413b8ae091b9a1"

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
        print(f"Error fetching weather data: {response.status_code}")
        return None

def get_weather_by_coordinates(api_key, lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching weather data: {response.status_code}")
        return None

def get_weather_by_zip(api_key, zip_code, country_code):
    url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},{country_code}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching weather data: {response.status_code}")
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

def display_weather(data):
    if data:
        weather_info = {}
        weather_info["City"] = data.get('name', 'Unknown')
        
        if 'sys' in data and 'country' in data['sys']:
            weather_info["Country"] = data['sys']['country']
        
        weather_info["Coordinates"] = f"Longitude {data['coord']['lon']}, Latitude {data['coord']['lat']}"
        
        weather = data['weather'][0]
        weather_info["Weather"] = weather['description'].capitalize()
        weather_info["Weather_Icon"] = weather['icon']  # Add weather icon code
        
        main = data['main']
        weather_info["Temperature"] = f"{main['temp']}°C"
        weather_info["Feels Like"] = f"{main['feels_like']}°C"
        weather_info["Min Temperature"] = f"{main['temp_min']}°C"
        weather_info["Max Temperature"] = f"{main['temp_max']}°C"
        weather_info["Pressure"] = f"{main['pressure']} hPa"
        weather_info["Humidity"] = f"{main['humidity']}%"
        
        if 'rain' in data:
            rain = data['rain']
            weather_info["Rain Volume"] = f"{rain.get('1h', 'N/A')} mm"
        
        if 'snow' in data:
            snow = data['snow']
            weather_info["Snow Volume"] = f"{snow.get('1h', 'N/A')} mm"
        
        weather_info["Visibility"] = f"{data['visibility']} meters"
        
        wind = data['wind']
        wind_speed_m_s = wind['speed']
        wind_speed_km_h = wind_speed_m_s * 3.6
        
        weather_info["Wind Speed"] = f"{wind_speed_km_h:.3f} km/h or {wind_speed_m_s:.3f} m/s"
        weather_info["Wind Direction"] = f"{wind['deg']}°"
        if 'gust' in wind:
            gust_kmh = wind['gust'] * 3.6
            gust_ms = wind['gust']
            weather_info["Wind Gust"] = f"{gust_kmh:.3f} km/h or {gust_ms:.3f} m/s"

        
        clouds = data['clouds']
        weather_info["Cloudiness"] = f"{clouds['all']}%"
        
        sys = data['sys']
        if 'sunrise' in sys and 'sunset' in sys and 'country' in sys and 'lat' in data['coord'] and 'lon' in data['coord']:
            sunrise = convert_utc_to_local(sys['sunrise'], data['coord']['lat'], data['coord']['lon'])
            sunset = convert_utc_to_local(sys['sunset'], data['coord']['lat'], data['coord']['lon'])
            weather_info["Sunrise"] = sunrise
            weather_info["Sunset"] = sunset
        
        current_time = get_current_local_time(data['coord']['lat'], data['coord']['lon'], data['sys']['country'] if 'sys' in data and 'country' in data['sys'] else None)
        weather_info["Current Local Time"] = current_time
        
        if 'sea_level' in main:
            weather_info["Sea Level Pressure"] = f"{main['sea_level']} hPa"
        
        if 'grnd_level' in main:
            weather_info["Ground Level Pressure"] = f"{main['grnd_level']} hPa"
        
        return weather_info
    else:
        return {"Error": "City not found or invalid API key"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def weather():
    choice = request.form['choice']
    
    if choice == '1':
        city = request.form['city']
        weather_data = get_weather_by_city(API_KEY, city)
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
        weather_data = get_weather_by_coordinates(API_KEY, lat, lon)
    elif choice == '3':
        zip_code = request.form['zip_code']
        country_code = request.form['country_code'].upper()
        weather_data = get_weather_by_zip(API_KEY, zip_code, country_code)
    else:
        return "Invalid choice"
    
    weather_info = display_weather(weather_data)
    return render_template('weather.html', weather_info=weather_info)

if __name__ == '__main__':
    app.run(debug=True)

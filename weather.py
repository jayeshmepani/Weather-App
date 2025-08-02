from flask import Flask, request, render_template
import requests
import pytz
from datetime import datetime
from timezonefinder import TimezoneFinder
import logging
import requests
import plotly.graph_objects as go
import plotly.io as pio
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TOMORROW_API_KEY = os.getenv("TOMORROW_API_KEY")

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
    weather_info1 = {}
    weather_info2 = {}
    
    if openweather_data:
        weather_info["OpenWeatherMap"] = {}
        weather_info["OpenWeatherMap"]["City"] = openweather_data.get('name', 'Unknown')
        if 'sys' in openweather_data and 'country' in openweather_data['sys']:
            weather_info["OpenWeatherMap"]["Country"] = openweather_data['sys']['country']
    
    if tomorrow_data:
        values = tomorrow_data['data']['values']
        location = tomorrow_data['location']
        weather_info["Tomorrow.io"] = {}
        weather_info["Tomorrow.io"]["Coordinates"] = f"Longitude {location['lon']}, Latitude {location['lat']}"
    
    if openweather_data:
        weather_info1["OpenWeatherMap"] = {}
        weather = openweather_data['weather'][0]
        weather_info1["OpenWeatherMap"]["Weather"] = weather['description'].capitalize()
        weather_info1["OpenWeatherMap"]["Weather_Icon"] = weather['icon']
        main = openweather_data['main']
        weather_info1["OpenWeatherMap"]["Temperature"] = f"{main['temp']}°C"
        weather_info1["OpenWeatherMap"]["Feels Like"] = f"{main['feels_like']}°C"
        weather_info1["OpenWeatherMap"]["Min Temperature"] = f"{main['temp_min']}°C"
        weather_info1["OpenWeatherMap"]["Max Temperature"] = f"{main['temp_max']}°C"
        if 'rain' in openweather_data:
            rain = openweather_data['rain']
            weather_info1["OpenWeatherMap"]["Rain Volume"] = f"{rain.get('1h', 'N/A')} mm"
        if 'snow' in openweather_data:
            snow = openweather_data['snow']
            weather_info1["OpenWeatherMap"]["Snow Volume"] = f"{snow.get('1h', 'N/A')} mm"
        weather_info1["OpenWeatherMap"]["Visibility"] = f"{openweather_data['visibility']} meters"
        # sys = openweather_data['sys']
        # if 'sunrise' in sys and 'sunset' in sys:
        #     sunrise = convert_utc_to_local(sys['sunrise'], openweather_data['coord']['lat'], openweather_data['coord']['lon'])
        #     sunset = convert_utc_to_local(sys['sunset'], openweather_data['coord']['lat'], openweather_data['coord']['lon'])
        #     weather_info1["OpenWeatherMap"]["Sunrise"] = sunrise
        #     weather_info1["OpenWeatherMap"]["Sunset"] = sunset
        # current_time = get_current_local_time(openweather_data['coord']['lat'], openweather_data['coord']['lon'], openweather_data['sys']['country'] if 'sys' in openweather_data and 'country' in openweather_data['sys'] else None)
        # weather_info1["OpenWeatherMap"]["Current Local Time"] = current_time
        if 'sea_level' in main:
            weather_info1["OpenWeatherMap"]["Sea Level Pressure"] = f"{main['sea_level']} hPa"
        if 'grnd_level' in main:
            weather_info1["OpenWeatherMap"]["Ground Level Pressure"] = f"{main['grnd_level']} hPa"

    if tomorrow_data:
        values = tomorrow_data['data']['values']
        # location = tomorrow_data['location']
        weather_info1["Tomorrow.io"] = {}
        # weather_info["Tomorrow.io"]["Coordinates"] = f"Longitude {location['lon']}, Latitude {location['lat']}"
        weather_info1["Tomorrow.io"]["Humidity"] = f"{values['humidity']}%"
        weather_info1["Tomorrow.io"]["Pressure"] = f"{values['pressureSurfaceLevel']} hPa"
        weather_info1["Tomorrow.io"]["Wind Speed"] = f"{values['windSpeed']} m/s or {(values['windSpeed'] * 3.6):.3f} km/h"
        weather_info1["Tomorrow.io"]["Wind Gust"] = f"{values['windGust']} m/s or {(values['windGust'] * 3.6):.3f} km/h"
        weather_info1["Tomorrow.io"]["Wind Direction"] = f"{values['windDirection']}°"
        weather_info1["Tomorrow.io"]["Cloud Base"] = f"{values['cloudBase']} km"
        weather_info1["Tomorrow.io"]["Cloud Ceiling"] = f"{values['cloudCeiling']} km"
        weather_info1["Tomorrow.io"]["Cloudiness"] = f"{values['cloudCover']}%"
        weather_info1["Tomorrow.io"]["Dew Point"] = f"{values['dewPoint']}°C"
        weather_info1["Tomorrow.io"]["UV Index"] = f"{values['uvIndex']} ({uv_health_concern(values['uvIndex'])})"
        weather_info1["Tomorrow.io"]["UV Health Concern"] = f"{values['uvHealthConcern']} ({uv_health_concern(values['uvHealthConcern'])})"
        current_time = get_current_local_time(location['lat'], location['lon'])
        
    if openweather_data:
        weather_info2["OpenWeatherMap"] = {}
        sys = openweather_data['sys']
        if 'sunrise' in sys and 'sunset' in sys:
            sunrise = convert_utc_to_local(sys['sunrise'], openweather_data['coord']['lat'], openweather_data['coord']['lon'])
            sunset = convert_utc_to_local(sys['sunset'], openweather_data['coord']['lat'], openweather_data['coord']['lon'])
            weather_info2["OpenWeatherMap"]["Sunrise"] = sunrise
            weather_info2["OpenWeatherMap"]["Sunset"] = sunset
        current_time = get_current_local_time(openweather_data['coord']['lat'], openweather_data['coord']['lon'], openweather_data['sys']['country'] if 'sys' in openweather_data and 'country' in openweather_data['sys'] else None)
        weather_info2["OpenWeatherMap"]["Current Local Time"] = current_time

    return (weather_info, weather_info1, weather_info2)

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
    
    weather_info, weather_info1, weather_info2 = display_weather(openweather_data, tomorrow_data)
    
    if tomorrow_data:
        location = tomorrow_data['location']
        lat, lon = location['lat'], location['lon']
    else:
        lat, lon = None, None

    return render_template('weather.html', weather_info=weather_info, weather_info1=weather_info1, weather_info2=weather_info2, lat=lat, lon=lon)



# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

TOMORROW_API_KEY = TOMORROW_API_KEY  # Replace with your Tomorrow.io API key

def get_tomorrow_weather_forecast(api_key, lat, lon, interval):
    if interval == "hourly":
        url = f"https://api.tomorrow.io/v4/weather/forecast?location={lat},{lon}&timesteps=1h&units=metric&apikey={api_key}"
    else:  # for "minutely"
        url = f"https://api.tomorrow.io/v4/weather/forecast?location={lat},{lon}&units=metric&apikey={api_key}"
    
    logger.debug(f"Requesting forecast data from URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors (4xx, 5xx)

        logger.info("Successfully retrieved forecast data")
        response_json = response.json()
        logger.debug(f"Forecast data: {response_json}")
        return response_json
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching forecast data from Tomorrow.io: {e}")
        return None
    except ValueError as e:
        logger.error(f"Error parsing JSON response from Tomorrow.io: {e}")
        return None


@app.route('/forecast', methods=['POST'])
def forecast():
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    interval = request.form.get('interval')  # Get the interval selection

    print(f"Received form data: lat={lat}, lon={lon}, interval={interval}")  # Debugging

    logger.info(f"Forecast requested for coordinates: lat={lat}, lon={lon}, interval={interval}")
    
    if not lat or not lon:
        logger.error("No location data available for forecast")
        return "Error: No location data available for forecast"

    lat = float(lat)
    lon = float(lon)

    forecast_data = get_tomorrow_weather_forecast(TOMORROW_API_KEY, lat, lon, interval)
    
    if forecast_data is None:
        logger.error("Failed to retrieve forecast data")
        return "Failed to retrieve forecast data"
    
    try:
        intervals = forecast_data['timelines'][interval]
        plots = plot_weather(intervals, lat, lon, interval)
        
        # Render the template with all plots
        return render_template(
            'forecast.html', 
            temp_plot_div=plots[0], 
            humidity_plot_div=plots[1], 
            wind_speed_plot_div=plots[2], 
            pressure_plot_div=plots[3],
            cloud_base_plot_div=plots[4], 
            cloud_ceiling_plot_div=plots[5], 
            cloud_cover_plot_div=plots[6],
            dew_point_plot_div=plots[7], 
            evapotranspiration_plot_div=plots[8], 
            apparent_temp_plot_div=plots[9],
            wind_direction_plot_div=plots[10], 
            wind_gust_plot_div=plots[11]
        )
    except KeyError as e:
        logger.error(f"Unexpected data structure: {e}")
        return f"Unexpected forecast data structure: {e}"
    except Exception as e:
        logger.exception("Error while generating weather plot")
        return f"Error generating weather plot: {str(e)}"


def plot_weather(data, lat, lon, interval):
    logger.debug(f"Plotting weather data. First entry: {data[0]}")
    
    # Find the local timezone based on latitude and longitude
    tf = TimezoneFinder()
    local_timezone = pytz.timezone(tf.timezone_at(lat=lat, lng=lon))

    # Convert UTC timestamps to local time
    timestamps = [
        datetime.fromisoformat(entry['time'][:-1]).replace(tzinfo=pytz.utc).astimezone(local_timezone).strftime('%Y-%m-%d %H:%M:%S') 
        for entry in data
    ]

    # Extracting values
    temperatures = [entry['values']['temperature'] for entry in data]
    humidities = [entry['values']['humidity'] for entry in data]
    wind_speeds = [entry['values']['windSpeed'] for entry in data]
    pressures = [entry['values']['pressureSurfaceLevel'] for entry in data]
    cloud_bases = [entry['values']['cloudBase'] for entry in data]
    cloud_ceilings = [entry['values']['cloudCeiling'] for entry in data]
    cloud_covers = [entry['values']['cloudCover'] for entry in data]
    dew_points = [entry['values']['dewPoint'] for entry in data]
    apparent_temperatures = [entry['values']['temperatureApparent'] for entry in data]
    wind_directions = [entry['values']['windDirection'] for entry in data]
    wind_gusts = [entry['values']['windGust'] for entry in data]

    # Define a common height for all plots
    plot_height = 571

    # Creating individual plots for each statistic

    # Temperature plot
    temp_fig = go.Figure()
    temp_fig.add_trace(go.Scatter(x=timestamps, y=temperatures, mode='lines', name='Temperature (°C)'))
    temp_fig.update_layout(
        title='Temperature Over Time',
        xaxis_title='Time',
        yaxis_title='Temperature (°C)',
        xaxis_tickangle=-45,
        height=plot_height
    )
    temp_plot_div = pio.to_html(temp_fig, full_html=False)

    # Humidity plot
    humidity_fig = go.Figure()
    humidity_fig.add_trace(go.Scatter(x=timestamps, y=humidities, mode='lines', name='Humidity (%)'))
    humidity_fig.update_layout(
        title='Humidity Over Time',
        xaxis_title='Time',
        yaxis_title='Humidity (%)',
        xaxis_tickangle=-45,
        height=plot_height
    )
    humidity_plot_div = pio.to_html(humidity_fig, full_html=False)

    # Wind Speed plot
    wind_speed_fig = go.Figure()
    wind_speed_fig.add_trace(go.Scatter(x=timestamps, y=wind_speeds, mode='lines', name='Wind Speed (m/s)'))
    wind_speed_fig.update_layout(
        title='Wind Speed Over Time',
        xaxis_title='Time',
        yaxis_title='Wind Speed (m/s)',
        xaxis_tickangle=-45,
        height=plot_height
    )
    wind_speed_plot_div = pio.to_html(wind_speed_fig, full_html=False)

    # Pressure plot
    pressure_fig = go.Figure()
    pressure_fig.add_trace(go.Scatter(x=timestamps, y=pressures, mode='lines', name='Pressure (hPa)'))
    pressure_fig.update_layout(
        title='Pressure Over Time',
        xaxis_title='Time',
        yaxis_title='Pressure (hPa)',
        xaxis_tickangle=-45,
        height=plot_height
    )
    pressure_plot_div = pio.to_html(pressure_fig, full_html=False)

    # Cloud Base plot
    cloud_base_fig = go.Figure()
    cloud_base_fig.add_trace(go.Scatter(x=timestamps, y=cloud_bases, mode='lines', name='Cloud Base (km)'))
    cloud_base_fig.update_layout(
        title='Cloud Base Over Time',
        xaxis_title='Time',
        yaxis_title='Cloud Base (km)',
        xaxis_tickangle=-45,
        height=plot_height
    )
    cloud_base_plot_div = pio.to_html(cloud_base_fig, full_html=False)

    # Cloud Ceiling plot
    cloud_ceiling_fig = go.Figure()
    cloud_ceiling_fig.add_trace(go.Scatter(x=timestamps, y=cloud_ceilings, mode='lines', name='Cloud Ceiling (km)'))
    cloud_ceiling_fig.update_layout(
        title='Cloud Ceiling Over Time',
        xaxis_title='Time',
        yaxis_title='Cloud Ceiling (km)',
        xaxis_tickangle=-45,
        height=plot_height
    )
    cloud_ceiling_plot_div = pio.to_html(cloud_ceiling_fig, full_html=False)

    # Cloud Cover plot
    cloud_cover_fig = go.Figure()
    cloud_cover_fig.add_trace(go.Scatter(x=timestamps, y=cloud_covers, mode='lines', name='Cloud Cover (%)'))
    cloud_cover_fig.update_layout(
        title='Cloud Cover Over Time',
        xaxis_title='Time',
        yaxis_title='Cloud Cover (%)',
        xaxis_tickangle=-45,
        height=plot_height
    )
    cloud_cover_plot_div = pio.to_html(cloud_cover_fig, full_html=False)

    # Dew Point plot
    dew_point_fig = go.Figure()
    dew_point_fig.add_trace(go.Scatter(x=timestamps, y=dew_points, mode='lines', name='Dew Point (°C)'))
    dew_point_fig.update_layout(
        title='Dew Point Over Time',
        xaxis_title='Time',
        yaxis_title='Dew Point (°C)',
        xaxis_tickangle=-45,
        height=plot_height
    )
    dew_point_plot_div = pio.to_html(dew_point_fig, full_html=False)

    if interval == "hourly":
        # Evapotranspiration plot
        evapotranspirations = [entry['values'].get('evapotranspiration', None) for entry in data]
        evapotranspiration_fig = go.Figure()
        evapotranspiration_fig.add_trace(go.Scatter(x=timestamps, y=evapotranspirations, mode='lines', name='Evapotranspiration (mm)'))
        evapotranspiration_fig.update_layout(
            title='Evapotranspiration Over Time',
            xaxis_title='Time',
            yaxis_title='Evapotranspiration (mm)',
            xaxis_tickangle=-45,
            height=plot_height
        )
        evapotranspiration_plot_div = pio.to_html(evapotranspiration_fig, full_html=False)
    else:
        evapotranspiration_plot_div = None

    # Apparent Temperature plot
    apparent_temp_fig = go.Figure()
    apparent_temp_fig.add_trace(go.Scatter(x=timestamps, y=apparent_temperatures, mode='lines', name='Apparent Temperature (°C)'))
    apparent_temp_fig.update_layout(
        title='Apparent Temperature Over Time',
        xaxis_title='Time',
        yaxis_title='Apparent Temperature (°C)',
        xaxis_tickangle=-45,
        height=plot_height
    )
    apparent_temp_plot_div = pio.to_html(apparent_temp_fig, full_html=False)

    # Wind Direction plot
    wind_direction_fig = go.Figure()
    wind_direction_fig.add_trace(go.Scatter(x=timestamps, y=wind_directions, mode='lines', name='Wind Direction (°)'))
    wind_direction_fig.update_layout(
        title='Wind Direction Over Time',
        xaxis_title='Time',
        yaxis_title='Wind Direction (°)',
        xaxis_tickangle=-45,
        height=plot_height
    )
    wind_direction_plot_div = pio.to_html(wind_direction_fig, full_html=False)

    # Wind Gust plot
    wind_gust_fig = go.Figure()
    wind_gust_fig.add_trace(go.Scatter(x=timestamps, y=wind_gusts, mode='lines', name='Wind Gust (m/s)'))
    wind_gust_fig.update_layout(
        title='Wind Gust Over Time',
        xaxis_title='Time',
        yaxis_title='Wind Gust (m/s)',
        xaxis_tickangle=-45,
        height=plot_height
    )
    wind_gust_plot_div = pio.to_html(wind_gust_fig, full_html=False)

    return (
        temp_plot_div, humidity_plot_div, wind_speed_plot_div, pressure_plot_div,
        cloud_base_plot_div, cloud_ceiling_plot_div, cloud_cover_plot_div,
        dew_point_plot_div, evapotranspiration_plot_div, apparent_temp_plot_div,
        wind_direction_plot_div, wind_gust_plot_div
    )


if __name__ == '__main__':
    app.run(debug=True)
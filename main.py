from flask import Flask, request, render_template
import requests
from datetime import datetime

app = Flask(__name__)

def get_weather_and_aqi(city):
    api_key = "7d20fc40dd41492488d2f91ea265388b"
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    air_quality_url = "https://api.openweathermap.org/data/2.5/air_pollution"

    weather_params = {"q": city, "appid": api_key, "units": "metric"}
    try:
        weather_response = requests.get(weather_url, params=weather_params)
        weather_data = weather_response.json()

        if weather_data["cod"] != 200:
            return {"error": weather_data["message"]}
        else:
            weather = weather_data["weather"][0]["description"]
            temp = weather_data["main"]["temp"]
            feels_like = weather_data["main"]["feels_like"]
            min_temp = weather_data["main"]["temp_min"]
            max_temp = weather_data["main"]["temp_max"]
            pressure = weather_data["main"]["pressure"]
            humidity = weather_data["main"]["humidity"]
            wind_speed = weather_data["wind"]["speed"]
            visibility = weather_data["visibility"]
            sunrise = datetime.utcfromtimestamp(weather_data["sys"]["sunrise"]).strftime('%I:%M %p')
            sunset = datetime.utcfromtimestamp(weather_data["sys"]["sunset"]).strftime('%I:%M %p')

            lat = weather_data["coord"]["lat"]
            lon = weather_data["coord"]["lon"]

            air_quality_params = {"lat": lat, "lon": lon, "appid": api_key}
            air_quality_response = requests.get(air_quality_url, params=air_quality_params)
            air_quality_data = air_quality_response.json()

            aqi_value = air_quality_data["list"][0]["main"]["aqi"]
            pm2_5 = air_quality_data["list"][0]["components"]["pm2_5"]
            pm10 = air_quality_data["list"][0]["components"]["pm10"]

            aqi_categories = {
                1: "Good",
                2: "Fair",
                3: "Moderate",
                4: "Poor",
                5: "Very Poor"
            }
            aqi_description = aqi_categories.get(aqi_value, "Unknown")

            visibility_km = visibility / 1000  # Convert meters to kilometers

            return {
                "weather": weather.capitalize(),
                "temp": temp,
                "feels_like": feels_like,
                "min_temp": min_temp,
                "max_temp": max_temp,
                "pressure": pressure,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "visibility": visibility_km,
                "sunrise": sunrise,
                "sunset": sunset,
                "aqi": aqi_value,
                "aqi_description": aqi_description,
                "pm2_5": pm2_5,
                "pm10": pm10
            }

    except Exception as e:
        return {"error": f"Error fetching data: {str(e)}"}

@app.route("/", methods=["GET", "POST"])
def index():
    data = {}
    city = None  # Initialize city as None
    if request.method == "POST":
        city = request.form.get("city")
        if city:
            data = get_weather_and_aqi(city)
    return render_template("index.html", data=data, city=city)  # Pass both data and city

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

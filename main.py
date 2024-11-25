from flask import Flask, request, render_template
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

def get_weather_and_aqi(city):
    api_key = "7d20fc40dd41492488d2f91ea265388b"
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    air_quality_url = "https://api.openweathermap.org/data/2.5/air_pollution"

    weather_params = {"q": city, "appid": api_key, "units": "metric"}
    try:
        # Fetch weather data
        weather_response = requests.get(weather_url, params=weather_params)
        weather_data = weather_response.json()

        logging.debug(f"Weather response: {weather_data}")

        if weather_data["cod"] != 200:
            return {"error": weather_data["message"]}
        else:
            weather = weather_data["weather"][0]["description"]
            temp = weather_data["main"]["temp"]
            humidity = weather_data["main"]["humidity"]
            wind_speed = weather_data["wind"]["speed"]

            # Fetch latitude and longitude
            lat = weather_data["coord"]["lat"]
            lon = weather_data["coord"]["lon"]

            # Fetch air quality data
            air_quality_params = {"lat": lat, "lon": lon, "appid": api_key}
            air_quality_response = requests.get(air_quality_url, params=air_quality_params)
            air_quality_data = air_quality_response.json()

            logging.debug(f"Air quality response: {air_quality_data}")

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

            return {
                "weather": weather.capitalize(),
                "temperature": temp,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "aqi_value": aqi_value,
                "aqi_description": aqi_description,
                "pm2_5": pm2_5,
                "pm10": pm10
            }

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {str(e)}")
        return {"error": "API request failed. Please check your internet connection or API key."}
    except KeyError as e:
        logging.error(f"KeyError: {str(e)}")
        return {"error": f"Unexpected data format from API: {str(e)}"}

@app.route("/", methods=["GET", "POST"])
def index():
    data = {}
    if request.method == "POST":
        city = request.form.get("city")
        if city:
            data = get_weather_and_aqi(city)
    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
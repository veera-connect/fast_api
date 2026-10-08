from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx

app = FastAPI()

# Serve CSS, JS, images, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")


# Open http://localhost:5000/
@app.get("/")
async def home():
    return FileResponse("static/index.html")


@app.get("/weather")
async def get_weather(city: str):

    async with httpx.AsyncClient() as client:

        # 1. Find city coordinates
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        geo_response = await client.get(
            geo_url,
            params=geo_params
        )

        geo_data = geo_response.json()

        if "results" not in geo_data:
            return {
                "success": False,
                "error": "City not found"
            }

        location = geo_data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        # 2. Get weather
        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,weather_code",
            "timezone": "auto"
        }

        weather_response = await client.get(
            weather_url,
            params=weather_params
        )

        weather_data = weather_response.json()
        current = weather_data["current"]

        return {
            "success": True,
            "city": location["name"],
            "country": location.get("country"),
            "temperature": current["temperature_2m"],
            "humidity": current["relative_humidity_2m"],
            "weather_code": current["weather_code"]
        }
import os

import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather(city: str) -> dict | None:
    """Return OpenWeatherMap current-weather JSON, or None if the request fails."""
    api_key = os.getenv("API_KEY")
    if not api_key or not city.strip():
        return None
    response = requests.get(
        WEATHER_URL,
        params={
            "appid": api_key,
            "q": city.strip(),
            "units": "imperial",
        },
        timeout=15,
    )
    if response.status_code != 200:
        return None
    return response.json()

         
def get_weather():
    print("\n **** Get Current Weather Conditions ****")

    city = input("\nEnter a city name: ")
    data = fetch_weather(city)
    if data is None:
        print("An error occurred.")
        return
    weather = data["weather"][0]["description"]
    temperature = round(data["main"]["temp"], 2)
    print(f"\nWeather: {weather}")
    print(f"Temperature: {temperature}°F")


if __name__ == "__main__":
    get_weather()
#
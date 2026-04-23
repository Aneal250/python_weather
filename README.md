# Weather

Small demo that shows **current weather** from the [OpenWeatherMap](https://openweathermap.org/api) API: a **Streamlit** web UI (`app.py`) and an optional **CLI** (`weather.py`).

## Prerequisites

- Python 3.10+ (uses `dict | None` type hints)
- An OpenWeatherMap API key

## Setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
API_KEY=your_openweathermap_api_key_here
```

## Run the Streamlit app

```bash
source .venv/bin/activate
streamlit run app.py
```

Enter a city (e.g. `Austin, US`) and submit. After results load, use **Save this city** under the chart to persist it; open the sidebar to **Fetch** saved cities. Results use **imperial** units (°F, mph) and are cached for five minutes.

## Run the CLI (optional)

```bash
source .venv/bin/activate
python weather.py
```

You will be prompted for a city name.

## Project layout

| File | Role |
|------|------|
| `app.py` | Streamlit UI |
| `saved_cities.py` | Persisted saved-city list (`saved_cities.json`) |
| `weather.py` | `fetch_weather()` + CLI |
| `requirements.txt` | Dependencies |

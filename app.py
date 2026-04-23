import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from saved_cities import format_saved_at, load_entries, upsert_city
from weather import fetch_weather

load_dotenv()

_LAST_CITY = "last_display_city"
_LAST_DATA = "last_display_data"
_SAVED_FLASH = "_saved_flash"


@st.cache_data(ttl=300, show_spinner=False)
def _cached_fetch(city: str) -> dict | None:
    return fetch_weather(city)


def _render_weather(data: dict) -> None:
    name = data.get("name", "")
    country = data.get("sys", {}).get("country", "")
    loc = f"{name}, {country}" if country else name
    st.subheader(loc)

    main = data["main"]
    w0 = data["weather"][0]
    temp = round(main["temp"], 1)
    feels = round(main["feels_like"], 1)

    c1, c2, c3 = st.columns(3)
    c1.metric("Temperature", f"{temp} °F")
    c2.metric("Feels like", f"{feels} °F")
    c3.metric("Humidity", f"{main['humidity']}%")

    st.info(w0["description"].title())

    chart_df = pd.DataFrame(
        {
            "°F": [
                main["temp"],
                main["feels_like"],
                main["temp_min"],
                main["temp_max"],
            ]
        },
        index=["Current", "Feels like", "Low", "High"],
    )
    st.caption("Temperature snapshot")
    st.bar_chart(chart_df, height=280)

    wind = data.get("wind", {})
    if "speed" in wind:
        st.caption(f"Wind: **{wind['speed']} mph**")


st.set_page_config(page_title="Weather", page_icon="🌤️", layout="centered")

st.title("Weather")
st.caption("Current conditions (OpenWeatherMap, imperial)")

if not os.getenv("API_KEY"):
    st.error("Set `API_KEY` in `.env` for your OpenWeatherMap API key.")
    st.stop()

if _SAVED_FLASH in st.session_state:
    st.success(f"Saved **{st.session_state.pop(_SAVED_FLASH)}**.")

saved = load_entries()
city_to_fetch: str | None = None

with st.sidebar:
    st.header("Saved cities")
    if not saved:
        st.caption("Look up a city below, then **Save this city** under the results.")
    else:
        for entry in saved:
            st.markdown(f"**{entry['city']}**  \nSaved: {format_saved_at(entry['saved_at'])}")
            if st.button("Fetch", key=entry["id"], type="secondary"):
                city_to_fetch = entry["city"]

with st.form("lookup", clear_on_submit=False):
    city = st.text_input("City", placeholder="e.g. Austin, US")
    submitted = st.form_submit_button("Get weather", type="primary")

if submitted and city.strip():
    city_to_fetch = city.strip()

data: dict | None = None
display_city: str | None = None

if city_to_fetch:
    with st.spinner("Fetching…"):
        fetched = _cached_fetch(city_to_fetch)
    if fetched is None:
        st.error("Could not load weather. Check the city name and your API key.")
    else:
        st.session_state[_LAST_CITY] = city_to_fetch
        st.session_state[_LAST_DATA] = fetched
        data = fetched
        display_city = city_to_fetch
elif _LAST_DATA in st.session_state and _LAST_CITY in st.session_state:
    data = st.session_state[_LAST_DATA]
    display_city = st.session_state[_LAST_CITY]

if data is not None and display_city is not None:
    _render_weather(data)
    st.divider()
    if st.button("Save this city", key="save_under_results", type="secondary"):
        upsert_city(display_city)
        st.session_state[_SAVED_FLASH] = display_city
        st.rerun()
elif submitted and not city.strip():
    st.warning("Enter a city name.")

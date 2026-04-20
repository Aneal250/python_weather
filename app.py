import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from weather import fetch_weather

load_dotenv()


@st.cache_data(ttl=300, show_spinner=False)
def _cached_fetch(city: str) -> dict | None:
    return fetch_weather(city)


st.set_page_config(page_title="Weather", page_icon="🌤️", layout="centered")

st.title("Weather")
st.caption("Current conditions (OpenWeatherMap, imperial)")

if not os.getenv("API_KEY"):
    st.error("Set `API_KEY` in `.env` for your OpenWeatherMap API key.")
    st.stop()

with st.form("lookup", clear_on_submit=False):
    city = st.text_input("City", placeholder="e.g. Austin, US")
    submitted = st.form_submit_button("Get weather", type="primary")

if submitted:
    if not city.strip():
        st.warning("Enter a city name.")
    else:
        with st.spinner("Fetching…"):
            data = _cached_fetch(city.strip())
        if data is None:
            st.error("Could not load weather. Check the city name and your API key.")
        else:
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

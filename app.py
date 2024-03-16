import asyncio
import requests
import threading
import numpy as np
import cv2
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit_drawable_canvas import st_canvas

import time

import matplotlib.pyplot as plt

# Indstillinger
st.set_page_config(page_title="UNFML24 Tegn og Gæt", page_icon=".streamlit/unflogo.svg", layout="wide")
dsize = (28, 28)
TEGNINGER = ["apple", "banana", "birthday cake", "blueberry", "bread", "broccoli", "carrot", "cookie", "coffee cup", "donut", "fish", "frying pan", "grapes", "hot dog", "ice cream", "lobster", "lollipop", "mushroom", "onion", "pear", "peas", "pineapple", "pizza", "strawberry", "watermelon"]

# definer funktion der henter reponse og returnerer svar
async def get_prediction(team_nr, avatar, request_url, input_image):
    await asyncio.sleep(5 * np.random.random_sample())
    response = "Jeg ved det ikke"
    st.chat_message("assistant", avatar=avatar).write(response)

# definer funktion der sender tegning til alle hold
async def parallel_calls(tegning_til_klassificering):
    calls = [get_prediction(team_nr, avatar, api_url, tegning_til_klassificering) for team_nr, (avatar, api_url) in enumerate(st.session_state.teams.items())]
    await asyncio.gather(*calls)

async def spinner():
    st.spinner(text="Får svar fra deltagere...")
    await asyncio.sleep(10)

# Title på side
col1, _, col2 = st.columns([10, 1, 2])
col1.title("Tegn og gæt konkurrence")
col1.subheader("*Hvem har bygget den bedste tegn-og-gæt maskine?*")
col2.image('.streamlit/unflogo.svg', width=160)

st.divider()

# Game setup: Tilmeld hold
if "teams" not in st.session_state.keys():
    st.session_state.teams = dict()

possible_teams = ["🧑‍🎨", "🧑‍💻", "🤖", "🦖", "🦄", "🐉", "🐲", "🐍", "🐢", "🦎", "🦚", "🦜", "🦢", "🦩", "🦤", "🪶", "🦅", "🦆", "🐓", "🦃", "🦉", "🦚", "🦜", "🦢", "🦩", "🦤", "🪶", "🦅", "🦆", "🐓", "🦃", "🦉", "🦚", "🦜"]

with st.form("Nyt hold", clear_on_submit=False):
    avatar = st.selectbox(
        'Vælg et hold tegn',
        [a for a in possible_teams if a not in st.session_state.teams.keys()],
        index=None,)
    team_api_url = st.text_input("Indtast holdets api url")
    
    if st.form_submit_button("Tilmeld hold", use_container_width=True, type='primary'):
        if avatar != None and team_api_url != None:
            st.session_state.teams[avatar] = team_api_url
    
    # Vis tilmeldte hold
    if st.session_state.teams:
        st.caption("Tilmeldte hold:")
        for avatar, api_url in st.session_state.teams.items():
            st.write(f"{avatar}: {api_url}")
    
        #definer holdenes gæt
        st.session_state.guesses = ['' for _ in st.session_state.teams.keys()]

    if st.form_submit_button("Genstart konkurrencen", use_container_width=True):
        st.session_state.teams = dict()

st.divider()

# To colonner: Første til tegning, anden til api forbindelser
col1, _, col2 = st.columns([1, 0.05, 1])

# Tegneboks
with col1:
    
    streg = st.slider("Stregtykkelse", 25, 50, 30, 1)
    tegning = st_canvas(
        fill_color="rgba(255, 165, 0, 0)",  # Fixed fill color with some opacity
        stroke_width= streg,
        stroke_color="#000000",
        background_color="#FFFFFF",
        background_image = None,
        update_streamlit=True,
        height = 750,
        width = 750,
        drawing_mode="freedraw",
        key="canvas",
    )
    
    # Konverter tegning til sort/hvid, inverter farver og lav størrelsen om
    tegning_til_klassificering = cv2.cvtColor(tegning.image_data.astype(np.uint8),cv2.COLOR_BGR2GRAY)
    tegning_til_klassificering = cv2.bitwise_not(tegning_til_klassificering)
    tegning_til_klassificering = cv2.resize(tegning_til_klassificering, dsize = dsize, interpolation = cv2.INTER_AREA)

with col2:
    st.write("")
    st.write("")
    # Når der er tegnet, sendes tegningen til alle holdene
    if tegning_til_klassificering.max() > 0:
        # API forbindelse
        loop = asyncio.new_event_loop()
        loop.create_task(parallel_calls(tegning_til_klassificering))
        loop.run_until_complete(spinner())

st.divider()
st.caption("UNFML24 Tegn og Gæt konkurrence - bygget af UNFML24 with :heart:")
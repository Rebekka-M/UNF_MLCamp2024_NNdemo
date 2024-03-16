import requests
import threading
import numpy as np
import cv2
import streamlit as st
from streamlit_drawable_canvas import st_canvas

import matplotlib.pyplot as plt

# Indstillinger
st.set_page_config(page_title="UNFML24 Tegn og Gæt", page_icon=".streamlit/unflogo.svg", layout="wide")
dsize = (28, 28)

# definer funktion der henter reponse og returnerer svar
def get_prediction(team_number, request_url, input_image):
    #response = requests.post(request_url, json={"image": input_image})
    response = "apple"
    prediction[team_number] = response

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

with st.form("Nyt hold"):
    avatar = st.selectbox(
        'Vælg et hold tegn',
        [a for a in possible_teams if a not in st.session_state.teams.keys()],
        index=None,)
    team_api_url = st.text_input("Indtast holdets api url")
    
    if st.form_submit_button("Tilmeld hold", use_container_width=True, type='primary'):
        st.session_state.teams[avatar] = team_api_url
    elif st.form_submit_button("Genstart konkurrencen", use_container_width=True):
        st.session_state.teams = dict()
    
    # Vis tilmeldte hold
    if st.session_state.teams:
        st.caption("Tilmeldte hold:")
        for avatar, api_url in st.session_state.teams.items():
            st.write(f"{avatar}: {api_url}")

st.divider()

# To colonner: Første til tegning, anden til api forbindelser
col1, _, col2 = st.columns([1, 0.05, 1])

# Tegneboks
with col1:
    streg = st.slider("Stregtykkelse", 25, 50, 40, 1)
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
    st.subheader("Her kommer holdenes gæt:")

    # Når der er tegnet, sendes tegningen til alle holdene
    if tegning_til_klassificering.max() > 0:
        # API forbindelse
        threads = []
        prediction = [None]*len(st.session_state.teams)
        for team_nr, (avatar, api_url) in enumerate(st.session_state.teams.items()):
            thread = threading.Thread(target=get_prediction, args=(team_nr,api_url, tegning_til_klassificering))
            threads.append(thread)
        
        starting = [t.start() for t in threads]
        joining = [t.join() for t in threads]

        for i, avatar in enumerate(st.session_state.teams.keys()):
            st.chat_message("assistant", avatar=avatar).write(prediction[i])

st.divider()
st.caption("UNFML24 Tegn og Gæt konkurrence - bygget af UNFML24 with :heart:")
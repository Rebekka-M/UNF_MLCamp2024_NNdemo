import os
import streamlit as st

from load_models import DriveWrapper
from modules.game_setup import choose_avatar, get_model
from modules.competition import write_tegn_og_gaet

# Indstillinger
st.set_page_config(page_title="UNFML24 Tegn og Gæt", page_icon=".streamlit/unflogo.svg", layout="wide")

# Title på side
col1, _, col2 = st.columns([10, 1, 2])
col1.title("Tegn og gæt konkurrence")
col1.subheader("*Hvem har bygget den bedste tegn-og-gæt maskine?*")
col2.image('.streamlit/unflogo.svg', width=160)

st.divider()

st.session_state.team_models = None
st.session_state.avatars = None

# Load models if models folder is empty
if len(os.listdir("models")) == 0:
    drive = DriveWrapper()
    drive.load_models()

# Lad alle tilmeldte hold vælge deres avatar
with st.form(key='columns_in_form'):
    team_models = {team[:-4]: get_model(f"models/{team}") for team in os.listdir("models")}
    avatars = choose_avatar(team_models.keys())
    
    submit_button = st.form_submit_button(
        "Start konkurrence",
        type="primary",
        use_container_width=True,
    )

    reset_button = st.form_submit_button(
        "Genindlæs hold",
        type="secondary",
        use_container_width=True,
    )

    if submit_button:
        st.session_state.team_models = team_models
        st.session_state.avatars = avatars


    if reset_button:
        drive = DriveWrapper()
        drive.load_models()
        st.cache_data.clear()
        st.cache_resource.clear()

st.divider()

write_tegn_og_gaet(
    st.session_state.team_models,
    st.session_state.avatars)

st.caption("UNFML24 Tegn og Gæt konkurrence - bygget af UNFML24 with :heart:")
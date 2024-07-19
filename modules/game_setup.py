# """Game setup"""

import streamlit as st
import torch

from configs import  AVATARS, TEGNINGER

@st.cache_resource
def get_model(path):
    """Load model from path"""
    # Load the saved model
    model = torch.jit.load(path)


    # Set the model to evaluation mode
    model.eval()
    
    return model

@st.cache_data(experimental_allow_widgets=True)
def choose_avatar(_teams: list):
    """Choose avatar for each team"""
    avatars = {}

    for team in _teams:
        col1, col2 = st.columns([1, 1])
        col1.write(f"Hold {team}")
        avatars[team] = col2.selectbox(
            f"Hold {team}", AVATARS,
            label_visibility="collapsed", 
            index=None,
            placeholder="Vælg avatar",
        )
    
    return avatars
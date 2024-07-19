import streamlit as st
from streamlit_drawable_canvas import st_canvas
import cv2
import numpy as np
import torch

import time

from configs import TEGNINGER, dsize


# definer funktion der henter reponse og returnerer svar
def predict(model, image):
    start_time = time.time()
    image = torch.tensor(image).float()
    image = image.to(next(model.parameters()).device)
    image = image.reshape(-1, 1, 28, 28)
    with torch.no_grad():
        y_hat_prob = model(image)
        y_hat_prob = torch.nn.functional.softmax(y_hat_prob, dim=1)
        y_hat = torch.argmax(y_hat_prob, dim=1)

    y_hat = y_hat.detach().numpy()[0]
    y_hat_prob = y_hat_prob[0].detach().numpy()

    prob = round(y_hat_prob[y_hat] * 100, 2)
    execution_time = time.time() - start_time

    return {
        'response': f"Jeg er {prob}% sikker på at det er *{TEGNINGER[y_hat]}*", 
        'time': execution_time
    }
    
def get_predictions(tegning_til_klassificering, team_models: dict = None, avatars: dict = None):
    print(team_models, avatars)
    predictions = {
        avatar: predict(team_models[team],tegning_til_klassificering)
        for team, avatar in avatars.items()
    }
    print(predictions)
    # rank predictions based on smallest time
    predictions = dict(sorted(predictions.items(), key=lambda item: item[1]['time']))
    for avatar, prediction in predictions.items():
        st.chat_message("assistant", avatar=avatar).write(prediction['response'])


def prepare_and_send_image(tegning, team_models: dict = None, avatars: dict = None):
    if tegning is not None:
        tegning_til_klassificering = cv2.cvtColor(tegning.astype(np.uint8),cv2.COLOR_BGR2GRAY)
        tegning_til_klassificering = cv2.bitwise_not(tegning_til_klassificering)
        tegning_til_klassificering = cv2.resize(tegning_til_klassificering, dsize = dsize, interpolation = cv2.INTER_AREA)

        if tegning_til_klassificering.max() > 0:
            get_predictions(tegning_til_klassificering, team_models, avatars)

@st.experimental_fragment()
def write_tegn_og_gaet(team_models: dict = None, avatars: dict = None):
    if team_models and avatars:
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
            
        with col2:
            st.write("")
            st.write("")
            # Når der er tegnet, sendes tegningen til alle holdene
            prepare_and_send_image(tegning.image_data, team_models, avatars)

    st.divider()
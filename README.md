# UNF_MLCamp2024_NNdemo
Streamlit app til live demo og konkurrance af de neurale netværk trænet i UNF Machine Learning Camp 2024 til tegn og gæt.

## Data
Data er hentet fra [GCP Quick, Draw!](https://storage.googleapis.com/quickdraw_dataset/full/numpy_bitmap) og består af billeder af forskellige hverdagsgenstande. Hver tegning er repræsenteret som et 28x28 pixel billede i gråtoner. 

For at hente bestemte data klasser kan følgende kode bruges:
```python
import io
import requests
import numpy as np

def get_doodles(name: str):
    url = f'https://storage.googleapis.com/quickdraw_dataset/full/numpy_bitmap/{name}.npy'
    r = requests.get(url, stream = True)
    return np.load(io.BytesIO(r.content))

get_doodles('apple')
```
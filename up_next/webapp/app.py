import pickle
import pandas as pd
from .. import viz, discover
from flask import Flask, request, render_template, jsonify


with open('up_next/webapp/sim_artist_model.pkl', 'rb') as f:
    model = pickle.load(f)
app = Flask(__name__, static_url_path="")


@app.route('/')
def index():
    """Return the main page."""
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """Return folium map."""
    artist = request.json
    untapped = model.find_similar_artist_venues(artist)
    m = viz.add_multi_artist_markers(artist, untapped)    
    # return jsonify({'probability': prediction[0][1]})
    return m
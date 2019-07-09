import pickle
import pandas as pd
from .. import viz, discover
from flask import Flask, request, render_template, jsonify


with open('up_next/webapp/sim_artist_model.pkl', 'rb') as f:
    model = pickle.load(f)
app = Flask(__name__, static_url_path="")

fp = 'up_next/data/cleaned/artists_list.csv'
artists_list = pd.read_csv(fp)['artist'].tolist()

@app.route('/')
def index():
    """Return the main page."""
    return render_template('index.html', artists=artists_list)


@app.route('/predict', methods=['GET', 'POST'])
def display():
    """Return folium map."""
    data = request.json
    artist = data['user_input']
    untapped = model.find_similar_artist_venues(artist)
    m = viz.add_multi_artist_markers(artist, untapped)    
    m.save('templates/artist_map.html')
    print(
        'HERE HERE HERE', m
    )
    # return jsonify({'probability': prediction[0][1]})
    # return jsonify({1:1})
    # return m
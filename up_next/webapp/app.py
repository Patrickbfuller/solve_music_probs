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
    return render_template('bootstrap_index.html', artists=artists_list)


@app.route('/predict', methods=['GET', 'POST'])
def display():
    """Return folium map."""
    data = request.json
    artist = data['artist_input']
    max_new_cities = int(data['max_cities'])
    num_artists = int(data['num_artists'])
    cutoff_dist = int(data['cutoff_dist'])
    untapped = model.find_similar_artist_venues(
        main_artist=artist,
        max_new_cities=max_new_cities,
        num_artists=num_artists,
        cutoff_dist=cutoff_dist
        )
    artist_map = viz.AritstMap(artist, untapped)
    map_html = artist_map.get_map_html()
    # m = viz.add_multi_artist_markers(artist, untapped) 
    # m_html = m._repr_html_()
    return map_html
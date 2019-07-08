# Python code for depicting map of artist concerts.

import folium

unplayed_colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'black',
                   'beige', 'darkblue', 'darkgreen', 'lightblue', 'lightgreen']


def get_under_twelve(i):
    """Recursive function to subtract 12 until less than 12"""
    if i >= 12:
        i -= 12
        i = get_under_twelve(i)
    return i

def get_home_icon():
    """Instantiate a home icon"""
    return folium.Icon(icon='home',
                       color='black',
                       icon_color='yellow')

def get_unplayed_icon(i):
    """Return a folium.Icon object with a particular color for an artist"""
    i = get_under_twelve(i)
    color = unplayed_colors[i]
    icon=folium.Icon(icon='fire',
                     color=color,
                     icon_color='white')
    return icon

# Set a map with good broad view of entire US
# m = folium.Map(location=(42,-100), zoom_start=5)

def add_city_marker(artist, city_dict, icon=None):
    """
    Add a marker for a city. Default to 'gray home' for main artist.
    For similar artists pass in an icon object.
    """
    if icon==None:
        icon = get_home_icon()
    cityname = city_dict['city']
    latlong = city_dict['latlong']

    info = artist+'\n-\n'+cityname

    folium.Marker(location=latlong,
              popup=info,
              tooltip=artist,
              icon=icon
             ).add_to(m)
    # return m

def add_marker_pair(main_aritst, sim_artist, sim_artist_idx, new_location_dict):
    """
    Add a marker for the unplayed and played locations in a new_location dictionary.
    """
    played_city_dict = new_location_dict['played']
    add_city_marker(main_aritst, played_city_dict)

    unplayed_city_dict = new_location_dict['unplayed']
    unplayed_icon = get_unplayed_icon(sim_artist_idx)
    add_city_marker(sim_artist, unplayed_city_dict, icon=unplayed_icon)
    # return m

def add_sim_artist_markers(main_aritst, sim_artist_dict, sim_artist_idx):
    """
    Add markers for each new city from an artist.
    New locations being a list of dictionaries with keys:
    'unplayed' and 'played.
    """
    sim_artist = sim_artist_dict['artist']
    new_locations = sim_artist_dict['new locations']
    for new_location in new_locations:
        add_marker_pair(main_aritst, sim_artist, sim_artist_idx, new_location)
    # return m

m = folium.Map(location=(42,-100), zoom_start=5)

def add_multi_artist_markers(main_aritst, similar_artists:list):
    """
    For each artist dictionary in similar artists, add markers 
    for unplayed cities.
    """
    if type(similar_artists)!= list:
        return similar_artists
    for idx, sim_artist in enumerate(similar_artists):
        add_sim_artist_markers(main_aritst, sim_artist, idx)
    return m
import folium

# unplayed_colors=[‘red’, ‘blue’, ‘green’, ‘purple’, ‘orange’, ‘darkred’,
#  ’lightred’, ‘beige’, ‘darkblue’, ‘darkgreen’, ‘cadetblue’, ‘darkpurple’, 
#  ‘white’, ‘pink’, ‘lightblue’, ‘lightgreen’, ‘gray’, ‘black’]
unplayed_colors = ['red']


# Set a map with good broad view of entire US
m = folium.Map(location=(42,-100), zoom_start=5)

home_icon = folium.Icon(icon='home',
                        color='lightgray',
                        icon_color='lightblue')

def get_artist_icon(i=0):
    """Return a folium.Icon object with a particular color for an artist"""
    color = unplayed_colors[i]
    icon=folium.Icon(icon='fire',
                     color=color,
                     icon_color='white')
    return icon

def add_city_marker(artist, city_dict, icon=None):
    """
    Add a marker for a city. Default to 'gray home' for main artist.
    For similar artists pass in an icon object.
    """
    if icon==None:
        icon = home_icon
    cityname = city_dict['city']
    latlong = city_dict['latlong']

    info = artist+'\n-\n'+cityname

    folium.Marker(location=latlong,
              popup=info,
              tooltip=artist,
              icon=icon
             ).add_to(m)
    # return m

def add_new_locations_row(main_aritst, sim_artist, new_location_dict):
    """
    Add a marker for the unplayed and played locations in a new_location dictionary.
    """
    played = new_location_dict['played']
    add_city_marker(main_aritst, played)

    unplayed = new_location_dict['unplayed']
    icon = get_artist_icon()
    add_city_marker(sim_artist, unplayed, icon=icon)
    return m



# def display_similar_artist(similar_artist:dict):
#     artist = similar_artist['artist']
#     print(artist)
#     color = unplayed_colors[0]
#     for location in similar_artist['new locations']:
#         add
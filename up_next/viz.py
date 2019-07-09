# Python code for depicting map of artist concerts.

import folium

unplayed_colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'black',
                   'beige', 'darkblue', 'darkgreen', 'lightblue', 'lightgreen']
unplayed_colors = [
    '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF',
    '#00FFFF', '#FF8800', '#FF0088', '#8800FF', '#BFF844'
]


def get_under_ten(i):
    """Recursive function to subtract 10 until less than 10"""
    if i >= 10:
        i -= 10
        i = get_under_ten(i)
    return i

def get_home_icon():
    """Instantiate a home icon"""
    return folium.Icon(icon='home',
                       color='lightgray',
                       icon_color= '#505050')

def get_unplayed_icon(i):
    """Return a folium.Icon object with a particular color for an artist"""
    i = get_under_ten(i)
    color = unplayed_colors[i]
    icon=folium.Icon(icon='fire',
                     color='black',
                     icon_color=color)
    return icon

# Set a map with good broad view of entire US
# m = folium.Map(location=(42,-100), zoom_start=5)

# def add_city_marker(artist, city_dict, icon=None):
#     """
#     Add a marker for a city. Default to 'gray home' for main artist.
#     For similar artists pass in an icon object.
#     """
#     if icon==None:
#         icon = get_home_icon()
#     cityname = city_dict['city']
#     latlong = city_dict['latlong']

#     info = artist+'\n-\n'+cityname

#     folium.Marker(location=latlong,
#               popup=info,
#               tooltip=artist,
#               icon=icon
#              ).add_to(m)
#     # return m

# def add_marker_pair(main_artist, sim_artist, sim_artist_idx, new_location_dict):
#     """
#     Add a marker for the unplayed and played locations in a new_location dictionary.
#     """
#     played_city_dict = new_location_dict['played']
#     add_city_marker(main_artist, played_city_dict)

#     unplayed_city_dict = new_location_dict['unplayed']
#     unplayed_icon = get_unplayed_icon(sim_artist_idx)
#     add_city_marker(sim_artist, unplayed_city_dict, icon=unplayed_icon)
#     # return m

# def add_sim_artist_markers(main_artist, sim_artist_dict, sim_artist_idx):
#     """
#     Add markers for each new city from an artist.
#     New locations being a list of dictionaries with keys:
#     'unplayed' and 'played.
#     """
#     sim_artist = sim_artist_dict['artist']
#     new_locations = sim_artist_dict['new locations']
#     for new_location in new_locations:
#         add_marker_pair(main_artist, sim_artist, sim_artist_idx, new_location)
#     # return m

# m = folium.Map(location=(42,-100), zoom_start=5)

# def add_multi_artist_markers(main_artist, sim_artist_cities:list):
#     """
#     For each artist dictionary in similar artists, add markers 
#     for unplayed cities.
#     """
#     if type(sim_artist_cities)!= list:
#         return sim_artist_cities
#     for idx, sim_artist in enumerate(sim_artist_cities):
#         add_sim_artist_markers(main_artist, sim_artist, idx)
#     return m

class AritstMap():
    """
    Class for instantiating a folium map and then displaying 
    artist markers.
    """
    
    def __init__(self, main_artist, sim_artist_cities:list):
        self.m = folium.Map(location=(42,-100), zoom_start=5)
        self.main_artist = main_artist
        self.sim_artist_cities = sim_artist_cities
        self.add_multi_artist_markers()

    def add_city_marker(self, artist, city_dict, icon=None):
        """
        Add a marker for a city. Default to 'gray home' for main artist.
        For similar artists pass in an icon object.
        """
        if icon==None:
            icon = get_home_icon()
        cityname = city_dict['city']
        latlong = city_dict['latlong']

        info = artist+'\n-\n'+cityname

        marker = folium.Marker(location=latlong,
                               popup=info,
                               tooltip=artist,
                               icon=icon
                              )
        marker.add_to(self.m)

    def add_marker_pair(self, sim_artist, sim_artist_idx, new_location_dict):
        """
        Add a marker for the unplayed and played locations in a new_location dictionary.
        """
        played_city_dict = new_location_dict['played']
        self.add_city_marker(self.main_artist, played_city_dict)

        unplayed_city_dict = new_location_dict['unplayed']
        unplayed_icon = get_unplayed_icon(sim_artist_idx)
        self.add_city_marker(sim_artist, unplayed_city_dict, icon=unplayed_icon)

    def add_sim_artist_markers(self, sim_artist_dict, sim_artist_idx):
        """
        Add markers for each new city from an artist.
        New locations being a list of dictionaries with keys:
        'unplayed' and 'played.
        """
        sim_artist = sim_artist_dict['artist']
        new_locations = sim_artist_dict['new locations']
        for new_location in new_locations:
            self.add_marker_pair(sim_artist, sim_artist_idx, new_location)

    def add_multi_artist_markers(self):
        """
        For each artist dictionary in similar artists, add markers 
        for unplayed cities.
        """
        for idx, sim_artist in enumerate(self.sim_artist_cities):
            self.add_sim_artist_markers(sim_artist, idx)
    
    def add_legend(self):
        """ Add a legend with a color and cosine sim for each artist. """
        pass
    
    def show(self):
        """Return a folium map object for viewing in a notebook"""
        return self.m 

    def get_map_html(self):
        """Return a string of html for a folium map"""
        m_html = self.m._repr_html_()
        return m_html

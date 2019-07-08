import folium

# unplayed_colors=[‘red’, ‘blue’, ‘green’, ‘purple’, ‘orange’, ‘darkred’,
#  ’lightred’, ‘beige’, ‘darkblue’, ‘darkgreen’, ‘cadetblue’, ‘darkpurple’, 
#  ‘white’, ‘pink’, ‘lightblue’, ‘lightgreen’, ‘gray’, ‘black’]
unplayed_colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'black',
                   'beige', 'darkblue', 'darkgreen', 'lightblue', 'lightgreen']

home_icon = folium.Icon(icon='home',
                        color='lightgray',
                        icon_color='lightblue')

def get_under_twelve(i):
    """Recursive function to subtract 12 until less than 12"""
    if i >= 12:
        i -= 12
        i = get_under_twelve(i)
    return i

def get_unplayed_icon(i):
    """Return a folium.Icon object with a particular color for an artist"""
    i = get_under_twelve(i)
    color = unplayed_colors[i]
    icon=folium.Icon(icon='fire',
                     color=color,
                     icon_color='white')
    return icon


class ConcertsMap():
    """Class for storing a folium map and adding markers"""

    def __init__(self):
        """Start a map of US"""
        self.m = folium.Map(location=(42,-100), zoom_start=5)

    def add_city_marker(self, artist, city_dict, icon=None):
        """ From below"""
        if icon==None:
            icon = home_icon
        city_name = city_dict['city']
        latlong = city_dict['latlong']

        info = artist+'\n-\n'+city_name


        folium.Marker(location=latlong,
              popup=info,
              tooltip=artist,
              icon=icon
             ).add_to(self.m)
    
    def add_marker_pair(self, main_aritst, sim_artist, new_location_dict, unplayed_icon=None):
        """
        Add a marker for the unplayed and played locations in a new_location dictionary.
        """
        played = new_location_dict['played']
        self.add_city_marker(main_aritst, played)

        unplayed = new_location_dict['unplayed']
        self.add_city_marker(sim_artist, unplayed, icon=unplayed_icon)

    def add_sim_artist_markers(self, main_aritst, sim_artist, new_locations:list, artist_idx=None):
        """
        Add markers for each new city from an artist.
        New locations being a list of dictionaries with keys:
        'unplayed' and 'played.
        """
        if artist_idx==None:
            artist_idx=0
        unplayed_icon = get_unplayed_icon(artist_idx)
        for new_location in new_locations:
            self.add_marker_pair(main_aritst, sim_artist, unplayed_icon, new_location)

    def show(self):
        """Dislpay map"""
        return self.m
    




# # Set a map with good broad view of entire US
# m = folium.Map(location=(42,-100), zoom_start=5)

# home_icon = folium.Icon(icon='home',
#                         color='lightgray',
#                         icon_color='lightblue')


# def add_city_marker(artist, city_dict, icon=None):
#     """
#     Add a marker for a city. Default to 'gray home' for main artist.
#     For similar artists pass in an icon object.
#     """
#     if icon==None:
#         icon = home_icon
#     cityname = city_dict['city']
#     latlong = city_dict['latlong']

#     info = artist+'\n-\n'+cityname

#     folium.Marker(location=latlong,
#               popup=info,
#               tooltip=artist,
#               icon=icon
#              ).add_to(m)
#     # return m

# def add_marker_pair(main_aritst, sim_artist, unplayed_icon, new_location_dict):
#     """
#     Add a marker for the unplayed and played locations in a new_location dictionary.
#     """
#     played = new_location_dict['played']
#     add_city_marker(main_aritst, played)

#     unplayed = new_location_dict['unplayed']
#     add_city_marker(sim_artist, unplayed, icon=unplayed_icon)
#     return m

# def add_sim_artist_markers(main_aritst, sim_artist, new_locations:list, artist_idx=None):
#     """
#     Add markers for each new city from an artist.
#     New locations being a list of dictionaries with keys:
#     'unplayed' and 'played.
#     """
#     if artist_idx==None:
#         artist_idx=0
#     unplayed_icon = get_unplayed_icon(artist_idx)
#     for new_location in new_locations:
#         add_marker_pair(main_aritst, sim_artist, unplayed_icon, new_location)
#     return m











# def display_similar_artist(similar_artist:dict):
#     artist = similar_artist['artist']
#     print(artist)
#     color = unplayed_colors[0]
#     for location in similar_artist['new locations']:
#         add
# Python script for getting information about similar artists

# Includes: 
# SimilarArtistModel
#   find_artists_sim_to

from sklearn.neighbors import NearestNeighbors
from haversine import haversine

class SimilarArtistModel():
    """
    A nearest neighbor model for finding information about similar artists.
    Fits to a dataframe of artists and one hot encoded playlist flags during instantiation.
    """
    def __init__(self, dataframe):
        """
        Fitting a nearest neighbor model to a dataframe of artists and hot 
        encoded playlist flags.
        """
        self.artists = dataframe[['artist']]
        self.playlists = dataframe.drop('artist', axis=1)
        self.model = NearestNeighbors(n_neighbors=5, metric='cosine', n_jobs=-1)
        self.model.fit(self.playlists)

    def find_artists_sim_to(self, main_artist:str, n_neighbors=None):
        """Find the artists appearing in same playlists most frequently."""
        art1_idx = self.artists.index[self.artists['artist']==main_artist][0] # sliced to extract from nested index object
        if n_neighbors == None:
            n_neighbors = 20
        self.distances, self.indices, = self.model.kneighbors(self.playlists, n_neighbors+1)

        sim_artist_dists = self.distances[art1_idx][1:]
        sim_artist_idxs = self.indices[art1_idx][1:]

        similars = []
        for dist, idx in zip(sim_artist_dists, sim_artist_idxs): 
            similar_artist = self.artists.loc[idx,'artist']
            similars.append(
                (similar_artist, round(dist,3))
                )
        return similars





# Helper function to find_unplayed_cities
def get_artist_cities(concerts_df, artist):
    """Find the unique cities where an artist plays"""
    artist_df = concerts_df.loc[concerts_df['artist']==artist]
    return artist_df['location'].unique()

# Helper function to pilfer
def find_unplayed_cities(concerts_df, main_artist, similar_artist):
    """Find cities where another artist has played, but the main artist HAS NOT."""
    main_places = get_artist_cities(concerts_df, main_artist)
    similar_artist_places = get_artist_cities(concerts_df, similar_artist)

    unplayed_cities = []
    for place in similar_artist_places:
        if place not in main_places:
            unplayed_cities.append(place)
    return unplayed_cities

# Helper function to NeighborModel
def prep_main_artist_df(concerts_df, main_artist):
    """ Takes in a dataframe of concert towns and dates for many artists 
    Returns a dataframe of unique towns for one artist """
    main_df = concerts_df.loc[concerts_df['artist']== main_artist, ['location', 'lat', 'lng']]
    main_df.drop_duplicates(subset='location', inplace=True)
    main_df.reset_index(drop=True, inplace=True)
    return main_df


class NeighborModel():
    """
    A nearest neighbor model for finding 1 closest city using haversine computation.
    """

    def __init__(self, concerts_df, main_artist):
        """
        Store a df of an artists conccerts including cities w latlongs
        AND fit a haversine nearest neighbors model to it.
        """
        self.main_artist_df = prep_main_artist_df(concerts_df, main_artist)
        self.model = NearestNeighbors(n_neighbors=1, n_jobs=-1, metric=haversine)
        self.model.fit(self.main_artist_df[['lat', 'lng']])

    def find_closest_city(self, latlong):
        """Given lat long and find the closest city in a stored dataframe of cities."""
        distances, indices = self.model.kneighbors(latlong)
        nn_distance, nn_index = distances[0][0], indices[0][0]
        nn_city = self.main_artist_df.loc[nn_index, 'location']
        nn = self.main_artist_df.loc[nn_index]
        nn_city = nn['location']
        nn_latlong = nn[['lat', 'lng']]
        nn_distance_miles = round(nn_distance / 1.609)
        return nn_city, nn_latlong, nn_distance_miles


def get_neighbors_of_new_cities(concerts_df, main_artist, new_cities:list):
    """For each """
    # Instantiate custom neighbor model
    neighbor_model = NeighborModel(concerts_df, main_artist)

    unplayed_and_played = []
    for new_city in new_cities:
        new_latlong = concerts_df.loc[concerts_df['location']==new_city, ['lat', 'lng']]
        new_latlong.drop_duplicates(inplace=True) # can remove if un-duped

        played, played_ll, distance = neighbor_model.find_closest_city(new_latlong)

        unplayed_and_played.append(
            {'unplayed': {'city': new_city, 'latlong': new_latlong},
             'played': {'city': played, 'latlong': played_ll},
             'distance': distance}
            )
    return unplayed_and_played


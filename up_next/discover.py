# Python code for getting information about similar artists

# Includes: 
# SimilarArtistModel
#   find_artists_sim_to

from sklearn.neighbors import NearestNeighbors
from haversine import haversine


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


class NeighborCitiesModel():
    """
    A nearest neighbor model for finding 1 closest city using haversine computation.
    """

    def __init__(self, concerts_df, main_artist):
        """
        Store a df of an artists conccerts including cities w latlongs
        AND fit a haversine nearest neighbors model to it.
        """
        self.main_artist_df = prep_main_artist_df(concerts_df, main_artist)
        self.model = NearestNeighbors(n_neighbors=1, metric=haversine)
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
    """
    Given a list of cities where an artist has not been, return info on nearest cities
    where an artist HAS been. 
    Input a list of strings for city names, return a list of dictionaries whose keys are:
    'unplayed', 'played', 'distance'. The values for 'unplayed' and 'played' are 
    dictionaries with keys: 'city' and 'latlong'.
    """
    # Instantiate custom neighbor model
    neighbor_model = NeighborCitiesModel(concerts_df, main_artist)

    unplayed_and_played = []
    for new_city in new_cities:
        new_latlong = concerts_df.loc[concerts_df['location']==new_city, ['lat', 'lng']]
        new_latlong.drop_duplicates(inplace=True) # can remove if un-duped

        played, played_ll, distance = neighbor_model.find_closest_city(new_latlong)

        unplayed_and_played.append(
            {'unplayed': {'city': new_city, 'latlong': list(new_latlong.values[0])},
             'played': {'city': played, 'latlong': list(played_ll)},
             'distance': distance}
            )
    return unplayed_and_played

def pilfer_similar_artist(concerts_df, main_artist, similar_artist, max_new_cities=None, cutoff_dist=None):
    """Given an main artist, and a similar artist, find info about cities where a similar artist has played 
    but the main artist has not. Remove any cities that are close together(within cutoff). Return a list of
    new cities and their corresponding data, with closer cities appearing first."""
    if max_new_cities == None:
        max_new_cities = 5
    if cutoff_dist == None:
        cutoff_dist == 100
    # Find new cities
    new_cities = find_unplayed_cities(concerts_df, main_artist, similar_artist)

    # Retrieve info for closet played cities.
    cities_and_nns = get_neighbors_of_new_cities(concerts_df,main_artist,new_cities)

    # Remove any new cities that are with in the cutoff distance 
    relevant_cities_and_nns = [x for x in cities_and_nns if x['distance'] > cutoff_dist]

    # Sort new cities by nearest to played
    cities_by_dist = sorted(relevant_cities_and_nns, key=lambda x: x['distance'])
    return cities_by_dist[:max_new_cities]


class SimilarArtistModel():
    """Nearest Neighbors model for finding similar artists by playlist co-presence."""

    def __init__(self, playlists_df, concerts_df=None):
        """
        Fitting a nearest neighbor model to a dataframe of artists and hot 
        encoded playlist flags and storing the dataframe.
        Option to pass in concerts df for find_similar_artist_venues() method at instantiaton.
        Or free to omit if just using find_artists_sim_to() method.
        """
        self.artists = playlists_df[['artist']]
        self.playlists = playlists_df.drop('artist', axis=1)
        self.model = NearestNeighbors(n_neighbors=5, metric='cosine')
        self.model.fit(self.playlists)
        self.concerts = concerts_df

    def find_artists_sim_to(self, main_artist, n_neighbors=None):
        """
        Find the artists appearing in same playlists most frequently.
        Return a list of tuples of the with similar playlist appearences and 
        their cosine distance in hyperspace.
        """
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

    def find_similar_artist_venues(self, main_artist, concerts_df=None, num_artists=None,
                                   max_new_cities=None, cutoff_dist=None):
        """
        Returns locations of similar artists starting with 
        most similar artist and cities furthest to closest
        """
        if num_artists==None:
            num_artists = 3
        if max_new_cities==None:
            max_new_cities =5
        if not concerts_df:
            concerts_df = self.concerts
        if main_artist not in concerts_df['artist'].values:
            return f'{main_artist.title()}: No Recent Shows OR Not In 20 Of Top Playlists'
        try:
            results = []
            similar_artists = self.find_artists_sim_to(main_artist, n_neighbors=num_artists)
            for artist, cosine_sim in similar_artists:
                sim_artist_dict = {}
                sim_artist_dict['artist'] = artist
                sim_artist_dict['cosine_sim'] = cosine_sim
                sim_artist_dict['new locations'] = pilfer_similar_artist(concerts_df, main_artist, artist,
                                                                         cutoff_dist=cutoff_dist,
                                                                         max_new_cities=max_new_cities)
                results.append(sim_artist_dict)
            return results
        except:
            return 'Unexpected Error'


def get_latest_date(concerts_df, artist:str, location:str):
    """Find the most recent concert of an artist in a location."""
    concerts = concerts_df[
        (concerts_df ['artist']==artist) & (concerts_df['location']==location)
    ]
    return concerts['date'].max()
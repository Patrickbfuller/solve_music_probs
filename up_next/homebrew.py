import pandas as pd
import json
import time
import random
from haversine import haversine
from sklearn.neighbors import NearestNeighbors


import googlemaps
with open('/Users/patrickfuller/.secrets/googlemap_api.json') as f:
    api_key = json.load(f)['api_key']
gmaps = gmaps = googlemaps.Client(key=api_key)


# - - Functions for Spotify's 'spotipy' python api wrapper - - 
def wait(constant=3, maybe_more=3):
    """Abbreviated version of time.sleep().
    Always will sleep for constant length, and will add 
    a random length between 0 and 'maybe_more'
    """
    time.sleep(constant + random.random() * maybe_more)

def extract_name_and_id(response:dict):
    """Given the result of a spotipy playlist query, return 
    a id and name of the playlist results.
    Parameters:
    ---
    Input: Dictionary
    ---
    Output: Dictionary
    """
    result = {}
    playlist_objects = response['playlists']['items']
    for playlist in playlist_objects:
        id_code = playlist['id']
        name = playlist['name']
        owner_id = playlist['owner']['id']
        result[id_code] = {'name': name, 'owner_id': owner_id}
    return result

def get_artists_in_playlist(playlist_data):
    """Given a spotify playlist tracks item, return a list of
     unique artists with tracks on the playlist"""
    artists = []
    track_list = playlist_data['items']
    for track_data in track_list:
        artist_data = track_data['track']['artists']
        for artist in artist_data:
            artists.append(artist['name'])
    return list(set(artists))


# - - Functions for scraping concerts from songkick.com with selenium - - 

def get_url_for_artist(browser, artist:str):
    """Given a selenium webdriver browser object, and an artist name,
    return the url of the artists page on songkick.com"""
    url_prefix = 'https://www.songkick.com/search?utf8=%E2%9C%93&type=initial&query='
    query = artist.replace(' ', '+')
    browser.get(url_prefix+query)
    selector = 'li.artist > div.subject > p.summary a'
    a_element = browser.find_element_by_css_selector(selector)
    # a_element = browser.find_element_by_css_selector('p.summary a')  # Old version didn't skip non artists
    return a_element.get_attribute('href')

def set_url(browser, page:str):
    """Given a selenium webdriver browser object and a page 
    title(calendar or gigography only), return the url for the page.
    WILL RETURN NONE if link is not on the page."""
    try:
        element = browser.find_element_by_css_selector(
            f'#{page}-summary > h2 > small > a')
        return element.get_attribute('href')
    except:
        return None

def get_shows_dates_in_ul(browser, artist:str, ul_path:str):
    """Given a selenium webdriver browser object and a 
    selector path for a unordered list, retreive the dates
    and locations of concerts in that list"""
    shows_list = []
    list_items = browser.find_elements_by_css_selector(ul_path+' > li')
    for li in list_items:
        try:
            loc_el = li.find_element_by_css_selector('p.location > span > span')
        except:
            continue      # Elements that do not have a location 
                          # are just inconsistent bolded timestamps
                          # and should be skipped to avoid dups
        time_el = li.find_element_by_css_selector('time')
        location = loc_el.text 
        time = time_el.get_attribute('datetime')
        row = {'artist': artist, 'loc': location, 'date': time}
        shows_list.append(row)
    return shows_list

def get_pages_shows_dates(browser, url:str, artist:str):
    """WRITE ME"""
    multipage_shows_list = []
    for i in range(2,4):    
        # 3 Pages of concerts should be enough.. ~ 3 yrs for Jason Aldean
        shows_list = get_shows_dates_in_ul(browser=browser,
                                           artist=artist,
                                           ul_path='#event-listings > ul')
        multipage_shows_list.extend(shows_list)
        if len(shows_list) < 50:
            break
        new_url = url + f'?page={i}'
        browser.get(new_url)
    return multipage_shows_list

def get_artist_concerts(browser, artist:str):
    """WRITE ME"""
    master_artist_shows_list=[]
    try:
        artist_url = get_url_for_artist(browser, artist)
        wait(2,1)
    except:
        return []
    browser.get(artist_url)
    # check if artist is recent
    past_summary = get_shows_dates_in_ul(browser=browser,
                                       artist=artist,
                                       ul_path='#gigography-summary > ul')
    if not past_summary:    # Some artists don't even have a gig-summary
        return []               # Skip these artists
    recent_check = past_summary[-1]['date'][:4]     # Look at last element
    if int(recent_check) < 2015:                    # in summary table
        return [] 
    wait()
    cal_url = set_url(browser, 'calendar')   # None if the link isn't present
    gig_url = set_url(browser, 'gigography')
    if not cal_url:
        # scrape upcoming on main page only 
        # if theres not a link to more upcomings
        shows_list = get_shows_dates_in_ul(browser=browser,
                                           artist=artist,
                                           ul_path='#calendar-summary > ul')
        master_artist_shows_list.extend(shows_list)
    if not gig_url:
        # Scrape past on main page only
        # if no link to more past gigs
        # Already have the list from recent check
        master_artist_shows_list.extend(past_summary)   # Already have the 
                                                        # list from 'recent check'

    if cal_url:
        # Scrape calendar pages if more upcomings on another page.
        browser.get(cal_url)
        wait()
        shows_list = get_pages_shows_dates(browser=browser,url=cal_url,artist=artist)
        master_artist_shows_list.extend(shows_list)
    if gig_url:
        # Scrape gigography pages if more past gigs on another page
        browser.get(gig_url)
        wait()
        shows_list = get_pages_shows_dates(browser=browser,url=gig_url,artist=artist)
        master_artist_shows_list.extend(shows_list)
    return master_artist_shows_list


# - - Functions for Neighboring Concert Locations

def get_latlong(query:str):
    """Use google maps geocode api to find the lat and long for a given text query."""
    response = gmaps.geocode(query)
    latlong = response[0]['geometry']['location']
    lat = latlong['lat']
    lng = latlong['lng']
    return lat, lng         # moved to gmap.py

def get_artist_places(ref_df, artist):
    """Write Me!!!"""
    artist_df = ref_df.loc[ref_df['artist']==artist]
    return artist_df['location'].unique()

def find_unplayed_cities(ref_df, main_artist, similar_artist):
    """ WRITE ME """
    main_places = get_artist_places(ref_df, main_artist)
    similar_artist_places = get_artist_places(ref_df, similar_artist)

    unplayed_cities = []
    for place in similar_artist_places:
        if place not in main_places:
            unplayed_cities.append(place)
    return unplayed_cities

def prep_main_artist_df(ref_df, main_artist):
    """ Takes in a dataframe of concert towns and dates for many artists 
    Returns a dataframe of unique towns for one artist """
    main_df = ref_df.loc[ref_df['artist']== main_artist, ['location', 'lat', 'lng']]
    main_df.drop_duplicates(subset='location', inplace=True)
    main_df.reset_index(drop=True, inplace=True)
    return main_df


class NeighborModel():
    """Write Me """

    def __init__(self, ref_df, main_artist):
        """ Store a df of cities w latlongs, and fit a nn model to it """
        self.main_artist_df = prep_main_artist_df(ref_df, main_artist)
        self.model = NearestNeighbors(n_neighbors=1, n_jobs=-1, metric=haversine)
        self.model.fit(self.main_artist_df[['lat', 'lng']])

    def predict(self, latlong):
        """Take in a lat long and predict the closest city from local df """
        distances, indices = self.model.kneighbors(latlong)
        nn_distance, nn_index = distances[0][0], indices[0][0]
        nn_city = self.main_artist_df.loc[nn_index, 'location']
        return nn_city, nn_distance


def get_neighbors_of_new_cities(ref_df, main_artist, new_cities:list):
    """WRITE ME"""
    # Instantiate custom neighbor model
    neighbor_model = NeighborModel(ref_df, main_artist)

    new_cities_and_neighbors = []
    for new_city in new_cities:
        new_latlong = ref_df.loc[ref_df['location']==new_city, ['lat', 'lng']]
        new_latlong.drop_duplicates(inplace=True) # can remove if un-duped
                                                            
        neighbor, distance = neighbor_model.predict(new_latlong)
        distance_miles = round(distance / 1.609)

        # date = ref_df.loc[
        #     (ref_df['artist']==main_artist & ref_df['location']==neighbor)
        #     , 'date'].values[0]

        new_cities_and_neighbors.append(
            {'new':new_city, 'played':neighbor, 'distance': distance_miles}
            )
    return new_cities_and_neighbors
        

def pilfer_similar_artist(ref_df, main_artist, similar_artist, max_new_cities=None):
    """WRITE ME"""
    if max_new_cities == None:
        max_new_cities = 5
    # Find new cities
    new_cities = find_unplayed_cities(ref_df, main_artist, similar_artist)
    # Match those cities with closest old cities, and the distance
        # Train model
    # Order new cities by distance to old(DESC)
    cities_and_neighbors = get_neighbors_of_new_cities(ref_df,main_artist,new_cities)
    cities_by_dist = sorted(cities_and_neighbors, key=lambda x: x['distance'], reverse=True)
    return cities_by_dist[:max_new_cities]



class SimilarArtistModel():
    """Write Me"""
    def __init__(self, dataframe):
        """WRITE ME"""
        self.artists = dataframe[['artist']]
        self.playlists = dataframe.drop('artist', axis=1)
        self.model = NearestNeighbors(n_neighbors=5, metric='cosine', n_jobs=-1)
        self.model.fit(self.playlists)

    def find_artists_sim_to(self, main_artist, n_neighbors=None):
        """WRITE ME"""
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

    def find_similar_artist_venues(self, main_artist, shows_df, num_artists=None, max_new_cities=None):
        """
        Returns locations of similar artists starting with 
        most similar artist and cities furthest to closest
        """
        if num_artists==None:
            num_artists = 3
        if max_new_cities==None:
            max_new_cities =5
        if main_artist not in shows_df['artist'].values:
            return f'{main_artist.title()}: No Recent Shows OR Not In 20 Of Top Playlists'
        try:
            results = []
            similar_artists = self.find_artists_sim_to(main_artist, n_neighbors=num_artists)
            for artist, cosine_sim in similar_artists:
                sim_artist_dict = {}
                sim_artist_dict['artist'] = artist
                sim_artist_dict['cosine_sim'] = cosine_sim
                sim_artist_dict['new locations'] = pilfer_similar_artist(shows_df, main_artist, artist)
                results.append(sim_artist_dict)
            return results
        except:
            return 'Unexpected Error'
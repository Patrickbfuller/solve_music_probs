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


def get_url_for_artist(browser, artist:str):
    """Given a selenium webdriver browser object, and an artist name,
    return the url of the artists page on songkick.com"""
    url_prefix = 'https://www.songkick.com/search?utf8=%E2%9C%93&type=initial&query='
    query = artist.replace(' ', '+')
    browser.get(url_prefix+query)
    a_element = browser.find_element_by_css_selector('p.summary a')
    return a_element.get_attribute('href')

def set_url(browser, page:str):
    """Given a selenium webdriver browser object and a page 
    title(calendar or gigography only), return the url for the page"""
    try:
        element = browser.find_element_by_css_selector(f'#{page}-summary > h2 > small > a')
        return element.get_attribute('href')
    except:
        return None

def get_artist_concerts(browser, artist:str):
    url = get_url_for_artist(browser, artist)
    # if not calendar link:
    #    scrape upcoming
    # if not gigography link:
    #    scrap past shows
    # if calendar link:
    #    go to calendar link
    #    scrap
    # if gigography link:
    pass
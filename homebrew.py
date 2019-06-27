import time
import random

def wait(constant=3, maybe_more=4):
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
    title(calendar or gigography only), return the url for the page.
    WILL RETURN NONE if link is not on the page."""
    try:
        element = browser.find_element_by_css_selector(
            f'#{page}-summary > h2 > small > a')
        return element.get_attribute('href')
    except:
        return None

def get_shows_dates_in_ul(browser, ul_path:str):
    """Given a selenium webdriver browser object and a 
    selector path for a unordered list, retreive the dates
    and locations of concerts in that list"""
    shows_dates_list = []
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
        shows_dates_list.append((location, time))
    return shows_dates_list

def get_artist_concerts(browser, artist:str):
    artist_url = get_url_for_artist(browser, artist)
    browser.get(artist_url)
    wait()
    cal_url = set_url(browser, 'calendar')   # None if the link isn't present
    gig_url = set_url(browser, 'gigography')
    if not cal_url:
        #scrape upcoming on main page
        pass
    if not gig_url:
        #scrape past shows on main page
        pass
    if cal_url:
        browser.get(cal_url)
        wait()
        #scrap page
        pass
    if gig_url:
        browser.get(gig_url)
        wait()
        #scrap page
        pass
    

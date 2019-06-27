import time
import random

def wait(constant=3, maybe_more=3):
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
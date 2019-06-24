def extract_name_and_id(response):
    """Given the result of a spotipy playlist query, return a id and name of the playlist results.
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
        result[id_code] = name
    return result

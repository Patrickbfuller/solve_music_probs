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

def get_playlists_w_artist(artist, df):
    """Given an artist and a dataframe of playlists and their artist lists, 
    return playists where that artist has a song"""
    result = []
    for artist_list, playlist_id in zip(df.artists, df.playlist_id):
        if artist in artist_list:
            result.append(playlist_id)
    return result
# Python script for processing concert data
import pandas as pd
import json
import time
import googlemaps

with open('/Users/patrickfuller/.secrets/googlemap_api.json') as f:
    api_key = json.load(f)['api_key']
gmaps = gmaps = googlemaps.Client(key=api_key)

def get_latlong(query:str):
    """Use google maps geocode api to find the lat and long for a given text query."""
    response = gmaps.geocode(query)
    latlong = response[0]['geometry']['location']
    lat = latlong['lat']
    lng = latlong['lng']
    return lat, lng

def get_multi_latlongs(unique_locations:list):
    """
    Given a list of cities, assign lat and long to the cities and return 
    a dataframe with columns, 'location', 'lat', 'long'.
    """
    unique_loc_w_latlong = []
    for i, location in enumerate(unique_locations):
        row = {}
        lat, lng = get_latlong(location)
        row['location'] = location
        row['lat'] = lat
        row['lng'] = lng
        unique_loc_w_latlong.append(row)
        if i % 50 == 0:
            time.sleep(2)
        if i % 100 == 0:
            print(i)
    return pd.DataFrame(unique_loc_w_latlong)

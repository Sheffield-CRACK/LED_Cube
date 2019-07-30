import json
from datetime import datetime
from os import system
from pprint import pprint
from time import sleep

import geocoder
import numpy as np
import requests
from fake_useragent import UserAgent


def get_sats(bins_x, bins_y, bins_alt, mylat, mylon, apiKey):
    '''Query for the satellites above me right now, and return a grid with the number of satellites per cell.

    Input:
    ------
    bins, 3D numpy array:
        The edges of the bins.
    mylat, float:
        Observer's latitude, degrees
    mylon, float:
        Observer's longitude, degrees

    Output:
    -------
    grid_sats, 3D numpy array:
        A grid of the same shape as <bins>, with the satellite count per cell.
    '''


    # The API string. 
    template = "https://www.n2yo.com/rest/v1/satellite/above/{observer_lat}/{observer_lng}/{observer_alt}/{search_radius}/{category_id}&apiKey={api_key}"

    # arguments for the above.
    kwargs = dict(
        api_key=apiKey,
        observer_lat=lat,
        observer_lng=lon,
        observer_alt='0.0',
        search_radius='3',
        category_id="0"
    )

    # Prep the request
    url = template.format(**kwargs)
    ua = ua = UserAgent()
    headers = {'User-Agent':str(ua.random)}

    # Post the request
    req = requests.get(url, headers=headers)
    time_recieved = datetime.now()

    data = req.json()

    print("Recieved response at {}".format(time_recieved.strftime("%d/%m/%Y, %H:%M:%S")))
    print("\n\nI found {} satellites above you.".format(data['info']['satcount']))
    print("This is query #{}\n\n".format(data['info']['transactionscount']))

    if data['info']['satcount'] == 0:
        sats = []
    else:
        sats = data['above']

    # Clunkily make a grid of cells.
    grid_sats = np.zeros(
        (bins_alt.shape[0], bins_x.shape[0], bins_x.shape[0])
    )

    for sat in sats:
        print("\n\n--------------------------------------------")
        satlat, satlon, satalt = float(sat['satlat']), float(sat['satlng']), float(sat['satalt'])
        print("Satellite {} is at:\n  lat: {}\n  lon: {}\n  alt: {}\n".format(sat['satname'], satlat, satlon, satalt))
        
        dlat = satlat - lat
        dlon = satlon - lon

        index_alt = np.digitize(satalt, bins_alt) -1
        index_x   = np.digitize(dlat,   bins_x) -1
        index_y   = np.digitize(dlon,   bins_y) -1

        print("This satellite is in index (dlat, dlon, alt): ({}, {}, {})".format(index_x, index_y, index_alt))
        grid_sats[index_alt, index_x, index_y] += 1

    return grid_sats


with open("n2yo_details.json", 'r') as f:
    api_key = json.load(f)['api_key']

g = geocoder.ip('me')
lat, lon = g.latlng
print("This computer has a lat, long (from IP address) of:\n   {}, {}".format(lat, lon))


# Set up the grid layer.
x_cells = 11
y_cells = 11

grid_x = np.linspace(-5, 5, x_cells) # lat
grid_y = np.linspace(-5, 5, y_cells) # lon

# Manually define altitude bands
grid_alt = np.array([2000, 10000, 20000, 30000])
alt_cells = grid_alt.shape[0]

# Cells will be incrimented if they contain a satellite
print("x bins:")
print(grid_x)
print("y bins:")
print(grid_y)
print("altitude bins:")
print(grid_alt)

while True:
    grid_sats = get_sats(grid_x, grid_y, grid_alt, lat, lon, api_key)

    system('clear')
    pprint(grid_sats[3])

    sleep(0.2)

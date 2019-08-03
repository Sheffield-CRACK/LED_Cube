'''Uses python-sgp4 to calculate which satellites will cross my zenith today.
Then, make a list of those satellites. 
Print a list periodically of the satellites overhead.

requires this repo to be installed:
https://github.com/brandon-rhodes/python-sgp4
https://github.com/satellogic/orbit-predictor
'''

import glob
import io
import os
import shutil
from datetime import datetime, timedelta

import geocoder
import numpy as np
from orbit_predictor import (angles, coordinate_systems, exceptions, keplerian,
                             locations, predictors, sources, utils)
from sgp4.earth_gravity import wgs84
from sgp4.io import twoline2rv

try:
    from urllib2 import urlopen
except:
    from urllib.request import urlopen


OVERHEAD_LIMIT = 5. # Degrees

TLE_URLS = ('http://celestrak.com/NORAD/elements/weather.txt',
            'http://celestrak.com/NORAD/elements/resource.txt',
            'https://www.celestrak.com/NORAD/elements/cubesat.txt',
            'http://celestrak.com/NORAD/elements/stations.txt',
            'https://www.celestrak.com/NORAD/elements/sarsat.txt',
            'https://www.celestrak.com/NORAD/elements/noaa.txt',
            'https://www.celestrak.com/NORAD/elements/amateur.txt',
            'https://www.celestrak.com/NORAD/elements/engineering.txt')


def fetch(urls):
    """Fetch TLE from internet and save it to `destination`."""
    print("Fetching TLE data...")
    # TODO: play nicely when recollecting data
    try:
        shutil.rmtree("TLE_data")
    except:
        pass
    os.mkdir('TLE_data')

    for url in urls:
        destination = url.split('/')[-1]
        destination = os.path.join("TLE_data", destination)
    
        with open(destination, "w", encoding="utf-8") as dest:
            response = urlopen(url)
            dest.write(response.read().decode("utf-8"))

def update_passing_sats(dt=1):
    # Where am I?
    g = geocoder.ip('me')
    lat, lon = g.latlng
    me = locations.Location('me', lat, lon, 0)

    # Get the current time.
    now = datetime.utcnow()
    # Get tomorrow, as the limit on when to check
    tomorrow = now + timedelta(days=dt)
    print('I want to find satellites that pass overhead between:\n', now, '\n', tomorrow)

    # Get a database of satellites.
    fetch(TLE_URLS)
    created_files = glob.glob("TLE_data/*")
    print("TLE files:\n{}".format(created_files))

    # Now read that data into my TLE database
    database = sources.MemoryTLESource()
    # Also track all my satellite IDs
    sat_IDs = []
    print("Parsing TLE data...")
    for fname in created_files:
        with open(fname, 'r') as f:
            while True:
                name = f.readline().strip()
                if name == '':
                    break

                sat_IDs.append(name)
                tle_1 = f.readline().strip()
                tle_2 = f.readline().strip()

                tle = (tle_1, tle_2)

                database.add_tle(name, tle, now)
    print("Done!")

    print("Checking my satellites...")
    alt_lim = abs(90 - OVERHEAD_LIMIT) # Degrees

    passes = []
    will_pass = []
    
    for ID in sat_IDs:
        try:
            predictor = predictors.TLEPredictor(ID, database)
            pred = predictor.get_next_pass(
                location=me,
                when_utc=now,
                aos_at_dg=alt_lim,
                limit_date=tomorrow
            )
            # print("The object {} will pass over {} deg at:\n--> {}\n".format(ID, alt_lim, pred))
            will_pass.append(ID)
            passes.append(pred)
        except AssertionError as e:
            pass
            # print(e)
        except exceptions.NotReachable as e:
            pass
            # print(e)
        except exceptions.PropagationError as e:
            pass
            # print(e)

    # print(will_pass)
    print("\n\nFound {} satellites that will pass through the top {} degrees above lat, lon: {}, {} within the next {} day(s)\n\n\n".format(
        len(will_pass), 90-alt_lim, lat, lon, dt
    ))


    with open('passing_sats.txt', 'w') as f:
        to_write = '\n'.join(will_pass)
        f.write(to_write)
    
    for ID, pred in zip(will_pass, passes):
        print("{}\n\n".format(pred))

    return database

def sat_locations(database,
                  mylat, mylon,
                  time=None,
                  lat_bins=11, lon_bins=11,
                  alt_edges=[0, 2000, 10000, 20000, 30000, 9e99],
                  quiet=True):
    '''For the satellite IDs in passing_sats.txt, check their current location. Then,
    fill in a grid of how many satellites are in each cell of a grid.

    Inputs:
    -------
    database, MemoryTLESource
        The orbit_predictor TLE database, populated with satellites
    time, datetime.datetime, optional
        The time to calculate the grid for. If None, use datetime.datetime.utcnow(). Requires UTC
    lat_bins, int, optional
        The number of latitude bins. Used to construct a numpy linspace for the bin edges.
    lon_bins, int, optional
        The same, for longitude
    alt_edges, iterable of floats, optional
        A list of the altitude bins.
    
    Output:
    -------
    grid, 3D numpy array
        A grid populated with the number of satellites per cell, at the current time.
    '''

    if time is None:
        time = datetime.utcnow()

    # What are my bin edges?
    altrange = abs(OVERHEAD_LIMIT)
    lat_edges = np.linspace(-altrange, +altrange, lat_bins)
    lon_edges = np.linspace(-altrange, +altrange, lon_bins)

    # Init an empty grid.
    grid = np.zeros((len(alt_edges), lat_bins, lon_bins), dtype=int)

    # I might be interested in which satellite is currently overhead
    overhead_now = []

    with open('passing_sats.txt', 'r') as f:
        for line in f:
            if not quiet:
                print("\n\n-------------------------------------------------------------------------------------\n\n")
            ID = line.strip()

            # create this satellite's predictor
            predictor = predictors.TLEPredictor(ID, database)

            # The positions are returned in Earth-centric, Earth fixed coords. I need to convert those.
            ecef_location = predictor.get_only_position(time)

            ### Convert ECEF to LLA ###
            lat, lon, alt = coordinate_systems.ecef_to_llh(ecef_location)

            if not quiet:
                print("satellite ID: {}".format(ID))
                print("ECEF coords (x, y, z): {}, {}, {}".format(*ecef_location))
                print("LLS coords (lat, lon, alt): {}, {}, {}".format(lat, lon, alt))

            # transform lat, lon, to relative to me
            dlat = lat - mylat
            dlon = lon - mylon

            if not quiet:
                print("Relative to me, the satellite is at {}, {}, {}".format(dlat, dlon, alt))

            if dlat < np.min(lat_edges) or dlat > np.max(lat_edges):
                if not quiet:
                    print("Satellite is not in the visible range")
                continue
            if dlon < np.min(lon_edges) or dlon > np.max(lon_edges):
                if not quiet:
                    print("Satellite is not in the visible range")
                continue
            if alt < np.min(alt_edges) or alt > np.max(alt_edges):
                if not quiet:
                    print("Satellite is not in the visible range")
                continue

            # What indexes is this satellite in?
            index_alt   = np.digitize(alt,  alt_edges)
            index_lat   = np.digitize(dlat, lat_edges)
            index_lon   = np.digitize(dlon, lon_edges)

            # If they fall outside the range, I don't care about the object
            if not quiet:
                print("This satellite is in index (lat, lon, alt): ({}, {}, {})".format(index_lat, index_lon, index_alt))

            # Save this satellite
            grid[index_alt, index_lat, index_lon] += 1
            overhead_now.append(ID)

    return grid, overhead_now

if __name__ == "__main__":
    # Not needed in the above functions
    from pprint import pprint

    # Create the database
    database = update_passing_sats()

    # Where am I?
    me = geocoder.ip('me')
    mylat, mylon = me.latlng

    while True:
        # Time to evaluate
        now = datetime.utcnow()

        # pop the grid
        grid, satlist = sat_locations(
            database, mylat, mylon, 
            time=now, quiet=True
        )

        os.system("clear")
        if np.sum(grid):
            print("--------------------------------------")
            print(now)
            for i, subgrid in enumerate(grid):
                if np.sum(subgrid):
                    print("Layer {}".format(i))
                    pprint(subgrid)
            pprint(np.sum(grid))

            print("Satellites overhead now:\n{}".format(satlist))

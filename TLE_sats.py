'''Uses python-sgp4 to calculate which satellites will cross my zenith today.
Then, make a list of those satellites. 
Print a list periodically of the satellites overhead.

requires this repo to be installed:
https://github.com/brandon-rhodes/python-sgp4
https://github.com/satellogic/orbit-predictor
'''

import geocoder
from datetime import datetime
from orbit_predictor import (angles, coordinate_systems, exceptions, keplerian,
                             locations, sources, utils, predictors)

from sgp4.earth_gravity import wgs84
from sgp4.io import twoline2rv
from datetime import datetime, timedelta

import glob
import io
import shutil
try:
    from urllib2 import urlopen
except:
    from urllib.request import urlopen
import os

def fetch(urls):
    """Fetch TLE from internet and save it to `destination`."""
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

def update_passing_sats():
    # Where am I?
    g = geocoder.ip('me')
    lat, lon = g.latlng
    me = locations.Location('me', lat, lon, 0)

    # Get the current time.
    now = datetime.utcnow()
    # Get tomorrow, as the limit on when to check
    tomorrow = now + timedelta(days=1)
    print('', now, '\n', tomorrow)


    # Get a database of satellites. As a test case, use GPS satellites
    TLE_urls = ('http://celestrak.com/NORAD/elements/weather.txt',
                'http://celestrak.com/NORAD/elements/resource.txt',
                'https://www.celestrak.com/NORAD/elements/cubesat.txt',
                'http://celestrak.com/NORAD/elements/stations.txt',
                'https://www.celestrak.com/NORAD/elements/sarsat.txt',
                'https://www.celestrak.com/NORAD/elements/noaa.txt',
                'https://www.celestrak.com/NORAD/elements/amateur.txt',
                'https://www.celestrak.com/NORAD/elements/engineering.txt')

    fetch(TLE_urls)
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
    alt_lim = 5 # Degrees

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
    print("\n\nFound {} satellites that will pass through the top {} degrees above lat, lon: {}, {}".format(
        len(will_pass), 90-alt_lim, lat, lon
    ))


    with open('passing_sats.txt', 'w') as f:
        to_write = '\n'.join(will_pass)
        f.write(to_write)

if __name__ == "__main__":
    update_passing_sats()
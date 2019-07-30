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

test_tle = '''ISS (ZARYA)
1 25544U 98067A   19211.03329231  .00004695  00000-0  87069-4 0  9995
2 25544  51.6437 148.6985 0006091 196.9496 269.4947 15.51024086181901'''

ID, tle_1, tle_2 = test_tle.split('\n')

tle = '\n'.join([tle_1, tle_2])

g = geocoder.ip('me')
lat, lon = g.latlng
me = locations.Location('me', lat, lon, 0)

print(me)

# Get the current time.
now = datetime.utcnow()

database = sources.MemoryTLESource()

# Add the test data to the datebase
sat = twoline2rv(tle_1, tle_2, wgs84)
database.add_tle(ID, sat, now)

predictor = predictors.TLEPredictor(ID, database)

pred = predictor.get_next_pass(
    location=me,
    when_utc=now,
    max_elevation_gt=85.,
    aos_at_dg=85
)

print(pred)
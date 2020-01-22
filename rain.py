from send_cube import connect_cube, send_cube
import numpy as np

from pprint import pprint
from time import sleep

N_LAYERS = 8
N_REGISTERS = 8
N_BITS = 8

DROP_RATE = 1
RAIN_FALL_RATE = 0.6 # seconds on screen per drop

delay = RAIN_FALL_RATE / N_LAYERS

arduino = connect_cube()

# List of my raindrops. (x, y)
drops = []
while True:
    grid = np.zeros((N_LAYERS, N_REGISTERS, N_BITS))

    new_drops = []
    for drop in drops:
        layer, reg, bit = drop
        layer += 1
        if layer < N_LAYERS:
            new_drops.append((layer, reg, bit))

    # Randomly add new drops
    if np.random.rand() < DROP_RATE:
        reg = np.random.randint(0, N_REGISTERS)
        bit = np.random.randint(0, N_BITS)

        new_drop = (0, reg, bit)
        new_drops.append(new_drop)
    drops = new_drops

    for drop in drops:
        grid[drop] = 1

    send_cube(arduino, grid)

    sleep(delay)
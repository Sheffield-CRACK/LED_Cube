'''Handler to light up the LEDs.

Anode rails must be on
'''

import gpiozero
import time
import numpy as np

def flash_LED(x, y, pulse_length=10):
    '''Flash an LED at coordinate x, y for z ms
    
    Inputs:
    -------
    x, int:
        The x pin, which will have a HI voltage applied
    y, int:
        The y pin, which will have a LO voltage applied
    pulse_length, float:
        The length of the pulse in milliseconds
    '''
    print("flashing {}, {}".format(x, y))
    time.sleep(pulse_length/1000.)

def flash_grid(grid, pulse_length=10):
    '''Flash a whole grid. Takes a 2D numpy array and passes it through

    The grid is N x MxM

    The first dimension is the height axis. This is treated as the cathodes, 
    and occupy the first bloc of pins, 0 -> N

    The second two dimensions are the anodes.
    '''
    pulse_length = pulse_length * 1e-3

    N, L, M = grid.shape

    cathodes = [gpiozero.LED(pin=int(i)) for i in range(N)]
    anodes = [gpiozero.LED(pin=int(j)) for j in range(N, L*M)]

    for cathode in cathodes:
        cathode.off()
    for anode in anodes:
        anode.off()

    for i, layer in enumerate(grid):
        # APPLY VOLTAGE TO CATHODE PIN, <i>
        cathodes[i].on()
        print("Applied GND to pin {}".format(i))
        layer = layer.flatten()
        for j, is_on in enumerate(layer):
            if is_on:
                # APPLY VOLTAGE TO ANODE PIN, <j>
                print("Applied +V to pin {}".format(j))
                anodes[j].on()
            time.sleep(pulse_length)

        cathodes[i].off()
        for anode in anodes:
            anode.off()
        
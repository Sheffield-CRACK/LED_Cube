'''Handler to light up the LEDs.

Anode rails must be on
'''

import gpiozero
import time
import numpy as np

class LEDHandler(object):
    '''Control the GPIO Pins to operate the LED cube.'''
    def __init__(self, grid, pulse_duration=20e-3):
        self.X, self.Y, self.Z = grid.shape
        self.grid = grid

        # TODO:
        # Should this be a grid flash frequency, rather than a pulse duration?
        self.pulse_duration = pulse_duration

        # The cathodes are assumed to be the first dimension.
        # These will control transistors that let the current flow through
        # a specific layer.
        # Pins 0 and 1 are reserved. Don't use them.
        self.anodes = [gpiozero.DigitalOutputDevice(
            pin=i, active_high=True, initial_value=False)
            for i in range(2, self.X+2)
        ]

        # There will be Y*Z anodes. They will control whether an index is on or off.
        start = self.X + 2
        stop = start + (self.Y * self.Z)
        self.cathodes = [gpiozero.DigitalOutputDevice(
            pin=j, active_high=True, initial_value=False)
            for j in range(start, stop)
        ]


    def flash_grid(self):
        for cathode, layer in zip(self.cathodes, self.grid):
            print("Activating {}".format(cathode.pin))
            cathode.on()

            # Get the layer in 1D - the LEDs are hooked up in only 2D,
            # but arranged in 3D!
            layer = layer.flatten()

            # Activate the pins we want
            for anode, is_on in zip(self.anodes, layer):
                if is_on:
                    print("Activating pin {}".format(anode.pin))
                    anode.on()

            # Leave them on for long enough to see
            time.sleep(self.pulse_duration)
            for anode in self.anodes:
                anode.off()
            cathode.off()

    def flash_LED(self, x, y, z, pulse_duration=1):
        '''Flash the LED at coordinate (x, y, z)'''
        # LAYER 1
        # [[[0, 0, 0],
        #   [0, 0, 0],
        #   [0, 0, 0]],

        # LAYER 2
        #  [[0, 0, 0],
        #   [0, 0, 0],
        #   [0, 0, 0]],

        # LAYER 3
        #  [[0, 0, 0],
        #   [0, 0, 0],
        #   [0, 0, 0]]]

        # The anode we want is easy - just the layer.
        self.anodes[x].on()

        # The relevant cathode is less trivial
        index = 2 + (y * self.Z) + z

        print("Flashing cathode GPIO{:02d}".format(index))
        self.cathodes[index].on()

        time.sleep(pulse_duration)

        # Turn off the pins again
        self.anodes[x].off()
        self.cathodes[index].off()

    def close(self):
        '''Gracefully shutdown the pins'''
        for anode in self.anodes:
            anode.close()
        for cathode in self.cathodes:
            cathode.close()
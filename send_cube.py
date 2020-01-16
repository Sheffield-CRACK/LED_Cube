import serial
import numpy as np
import time
from pprint import pprint
import binascii

N_REGISTERS = 8 # How many registers are daisy-chained?
N_BITS      = 8 # How many bits does each SR handle? (usulaly 8)
N_LAYERS    = 8 # How many layers do we have?


def conv2byte(byte):
    '''Convert iterable data to a byte. This can be presented three ways:
      - int, either 0 or any number >0
      - bool
      - str, the string 1 vs any other string (including an empty one)

    The iterable must be exactly 8 items long. So, the follwoing will all will give the same result:
      - "00110101"
      - ['0','0','1','1','0','1','0','1']
      - [0, 0, 1, 1, 0, 1, 0, 1]
      - [False, False, True, True, False, True, False, True]

    Returns the integer form of that byte.'''

    assert len(byte) == 8, "Byte must be 8 items long, got {}".format(len(byte))

    if type(byte[0]) != str:
        byte = ['1' if bit else '0' for bit in byte]

    byte = ''.join(byte)
    out = int(byte, base=2)

    return out


def conv2byte_vect(cube):
    '''Convert a cube to bytes. The cube provided will be converted to a numpy array

    !!! BE AWARE!!!
    To write to the LED cube, it should be in the shape (N_LAYERS, N_REGISTERS, N_BITS)'''
    new_cube = []
    cube = np.array(cube)
    if cube.shape == (N_LAYERS, N_REGISTERS, N_BITS):
        for layer in cube:
            for line in layer:
                new_cube.append(conv2byte(line))
    else:
        for line in cube:
            new_cube.append(conv2byte(line))

    new_cube = bytearray(new_cube)
    return new_cube

if __name__ in "__main__":
    data = np.zeros((N_LAYERS, N_REGISTERS, N_BITS), dtype=int)
    data[0,  :,  0] = 0
    data[0,  :, -1] = 0
    data[0,  0,  :] = 0
    data[0, -1,  :] = 0

    data[-1, :,  0] = 0
    data[-1, :, -1] = 0
    data[-1, 0,  :] = 0
    data[-1,-1,  :] = 0

    data[:,  0,  0] = 0
    data[:, -1,  0] = 0
    data[:,  0, -1] = 0
    data[:, -1, -1] = 0


    # Start the serial connection
    ser = serial.Serial('/dev/cu.wchusbserial72', 9600, timeout=.1)
    print("Waiting for Arduino to start...")
    time.sleep(2)
    print("\n\n\nReady to start transmitting!")


    # Bouncing Box
    di = 1
    i = 1
    while True:
        if i == 6 or i == 0:
            di = -di
        i += di

        temp_data = np.array(data, copy=True)
        temp_data[i:i+2, i:i+2, i:i+2] = 1

        writeable_data = conv2byte_vect(temp_data)
        ser.write(writeable_data)

        time.sleep(0.1)

    ser.close()

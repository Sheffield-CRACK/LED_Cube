import gpiozero
import time

PULSE_WIDTH = 300/1000
DELAY = 5


data = gpiozero.DigitalOutputDevice(17, initial_value=False, active_high=True)
clock = gpiozero.DigitalOutputDevice(27, initial_value=False, active_high=True)

print("Okay, going")

for _ in range(8):
    data.off()
    print("Data off, sending clock pulse")
    clock.on()
    time.sleep(PULSE_WIDTH) # 100ms
    clock.off()
    print("Sent!")
    time.sleep(DELAY)

    data.on()
    print("Data on, sending clock pulse")
    clock.on()
    time.sleep(PULSE_WIDTH) # 100ms
    clock.off()
    print("Sent!")
    time.sleep(DELAY)


print("Setting data and clock both to off")
data.off()
clock.off()
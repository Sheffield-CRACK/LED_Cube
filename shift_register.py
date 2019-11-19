import gpiozero
import time

PULSE_WIDTH = 300/1000
DELAY = 5


data = gpiozero.DigitalOutputDevice(27, initial_value=False, active_high=True)
clock = gpiozero.DigitalOutputDevice(17, initial_value=False, active_high=True)
reset = gpiozero.DigitalOutputDevice(22, initial_value=True, active_high=True)

def clockpulse():
    clock.on()
    time.sleep(PULSE_WIDTH)
    clock.off()


print("Okay, going")

print("Sending reset pulse:")
reset.off()
clockpulse()
reset.on()

print("Sending data...")

for _ in range(8):
    data.off()
    print("Data off, sending clock pulse")
    clockpulse()
    print("Sent!")
    time.sleep(DELAY)

    data.on()
    print("Data on, sending clock pulse")
    clockpulse()
    print("Sent!")
    time.sleep(DELAY)


print("Setting data and clock both to off")
data.off()
clock.off()
reset.on()

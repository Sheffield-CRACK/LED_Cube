import gpiozero
import time

DELAY = 5

data = gpiozero.DigitalOutputDevice(17, initial_value=False)
clock = gpiozero.DigitalOutputDevice(18, initial_value=False)

print("Okay, going")

data.off()

clock.on()
time.sleep(DELAY) # 100ms
clock.off()
time.sleep(DELAY)

data.on()

clock.on()
time.sleep(DELAY) # 100ms
clock.off()
time.sleep(DELAY)




data.off()
clock.off()

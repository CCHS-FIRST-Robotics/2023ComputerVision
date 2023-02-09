import time
from networktables import NetworkTables

# To see messages from networktables, you must setup logging
import logging

logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize("127.0.0.1")

sd = NetworkTables.getTable("numbers")
dog = sd.getNumberArray("foo", 0)

while True:
    dog = sd.getNumberArray("foo", [])
    print(dog)
    time.sleep(1)
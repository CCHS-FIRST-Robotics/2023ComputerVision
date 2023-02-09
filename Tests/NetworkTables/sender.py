from networktables import NetworkTables
import time


NetworkTables.initialize()

numbers = NetworkTables.getTable("numbers")


my_coords = [0.5, 0.5, 2.2]
numbers.putNumberArray("foo", my_coords)
NetworkTables.flush()
time.sleep(1)
    
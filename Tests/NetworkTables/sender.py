from networktables import NetworkTables
import time

NetworkTables.get
numbers = NetworkTables.getTable("numbers")

while True:
    words = input("Enter string: ")
    numbers.putString("foo", words)
    NetworkTables.flush()
    
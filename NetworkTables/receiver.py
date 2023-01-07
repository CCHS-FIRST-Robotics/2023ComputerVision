import time
from networktables import NetworkTables

# To see messages from networktables, you must setup logging
import logging

logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize()

def valueChanged(table, key, value, isNew):
    print("valueChanged: key: '%s'; value: %s" % (key, value))


def connectionListener(connected, info):
    print(info, "; Connected=%s" % connected)


NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

sd = NetworkTables.getTable("wordz")
sd.addEntryListener(valueChanged)

while True:
    time.sleep(1)
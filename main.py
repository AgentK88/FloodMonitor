import webConnect # handles connecting to WiFi
import apiRequest # Calls Flood Level API
import time # Acquire current time

try:
    webConnect.connect()
except KeyboardInterrupt:
    machine.reset()

latestReading = apiRequest.request("latestReading")
currentLevel = apiRequest.request("currentLevel")
state = apiRequest.request("state")

t = time.localtime()
#print(t)
print("{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
        )
      )

print(latestReading, currentLevel, state)
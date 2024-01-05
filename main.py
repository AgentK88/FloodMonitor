from Pico_ePaper_37 import EPD_3in7 # ePaper driver
import webConnect # handles connecting to WiFi
import apiRequest # Calls Flood Level API
import time # Acquire current time

try:
    webConnect.connect()
except KeyboardInterrupt:
    machine.reset()

# ePaper writes something...?
# Initialize the e-paper display
epd = EPD_3in7()
    
epd.image1Gray.fill(0xff)
epd.image4Gray.fill(0xff)

# Get API values
latestReading = str(apiRequest.request("latestReading"))
currentLevel = "Current Level: " + str(apiRequest.request("currentLevel"))
state = "State: " + apiRequest.request("state")

# Show this text
epd.image4Gray.text(latestReading, 50, 10, epd.black)
epd.image4Gray.text(currentLevel, 50, 40, epd.black)
epd.image4Gray.text(state, 100, 70, epd.black)
epd.image4Gray.text("Written by Kevin Roberts", 50, 150, epd.black)

# Buffer? This is required
epd.EPD_3IN7_4Gray_Display(epd.buffer_4Gray)

# Wait for something to break...
time.sleep(10)

'''
while True:    
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

    time.sleep(900) # API updates every 15 minutes = 60*15
'''
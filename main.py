from Pico_ePaper_37 import EPD_3in7 # ePaper driver
import webConnect # handles connecting to WiFi
import apiRequest # Calls Flood Level API
import time
import ntptime # Acquire current time

# Initialize the e-paper display
epd = EPD_3in7()
    
#epd.image1Gray.fill(0xff)
#epd.image4Gray.fill(0xff)

try:
    webConnect.connect()
except KeyboardInterrupt:
    machine.reset()

# Set time - This sometimes returns errors
ntptime.settime()

while True:
    #Clear display
    epd.image4Gray.fill(0xff)
    
    # Get API values
    apiResults = apiRequest.request() # A list of values from API
    print("API values returned")
    currentLevel,latestReading,typicalRangeHigh,typicalRangeLow,state = apiResults # Unpack list in this order
    
    # Tidy up returned values as strings for display
    latestReading = str(latestReading) # Clean up date as a string
    latestReading = latestReading.replace("T", " ") # Remove chars as can't convert ISO datetime to string
    latestReading = latestReading.replace("Z", " ") # Remove chars as can't convert ISO datetime to string
    currentLevel = "Current Level: " + str(currentLevel)
    state = "State: "+ state

    # Display the river level values
    epd.image4Gray.text(latestReading, 60, 10, epd.black)
    epd.image4Gray.text(currentLevel, 60, 40, epd.black)
    epd.image4Gray.text(state, 100, 70, epd.black)
    
    # Display the current time
    t = time.localtime()
    epd.image4Gray.text("{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            t[0], t[1], t[2], t[3], t[4], t[5]
            ), 60, 110, epd.darkgray)

    # Display vanity
    epd.image4Gray.text("Written by Kevin Roberts", 50, 150, epd.grayish)
    
    # Buffer? This is required
    epd.EPD_3IN7_4Gray_Display(epd.buffer_4Gray)

    # Wait a minute
    #machine.deepsleep(900) # Deep sleep
    time.sleep(600) # API updates every 15 minutes 60*15 = 900
    print("refreshing now")

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
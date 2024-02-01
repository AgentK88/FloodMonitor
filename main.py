from Pico_ePaper_37 import EPD_3in7 # ePaper driver
import webConnect # handles connecting to WiFi
import apiRequest # Calls Flood Level API
import apiRequestTrend # Calls Flood Level API trend
import time
import ntptime # Acquire current time

# For development purposes
import gc # For garbage collection!
#import os # For checking storage

# Initialize the e-paper display
epd = EPD_3in7()
    
#epd.image1Gray.fill(0xff)
#epd.image4Gray.fill(0xff)

try:
    webConnect.connect()
except KeyboardInterrupt:
    machine.reset()

# Set time - Only if needed. Time defaults to 2021-01-01
# A client MUST NOT under any conditions use a poll interval less than 15 seconds.
tc = time.localtime()
if tc[0] == 2021: # Check if the year is 2021
    try:
        ntptime.settime()
        print("Time set")
    except OSError as error:
        print(error)

while True:
    # Check memory used and run garbage collection
    #s = os.statvfs('/')
    #print(f"Free storage: {s[0]*s[3]/1024} KB")
    print(f"Memory: {gc.mem_alloc()} of {gc.mem_free()} bytes used.")
    gc.collect() # garbage collection
    
    # Clear display - otherwise new text will displayed on top
    epd.image4Gray.fill(0xff)
    
    # Get API values
    apiResults = apiRequest.request() # A list of values from API
    currentLevel,latestReading,typicalRangeHigh,typicalRangeLow,state = apiResults # Unpack list in this order
    
    # Tidy up returned values as strings for display
    latestReading = str(latestReading) # Clean up date as a string
    latestReading = latestReading.replace("T", " ") # Remove chars as can't convert ISO datetime to string
    latestReading = latestReading.replace("Z", " ") # Remove chars as can't convert ISO datetime to string
    currentLevel = "Current Level: " + str(currentLevel)
    state = "State: " + state
    trend = "Trend: " + apiRequestTrend.requestTrend()
    
    # Display the river level values
    epd.image4Gray.text(latestReading, 60, 10, epd.black)
    epd.image4Gray.text(currentLevel, 60, 40, epd.black)
    epd.image4Gray.text(state, 100, 70, epd.black)
    epd.image4Gray.text(trend, 80, 100, epd.black)
    
    # Display the current time
    t = time.localtime()
    epd.image4Gray.text("{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            t[0], t[1], t[2], t[3], t[4], t[5]
            ), 60, 140, epd.darkgray)

    # Display vanity
    epd.image4Gray.text("Written by Kevin Roberts", 50, 180, epd.grayish)
    
    # Buffer? This is required
    epd.EPD_3IN7_4Gray_Display(epd.buffer_4Gray)
    # Partial Update?
    #epd.EPD_3IN7_1Gray_Display_Part(epd.buffer_1Gray)

    # Wait a minute
    #epd.Sleep() # Put ePaper to sleep 
    time.sleep(60) # API updates every 15 minutes 60*15 = 900
    print("refreshing now")
    
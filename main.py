from Pico_ePaper import EinkPIO # This is preferrable to using Eink
import framebuf
from writer import Writer
import freesans20

import webConnect # handles connecting to WiFi
import apiRequest # Calls Flood Level API
import apiRequestTrend # Calls Flood Level API trend

import time
import ntptime # Acquire current time

# For development purposes
import gc # For garbage collection!
#import os # For checking storage

# Initialize the e-paper display
epd = EinkPIO(rotation=90, use_partial_buffer=True)
epd.fill() # Clear screen on first run
epd.show()
epd.partial_mode_on() # Enabling partial mode blocks the use of gray

'''
class DummyDevice(framebuf.FrameBuffer):
    def __init__(self, width, height, buf_format):
        self.width = width
        self.height = height
        self._buf = bytearray(self.width * self.height // 8)
        super().__init__(self._buf, self.width, self.height, buf_format)
        self.fill(1)

# Create DummyDevice object with the same dimensions as the display.
dummy = DummyDevice(epd.width, epd.height, framebuf.MONO_HLSB)
# Create Writer instance using dummy as device and freesans20 font.
wri = Writer(dummy, freesans20)
# Setup Writer (refer to documentation for details).
wri.set_clip(row_clip=True, col_clip=True, wrap=True)
'''
# Connect to internet
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
    '''
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
    epd.text(latestReading, 60, 10, epd.black)
    epd.text(currentLevel, 60, 40, epd.black)
    epd.text(state, 100, 70, epd.black)
    epd.text(trend, 80, 100, epd.black)
    '''
    # Display the current time
    t = time.localtime()
    epd.text("{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            t[0], t[1], t[2], t[3], t[4], t[5]
            ), 60, 140, c=epd.black)

    # Display vanity
    epd.text("Written by Kevin Roberts", 50, 180, c=epd.lightgray)

    epd.show()

    # Clear display - otherwise new text will displayed on top
    epd.fill() # Clear display
    epd.rect(60, 140, 160, 10, epd.white, f=True) # x, y, wide, high
    
    # Wait a minute
    #epd.sleep() # Put ePaper to sleep
    time.sleep(10) # API updates every 15 minutes 60*15 = 900
    print("refreshing now")
    #epd.reinit()
    
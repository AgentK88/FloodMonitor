from Pico_ePaper import EinkPIO # This is preferrable to using Eink
from framebuf import FrameBuffer, MONO_HLSB
from writer import Writer
import freesans20

from webConnect import connect # handles connecting to WiFi
from apiRequest import request # Calls Flood Level API
from apiRequestTrend import requestTrend # Calls Flood Level API trend
from metRequest import metRequest # Calls Met Office Weather API

import time
import ntptime # Acquire current time

# For development purposes
import gc # For garbage collection!

# Constants for text positions
TEXT_POSITIONS = [
    (10, 20),	# latestReading and time
    (60, 20),	# currentLevel
    (60, 270),	# normalRange
    (90, 20),	# state
    (90, 270),	# trend
    (150, 20),	# weatherType
    (150, 270),	# windDirection
    (180, 20),	# temp
    (180, 270),	# windSpeed
]

# Global variables for re-use
global url
global resp
global resp_json

# Initialize the e-paper display
epd = EinkPIO(rotation=90, use_partial_buffer=True)
epd.fill() # Clear screen on first run
#epd.partial_mode_on() # Enabling partial mode blocks the use of gray

class DummyDevice(FrameBuffer):
    def __init__(self, width, height, buf_format):
        self.width = width
        self.height = height
        super().__init__(bytearray(self.width * self.height // 8), self.width, self.height, MONO_HLSB)
        self.fill(1)

# Create DummyDevice object with the same dimensions as the display.
dummy = DummyDevice(epd.width, epd.height, MONO_HLSB)
# Create Writer instance using dummy as device and freesans20 font.
wri = Writer(dummy, freesans20)
# Setup Writer (refer to documentation for details).
wri.set_clip(row_clip=True, col_clip=True, wrap=True)

# Connect to internet
try:
    ip = connect()
    ip = "IP Address: {}".format(ip[0])
except KeyboardInterrupt:
    machine.reset()

# Set time - Only if needed. Time defaults to 2021-01-01
tc = time.localtime()
if tc[0] == 2021: # Check if the year is 2021
    try:
        ntptime.settime()
    except OSError as error:
        tc = [error,1,2,3,4,5]
    finally:
        tc = time.localtime()

tc = "{}, {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(ip,
            tc[0], tc[1], tc[2], tc[3], tc[4], tc[5]
            )
epd.text(tc, 20, 270, c=epd.lightgray)
epd.show()

RC = 0 # Refresh Counter

while True:
    # Check memory used and run garbage collection
    gc.collect() # garbage collection
    print('Initial free: {} allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))
    
    t = time.localtime()
    RC += 1 # Increment Refresh Counter
    
    # Get API trend values
    try:
        trend = requestTrend(t) # Get the trend results first to avoid memory fragmentation
    except MemoryError as e:
        print(e)
        trend = "\n {}".format(e)
        #machine.reset()
    
    # Get API values
    apiResults = request() # A list of values from API
    currentLevel, latestReading, typicalRangeHigh, typicalRangeLow, state, rangePercentage = apiResults # Unpack list in this order
    #del apiResults
    
    # If after 18:00 get tomorrow's weather not today's
    if t[3] <= 18:
        metResults = metRequest(0) # A list of values from Weather API
    else:
        metResults = metRequest(1) # A list of values from Weather API
        
    dayMaximum, feelsDayMaximum, windDirection, windSpeed, precipProb, weatherType = metResults # Unpack list in this order
    del metResults
    
    # Add text to returned values for display
    texts = [
        "{}            {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(latestReading,
            t[0], t[1], t[2], t[3], t[4], t[5]),
        "Current Level: {:.2f}".format(currentLevel),
        "Normal Range: {:.1f}-{:.1f}".format(typicalRangeLow, typicalRangeHigh),
        "Trend: {}".format(trend),
        "State: {} {:d}%".format(state, int(round(rangePercentage,0))),
        "{} {}%".format(weatherType, precipProb),
        "Wind Direction: {}".format(windDirection),
        "Temperature: {}c".format(dayMaximum), # degrees symbol chr(176) or str(b'\xc2\xb0', 'utf8')
        "Wind Speed: {} mph".format(windSpeed)
        ]

    for text, (x, y) in zip(texts, TEXT_POSITIONS):
            wri.set_textpos(dummy, x, y)
            wri.printstring(text, invert=True)
    
    tcRC = "{}, RC={}".format(tc, RC)
    
    epd.text(tcRC, 20, 270, c=epd.lightgray) # Initial run values with ip address
    
    epd.blit(dummy, 0, 0, key=1, ram=epd.RAM_RED) # grayscale can be used
    epd.show()

    # Wait a minute
    epd.sleep() # Put ePaper to sleep
    time.sleep(60) # API updates every 15 minutes 60*15 = 900
    
    #machine.reset() # You're cheating!!!
    print("refreshing now {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(t[0], t[1], t[2], t[3], t[4], t[5]))
    
    # Reinitialise and clear display - otherwise new text will displayed on top
    epd.reinit()
    epd.fill() # Clear display
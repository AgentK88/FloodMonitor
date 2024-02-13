from Pico_ePaper import EinkPIO # This is preferrable to using Eink
from framebuf import FrameBuffer, MONO_HLSB
from writer import Writer
import freesans20

import webConnect # handles connecting to WiFi
import apiRequest # Calls Flood Level API
import apiRequestTrend # Calls Flood Level API trend

import time
import ntptime # Acquire current time

# For development purposes
import gc # For garbage collection!

# Constants for text positions
TEXT_POSITIONS = [
    (10, 60),  # latestReading
    (40, 60),  # currentLevel
    (70, 100),  # state
    (100, 80),   # trend
    (140, 60)   # time
]

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
    ip = webConnect.connect()
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
epd.text(tc, 25, 270, c=epd.lightgray)
epd.show()

while True:
    # Check memory used and run garbage collection
    gc.collect() # garbage collection
    print('Initial free: {} allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))
    
    t = time.localtime()
    
    # Get API values
    trend = apiRequestTrend.requestTrend(t) # Get the trend results first to avoid memory fragmentation
    apiResults = apiRequest.request() # A list of values from API
    currentLevel,latestReading,typicalRangeHigh,typicalRangeLow,state = apiResults # Unpack list in this order
    
    # Add text to returned values for display
    texts = [
        latestReading,
        "Current Level: {}".format(str(currentLevel)),
        "State: {}".format(state),
        "Trend: {}".format(trend),
        "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            t[0], t[1], t[2], t[3], t[4], t[5]
            )
        ]

    for text, (x, y) in zip(texts, TEXT_POSITIONS):
            wri.set_textpos(dummy, x, y)
            wri.printstring(text, invert=True)
    
    epd.blit(dummy, 0, 0, key=1, ram=epd.RAM_RED) # grayscale can be used
    epd.show()

    # Wait a minute
    epd.sleep() # Put ePaper to sleep
    time.sleep(3600) # API updates every 15 minutes 60*15 = 900
    print("refreshing now")
    
    # Reinitialise and clear display - otherwise new text will displayed on top
    epd.reinit()
    epd.fill() # Clear display
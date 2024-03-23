from Pico_ePaper import EinkPIO # This is preferrable to using Eink
from framebuf import FrameBuffer, MONO_HLSB
from writer import Writer
import freesans20

from webConnect import connect # handles connecting to WiFi
import urequests # handles making and servicing network requests
from array import array
import time
import ntptime # Acquire current time
from date import Date # for calendar dates used in trendUrl
import WeatherType

# For development purposes
import gc # For garbage collection!

r = "96" # Reading every 15 mins (4*24=96) or last 24 hours
#trend_url = "https://environment.data.gov.uk/flood-monitoring/id/stations/2134/readings?parameter=level&startdate=2024-03-22&enddate=2024-03-23&_sorted&_limit=96"
level_url = "https://environment.data.gov.uk/flood-monitoring/id/stations/2134" # Buildwas station
met_url = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/324224?res=daily&key=c9785cd8-dcb0-4cb5-aaf2-adf777389db7" # Telford

resp_json = []

RC = 0 # Refresh Counter

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
t = time.localtime()
if t[0] == 2021: # Check if the year is 2021
    try:
        ntptime.settime()
    except OSError as error:
        t = [error,1,2,3,4,5]
    finally:
        t = time.localtime()

'''
Functions
'''
def formatDateTime():
    return "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(t[0], t[1], t[2], t[3], t[4], t[5])

def call_api(url):
    resp = urequests.get(url)

    if resp.status_code != 200:
        print("Error: Status code", status_code)
        resp.close() # Essential for memory reclamation
    else:
        json_response = resp.json()
        resp.close() # Essential for memory reclamation
        return json_response

def trendUrl():
    endDate = Date(t) # Today
    startDate = Date()
    startDate.day -= 1 # Yesterday
    endDate = "{}-{:02d}-{:02d}".format(endDate.year, endDate.month, endDate.mday)
    startDate = "{}-{:02d}-{:02d}".format(startDate.year, startDate.month, startDate.mday)

    # Buildwas station last 24 hours
    url = "https://environment.data.gov.uk/flood-monitoring/id/stations/2134/readings?parameter=level&startdate={}&enddate={}&_sorted&_limit={}".format(startDate,endDate,r)
    return url

def requestTrend(trendResponse):
    value_list = array('d',[]) # Array is more memory efficient and only holds decimal 'd'
    # Iterate over the items and extract value key pairs
    for item in trendResponse['items']:
        value_list.append(item.get("value"))

    average = sum(value_list) / len(value_list)
    latest = value_list[0] # First value in the list as it is sorted

    # Trend where last reading is compared to 2% of average
    def trend():
        if latest >= average*1.02 :
            return "Rising"
        elif latest <= average*0.98 :
            return "Falling"
        else:
            return "Steady"
    
    return trend()

def requestLevel(levelResponse): 
    # Parse each element of json into its own dictionary and assign key values to variables
    #latestFlow = resp_json["items"]["measures"][0]["latestReading"]["value"] # measures is a list, "parameter": "flow" is first in measures array
    latestReading = levelResponse["items"]["measures"][1]["latestReading"]["dateTime"] # measures is a list, "parameter": "level" is second in measures array
    currentLevel = levelResponse["items"]["measures"][1]["latestReading"]["value"] # measures is a list, "parameter": "level" is second in measures array
    typicalRangeHigh = levelResponse["items"]["stageScale"]["typicalRangeHigh"]
    typicalRangeLow = levelResponse["items"]["stageScale"]["typicalRangeLow"]
    rangePercentage = ((currentLevel - typicalRangeLow) * 100) / (typicalRangeHigh - typicalRangeLow)
        
    # Tidy up returned values as strings for display
    latestReading = str(latestReading) # Clean up date as a string
    latestReading = latestReading.replace("T", " ") # Remove chars as can't convert ISO datetime to string
    latestReading = latestReading.replace("Z", " ") # Remove chars as can't convert ISO datetime to string
    
    # Find State (High, Normal, Low)
    def state(currentLevel):
        if currentLevel >= typicalRangeHigh :
            return "High"
        elif currentLevel <= typicalRangeLow :
            return "Low"
        else:
            return "Normal"
    
    # Return all values as a list
    return [currentLevel, latestReading, typicalRangeHigh, typicalRangeLow, state(currentLevel), rangePercentage]

def after6(t):
    # If after 18:00 get tomorrow's weather not today's
    if t[3] <= 18:
        return 0
    else:
        return 1

def requestMet(metResponse):
    period = after6(t)
    # Parse each element of json into it's own dictionary
    DV = resp_json["SiteRep"]["DV"]["Location"]["Period"][period]["Rep"][0] # ["Period"][1] is tomorrow's weather etc
    
    Dm = DV["Dm"] # Day Maximum Temperature
    FDm = DV["FDm"] # Feels Like Day Maximum Temperature
    WD = DV["D"] # Wind Direction
    WS = DV["S"] # Wind Speed
    W = DV["W"] # Weather Type
    PPd = DV["PPd"] # Precipitation Probability Day
    #Hours = DV["$"] # The number of minutes after midnight UTC
    
    WT = WeatherType.weatherType(W)
    #WDC = Compass.compassPoint(WD)
    
    return [Dm, FDm, WD, WS, PPd, WT]

trend_url = trendUrl()

tc = "{}, {}".format(ip, formatDateTime())
epd.text(tc, 20, 270, c=epd.lightgray)
epd.show()

gc.collect() # Initial run fails without this

'''
Here's the start of the loop!
'''
while True:
    
    print('Initial free: {} allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))
    
    RC += 1 # Increment Refresh Counter
    tc = "{}, {}, RC = {}".format(ip, formatDateTime(), RC)
    epd.text(tc, 20, 270, c=epd.lightgray)

    # Get API trend values
    try:
        resp_json = call_api(trend_url)
        trend = requestTrend(resp_json) # Get the trend results first to avoid memory fragmentation
    except MemoryError as e:
        print(e)
        trend = "\n {}".format(e)
    
    # Get API level values
    resp_json = call_api(level_url)
    currentLevel, latestReading, typicalRangeHigh, typicalRangeLow, state, rangePercentage = requestLevel(resp_json) # Unpack list in this order
    
    # Get API Met values
    resp_json = call_api(met_url)
    dayMaximum, feelsDayMaximum, windDirection, windSpeed, precipProb, weatherType = requestMet(resp_json) # Unpack list in this order
    
    # Add text to returned values for display
    texts = [
        "{}            {}".format(latestReading, formatDateTime()),
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
    
    epd.blit(dummy, 0, 0, key=1, ram=epd.RAM_RED) # grayscale can be used
    epd.show()
    
    # Wait a minute
    epd.sleep() # Put ePaper to sleep
    time.sleep(30) # API updates every 15 minutes 60*15 = 900
    
    # Reinitialise and clear display - otherwise new text will displayed on top
    epd.reinit()
    epd.fill() # Clear display
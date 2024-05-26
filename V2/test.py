import urequests # handles making and servicing network requests
from array import array
import time
import ntptime # Acquire current time
from date import Date # for calendar dates used in trendUrl
import WeatherType

#trend_url = "https://environment.data.gov.uk/flood-monitoring/id/stations/2134/readings?parameter=level&startdate=2024-03-22&enddate=2024-03-23&_sorted&_limit=96"
level_url = "https://environment.data.gov.uk/flood-monitoring/id/stations/2134" # Buildwas station
met_url = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/324224?res=daily&key=c9785cd8-dcb0-4cb5-aaf2-adf777389db7" # Telford
r = "96"

RC = 0 # Refresh Counter

# Set time - Only if needed. Time defaults to 2021-01-01
t = time.localtime()

resp = None
resp_json = []

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
    if 'items' in trendResponse:
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
#print(trend_url)

resp_json = call_api(trend_url)
print(requestTrend(resp_json))

#resp_json = call_api(level_url)
#print(requestLevel(resp_json))

#resp_json = call_api(met_url)
#print(requestMet(resp_json))

#print(formatDateTime())
#print(trendUrl())
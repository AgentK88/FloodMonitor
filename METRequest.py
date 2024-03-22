import urequests # handles making and servicing network requests
import WeatherType
#import Compass
import gc

url = 'http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/324224?res=daily&key=c9785cd8-dcb0-4cb5-aaf2-adf777389db7' # Telford

def metRequest(period):
    
    print("GETing Weather API data")
    
    # GET API and convert json into dictionary
    try:
        resp = urequests.get(url)
        status_code = resp.status_code
        if status_code != 200:
            print("Error: Status code", status_code)
            return
    except Exception as e:
        print(f"Error accessing API: {e}")
        return
    finally:
        resp_json = resp.json()
        resp.close() # Essential for memory reclamation
        del resp, status_code
        gc.collect()  # Ensure proper garbage collection
    
    # Parse each element of json into it's own dictionary
    DV = resp_json["SiteRep"]["DV"]["Location"]["Period"][period]["Rep"][0] # ["Period"][1] is tomorrow's weather etc
    
    del resp_json
    
    Dm = DV["Dm"] # Day Maximum Temperature
    FDm = DV["FDm"] # Feels Like Day Maximum Temperature
    WD = DV["D"] # Wind Direction
    WS = DV["S"] # Wind Speed
    W = DV["W"] # Weather Type
    PPd = DV["PPd"] # Precipitation Probability Day
    #Hours = DV["$"] # The number of minutes after midnight UTC
    
    WT = WeatherType.weatherType(W)
    #WDC = Compass.compassPoint(WD)
    
    print("Weather API values returned")
    
    return Dm, FDm, WD, WS, PPd, WT
    
#print(metRequest(1)) # Tomorrow's weather
import urequests # handles making and servicing network requests
import gc

url = 'https://environment.data.gov.uk/flood-monitoring/id/stations/2134' # Buildwas station
latestReading = ""
currentLevel = ""
typicalRangeHigh = ""
typicalRangeLow = ""
rangePercentage = ""

def request():
    
    print("GETing API data")
    
    # GET API and convert json into dictionary
    def get_level_data():
        try:
            resp = urequests.get(url)
            status_code = resp.status_code
            if status_code != 200:
                print("Error: Status code", status_code)
                return("Error: Status code", status_code)
        except Exception as e:
            print(f"Error accessing API: {e}")
            return(f"Error accessing API: {e}")
        finally:
            resp_json = resp.json()
            resp.close() # Essential for memory reclamation
            return resp_json
    
    resp_json = get_level_data()
    
    # Parse each element of json into its own dictionary and assign key values to variables
    #latestFlow = resp_json["items"]["measures"][0]["latestReading"]["value"] # measures is a list, "parameter": "flow" is first in measures array
    latestReading = resp_json["items"]["measures"][1]["latestReading"]["dateTime"] # measures is a list, "parameter": "level" is second in measures array
    currentLevel = resp_json["items"]["measures"][1]["latestReading"]["value"] # measures is a list, "parameter": "level" is second in measures array
    typicalRangeHigh = resp_json["items"]["stageScale"]["typicalRangeHigh"]
    typicalRangeLow = resp_json["items"]["stageScale"]["typicalRangeLow"]
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
        else :
            return "Normal"
    
    print("API values returned")
    
    # Return all values as a list
    return [currentLevel, latestReading, typicalRangeHigh, typicalRangeLow, state(currentLevel), rangePercentage]

#print(request())
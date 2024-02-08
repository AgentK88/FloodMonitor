import urequests # handles making and servicing network requests
import gc

url = 'https://environment.data.gov.uk/flood-monitoring/id/stations/2134' # Buildwas station

# Consider checking API response code is 200
#try:

def request():
    
    print("GETing API data")
    
    # GET API and convert json into dictionary
    try:
        resp = urequests.get(url)
        status_code = resp.status_code
        if status_code != 200:
            print("Error: Status code", status_code)
            return
        resp_dict = resp.json()
    except Exception as e:
        print(f"Error accessing API: {e}")
        return
    finally:
        resp.close() # Essential for memory reclamation
        del resp, status_code
        gc.collect()  # Ensure proper garbage collection
    
    # Parse each element of json into it's own dictionary
    items_dict = resp_dict.get("items")
    del resp_dict
    
    measures_list = items_dict.get("measures") # measures is a list
    
    stageScale_dict = items_dict.get("stageScale")
    del items_dict
    #paramFlow_dict = measures_list[0] # "parameter": "flow" is first in measures array
    paramLevel_dict = measures_list[1] # "parameter": "level" is second in measures array
    latestReading_dict = paramLevel_dict.get("latestReading")

    del measures_list, paramLevel_dict
    
    # Assign key values to variables
    currentLevel = latestReading_dict.get("value")
    latestReading = latestReading_dict.get("dateTime")
    typicalRangeHigh = stageScale_dict.get("typicalRangeHigh")
    typicalRangeLow = stageScale_dict.get("typicalRangeLow")
    # Tidy up returned values as strings for display
    latestReading = str(latestReading) # Clean up date as a string
    latestReading = latestReading.replace("T", " ") # Remove chars as can't convert ISO datetime to string
    latestReading = latestReading.replace("Z", " ") # Remove chars as can't convert ISO datetime to string
    
    gc.collect()
    
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
    return [currentLevel,latestReading,typicalRangeHigh,typicalRangeLow,state(currentLevel)]

#print(request())
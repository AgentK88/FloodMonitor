import time
import urequests # handles making and servicing network requests

t = time.localtime()
r = "96" # Reading every 15 mins (4*24=96) or last 24 hours
startDate = "{}-{:02d}-{:02d}".format(t[0], t[1], t[2]-1) # Yesterday
endDate = "{}-{:02d}-{:02d}".format(t[0], t[1], t[2]) # Today

url = 'https://environment.data.gov.uk/flood-monitoring/id/stations/2134/readings?parameter=level&startdate='+startDate+'&enddate='+endDate+'&_sorted&_limit='+r # Buildwas station last 24 hours

def requestTrend():
    
    print("GETing API trend data")
    
    # GET API and convert json into dictionary
    resp_dict = urequests.get(url).json()
    
    # Items list
    items_list = resp_dict.get("items")
    
    # For each loop over items_list to gather all values into list
    value_list = []
    for i in items_list:
        value_list.append(i.get("value"))
    
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

    print("API trend values returned")
    return trend()
    
#requestTrend()
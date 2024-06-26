from date import Date
import urequests # handles making and servicing network requests
import array
import gc

r = "96" # Reading every 15 mins (4*24=96) or last 24 hours
endDate = Date() # Today
startDate = Date()
startDate.day -= 1 # Yesterday
endDate = "{}-{:02d}-{:02d}".format(endDate.year, endDate.month, endDate.mday)
startDate = "{}-{:02d}-{:02d}".format(startDate.year, startDate.month, startDate.mday)

url = 'https://environment.data.gov.uk/flood-monitoring/id/stations/2134/readings?parameter=level&startdate='+startDate+'&enddate='+endDate+'&_sorted&_limit='+r # Buildwas station last 24 hours

def requestTrend():
    
    print("GETing API trend data")
    
    # GET API and convert json into dictionary
    try:
        r = urequests.get(url)
        resp_dict = r.json()
        sc = r.status_code
    finally:
        r.close() # Essential for memory reclamation
        del r
    
    print("Status code: {}".format(sc))
    #resp_dict = urequests.get(url).json()
    
    if sc == 200 : # else?
        # Items list - Need to check whether this is not empty!
        items_list = resp_dict.get("items")
        del resp_dict, sc
        #print(startDate, endDate, items_list)
        
        # For each loop over items_list to gather all values into list
        #value_list = []
        value_list = array.array('d',[]) # Array is more memory efficient and only holds float 'd'
        for i in items_list:
            value_list.append(i.get("value"))
        
        del items_list
        
        average = sum(value_list) / len(value_list)
        latest = value_list[0] # First value in the list as it is sorted
        
        del value_list
        gc.collect()
        
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
    
    else :
        print("Incorrect status code returned")
    
#print(requestTrend())
#print(gc.mem_free())
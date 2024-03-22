from date import Date
import urequests # handles making and servicing network requests
import array
import gc
#import time # for testing only!

r = "96" # Reading every 15 mins (4*24=96) or last 24 hours

def requestTrend(date):

    endDate = Date(date) # Today
    startDate = Date()
    startDate.day -= 1 # Yesterday
    endDate = "{}-{:02d}-{:02d}".format(endDate.year, endDate.month, endDate.mday)
    startDate = "{}-{:02d}-{:02d}".format(startDate.year, startDate.month, startDate.mday)

    # Buildwas station last 24 hours
    url = "https://environment.data.gov.uk/flood-monitoring/id/stations/2134/readings?parameter=level&startdate={}&enddate={}&_sorted&_limit={}".format(startDate,endDate,r)

    print("GETing API trend data")
    '''
    def get_trend_data():
        status_code = urequests.get(url).status_code
        
        if status_code != 200:
            print("Error: Status code", status_code)
        else:
            return urequests.get(url).json()#["items"] # I thought this line would be more efficient
        
        resp.close() # Essential for memory reclamation
    '''
    # GET API and convert json into dictionary
    try:
        #print('Initial free: {} allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))
        resp = urequests.get(url)
        status_code = resp.status_code
        #print('Initial free: {} allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))
        if status_code != 200:
            print("Error: Status code", status_code)
            return
    except Exception as e:
        print(f"Error accessing API: {e}")
        return
    finally:
        #print('Initial free: {} allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))
        #value_list = [items['value'] for items in resp.json()["items"] ] # I thought this line would be more efficient
        resp_json = resp.json()
        resp.close() # Essential for memory reclamation
        del resp, status_code
        gc.collect()  # Ensure proper garbage collection

    # Above can be done without creating both resp and resp_json and may save ram
    # However, response code can't be checked!
    #resp_json = urequests.get(url).json()["items"]
    #value_list = [items['value'] for items in urequests.get(url).json()["items"] ] # I thought this line would be more efficient
    #resp_json = get_trend_data()
    
    # Check if 'items' key exists in the response
    if 'items' in resp_json:
        value_list = array.array('d',[]) # Array is more memory efficient and only holds decimal 'd'
        # Iterate over the items and extract value key pairs
        for item in resp_json['items']:
            value_list.append(item.get("value"))
    
    print('Initial free: {} allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))
    #del resp_json

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
    
#print(requestTrend(time.localtime()))
#print('Initial free: {} allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))
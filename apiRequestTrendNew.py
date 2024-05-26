from date import Date
import urequests
import ujson
import time # for testing only!

class JSONParser:
    def __init__(self):
        self.buffer = b""
        self.pos = 0

    def feed(self, data):
        self.buffer += data

        # Keep searching for JSON objects until buffer is exhausted
        while self.pos < len(self.buffer):
            try:
                obj, pos = ujson.loads(self.buffer[self.pos:]), len(self.buffer)
                yield obj
                self.pos += pos
            except ValueError:
                # Incomplete JSON, need more data
                break

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
    
    def get_trend_data():

        # Make a request to the URL
        response = urequests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Create a JSON parser instance
            parser = JSONParser()

            # Read the response content
            response_text = response.text

            # Feed the response content into the JSON parser
            for obj in parser.feed(response_text.encode()):
                # Process each parsed JSON object
                #print(obj)
                return ([items['value'] for items in obj["items"] ]) # I thought this line would be more efficient
        else:
            print("Failed to retrieve data:", response.status_code)

        # Close the response connection
        response.close()
        
    value_list = get_trend_data()

    average = sum(value_list) / len(value_list)
    latest = value_list[0] # First value in the list as it is sorted
    
    del value_list
    
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

print(requestTrend(time.localtime()))
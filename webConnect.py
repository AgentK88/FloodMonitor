import network # handles connecting to WiFi
from time import sleep

# Fill in your network name (ssid) and password here:
ssid = 'TP-Link_7B64'
password = '61025646'

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    print(wlan.ifconfig())
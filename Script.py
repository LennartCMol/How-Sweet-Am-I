import RequestSensorData
import ParseSensorData
import StatusQuotes
from pypresence import Presence
import time
import os


def getEnvironmentVariables():
    """ Gets environment variables and sets them in global variables
    """

    global email, password, client_id
    email = os.environ.get("EMAIL")
    password = os.environ.get("PASSWORD")
    client_id = os.environ.get("CLIENT_ID")
    if email == None or password == None or client_id == None:
        print(f"\nMake sure to correctly set your environment variables.\n")
        exit()

def connectToLibreLinkUp():
    """ Tries to make a connection to LibreLinkUp and requests patiend_id
    """

    global patient_id
    try:
        RequestSensorData.setToken(email, password)
        patient_id = RequestSensorData.getPatientId()
    except:
        print(f"\n{time.strftime('%H:%M:%S')} - API timeout. Trying again.")

def connectToPresence():
    """ Tries to make a connection to Rich Presence and create RPC object
    """
    
    global RPC 
    RPC = Presence(client_id)
    try:
        RPC.connect()
    except:
        print(f"\n{time.strftime('%H:%M:%S')} - Discord is closed. Make sure to have it running.")


getEnvironmentVariables()        
connectToLibreLinkUp()
connectToPresence()

while True: 
    
    # request data from LibreLinkUp
    try:
        data = RequestSensorData.getData(patient_id)
    except:
        connectToLibreLinkUp()

    # get blood glucose and quote
    BG_value = ParseSensorData.getLatestMeasurement(data)
    info = StatusQuotes.getQuote(BG_value)

    # update Discord playing status
    try:
        RPC.update( #state = f"BG: {BG_value} mmol/L - {info['level']}", 
                    state = f"BG: {BG_value} mmol/L - {info['level']}", 
                    details = info['quote'],
                    large_image = "blood-sugar-roller-coaster",
                    large_text = "Riding highs and lows like there's no tomorrow.")
        print(f"\n{time.strftime('%H:%M:%S')} - Updated Discord playing status.")
    except Exception as e:
        if e.args[0] == "Client ID is Invalid":
            print(f"Client ID is invaled. Check and reset the environment variable.")
            exit()
        else:
            connectToPresence()

    # minimum delay between updating Discord playing status
    time.sleep(15)
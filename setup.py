## Run this to connect to your local Bridge and add lights to your profile
## Generates config.ini (textfile) and drive.db (sqlite3 database)

import requests
import sys
import configparser
import socket
from db import DB

global config

def throwError(msg):
    print(msg)
    sys.exit()

def connectToBridge():
    """Returns (address, bridge_id)"""

    # Search for bridges
    print("Searching for bridges.. ", end="")
    res = requests.get("https://discovery.meethue.com")
    if res.status_code != 200: throwError("ERROR: Unable to query discovery.meethue.com to find your bridge. Check your internet connection.")
    bridges = res.json()

    # Figure out which bridge to configure with
    if len(bridges) == 0:
        throwError("ERROR: No bridges found. Check that this device is on the same local connection as your Hue Bridge.")
    elif len(bridges) == 1:
        bridge_index = 0  # internally use 0-based indexing
        print("1 bridge found:")
        print(f"[1]: id={bridges[0]['id'].upper()}, address={bridges[0]['internalipaddress']}")  # output with 1-based indexing
    else:  # len(bridges) >= 2
        print("This branch hasn't been tested because the developer doesn't have two Hue Bridges.\n"
              "If it doesn't work, open an issue or message rishabhverma.rv@gmail.com")
        print(f"{len(bridges)} bridges found:")
        for i, bridge in enumerate(bridges):
            print(f"[{i+1}]: id={bridge['id'].upper()}, address={bridge['internalipaddress']}")
        bridge_index = -1
        while bridge_index == -1:
            try:
                bridge_index = int(input("Enter the index of the bridge to connect to\n>> ")) - 1
            except ValueError:
                print("ERROR: Invalid bridge id")
            if bridge_index >= len(bridges):
                bridge_index = -1

    # Configure to use that bridge
    address = bridges[bridge_index]['internalipaddress']
    bridge_id = bridges[bridge_index]['id']
    config["Philips Hue"] = {'BridgeAddress': address}
    print(f"Configured to access Hue bridge {bridge_index+1} at {address}")
    return (address, bridge_id)

def authenticateBridge(address, bridge_id):
    db = DB()
    user, key = db.get_bridge_key(bridge_id)
    if key is None:
        print("Bridge not found in local database.\n"
              "You will need to register this application with your Hue Bridge.")

        device_name = "_".join(socket.gethostname().split())
        request_body = {"devicetype":f"LeagHue#{device_name}", "generateclientkey":True}

        while key is None:
            input("Press the link button on your Hue Bridge, then hit Enter on this device:")
            res = requests.post(url=f"http://{address}/api", json=request_body)
            if res.status_code != 200:
                throwError("Error: Unable to communicate with Hue Bridge")
            reply = res.json()[0]
            if 'error' in reply:
                print('Error:', reply['error']['description'])
            elif 'success' in reply:
                user = reply['success']['username']
                key = reply['success']['clientkey']

        print("Key successfully generated!")
        db.insert_bridge_key(bridge_id, user, key)


    print("Storing key.. ", end="")
    config["Philips Hue"]['User'] = user
    config["Philips Hue"]['Key'] = key
    print("Done.")
    return (user, key)

def selectLights(address, user, key):
    # TODO this whole thang.
    pass


def setup():
    proceed = input("Welcome to the LeagHue configuration wizard! Would you like to configure LeagHue? [y/N]\n>>")
    if proceed != "y":
        throwError("Cancelling configuration.")

    print("\nSTEP ONE: Find a Hue Bridge")
    address, bridge_id = connectToBridge()  # configuration stuff
    print("STEP ONE COMPLETE.")

    print("\nSTEP TWO: Authenticate and Connect to the Hue Bridge ")
    user, key = authenticateBridge(address, bridge_id)  # authentication stuff
    print("STEP TWO COMPMLETE.")

    print("\nSTEP THREE: Select Lights")
    selectLights(address, user, key)  # configuration stuff
    print("STEP THREE COMPLETE.")

    with open('config.ini', 'w') as configfile:
        config.write(configfile)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    setup()
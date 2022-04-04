## Run this to connect to your local Bridge and add lights to your profile

import requests
import sys
import configparser

global config

def throwError(msg):
    print(msg)
    sys.exit()

def connectToBridge():
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
            if bridge_index > len(bridges):
                bridge_index = -1

    # Configure to use that bridge
    address = bridges[bridge_index]['internalipaddress']
    config["Philips Hue"] = {'BridgeAddress': address}
    print(f"Configured to access Hue bridge {bridge_index+1} at {address}")

def selectLights():
    address = config["Philips Hue"]["BridgeAddress"]



def setup():
    print("STEP ONE: Connect To a Hue Bridge")
    connectToBridge()
    print("STEP TWO: Select Lights")
    selectLights()




if __name__ == '__main__':
    config = configparser.ConfigParser()
    setup()
## Run this to connect to your local Bridge and add lights to your profile
## Generates config.ini (textfile) and drive.db (sqlite3 database)

import requests
import sys
import configparser
import socket
from db import DB

global config

def throwError(msg):  # TODO add logging here
    print(msg)
    sys.exit()

def connectToBridge():
    """Returns (address, bridge_id)"""

    print("Searching for bridges.. ", end="")
    try:
        res = requests.get("https://discovery.meethue.com")
        if res.status_code != 200:
            raise Exception
    except Exception as e:
        throwError("ERROR: Unable to query discovery.meethue.com to find your bridge. Check your internet connection.")
    bridges = res.json()

    # Figure out which bridge to configure with
    # 3 cases based on number of available bridges
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

    # Configure to use the selected bridge
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
        request_url = f"http://{address}/api"
        request_body = {"devicetype":f"LeagHue#{device_name}", "generateclientkey":True}
        while key is None:
            input("Press the link button on your Hue Bridge, then hit Enter on this device:")
            res = requests.post(url=request_url, json=request_body)
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

    config["Philips Hue"]['User'] = user
    config["Philips Hue"]['Key'] = key
    print("Bridge key found and configured.")
    return (user, key)

def selectGroup(address, user, key):
    request_header = {"hue-application-key": user}
    request_url = f"https://{address}/clip/v2/resource"
    try:
        zone_res = requests.get(url=f"{request_url}/zone", headers=request_header,
                           verify=False)
        # cert="cert.pem")  # TODO figure out SSL and clean this try/except
        room_res = requests.get(url=f"{request_url}/room", headers=request_header,
                                verify=False)
        if zone_res.status_code != 200 or room_res.status_code != 200:
            raise BaseException
    except:
        throwError("ERROR: Unable to get rooms and zones from Bridge.")
    zones = zone_res.json()["data"]
    rooms = room_res.json()["data"]

    groups = zones + rooms

    print(f"{len(groups)} groups found:")
    for i, group in enumerate(groups):
        group_index = f"[{i+1}]"
        print(f"{group_index: >5}: {group['metadata']['name']}")

    print("Enter the index of the room or zone to control:")
    group_to_select = -1
    while group_to_select == -1:
        response = input(">>")
        try:
            response = int(response)
            if response <= 0 or response > len(groups):
                raise ValueError
            group_to_select = response
        except:
            print("ERROR: Invalid group index. Try a valid number.")

    group = groups[group_to_select - 1]
    config["Philips Hue"]['GroupType'] = group['type']
    config["Philips Hue"]['GroupID'] = group['id']

    print(f"Configuring to control {group['metadata']['name']}")


def setup(debug=False):
    proceed = "y"
    if not debug:
        proceed = input("Welcome to the LeagHue configuration wizard! Would you like to configure LeagHue?\n"
                    "(Your existing configuration will be overwritten) [y/N]\n>>")
    if proceed != "y":
        throwError("Cancelling configuration.")

    print("\nSTEP ONE: Find a Hue Bridge")
    address, bridge_id = connectToBridge()  # configuration stuff
    print("STEP ONE COMPLETE.")

    print("\nSTEP TWO: Authenticate and Connect to the Hue Bridge")
    user, key = authenticateBridge(address, bridge_id)  # authentication stuff
    print("STEP TWO COMPLETE.")

    print("\nSTEP THREE: Select Light Zone")
    selectGroup(address, user, key)
    print("STEP THREE COMPLETE.")
    """
    print("\nSTEP THREE: Select Lights")
    selectLights(address, user, key)  # configuration stuff
    print("STEP THREE COMPLETE.")
    """

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    print("CONFIGURATION COMPLETE.")


if __name__ == '__main__':
    config = configparser.ConfigParser()
    setup(debug=False)
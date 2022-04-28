from db import DB
import setup
import requests
import socket


def testAddKeyAndUpdate():
    db = DB()
    db.insert_bridge_key("Test Bridge One", "First User", "First Key")
    firstUser, firstKey = db.get_bridge_key("Test Bridge One")
    db.insert_bridge_key("Test Bridge One", "Second User", "Second Key")
    secondUser, secondKey = db.get_bridge_key("Test Bridge One")
    assert firstKey == "First Key" and secondUser == "Second User" and secondKey == "Second Key"


def testNeedToAuthenticateNewBridge():
    db = DB()
    noneKey = db.get_bridge_key("New Bridge")
    assert noneKey is None


def testAuthentication(address="10.0.0.50"):
    # This test only works with the right address hardcoded.
    device_name = "_".join(socket.gethostname().split())
    request_body = {"devicetype":f"LeagHue#{device_name}", "generateclientkey":True}

    res = requests.post(url=f"http://{address}/api", json=request_body)
    print(res.status_code)
    assert False


def testLights
#LeagHue

This repository contains a Python script which can coordinate your Philips Hue lights with the League of Legends client.

####Features:
* Auto-load a color scheme to match your favorite champion.
* Tweak your color scheme mid-game, and it will remember.
* Mark in-game events such as Ace, Victory, or Defeat



####Performance:
This script will run in the background and check every 2 seconds whether a League game is running.
During a game, it will sample the LocalHost API at no more than 10 Hz for in-game events.  

#### Setup:
1. Follow the Philips Hue API ["Get Started" guide](https://developers.meethue.com/develop/get-started-2/) to create an authorized user. 
2. Store the Bridge local IP Address, your new username, and the IDs of the lights you want to control in `main.pyw`, in the parameters `ip`,`active_IDs`, `username` respectively.
3. Install Python
5. Ensure that the default program to open a .pyw file is `pythonw.exe` in your Python installation 
5. Install the libraries **phue** and **requests** with `pip`.
6. If all has gone well, you should be able to input `python`,`import phue`,`import requests` into Command Prompt and get no errors.  
6. Create a shortcut to `main.pyw` and add this shortcut to your system Startup folder:         

```C:\Users\{current_user}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\```


#### Tickets (roughly ordered):
* Implement a logger
* Create a config.txt with all parameters for easier configuration
* Get the latest patch automatically without it being a parameter in GameState.py
* Monitor system processes for `LeagueClient.exe` so that LeagHue can check less frequently when you're not playing vidya.
* Store brightness in addition to color? It would be nice so that a user can get exactly the color they want, but users would then be unable to adjust brightness to match their room environment. The resolution would have to be to store a brightness coefficient, not the brightness. 
* Go to ColorLoop between games
* Include functionality to make step 2 of the setup easier by pressing the Bridge button.


####non-Standard Dependencies:
* phue
* requests

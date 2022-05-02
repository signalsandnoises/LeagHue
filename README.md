<img src="https://user-images.githubusercontent.com/11370378/166312216-c5be9194-e41d-4a64-afa1-54a1bdafcf57.png" alt="LeagHue" width="400"/>

---

If you've got Philips Hue lights at your desk and you play League of Legends, try using LeagHue! 

https://user-images.githubusercontent.com/11370378/166311914-ada2ad1b-c9fd-4764-9710-4cba0e56e420.mp4

On game start, LeagHue will read your champion's art and build a dynamic scene to match the colors. During the game, it will celebrate aces with an RGB color sweep.

## Installation

LeagHue is under active development, and I don't have an installer put together right now. You will have to install this manually.

1. Download this repository and place it in a safe folder. I suggest your documents folder. 
1. Install [Python](https://www.python.org/).
3. Open a command-line interface in the LeagHue directory, and install the package requirements. 
   * Windows: `py -m pip install -r requirements.txt`
   * Unix/macOS: `python -m pip install -r requirements.txt` 
4. In the same command-line interface, run setup.py. It will first have you authenticate by pressing the Link button on your Philips Hue Bridge. It will then have you select a room or zone containing the lights at your desk. 
   * Windows: `py setup.py`
   * Unix/macOS: `python setup.py` 
5. Ensure that the default program to open a .pyw file is `pythonw.exe`, located in your Python installation.
    * Windows, assuming default Python installation: 
        1. Open the LeagHue folder in File Explorer 
        2. Right-click `main.pyw` > "Open with" > "Choose another app"
        4. Check "Always use this app to open .pyw files"
        5. Click "More apps", scroll down, and click "Look for another app on this PC"
        6. Navigate to `C:\Users\{user}\AppData\Local\Programs\Python\Python{XY}` and open `pythonw.exe` 
6. Add `main.pyw` to your startup programs.
    * Windows:
        1. Create a shortcut to `main.pyw`
        2. Add this shortcut to `C:\Users\{user}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\`
7. Restart your computer

---

<sup>LeagHue was created under Riot Games' "Legal Jibber Jabber" policy using assets owned by Riot Games.  Riot Games does not endorse or sponsor this project.</sup>

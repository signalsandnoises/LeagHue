# LeagHue

If you've got Philips Hue lights at your desk and you play League of Legends, try using LeagHue! 
It will run in the background and build a dynamic scene to match your champion. It will also celebrate aces with an RGB color sweep.  

### Setup:

LeagHue is under active development, and I don't have an installer put together right now. You will have to install this manually.

1. Download this repository and place it in a safe folder. I suggest your documents folder. 
1. Install [Python](https://www.python.org/).
3. Open a command-line interface in the LeagHue directory, and install the package requirements. 
   * Windows: `py -m pip install -r requirements.txt`
   * Unix/macOS: `python -m pip install -r requirements.txt`
   * Details on using [pip](https://pip.pypa.io/en/stable/user_guide/#requirements-files) 
4. In the same command-line interface, run `setup.py`. It will tell you when to press the Link button on your Philips Hue Bridge, 
and it will need you to select a room or zone containing the lights around your desk.    
   * Windows: `py setup.py`
   * Unix/macOS: `python setup.py` 
   1. `setup.py` will first have you authenticate by pressing the Link button on your Hue Bridge.
   2. `setup.py` will then have you select a room or zone containing the lights around your desk.
5. Ensure that the default program to open a `.pyw` file is `pythonw.exe`, located in your Python installation.
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



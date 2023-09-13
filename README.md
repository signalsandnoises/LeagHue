<p align="center">
  <img src="https://user-images.githubusercontent.com/11370378/166312216-c5be9194-e41d-4a64-afa1-54a1bdafcf57.png" alt="LeagHue" width="400">
  <br>
  If you have Hue lights and you play League, this is for you.
</p>



----

https://user-images.githubusercontent.com/11370378/166326260-63a8cf71-5a86-424c-9ee0-9c90ce1b439c.mp4

## Behavior

LeagHue is a background application that **controls your Philips Hue lights to match your League of Legends skins** and respond to in-game 
information. It makes the game more immersive, brings out more personality from your champions, and brings the hype for key objective victories.

Once installed, LeagHue will:
* Build dynamic color palettes to match each champion skin at game start.
* Celebrate aces and pentakills with rainbows.
* Mark the destruction of a nexus with red or blue upon defeat or victory.
* Return your lights to their previous state at game end.

If you enjoy playing ARAM or any rotating game modes (e.g. 2v2v2v2, URF), I think you will love the vibes that LeagHue can bring.

## Installation

1. **Download or clone this repository** and place it in the desired location. 
2. **Install [Python](https://www.python.org/)**.
3. Open a terminal in the LeagHue folder and **install the package requirements**. 
   * Windows: `py -m pip install -r requirements.txt`
   * Unix/macOS: `python -m pip install -r requirements.txt` 
4. In the same terminal, **run setup.py** and follow the instructions:
   * Windows: `py setup.py`
   * Unix/macOS: `python setup.py` 
   
   a. First, it will ask you to **press the Link button** on your Philips Hue Bridge. 
   
   b. Then, it will ask you to **select a room or zone** containing the lights at your desk. 
   
5. **Ensure the default program** to open a .pyw file is `pythonw.exe`, located in your Python installation.
    * Windows, assuming default Python installation: 
        1. Open the LeagHue folder in File Explorer 
        2. Right-click `main.pyw` > "Open with" > "Choose another app"
        4. Check "Always use this app to open .pyw files"
        5. Click "More apps", scroll down, and click "Look for another app on this PC"
        6. Navigate to `%USERPROFILE%\AppData\Local\Programs\Python\` and open `Python[XY]/pythonw.exe` 
6. **Add** `main.pyw` **to your startup programs**.
    * Windows:
        1. Create a shortcut to `main.pyw`
        2. Add this shortcut to `%USERPROFILE\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\`
7. **Restart** your computer

If you need help with the installation process, open an issue and I will be happy to clarify so future users 
will have an easier time. 

## How it Works

Technical write-up: Coming Soon!

## Disclaimer

LeagHue was created under Riot Games' "Legal Jibber Jabber" policy using assets owned by Riot Games.  Riot Games does not endorse or sponsor this project.

This project is maintained under an MIT License.
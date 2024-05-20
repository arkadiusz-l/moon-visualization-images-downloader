# Moon Visualization Images Downloader
I'm writing this small program in order to improve my programming skills.\
It uses [requests](https://requests.readthedocs.io/en/latest/) to connect with API,
[logging](https://docs.python.org/3/library/logging.html) for additional debug information,
[tqdm](https://tqdm.github.io/) for file download progress bar.\
I also used [Pytest](https://docs.pytest.org/) for testing.

## Description
This program runs on the terminal/command-line and is used to download visualization images of the Moon
for a given day and time from the [NASA Scientific Visualization Studio (SVS) API](https://nasaviz.gsfc.nasa.gov/help/#apis-dialamoon).

### History
I needed visualization images of the Moon for a given day and time when planning my telescope
observing/astrophotography sessions.\
These visualizations contains a view of the [terminator](https://en.wikipedia.org/wiki/Terminator_(solar)#Lunar_terminator),
labeled [features](https://en.wikipedia.org/wiki/List_of_lunar_features) and lunar mission landing sites.\
Previously, I downloaded this images manually from the
[NASA Scientific Visualization Studio (SVS)](https://svs.gsfc.nasa.gov/gallery/moonphase/) website, but when I found out
that NASA provides an API, I wrote this small program.

## Installation
For Windows users without Python installed on their operating system,
please download [this zip archive](https://github.com/arkadiusz-l/moon-visualization-images-downloader/releases/download/v1.0.1/moon-visualization-images-downloader.zip)
with the EXE file inside.

For users/developers with Python installed:\
3 options to choose from:
#### I. PyCharm or IntelliJ IDEA with the "Python Community Edition" plugin
1. Create a New Project with the virtual environment, for example **Virtualenv**.
2. Open the IDE terminal.
3. Type:
   ```
   git clone git@github.com:arkadiusz-l/moon-visualization-images-downloader.git
   ```
   or
   ```
   git clone https://github.com/arkadiusz-l/moon-visualization-images-downloader.git
   ```
4. Navigate to the program's directory by typing:
   ```
   cd moon-visualization-images-downloader
   ```
5. Make sure that you are inside the virtual environment - you should see `(venv)` before the path.
6. Type:
   ```
   pip install -r requirements.txt
   ```
   to install the required dependencies necessary for the program to run.
7. Now you can run the program by typing:
   ```
   python main.py
   ```
8. After using the program, exit the virtual environment by typing:
   ```
   deactivate
   ```
9. The `(venv)` should disappear.

#### II. Downloading release
1. Download the [latest release](https://github.com/arkadiusz-l/moon-visualization-images-downloader/releases/latest)
   in a .zip archive.
2. Unpack the downloaded archive in a directory of your choice.
3. Open the terminal.
4. Navigate to the directory with the unpacked program by typing:
   ```
   cd directoryname
   ```
5. Type:
   ```
   python -m venv venv
   ```
   to create virtual environment and wait for confirmation.
6. If you are on Windows, type:
   ```
   venv\Scripts\activate
   ```
   If you are on Linux or macOS, type:
   ```
   source venv/bin/activate
   ```
7. Make sure that you are inside the virtual environment - you should see `(venv)` before the path.
8. Type:
   ```
   pip install -r requirements.txt
   ```
   to install the required dependencies necessary for the program to run.
9. Now you can run the program by typing:
   ```
   python main.py
   ```
10. After using the program, exit the virtual environment by typing:
    ```
    deactivate
    ```
11. The `(venv)` should disappear.

#### III. Cloning repository
1. Open the terminal.
2. Create a new directory by typing:
   ```
   mkdir directoryname
   ```
3. Navigate to that directory by typing:
   ```
   cd directoryname
   ```
4. Type:
   ```
   git clone git@github.com:arkadiusz-l/moon-visualization-images-downloader.git
   ```
   or
   ```
   git clone https://github.com/arkadiusz-l/moon-visualization-images-downloader.git
   ```
5. Navigate to the program's directory by typing:
   ```
   cd moon-visualization-images-downloader
   ```
6. Type:
   ```
   python -m venv venv
   ```
   to create virtual environment and wait for confirmation.
7. If you are on Windows, type:
   ```
   venv\Scripts\activate
   ```
   If you are on Linux or macOS, type:
   ```
   source venv/bin/activate
   ```
8. Make sure that you are inside the virtual environment - you should see `(venv)` before the path.
9. Type:
   ```
   pip install -r requirements.txt
   ```
   to install the required dependencies necessary for the program to run.
10. Now you can run the program by typing:
    ```
    python main.py
    ```
11. After using the program, exit the virtual environment by typing:
    ```
    deactivate
    ```
12. The `(venv)` should disappear.

## Usage
The program will ask you the following things:
- the date for which you want to download the visualization images,
- the hour of the first image of the visualization,
- the hour of the last image of the visualization.

You can enter the date in format **YYYY-MM-DD** or **t** for today, **tm** for tommorow.\
You can also enter **+1** for tommorow, **+2** for the day after tommorow, etc.

The program validates dates according to API requirements:
- date and time cannot be earlier than **2011-01-01 00:00 UTC**,
- date and time cannot be later than the **current year-12-31 23:59 UTC**.

The program displays a progress bar with information as each file is downloading.\
The downloaded files are saved in the **Downloads\Moon Visualizations** directory of the currently logged-in user
(for Windows, for Linux I still have to write :))\
Once the files have finished downloading, the download directory will automatically open in File Explorer.
The program handles exceptions in the event of loss of connection to the API or unverified SSL certificate.

### Usage example
If your current time zone is UTC+2 and you enter:
- date: **t**
- the hour of the first image: **20**
- the hour of the last image: **23**

the program will convert the hours to **18** and **21**, and then start downloading **4** images for
**18**, **19**, **20** and **21** UTC of the **current day**.\
However, for your convenience, the downloaded files are named with the date and time you entered (local).\
The letter "L" in filename reminds us of this.

### Debug mode
You can run the program in debug mode, which displays the values calculated by the program:
- date and time converted from local time zone to UTC,
- endpoints,
- path to the image file on the NASA server,
- file size to download,
- path where the file will be saved.

To run the program in debug mode, type:
```
python main.py -d
```

## Screenshot
![screenshot](https://github.com/arkadiusz-l/moon-visualization-images-downloader/assets/104087320/10039636-7610-4d13-b755-b7322b8be462)

## Documentation
NASA SVS API documentation is available [here](https://nasaviz.gsfc.nasa.gov/help/#apis-dialamoon).

## Project Status
In progress...
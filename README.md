# Moon Phase Images Downloader
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

## Usage
After downloading the latest release or cloning the repository, launch a terminal on your operating system,
go to the program directory and type:
`python main.py`.

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
The downloaded files are saved in the **Downloads\Moon Phase** directory of the currently logged-in user
(for Windows, for Linux I still have to write :))\
The program handles exceptions in the event of loss of connection to the API or unverified SSL certificate.

#### Usage example:
If your current time zone is UTC+2 and you enter:
- date: **t**
- the hour of the first image: **20**
- the hour of the last image: **23**

the program will convert the hours to **18** and **21**, and then start downloading **4** images for
**18**, **19**, **20** and **21** UTC of the **current day**.\
However, for your convenience, the downloaded files are named with the date and time you entered (local).\
The letter "L" in filename reminds us of this.

## Documentation
NASA SVS API documentation is available [here](https://nasaviz.gsfc.nasa.gov/help/#apis-dialamoon).

## Project Status
In progress...

# Torrent scraper TUI

This program is slow. Idc about the speed :)

### Dependencies:

You'll need **qbittorrent** to use this. Other torrent clients also will probably work, I haven't tested with them.

Also only works with **Firefox** browser.

Also only works on **Linux** (and probably MacOS)

### Usage:

When on the TUI after the torrents have been scraped, you have 2 options:
1. Press `Enter` to open your qbittorrent for that magnet link
2. Press `o` to launch that torrent link in the browser

```
git clone git@github.com:Typeaway14/torrent_scraper.git
cd torrent_scraper
pip install -r requirements.txt
python torrent_scraper.py
```

Note: Consider creating a venv 
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python torrent_scraper.py
```
You will have to run `source venv/bin/activate` everytime before running the program if you're using a venv



from bs4 import BeautifulSoup
from requests_html import HTMLSession
from pathlib import Path
import youtube_dl
import pandas as pd
import demoji

SONG = [] # global vaiable to store list of songs
counter = 0 # global variable to store count from logger. (cant be done normally in logger function due to it constantly being reset)

def DownloadVideosFromTitles(los):
    ids = []
    print("Looking for playlist links...")
    print("")
    for idx, item in enumerate(los, 1):
        vid_id = ScrapeVidId(item)
        ids += [vid_id]
        if (idx > 1):
            print(f"Found {idx} song links")
            print("")
        else:
            print(f"Found {idx} song link")
            print("")

    DownloadVideosFromIds(ids)
    print("")
    print("You can find your songs in the ydtl_folder")

class MyLogger(object):
    def debug(self, msg):
        # Excepts IndexError when indexing logger messages with variable lengths
        try:
            of = msg.split(" ")[3]
            complete = msg.split(" ")[1]
            progress = msg.split(" ")[2]
        except IndexError:
            of = 'null'
            complete = 'null'
            progress = 'null'

        # "of" is index 3 which is used to identify the logging message for download
        if "of" in of:
            print(f"\rDownloading song {counter} ({SONG[-1]}) {progress}", end="")
        if "100.0%" in complete:
            showSong()

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

def finished(d):
    if d['status'] == 'finished':
        print('')
        print('Done downloading, now converting ...')

def DownloadVideosFromIds(lov):
    desktop = Path.home() / 'Desktop'
    ytdl_folder = desktop / 'ytdl_folder'
    dl_folder = desktop / 'ytdl_folder' / 'Downloads'
    SAVE_PATH = desktop / 'ytdl_folder' / 'Downloads' / getAlbumName()
    str_SAVE_PATH = str(SAVE_PATH)

    if not ytdl_folder.exists():
        print("Creating ytdl_folder ...")
        ytdl_folder.mkdir(exist_ok=True)
    if not dl_folder.exists():
        print("Creating Downloads folder ...")
        dl_folder.mkdir(exist_ok=True)
    if not SAVE_PATH.exists():
        print("Creating folder with playlist name ...")
        SAVE_PATH.mkdir(exist_ok=True)
    else:
        print("ytdl folder exists!")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': MyLogger(),
        'default_search': "ytsearch", # fixes downloading problem (download ffmpeg in cmd)
        'cachedir': False, # attempt to fix 403 Forbidden error
        'progress_hooks': [finished],
        'outtmpl': str_SAVE_PATH + '/%(title)s.%(ext)s'
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(lov)

def ScrapeVidId(query):
    BASE = "https://www.youtube.com"
    SEARCH = "/results?search_query="
    search_url = (BASE + SEARCH + query + " audio")
    session = HTMLSession()
    response = session.get(search_url)
    response.html.render(sleep=1)
    soup = BeautifulSoup(response.html.html, "html.parser")
    results = soup.find('a', id="video-title")
    href = results.get('href')
    WATCH = (BASE + href)
    return WATCH

def getAlbumName():
     data = pd.read_csv("songs.csv")
     nameWithoutEmoji = demoji.replace(str(data.columns[0].split("- ")[1]), repl="")
     return nameWithoutEmoji

def playlist():
    data = pd.read_csv('songs.csv')
    data = data[data.columns[0]].tolist()
    return data

def showSong():
    global SONG
    global counter
    data = pd.read_csv('songs.csv')
    data = data[data.columns[0]].tolist()
    if counter < len(playlist()):
        SONG.append(data[counter])
        counter += 1
    else:
        SONG.clear()

def __main__():
# Loads the csv
    showSong() # Fills SONG with first song in the playlist
    print ("Found", len(playlist()), "songs in your playlist")
    print("")
    DownloadVideosFromTitles(playlist())
__main__()
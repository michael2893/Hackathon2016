# all the imports
import os
import fnmatch
import eyed3
from flask import Flask, request, g, redirect, url_for, abort, \
     render_template, session
import json

# create the application
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.from_envvar('MUSICPLAYER_SETTINGS', silent=True)
db = "library.json"
current_track = None

@app.route('/')
def show_library():
    refresh_library()
    return render_template('show_library.html', tracks=load_library())

def load_library():
    return json.load(open(db, "r"))

def refresh_library(dir_name="./library", ext="*.mp3"):
    metadata = load_library()
    paths = [track["path"] for track in metadata]
    
    # check if the folder exists
    if(not os.path.isdir(dir_name)):
        return []

    # walk all the subdirectories
    eyed3.log.setLevel("ERROR")
    folders = os.listdir(dir_name)
    for folder in folders:
        for (path, _, files) in os.walk(os.path.join(dir_name, folder)):
            for f in files:
                if(fnmatch.fnmatch(f.lower(), ext.lower())):
                    track_path = os.path.join(path, f)
                    if(track_path not in paths):
                        track = eyed3.load(track_path)
                        paths.append(track_path)
                        metadata.append({"title":track.tag.title, 
                                        "artist":track.tag.artist,
                                        "album":track.tag.album,
                                        "track_num":track.tag.track_num[0],
                                        "path":track_path,
                                        "tags":[]})
    dump_library(metadata)

def dump_library(jsondata):
    json.dump(jsondata, open(db, "w"))

@app.route("/play", methods=['GET', 'POST'])
def play():
    sound = pygame.mixer.music.load(load_library()[0]["path"])
    clock = pygame.music.play()
    time.sleep(2)
    pygame.mixer.music.stop()

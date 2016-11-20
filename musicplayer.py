# all the imports
import os
import fnmatch
import eyed3
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template

# create the application
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'tracklist.db'),
))
app.config.from_envvar('MUSICPLAYER_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print 'Initialized the database.'

@app.route('/')
def show_library():
    db = get_db() 
    populate_db(db)
    cur = db.execute('select title, artist, album from tracks order by id desc')
    library = cur.fetchall()
    return render_template('show_library.html', tracks=library)

def populate_db(db):
    metadata = parse_library("./library")
    for track_entry in metadata:
        db.execute("insert into tracks (title, artist, album, track_num) values (?, ?, ?, ?)",
                    [track_entry[0], track_entry[1], track_entry[2], track_entry[3]])
    db.commit()

def parse_library(dir_name, ext="*.mp3"):
    paths, metadata = [], []

    # check if the folder exists
    if(not os.path.isdir(dir_name)):
        return []

    # walk all the subdirectories
    folders = os.listdir(dir_name)
    for folder in folders:
        for (path, _, files) in os.walk(os.path.join(dir_name, folder)):
            for f in files:
                if(fnmatch.fnmatch(f.lower(), ext.lower())):
                    track_path = os.path.join(path, f)
                    track = eyed3.load(track_path)
                    metadata.append([track.tag.title, track.tag.artist,
                                     track.tag.album, track.tag.track_num[0]])
    return metadata
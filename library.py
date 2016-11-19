import os
import fnmatch
import eyed3

def get_tracks(dir_name):
	paths = get_paths(dir_name)
	return parse_metadata(paths)

def get_paths(dir_name, ext="*.mp3"):
    names = []
    fullnames = []

    # check if the folder exists
    if(not os.path.isdir(dir_name)):
        return [], [], []

    # if the dir_name finishes with the file separator,
    # remove it so os.walk works properly
    dir_name = dir_name[:-1] if dir_name[-1] == os.sep else dir_name

    # walk all the subdirectories
    folders = os.listdir(dir_name)
    for folder in folders:
        print(folder)
        for (path, _, files) in os.walk(os.path.join(dir_name, folder)):
            for f in files:
                if(fnmatch.fnmatch(f.lower(), ext.lower())):
                    try:
                        names.append(unicode(f, 'utf-8'))
                    except TypeError:  # already unicode
                        names.append(path)
                    fullnames.append(os.path.join(path, f))
    return fullnames

def parse_metadata(pathlist):
	metadata = []
	for path in pathlist:
		track = eyed3.load(path)
		metadata.append([track.tag.title, track.tag.artist, 
						track.tag.album, track.tag.track_num[0], 
						track.tag.album_artist])
	return metadata
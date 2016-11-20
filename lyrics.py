import urllib
import sys
import os
import re
import subprocess
import lxml.html

def lyricwikicase(s):

	words = s.split()
	newwords = []
	for word in words:
		newwords.append(word[0].capitalize() + word[1:])
	s = "_".join(newwords)
	s = s.replace("<", "Less than")
	s = s.replace(">", "Greater than")
	s = s.replace("[", "(")
	s = s.replace("]", ")")
	s = s.replace("{", "(")
	s = s.replace("}", ")")
	s = urllib.urlencode([(0, s)])[2:]
	return s

def lyricwikipagename(artist, title):
	return "%s:%s" % (lyricwikicase(artist), lyricwikicase(title))

def lyricwikiurl(artist, title, edit=False, fuzzy=False):

	if fuzzy:
		base = "http://lyrics.wikia.com/index.php?search="
		pagename = artist + ':' + title
		if not edit:
			url = base + pagename
			doc = lxml.html.parse(url)
			return doc.docinfo.URL
	else:
		base = "http://lyrics.wikia.com/"
		pagename = lyricwikipagename(artist, title)
	if edit:
		if fuzzy:
			url = base + pagename
			doc = lxml.html.parse(url)
			return doc.docinfo.URL + "&action=edit"
		else:
			return base + "index.php?title=%s&action=edit" % pagename
	return base + pagename

def __executableexists(program):

	for path in os.environ["PATH"].split(os.pathsep):
		exefile = os.path.join(path, program)
		if os.path.exists(exefile) and os.access(exefile, os.X_OK):
			return True
			return False

def currentlyplaying():
	"""Return a tuple (artist, title) if there is a currently playing song in 
	MPD or Rhythmbox, otherwise None.
	Raise an OSError if no means to get the currently playing song exist."""

	artist = None
	title = None

	mpc = __executableexists("mpc")
	rhythmbox = __executableexists("rhythmbox-client")

	if not mpc and not rhythmbox:
		raise OSError("neither mpc nor rhythmbox-client are available")

	if mpc:
		output = subprocess.Popen(["mpc", "--format", "%artist%\\n%title%"],
				stdout=subprocess.PIPE).communicate()[0].split("\n")
		if not output[0].startswith("volume: "):
			(artist, title) = output[0:2]

	if artist is None and rhythmbox:
		output = subprocess.Popen(
				["rhythmbox-client", "--no-start", "--print-playing", 
						"--print-playing-format=%ta\n%tt"],
				stdout=subprocess.PIPE).communicate()[0]
		if len(output) > 0 and output != "Not playing\n":
			(artist, title) = output.split("\n")[0:2]

	if artist is None or title is None:
		return None
	return (artist, title)

def getlyrics(artist, title, fuzzy=False):
	"""Get and return the lyrics for the given song.
	Raises an IOError if the lyrics couldn't be found.
	Raises an IndexError if there is no lyrics tag.
	Returns False if there are no lyrics (it's instrumental)."""

	try:
		doc = lxml.html.parse(lyricwikiurl(artist, title, fuzzy=fuzzy))
	except IOError:
		raise

	try:
		lyricbox = doc.getroot().cssselect(".lyricbox")[0]
	except IndexError:
		raise

	# look for a sign that it's instrumental
	if len(doc.getroot().cssselect(".lyricbox a[title=\"Instrumental\"]")):
		return False

	# prepare output
	lyrics = []
	if lyricbox.text is not None:
		lyrics.append(lyricbox.text)
	for node in lyricbox:
		if str(node.tag).lower() == "br":
			lyrics.append("\n")
		if node.tail is not None:
			lyrics.append(node.tail)
	return "".join(lyrics).strip()



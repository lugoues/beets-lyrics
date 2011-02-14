#parts of this plugin were borrowed from https://github.com/Xjs/lyricwiki/blob/master/lyricwiki.py
import os
import logging
import shutil
import logging
import sys
import unicodedata
from restkit import Resource
import html5lib
from html5lib import treebuilders
import simplejson
from urllib import unquote

from beets.plugins import BeetsPlugin
from beets import autotag
from beets.autotag import mb
from beets.mediafile import MediaFile, FileTypeError, UnreadableFileError, FileTypeError

from beets.ui import Subcommand
from beets import ui
from beets.ui import print_
from beets import library

DEFAULT_LYRICS_FORCE = False

parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("lxml"))
charset = 'utf-8' # TODO: get this from HTTP response

def proper_unicode(string):
	return unicodedata.normalize('NFC', unicode(string, charset))

def url_from_api(artist, song):
	"""Get URL to lyrics article from lyrics.wikia.com API"""
	r =  Resource('http://lyrics.wikia.com', headers={'Accept':'application/json'})
	json = r.get('/api.php', fmt='json', artist=proper_unicode(artist), song=proper_unicode(song))
	if not isinstance(json, basestring):
		# Compatibility for restkit >= 0.9
		json = json.body_string()#.unicode_body
	json = json[6:].replace("'", '"') # replace needed because wikia doesn't provide us with valid JSON. [6:] needed because it says "song = " first.
	d = simplejson.loads(json)
	if d['lyrics'] == 'Not found':
		raise ValueError("No lyrics for {song} by {artist}".format(song=song, artist=artist))
	else:
		#print >>sys.stderr, 'url =', d['url']
		return unicode(unquote(d['url'].encode(charset)), charset)
	
def artist_song_from_api_url(url):
	"""Get wiki-compatible artist, song tuple from URL retrieved from API"""
	return tuple(url[len('http://lyrics.wikia.com/'):].rsplit(':', 1))

def edit_url_from(url):
	"""Get URL to "edit this page" from a given lyrics page"""
	source = Resource(url).get()
	if not isinstance(source, basestring):
		source = source.unicode_body
	document = parser.parse(source)
	
	edit_link = document.find(".//{http://www.w3.org/1999/xhtml}a[@id='ca-edit']")
	return ''.join(['http://lyrics.wikia.com', dict(edit_link.items())['href']])
	
def lyrics_from(base_url, *arguments, **parameters):
	"""Get lyrics string from an edit page"""
	edit_source = Resource(base_url).get(*arguments, **parameters)
	if not isinstance(edit_source, basestring):
		edit_source = edit_source.body_string()#.unicode_body
	edit_document = parser.parse(edit_source)
	
	wiki_source = edit_document.find(".//{http://www.w3.org/1999/xhtml}textarea[@id='wpTextbox1']").text
	start = wiki_source.find("<lyrics>")+len("<lyrics>")
	end = wiki_source.find("</lyrics>")
	return wiki_source[start:end].strip()

def lyrics(artist, song):
	"""Get lyrics using the API and an edit page"""
	api_url = url_from_api(artist, song)
	artist_song = artist_song_from_api_url(api_url)
	return lyrics_from('http://lyrics.wikia.com/', 'index.php', title=u'{0}:{1}'.format(*artist_song), action='edit')
	

def lyrics_tag(paths, force=False):
 for path in paths:
	if os.path.isdir(path):
		# Find all files in the directory.
		filepaths = []
		for root, dirs, files in autotag._sorted_walk(path):
			for filename in files:
				filepaths.append(os.path.join(root, filename))
	else:
		# Just add the file.
		filepaths = [path]

	# Add all the files.
	for filepath in filepaths:
		try:
			mf = MediaFile(filepath)
			item = library.Item.from_path(filepath)
		except FileTypeError:
			continue
		except UnreadableFileError:
			log.warn('unreadable file: ' + filepath)
			continue		
			
		if( len(mf.lyrics) == 0 or force):
			print 'Tagging: ' + mf.artist + ' : ' + mf.title
			mf.lyrics = lyrics(mf.artist.encode(), mf.title.encode())
			mf.save()
		else:
			print 'Skipping: ' + mf.artist + ' : ' + mf.title
			
	
DEFAULT_LYRICS_FORCE = False
lyrics_cmd = Subcommand('lyrics', help='fetch lyrics')
def lyrics_func(lib, config, opts, args):
	force  = opts.force  if opts.force  is not None else \
        ui.config_val(config, 'lyrics', 'force',
            DEFAULT_LYRICS_FORCE, bool)
	lyrics_tag(args, force)
lyrics_cmd.func = lyrics_func
lyrics_cmd.parser.add_option('-f', '--force', action='store_true', default=None, help='overwrite tag updates')

	

class LyricsPlugin(BeetsPlugin):	
    def commands(self):
		return [lyrics_cmd]


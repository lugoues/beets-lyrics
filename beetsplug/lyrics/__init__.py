#parts of this plugin were borrowed from https://github.com/Xjs/lyricwiki/blob/master/lyricwiki.py
import os, logging, shutil, logging, sys, unicodedata

from beets.plugins import BeetsPlugin
from beets import autotag
from beets.mediafile import MediaFile, FileTypeError, UnreadableFileError, FileTypeError
from beets import library
from beets import ui
from beets.ui import print_
from beets.ui import Subcommand

sys.path.append('./engines')
from engines import *
from engines.engine import *

from twisted.internet import reactor, threads, defer


DEFAULT_LYRICS_FORCE = False
DEFAULT_ENGINES = ['ailrc','ALSong', 'baidu', 'cdmi', 'evillyrics', 'google', 'lrcdb', 'lyrdb', 'miniLyrics', 'sogou', 'ttPlayer', 'winampcn', 'youdao']

def scrubEncoding(str):
	encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
	try:
		return str.encode(encoding)
	except UnicodeError:
		return str.encode('utf8')

def find_lyrics(engines, artist, title):
	try:
		eng, lyrList =  multiSearch(engines, artist, title)
	except TypeError:				
		return None;
	
	if( lyrList is None or len(lyrList) == 0):
		print 'No Lyrics found for'
		return None
	
	if( len(lyrList) == 1):		
		lyr, timeOut = eng.downIt(lyrList[0][2])
	else:		
		#todo: allow user to select?
		lyr, timeOut = eng.downIt(lyrList[0][2])	
		
	if( not timeOut):
		return unicode(lyr, 'utf-8')
	else:
		return None
	
def tag_file(engines, filepath, force):
	try:
		mf = MediaFile(filepath)			
	except FileTypeError:
		return 
	except UnreadableFileError:
		log.warn('unreadable file: ' + filepath)
		return
		
	if( len(mf.lyrics) == 0 or force):								
		lyr = find_lyrics(engines,scrubEncoding(mf.artist),scrubEncoding(mf.title))
		
		if( lyr ):
			mf.lyrics = lyr				
			mf.save()
			print_("Lyrics for: [%s - %s]" % (mf.artist, mf.title), ui.colorize('green', 'Updated!'))
		else:
			print_("Lyrics for: [%s - %s]" % (mf.artist, mf.title), ui.colorize('red', 'Nothing Found'))
	else:
		print_("Lyrics for: [%s - %s]" % (mf.artist, mf.title), ui.colorize('yellow', 'Not Updated'))
	
	
def lyrics_tag(engines, paths, force=False):
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
			
	ds = []
  		
	# Add all the files.
	for filepath in filepaths:
		d = threads.deferToThread(tag_file,engines, filepath, force)	
		ds.append(d)		
		
	dlist = defer.DeferredList(ds, consumeErrors=True)	
	def stop_loop(x):	
		print 'Done!'
		reactor.stop()	
		exit		
	dlist.addCallback(stop_loop)
	
	def err_call(x):
		print x
		exit	
	dlist.addErrback(err_call)	
	
	reactor.run()		

			
lyrics_cmd = Subcommand('lyrics', help='fetch lyrics')
def lyrics_func(lib, config, opts, args):
	force  = opts.force  if opts.force  is not None else \
        ui.config_val(config, 'lyrics', 'force',
            DEFAULT_LYRICS_FORCE, bool)
			
	engines = ui.config_val(config, 'lyrics', 'engines', '').split()
	
	if( len(engines) == 0):
		engines = DEFAULT_ENGINES
	
	lyrics_tag(engines, args, force)
lyrics_cmd.func = lyrics_func
lyrics_cmd.parser.add_option('-f', '--force', action='store_true', default=None, help='overwrite tag updates')

class LyricsPlugin(BeetsPlugin):	
    def commands(self):
		return [lyrics_cmd]


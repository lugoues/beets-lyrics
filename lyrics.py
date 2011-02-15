#parts of this plugin were borrowed from https://github.com/Xjs/lyricwiki/blob/master/lyricwiki.py
import os
import logging
import shutil
import logging
import sys
import unicodedata

from beets.plugins import BeetsPlugin
from beets import autotag
from beets.autotag import mb
from beets.mediafile import MediaFile, FileTypeError, UnreadableFileError, FileTypeError

from beets.ui import Subcommand
from beets import ui
from beets.ui import print_
from beets import library

sys.path.append('./engines')
from engines import *
from engines.engine import *

DEFAULT_LYRICS_FORCE = False
DEFAULT_ENGINES = ['ailrc','ALSong', 'baidu', 'cmdi', 'evillyrics', 'google', 'lrcdb', 'lyrdb', 'miniLyrics', 'sogou', 'ttPlayer', 'winampcn', 'youdao']

def find_lyrics(engines, artist, title):
	eng, lyrList =  multiSearch(engines, artist, title)
	
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
			#print_("Lyrics for: [%s - %s]" % (mf.artist, mf.title))
			lyr = find_lyrics(engines, mf.artist, mf.title)
			
			if( lyr ):
				mf.lyrics = lyr				
				mf.save()
				print_("Lyrics for: [%s - %s]" % (mf.artist, mf.title), ui.colorize('green', 'Updated!'))
		else:
			print_("Lyrics for: [%s - %s]" % (mf.artist, mf.title), ui.colorize('red', 'Nothing Found'))
			
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


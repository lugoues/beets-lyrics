import os, logging, logging, sys
from importlib import import_module

from beets import autotag, ui
from beets.mediafile import MediaFile, FileTypeError, UnreadableFileError
from beets.plugins import BeetsPlugin
from beets.ui import print_, Subcommand

from beetsplug.lyrics.engines.engine import *
from beetsplug.lyrics.utilites import *

from twisted.internet import reactor, threads, defer

DEFAULT_LYRICS_FORCE = False
DEFAULT_ENGINES = ['ailrc','ALSong', 'baidu', 'cdmi', 'evillyrics', 'google', 'lrcdb', 'lyrdb', 'miniLyrics', 'sogou', 'ttPlayer', 'winampcn', 'youdao']

log = logging.getLogger('beets')
log.addHandler(logging.StreamHandler())

class LyricsPlugin(BeetsPlugin):
	'''Lyrics plugin for beets'''
	engines = []
	proxy = None
	locale = "utf-8"
	force = False
		
	def commands(self):
		lyrics_cmd = Subcommand('lyrics', help='fetch lyrics')	
		lyrics_cmd.func = self.lyrics_func
		lyrics_cmd.parser.add_option('-f', '--force', action='store_true', default=None, help='overwrite tag updates')

		return [lyrics_cmd]		
				
	def lyrics_func(self, lib, config, opts, args):
		#load force option
		self.force  = opts.force  if opts.force  is not None else \
			ui.config_val(config, 'lyrics', 'force',
				DEFAULT_LYRICS_FORCE, bool)
				
		#load engine options
		engine_names = ui.config_val(config, 'lyrics', 'engines', '').split()
		if( len(engine_names) == 0):
			engine_names = DEFAULT_ENGINES

		#load all requested engines		
		for eng_name in engine_names:								
			try:
				self.engines.append(  getattr(import_module(".engine_%s"%eng_name, 'beetsplug.lyrics.engines'),eng_name)(self.proxy, 'utf-8')		)			
			except Exception,e:						
				print e

		#start tagging
		#lyrics_tag( engines, args, force)
		self.process_directories(args)
		
		
	def process_directories(self, paths):
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
							
			try:	
				ds = []
			
				# Add all the files.
				for filepath in filepaths	:
					try:						
						mf = MediaFile(filepath)														
						#lyr = self.download_lyrics( mf )												
						#self.tag_file(mf, lyr)
						
						d = threads.deferToThread(self.download_lyrics, mf)	
						d.addCallback( self.tag_file,mf )
						
						ds.append(d)									
					except FileTypeError:												
						continue
					except UnreadableFileError:
						log.warn('unreadable file: ' + filepath)
						continue
						
						
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
						
			except Exception, e:
				print e
								
	def download_lyrics(self, mf):		
		try:
			artist = scrub(mf.artist)
			title = scrub(mf.title)
		except Exception, e:
			print e
		
		try:
			eng, lyrList =  multiSearch(self.engines, artist, title)
		except TypeError:				
			return None;

		if( lyrList is None or len(lyrList) == 0):		
			return None

		if( len(lyrList) == 1):		
			lyr, timeOut = eng.downIt(lyrList[0][2])
		else:		
			#todo: allow user to select?
			lyr, timeOut = eng.downIt(lyrList[0][2])	
			
		if( not timeOut):
			return unicode(lyr, 'utf-8')
		else:
			return  None
		
	def tag_file(self, lyrics, mf):							
		if( lyrics ):
			if( len(mf.lyrics) == 0 or self.force):														
				mf.lyrics = lyrics
				mf.save()
				print_("Lyrics for: [%s - %s]" % (mf.artist, mf.title), ui.colorize('green', 'Updated!'))			
			else:
				print_("Lyrics for: [%s - %s]" % (mf.artist, mf.title), ui.colorize('yellow', 'Not Updated'))
		else:
			print_("Lyrics for: [%s - %s]" % (mf.artist, mf.title), ui.colorize('red', 'Nothing Found'))
		
		
		
		
		
		
		
		
		
	


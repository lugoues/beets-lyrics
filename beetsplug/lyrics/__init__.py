import os, logging, logging, sys, multiprocessing, copy_reg, types, threading, time
from Queue import Queue
from importlib import import_module

from beets import autotag, ui
from beets.mediafile import MediaFile, FileTypeError, UnreadableFileError
from beets.plugins import BeetsPlugin
from beets.ui import print_, Subcommand

from beetsplug.lyrics.engines.engine import *
from beetsplug.lyrics.utilites import *

DEFAULT_LYRICS_FORCE = False
DEFAULT_ENGINES = ['miniLyrics', 'ailrc','ALSong', 'baidu', 'cdmi', 'lrcdb', 'lyrdb', 'sogou', 'ttPlayer', 'winampcn', 'youdao', 'evillyrics', 'google']
DEFAULT_PROCESS_COUNT = 5

log = logging.getLogger('beets')
log.addHandler(logging.StreamHandler())


class LyricsPlugin(BeetsPlugin):
	'''Lyrics plugin for beets'''

	engines = []
	proxy = None
	locale = "utf-8"
	force = False
	processcount = 1

	class LyricsFetcher(threading.Thread):
		def __init__(self, engines, fileQueue, lyricsQueue):   
			self.fileQueue = fileQueue
			self.lyricsQueue = lyricsQueue
			self.engines = engines
			threading.Thread.__init__(self)

		def run(self):         
			while True:    
				mf = self.fileQueue.get()

				if mf == None:
					self.lyricsQueue.put((None,None))
					self.fileQueue.task_done()     
					break

				#print_("Lyrics for: [%s - %s] - Fetching" % (mf.artist, mf.title))
				lyrics = self.fetchLyrics(mf)
				self.lyricsQueue.put( (mf, lyrics))    
				self.fileQueue.task_done()


		def fetchLyrics(self, mf):
			try:
				artist = scrub(mf.artist)
				title = scrub(mf.title)
			except Exception, e:
				print e

			try:
				eng, lyrList = multiSearch(self.engines, artist, title)
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
				return None


	class LyricsWriter(threading.Thread):
		def __init__(self, lyricsQueue):
			self.lyricsQueue = lyricsQueue   
			threading.Thread.__init__(self)

		def run(self):
			while True:
				mf, lyrics = self.lyricsQueue.get()    

				if mf == None: 
					self.lyricsQueue.task_done()
					break;

				self.tag_file(mf, lyrics)

				self.lyricsQueue.task_done()    

		def tag_file(self, mf, lyrics):       
			if( lyrics ):    
				mf.lyrics = lyrics
				mf.save()
				print_("Lyrics for: [%s - %s]" % (mf.artist, mf.title), ui.colorize('green', 'Updated!'))
			else:
				print_("Lyrics for: [%s - %s]" % (mf.artist, mf.title), ui.colorize('red', 'Nothing Found'))


	def commands(self):
		lyrics_cmd = Subcommand('lyrics', help='fetch lyrics') 
		lyrics_cmd.func = self.lyrics_func
		lyrics_cmd.parser.add_option('-f', '--force', action='store_true', default=None, help='overwrite tag updates')
		lyrics_cmd.parser.add_option('-p', '--processes', dest='processes', help='number of concurrent threads to run')
		  
		return [lyrics_cmd]  
	

	def lyrics_func(self, lib, config, opts, args):
	#load force option
		self.force = opts.force if opts.force is not None else \
			ui.config_val(config, 'lyrics', 'force',
				DEFAULT_LYRICS_FORCE, bool)

		#load engine options
		engine_names = ui.config_val(config, 'lyrics', 'engines', '').split()
		if( len(engine_names) == 0):
			engine_names = DEFAULT_ENGINES

		#load process count
		self.processcount = opts.processes if opts.processes is not None else \
		int(ui.config_val(config, 'lyrics', 'processes', DEFAULT_PROCESS_COUNT))

		#load all requested engines  
		for eng_name in engine_names:        
			try:
				self.engines.append( getattr(import_module(".engine_%s"%eng_name, 'beetsplug.lyrics.engines'),eng_name)(self.proxy, 'utf-8')  )   
			except Exception,e:      
				print e  

		if len(args) != 0:
			self.process_path(args)

	def process_path(self, basePath):
		try:
			fileQueue = Queue()
			lyricsQueue = Queue()  

			#spawn threads
			lyricsWriter = self.LyricsWriter(lyricsQueue)
			lyricsWriter.setDaemon(True)
			lyricsWriter.start()  

			for i in xrange(self.processcount):				
				print "worker created"
				lf = self.LyricsFetcher(self.engines, fileQueue, lyricsQueue)
				lf.setDaemon(True)
				lf.start()

			#loop path and add files to parse
			for path in basePath:
				if os.path.isdir(path):
				# Find all files in the directory.
					filepaths = []    
					for root, dirs, files in autotag._sorted_walk(path):
						for filename in files:           
							self.try_queue_path(fileQueue, os.path.join(root, filename))      
				else:
					# Just add the file.
					self.try_queue_path(fileQueue, path)       

			#queue none to show end of file list
			fileQueue.put(None)

			#wait till we are finished 
			while lyricsWriter.is_alive(): time.sleep(1)        
		except (KeyboardInterrupt, SystemExit):
			return

	def try_queue_path(self, q, path):  
		try:      
			mf = MediaFile(path)

			if( len(mf.lyrics) == 0 or self.force):
				q.put(mf)    

		except FileTypeError:   
			return

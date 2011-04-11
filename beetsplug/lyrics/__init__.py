#Copyright (c) 2011, Peter Brunner (Lugoues)
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

import os, logging, logging, sys, multiprocessing, copy_reg, types, threading, time
from Queue import *
from importlib import import_module
from collections import defaultdict

from beets import autotag, ui
from beets.mediafile import MediaFile, FileTypeError, UnreadableFileError
from beets.plugins import BeetsPlugin
from beets.ui import print_, Subcommand
from beets.util.pipeline import *

from beetsplug.lyrics.engines.engine import *
from beetsplug.lyrics.utilites import *

DEFAULT_LYRICS_FORCE = False
DEFAULT_ENGINES = ['miniLyrics', 'ailrc','ALSong', 'baidu', 'cdmi', 'lrcdb', 'lyrdb', 'sogou', 'ttPlayer', 'winampcn', 'youdao', 'evillyrics', 'google']
DEFAULT_PROCESS_COUNT = 5
DEFAULT_ON_IMPORT = True

log = logging.getLogger('beets')
log.addHandler(logging.StreamHandler())

class LyricsPlugin(BeetsPlugin):
    '''Lyrics plugin for beets'''

    engines = []
    proxy = None
    locale = "utf-8"
    force = False
    processcount = 1
    on_import = True

    def fetchLyrics(self, artist, title):
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

    def __init__(self):
        #register listeners
        self.register_listener('album_imported', self.album_imported)

    def commands(self):
        lyrics_cmd = Subcommand('lyrics', help='fetch lyrics')
        lyrics_cmd.func = self.lyrics_func
        lyrics_cmd.parser.add_option('-f', '--force', action='store_true', default=None, help='overwrite tag updates')
        lyrics_cmd.parser.add_option('-p', '--processes', dest='processes', help='number of concurrent threads to run')

        return [lyrics_cmd]

    def configure(self, config):
        self.on_import = ui.config_val(config, 'lyrics', 'on_import', DEFAULT_ON_IMPORT, bool)
        self.processcount = int(ui.config_val(config, 'lyrics', 'processes', DEFAULT_PROCESS_COUNT))

        #load engine options
        engine_names = ui.config_val(config, 'lyrics', 'engines', '').split()
        if( len(engine_names) == 0):
            engine_names = DEFAULT_ENGINES

        #load all requested engines
        for eng_name in engine_names:
            try:
                self.engines.append( getattr(import_module(".engine_%s"%eng_name, 'beetsplug.lyrics.engines'),eng_name)(self.proxy, 'utf-8')  )
            except Exception,e:
                print e

    def item_imported(self, lib, item):
        lyrics = self.fetchLyrics(scrub(item.artist), scrub(item.title))

        item.lyrics = lyrics
        item.write()
        lib.store(item)


    def album_imported(self, lib, album):
        if self.on_import == False :
            pass
        print_("Tagging Lyrics:  %s - %s" % (album.albumartist, album.album))

        def produce():
            def create_mf(path):
                for item in album.items():
                    yield(item, item.artist, item.title)

        def work():
            while True:
                item, artist, title = yield
                lyrics = self.fetchLyrics(scrub(artist), scrub(title))
                yield((item, lyrics))

        def consume():
            while True:
                item, lyrics = yield
                item.lyrics = lyrics
                item.write()
                lib.store(item)


        Pipeline([produce(), work(), consume()]).run_parallel(1)


    def lyrics_func(self, lib, config, opts, args):
        pass
        #load force option
        self.force = opts.force if opts.force is not None else \
            ui.config_val(config, 'lyrics', 'force',
                DEFAULT_LYRICS_FORCE, bool)

        #load process count
        self.processcount = opts.processes if opts.processes is not None else \
        int(ui.config_val(  config, 'lyrics', 'processes', DEFAULT_PROCESS_COUNT))

        if len(args) != 0:
            self.process_path(args)

    def process_path(self, basePath):
        def produce():
            def create_mf(path):
                try:
                    mf = MediaFile(path)
                    if( len(mf.lyrics) == 0 or self.force):
                        #print_("    -%s:" % (mf.title), ui.colorize('yellow', 'Queued'))
                        return mf
                except FileTypeError:
                    return BUBBLE
            for path in basePath:
                if os.path.isdir(path):
                # Find all files in the directory.
                    filepaths = []
                    for root, dirs, files in autotag._sorted_walk(path):
                        for filename in files:
                            mf = create_mf(os.path.join(root, filename))
                            if mf != None:
                                yield mf
                else:
                    # Just add the file.
                    mf = create_mf(path)
                    if mf != None:
                        yield mf

        def work():
            mf = yield
            while True:
                print_("    -%s:" % (mf.title), ui.colorize('yellow', 'Fetching'))
                lyrics = self.fetchLyrics(scrub(mf.artist), scrub(mf.title))
                result = (mf, lyrics);
                print "worker results: %s" % str(result)
                mf = yield result

        def consume():
            while True:
                res = yield
                print res
                if res != None:
                    mf, lyrics = res
                    if( lyrics ):
                        mf.lyrics = lyrics
                        mf.save()

                        print_("    -%s:" % (mf.title), ui.colorize('green', 'Updated!'))
                    else:
                        print_("    -%s: " % (mf.title), ui.colorize('red', 'Not Found'))


        Pipeline([produce(), work(), consume()]).run_parallel(1)

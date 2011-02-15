#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: plain_lyrics.py
#
#

import sys,os
import urllib,re,time
import urllib2,cookielib
from htmlentitydefs import name2codepoint as n2cp

def importChardet():
	if "chardet" in sys.modules:
		return sys.modules["chardet"]
	try:
		import chardet
	except:
		#get the file path
		ap = os.path.abspath(sys.modules[self.__module__].__file__)
		#get the file directory
		ap = os.path.dirname(ap)
		#get lrcShow directory
		ap = os.path.dirname(ap)
		sys.path.append(ap)
		import chardet
		sys.path.remove(ap)
	return sys.modules["chardet"]

def autoDecode(string):
	chardet = importChardet()
	enc = chardet.detect(string)['encoding']
	if enc == "GB2312":
		try:
			string = string.decode("gb18030")
		except:
			string = string.decode("GB2312")
	elif enc == "windows-1251":
		try:
			string = string.decode("windows-1252")
		except:
			string = string.decode("windows-1251")
	else:
		string = string.decode(enc)
	return string

def substitute_entity(match):
	ent = match.group(2)
	if match.group(1) == "#":
		return unichr(int(ent))
	else:
		cp = n2cp.get(ent)
		if cp:
			return unichr(cp)
		else:
			return match.group()

def decode_htmlentities(string):
	entity_re = re.compile("&(#?)(\d{1,5}|\w{1,8});",re.DOTALL)
	string = entity_re.sub(substitute_entity, string)
	return string.replace("&apos;","'")

junk_messages = (
	r"You must agree to the following statement or leave this website",
	r"being added to our catalog as we speak\.  If you would like to submit",
	r"We apologize for the inconvience",
	r"Please support the artists by purchasing",
	r"display these lyrics due to licensing restrictions"
)

valid_sites = (r'6lyrics.com',r'actionext.com',r'allthelyrics.com',r'asklyrics.com',r'azlyrics.com',r'free-lyrics.net',r'hotlyrics.net',
	r'justsomelyrics.com',r'kohit.net',r'kovach.co.yu',r'kovideo.net/lyrics',r'leoslyrics.com',r'letras.terra.com.br',r'letssingit.com',
	r'lyrics007.com',r'lyricsbay.com',r'lyricsbox.com',r'lyricsdepot.com',r'lyricsdir.com',r'lyricsdomain.com',r'lyricsdownload.com',
	r'lyrics.ee',r'lyricsfreak.com',r'lyrics-keeper.com',r'lyricsmania.com',r'lyricsmode.com',r'lyricsondemand.com',r'lyricspy.com',
	r'lyricsspot.com',r'lyricstime.com',r'lyricwiki.org',r'lyriki.com',r'themadmusicarchive.com',r'megalyrics.ru',r'metrolyrics.com',
	r'mldb.org',r'mp3-bg.com',r'mp3-download-lyrics.com',r'mp3lyrics.org',r'musicsonglyrics.com',r'mylyricsbox.com',r'plyrics.com',
	r'rare-lyrics.com',r'rockpoplyrics.com',r'sing365.com',r'song-lyrics.net',r'songmeanings.net',r'stlyrics.com',r'sweetslyrics.com',
	r'wearethelyrics.com')

junk_sites = ("google","youtube","last.fm","lastfm","rhapsody","aol","tabscout")

#
# Tries to detect the lyrics in the given html code
# Strips all the head section, strips all empty tags
# splits the remaing html in tags and gets the longest
# (the one with more text)
#
def getTextFromHtml(html):
	try:
		#get the body
		html = re.compile(r'<body[^>]*>(.*?)</body>',re.DOTALL | re.IGNORECASE).findall(html)[0]
	except:
		pass
	#convert br in "new line"
	html = re.compile(r'<br[ /]*>',re.IGNORECASE | re.DOTALL).sub("\n", html)
	#convert "no breaking space" into "space"
	html = html.replace('&nbsp;',' ')
	tags_to_remove = ("script","style")
	for i in tags_to_remove:
		#delete the whole tag
		html = re.compile(r'<%s>.*?</%s>' % (i,i),re.IGNORECASE | re.DOTALL).sub("",html)
		html = re.compile(r'<%s .*?</%s>' % (i,i),re.IGNORECASE | re.DOTALL).sub("",html)
	tags_to_mantain = ()
	for i in tags_to_mantain:
		#mantain the tag content
		html = re.compile(r'<%s>(.*?)</%s>' % (i,i),re.IGNORECASE | re.DOTALL).sub(r"\1",html)
		html = re.compile(r'<%s [^>]*>(.*?)</%s>' % (i,i),re.IGNORECASE | re.DOTALL).sub(r"\1",html)
	tags_to_check = ("u","strike","a","b","i","big","small","em","strong","tt","font")
	f = lambda x: x.group(1) if len(x.group(1)) > 300 else ""
	for i in tags_to_check:
		#mantain the tag content
		html = re.compile(r'<%s>(.*?)</%s>' % (i,i),re.IGNORECASE | re.DOTALL).sub( f , html )
		html = re.compile(r'<%s [^>]*>(.*?)</%s>' % (i,i),re.IGNORECASE | re.DOTALL).sub( f , html )
	#remove self closing tags
	html = re.compile(r'<[^>]+/>').sub("", html)
	#remove html comments
	html = re.compile(r'<!--.*?-->',re.DOTALL).sub("", html)
	#convert all tags into "tag"
	html = re.compile(r'<[^>]+>',re.DOTALL).sub(r"<tag>", html)
	while re.search(r'<[^>]+>\s*<[^>]+>',html,re.DOTALL):
		#remove empty tags
		html = re.compile(r'<tag>\s*<tag>',re.DOTALL).sub(r"<tag>", html)
	html = html.split('<tag>')
	html = [i.strip() for i in html]
	#get the part of html with more text
	html = max(html, key = len )
	html = re.compile(r'Please enable javascript to see this content.').sub("", html)
	#br check
	html = html.replace('&#10;','\n')
	html = html.replace('&#13;','\r')
	html = re.compile(r'(\r\n){1,1}',re.DOTALL).sub("\n", html)
	html = re.compile(r'(\r){1,1}',re.DOTALL).sub("\n", html)
	html = re.compile(r'\n[^\n\w]+\n',re.DOTALL).sub("\n", html)
	html = re.compile(r'\n+$',re.DOTALL).sub("",html)
	try:
		br_th = len(min(re.findall(r'\n{1,}',html,re.DOTALL), key=len))
		html = re.compile(r'\n{%d,%d}' % (br_th,br_th),re.DOTALL).sub("\n", html)
	except:
		br_th = 0
	if len(re.findall(r'\n{2,}',html,re.DOTALL)) > len(re.findall(r'\n{1,}',html,re.DOTALL))/2:
		html = re.compile(r'\n{2,}',re.DOTALL).sub("\n", html)
	else:
		html = re.compile(r'\n{2,}',re.DOTALL).sub("\n\n", html)
	#decode and return
	try:
		html = decode_htmlentities(html)
	except:
		html = autoDecode(html)
		html = decode_htmlentities(html)
	return html

#
# Given an url, it gets the html retrieving the web page
# and parses it using the getTextFromHtml function.
#
def getLyricsFromUrl(url,proxy=None):
	req=urllib2.Request(url)
	req.add_header("User-Agent","Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0)")
	cj = cookielib.LWPCookieJar()
	if proxy:
		opener = urllib2.build_opener(urllib2.ProxyHandler(proxy),urllib2.HTTPCookieProcessor(cj))
	else:
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	try:
		ff=opener.open(req,timeout = 1.5)
	except:
		return (None,True)
	text = ff.read()
	text = autoDecode(text)
	text = getTextFromHtml(text)
	#print text
	if len(text) > 10:
		return (text,False)
	return (None,False)

#
# Returns a tuple (url_list,timeout)
# timeout is True if failed to query google
# url_list contains the urls provided by google
#
def getUrlsFromGoogle(artist,title,proxy=None):
	#TODO: check on title/artist in url
	query="lyrics intitle:\"%s\" intitle:\"%s\"" % (artist,title)
	url="http://www.google.com/pda/search?mrestrict=xhtml&hl=en&lr=&num=5&q=%s" % (urllib.quote_plus(query))
	#sys.stdout.wirte(url+'\n')
	req=urllib2.Request(url)
	req.add_header("User-Agent","Opera/9.50 (J2ME/MIDP; Opera Mini/4.1.11355/546; U; en)")
	if proxy:
		opener = urllib2.build_opener(urllib2.ProxyHandler(proxy))
	else:
		opener = urllib2.build_opener()
	try:
		html=opener.open(req).read()
	except Exception,e:
		return (None,True)
	tmp = re.findall("href=\"(http://.*?)\"",html)#[:5]
	urls = []
	junk = ["google","youtube","last","rhapsody","aol","tabscout"]
	for url,i in map(lambda x: (tmp[x],len(tmp)-x),range(len(tmp))):
		host = re.findall("http://(.*?)/",url)[0]
		if tuple( (j for j in junk_sites if host.count(j) > 0) ):
			continue #Skip sites like google, youtube and others
		elif tuple( (j for j in valid_sites if host.count(j) > 0) ):
			i += 10 #give priority to known lyrics sites
		url=decode_htmlentities(url)
		urls.append((i,url))
	urls = map(lambda x: x[1],reversed(sorted(urls)))
	if urls:
		return (urls,False)
	return (None,False)

#
# Given artist and title, calls the getUrlsFromGoogle function
# and using those urls calls the getLyricsFromUrl function
#
def getLyrics(artist,title,proxy=None,withUrl=False):
	l,timeout = getUrlsFromGoogle(artist,title,proxy)
	if timeout or not l:
		return (None,timeout)
	for url in l:
		#sys.stdout.write(url+'\n')
		lyrics,timeout = getLyricsFromUrl(url,proxy=proxy)
		if timeout or not lyrics or len(lyrics) < 100:
			continue
		elif len(lyrics) < 300:
			if tuple( (True for i in junk_messages	if re.search(i,lyrics,re.IGNORECASE | re.DOTALL)) ):
				continue
		if withUrl:
			lyrics = "[url:%s]\n" % (url) + lyrics
		return (lyrics,False)
	return (None,False)


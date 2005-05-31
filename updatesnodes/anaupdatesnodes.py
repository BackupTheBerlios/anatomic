#!/usr/bin/env python

# this is a temporary script so that nodes aka. supertrackers are discovered quickly
# hopefully this will be embedded into the client in the future
# embedding into the client is only useful with many more supertrackers
# thanks to the teachers whose boring lessons gave me time to dream up this crazy idea  ;)
# see LICENSE.txt for license information

from bencode import bencode, bdecode
from urllib import urlencode
import os
from sys import argv
import time

VERSION = 'CVS'

print 'anaupdatesnodes.py %s - download a recent list of nodes' % VERSION
print 'USAGE:'
print 'anaupdatesnodes.py -url "URL OF A SUPERTRACKER" (if strackers.dat'
print 'is not present locally)'
DEFAULTURL = ["http://anatomic.berlios.de/network/node-b/cache.php", "http://anatomic.berlios.de/network/node-a/cache.php"]
url = DEFAULTURL # for now until it gets changed
import random
random.shuffle(url)
if os.path.isfile('strackers.dat') is True and (time.time() - os.path.getmtime('strackers.dat')) < 2592000: # check if file exists
	try:
		f = open('strackers.dat', "r")
	except IOError, e:
		print "WARNING Cannot open file:", e.filename
	else:
		file = f.readline()
		f.close()
		try:
			bdata = bdecode(file)
		except ValueError, e:
			print "WARNING: local strackers.dat is not valid BEncoded data: Using defaults"
		else:
			random.shuffle(bdata)
			url = bdata
else:
	if len(argv) == 3 and argv[1] == "--url":
		possurl = argv[2]
		if possurl[0:7] == "http://":
			url = [argv[2]]
		else:
			print "NOT A VALID URL (NO http://) - USING DEFAULT SUPERTRACKER LIST"
	else:
		print "WARNING: USING DEFAULT SUPERTRACKER LIST"

stracker = url
status = 0
strackerlist = []
for x in stracker:
	y = x
	x += "?strackers=1"
	try:
		import urllib2
		f = urllib2.Request(x)
		f.add_header('User-agent', 'Anatomic P2P Node Updater CVS +http://anatomic.berlios.de/' )
		opener = urllib2.build_opener()
		data = opener.open(f).read()
	except IOError, e:
		print "ERROR: Connection failed."
		print e
	else:
		try:
			bdata = bdecode(data)
			import types
			if type(bdata) == types.ListType:
				if y not in bdata:
					bdata.append(y) # Since it is alive it is probably useful
				for x in bdata:
					if x not in strackerlist:
						strackerlist.append(x)
		except ValueError, e:
			print "WARNING: No valid data received."
if len(strackerlist) == 0:
	print "ERROR: No useful data could be found. Please visit http://anatomic.berlios.de"
	print "for more help"
else:
	try:
		random.shuffle(strackerlist)
		bedata = bencode(strackerlist)
		f2 = open('strackers.dat', "w+")
	except IOError, e:
		print "WARNING Cannot write file:", e.filename
	else:
		f2.write(bedata)
		f2.close
		print "Data successfully downloaded and written"











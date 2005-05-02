#!/usr/bin/env python
# this script plants torrents on the Anatomic P2P network with a graphical interface
# thanks to the teachers whose boring lessons gave me time to dream up this crazy idea  ;-)
# see LICENSE.txt for license information
import sys
try:
	import pygtk	
	pygtk.require("2.0")
except:
	pass
try:
	import gtk
	import gtk.glade
except:
	print "You need to install pygtk or GTK+2"
	print "or set your PYTHONPATH correctly"
	print "Type 'export PYTHONPATH=/usr/lib/python2.4/site-packages/'"
	sys.exit(1)
import threading

# This code is a mess in places
# Httpplant is the thread that handles all web transactions
class Httpplant(threading.Thread):
	def __init__ ( self, filename, trackers ):
		self.filename = filename
		self.trackers = trackers
		threading.Thread.__init__(self)
	def run(self):
		from bencode import bencode, bdecode
		from sha import sha
		import os
		import time
		try:
			f = open(self.filename, "rb")
		except IOError, e:
			app.logbuffer.insert_with_tags_by_name(app.iter, "\rFATAL ERROR: Cannot open file: ", e.filename , "red_foreground")
			app.haltplant()
			sys.exit()
		file = f.read()
		f.close() 
		try:
			bdata = bdecode(file)
			if bdata.has_key("planted"):
				app.logbuffer.insert_with_tags_by_name(app.iter, "\rWARNING: The Torrent is being REPLANTED", "red_foreground")
		except ValueError, e:
			app.logbuffer.insert_with_tags_by_name(app.iter, "\rtorrent file is not valid BEncoded data", "red_foreground")
			app.haltplant()
			sys.exit(2)
		infohash = sha(bencode(bdata['info'])).digest()
		DEFAULTURL = ["http://anatomic.berlios.de/network/node-b/cache.php", "http://anatomic.berlios.de/network/node-a/cache.php"]
		url = DEFAULTURL # for now until it gets changed by other means
		if os.path.isfile('strackers.dat') is True and (time.time() - os.path.getmtime('strackers.dat')) < 2592000: # check if file exists and is recent(ish)
			try:
				f = open('strackers.dat', "r")
			except IOError, e:
				app.logbuffer.insert_with_tags_by_name(app.iter, "\rERROR: Cannot open file: "+str(e.filename), "red_foreground")
			file = f.read()
			f.close()
			try:
				b2data = bdecode(file)
				url = b2data
			except ValueError, e:
				app.logbuffer.insert_with_tags_by_name(app.iter, "\rWARNING: local strackers.dat is not valid BEncoded data: Using defaults" , "red_foreground") 
				url = DEFAULTURL
		else:
			app.logbuffer.insert_with_tags_by_name(app.iter,"\rWARNING: USING DEFAULT SUPERTRACKER LIST. LOCAL DATA FILE IS NOT PRESENT OR TOO OLD", "red_foreground") 
		from urllib import urlencode
		from random import shuffle
		shuffle(url)
		# Single Plant
		if self.trackers == 1:
			app.logbuffer.insert_with_tags_by_name(app.iter,"\rAttempting Single Tracker Plant", "purple_foreground") 
			urldict = {"plant" : 1, "client" : 1}
			urldict = urlencode(urldict)
			urlend = "?"
			urlend += urldict
			status = 0 # for now
			for x in url:
				stracker = x
				x += urlend
				try:
					import urllib2
					f = urllib2.Request(x)
					f.add_header('User-agent', 'Anatomic P2P Planter GUI CVS Edition (S)  +http://anatomic.berlios.de/' ) 
					opener = urllib2.build_opener()
					data = opener.open(f).read()
				except IOError:
					pass
				else:
					try:
						bdata3 = bdecode(data)
					except ValueError:
						pass
					else:  
						if len(bdata3) >= 8:
							status = 1 # i.e. successful first stage
							url.remove(stracker) # url becomes a list of other supertrackers
							break
			# if all of the strackers have been cycled through and nothing useful has been replied then die				
			if status == 0:
				app.logbuffer.insert_with_tags_by_name(app.iter,"\rError: No Response from any nodes. Please run anaupdatesnodes", "red_foreground") 
				app.haltplant()
				sys.exit(2)
			# or else
			# bdata3 is a single tracker left behind. tracker is going to have the querystring concatenated on it
			tracker = bdata3
			tracker = tracker.replace("/announce", "/plant")
			tracker += "?"
			tracker += urlencode({"client" : 1, "plant" : infohash})
			try:
				t = urllib2.Request(tracker)
				t.add_header('User-agent', 'Anatomic P2P Planter GUI CVS Edition (S)  +http://anatomic.berlios.de/' ) 
				opener = urllib2.build_opener()
				response = opener.open(t).read()
			except IOError, e:
				app.logbuffer.insert_with_tags_by_name(app.iter, "\rError: Tracker cannot be accessed. Please Try Again"+str(e), "blue_foreground")
			else:
				message = bdecode(response)
				import types
				if type(message) == types.DictType and message.has_key("failure reason"):
					app.logbuffer.insert_with_tags_by_name(app.iter, "\rError: "+message["failure reason"], "red_foreground")
					app.haltplant()
					sys.exit(1)
				else:
					app.logbuffer.insert_with_tags_by_name(app.iter, "\rMessage from tracker: "+message, "red_foreground")
					import random
					strackerlist = [random.choice(url), stracker] # this list contains a stracker and a backup stracker
					qstring = urlencode({"client" : 1, "tpush" : bdata3})
					for z in strackerlist:
						z += "?"
						z += qstring
						try:
							f3 = urllib2.Request(z)
							f3.add_header('User-agent', 'Anatomic P2P Planter GUI CVS Edition (S)  +http://anatomic.berlios.de/' ) 
							opener = urllib2.build_opener()
							data = opener.open(f3).read()
						except IOError:
							app.logbuffer.insert_with_tags_by_name(app.iter, "\rNo response from Supernode: Please try again.", "red_foreground") 
							app.haltplant()
							sys.exit(1)
					try:
						bdata2 = bdecode(data)
						if bdata2 == "TRUE":
							if bdata.has_key("announce-list"):
								del bdata["announce-list"]
							#hackwards compatibility
							announcelist = []
							for url in strackerlist:
								url = url.replace("/cache", "/announce") 
								announcelist.append(url)
							bdata["announcelist"] = [announcelist]
							stracker = stracker.replace("/cache", "/announce")
							bdata["announce"] = stracker		
							bdata["planted"] = 1
							bdata = bencode(bdata)
							try:
								f = open(self.filename, "wb")
							except IOError, e:
								app.logbuffer.insert_with_tags_by_name(app.iter, "\rERROR: Cannot write to file: "+e.filename, "red_foreground")  
							else:
								file = f.write(bdata)
								f.close()
								app.logbuffer.insert_with_tags_by_name(app.iter, "\rTorrent Successfully Planted on Anatomic P2P", "green_foreground")  
						else: 
							app.logbuffer.insert_with_tags_by_name(app.iter, "\rError: Supernode Response is very unexpected: "+bdata2, "red_foreground")   
					except ValueError:
							app.logbuffer.insert_with_tags_by_name(app.iter, "\rError: Supernode Response corrupt" , "red_foreground")  		
					app.haltplant()
					sys.exit()
		else:
			needed = self.trackers
			app.logbuffer.insert_with_tags_by_name(app.iter,"\rAttempting MultiPlant", "purple_foreground") 
 			qstring = "?" #querystring
			qstring += urlencode({"multiseed" : needed, "client" : 1})
			status = 0
			import types
			# to make sure data is in a list from tracker
			for x in url:
				stracker = x
				x += qstring
				try:
					import urllib2
					f = urllib2.Request(x)
					f.add_header('User-agent', 'Anatomic P2P Planter (MS) GUI CVS Edition +http://anatomic.berlios.de/' ) 
					opener = urllib2.build_opener()
					data = opener.open(f).read()
				except IOError:
					pass
				else:
					try:
						bdata3 = bdecode(data)
					except ValueError:
						pass
					else: 			
						if type(bdata3) == types.ListType:
							status = 1 # i.e. successful first stage
							trackers = bdata3
							url.remove(stracker)
					break
					
			if status == 0:
				app.logbuffer.insert_with_tags_by_name(app.iter, "\rError: No valid Response from any nodes. Please run anaupdatesnodes or lower the required trackers" , "red_foreground")  	 
				app.haltplant()
				sys.exit(2)	
			import copy
			trackers2 = copy.deepcopy(trackers)
			z = trackers2[0]
			del(trackers2[0])
			trackers2.append(z)
			for num in range(0,len(trackers)):
				tracker = trackers[num]
				tracker = tracker.replace("/announce", "/plant")
				othertracker = trackers2[num]
				qstring = "?"
				qstring += urlencode({"client" : 1, "multiplant" : infohash, "url" : othertracker})
				tracker += qstring
				try:
					t = urllib2.Request(tracker)
					t.add_header('User-agent', 'Anatomic P2P Planter (MS) GUI CVS Edition +http://anatomic.berlios.de/' ) 
					opener = urllib2.build_opener()
					response = opener.open(t).read()
				except IOError, e:
					app.logbuffer.insert_with_tags_by_name(app.iter, "\rError: Tracker cannot be accessed. Please Try Again - "+str(e) , "red_foreground")  	 
				else:
					message = bdecode(response)
					if type(message) == types.DictType and message.has_key("failure reason"):
						app.logbuffer.insert_with_tags_by_name(app.iter, "\rError: "+message["failure reason"] , "red_foreground")  	 
 					else:
						app.logbuffer.insert_with_tags_by_name(app.iter, "\rMessage from tracker: "+message , "purple_foreground")   
			import random
			strackerlist = [random.choice(url), stracker] 
			for tracker in trackers:
				qstring = "?"
				qstring += urlencode({"client" : 1, "tpush" : tracker})
				stracker = strackerlist[1] # this is the important stracker. [0] is a backup
				for z in strackerlist:	
					z += qstring
					try:
						import urllib2
						f = urllib2.Request(z)
						f.add_header('User-agent', 'Anatomic P2P Planter (MS) GUI CVS Edition +http://anatomic.berlios.de/' ) 
						opener = urllib2.build_opener()
						data = opener.open(f).read()
					except IOError:
						pass
					else:
						try:
							bdata3 = bdecode(data)
							app.logbuffer.insert_with_tags_by_name(app.iter, "\rMessage from Supertracker: "+bdata3, "purple_foreground")   
						except ValueError:
							pass
			
			#hackwards compatibility
			announcelist = []
			for url in strackerlist:
				url = url.replace("/cache", "/announce") 
				announcelist.append(url)
			bdata["announce-list"] = [announcelist]
			stracker = stracker.replace("/cache", "/announce")
			bdata["announce"] = stracker	
			bdata["planted"] = 1
			bdata = bencode(bdata)
			try:
				f = open(self.filename, "wb")
			except IOError, e:
				app.logbuffer.insert_with_tags_by_name(app.iter, "\rERROR: Cannot write to file: "+str(e.filename), "green_foreground")    
			else:
				file = f.write(bdata)
				f.close()
				app.logbuffer.insert_with_tags_by_name(app.iter, "\rTorrent Successfully MultiPlanted on Anatomic P2P (if there are no errors above)", "green_foreground")   
				app.haltplant()
class Plantergui:
	def __init__(self):
		# Main window (window1) is glade driven
		gladefile = "planter.glade"
		windowname = "window1"
		# This variable is for the file selector to remember the last directory
		self.lastdirname = ""
		# Whether this script is actively planting a torrent or not
		self.planting = 0
		self.window = gtk.glade.XML(gladefile, windowname)
		self.window.get_widget("window1").connect("delete_event", self.destroy)
		# button1 is the browse button
		# button2 is the quit button
		# button3 is the plant button
		self.window.get_widget("button2").connect("clicked", self.destroy)
		self.window.get_widget("button3").connect("clicked", self.check)
		self.window.get_widget("button1").connect("clicked", self.browsefile)
		# This is the main text logger that logs the planting script
		self.log = self.window.get_widget("textview1")
		self.logbuffer = gtk.TextBuffer(None)
		self.log.set_buffer(self.logbuffer)
		self.logbuffer.create_tag("blue_foreground", foreground="blue")
		self.logbuffer.create_tag("red_foreground", foreground="red")
		self.logbuffer.create_tag("purple_foreground", foreground="purple")
		self.logbuffer.create_tag("green_foreground", foreground="#009900")
		import time
		time = time.ctime()
		self.iter = self.logbuffer.get_iter_at_offset(0)
		self.textdata = time+": Program Loaded\rAnatomic P2P Planter CVS Edition\rLicenced under the MIT / X Consortium Licence"
		self.logbuffer.insert_with_tags_by_name(self.iter, self.textdata, "blue_foreground")
	def check(self, widget, data=None):
		# This function makes sure that a torrent file has been chosen
		if self.window.get_widget("entry1").get_text() == "":
			# Error messages are not glade based anymore
			self.dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR)
			self.dialog.set_title("Please choose a torrent file")
			self.dialog.set_markup("No torrent file has been chosen to plant. Please choose a valid torrent file using the 'Browse' button.")
			self.dialog.add_buttons(gtk.STOCK_OK,gtk.RESPONSE_OK)
			self.dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
			self.dialog.connect_object("delete_event", self.dialogdestroy, self.dialog)
			response = self.dialog.run()
			if response == gtk.RESPONSE_OK: # the response can't be much else
				self.dialog.destroy()					
		else:
			# Tells the user to check their options
			self.dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING)
			self.dialog.set_title("Are you sure you want to continue?")
			self.dialog.set_markup("Are you sure you want to plant this torrent file? Please check your options have been correctly chosen.")
			self.dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
			self.dialog.add_buttons(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK,gtk.RESPONSE_OK)
			self.dialog.connect_object("delete_event", self.dialogdestroy, self.dialog)
			response = self.dialog.run()
			if response == gtk.RESPONSE_OK:
				self.startplant()
			elif response == gtk.RESPONSE_CANCEL:
				self.dialog.destroy()
	def haltplant(self, data=None):
		# This important function is there to reactivate the 'greyed-out' buttons
		self.logbuffer.insert_with_tags_by_name(self.iter, "\rAll the buttons below have been re-enabled", "purple_foreground")
		self.window.get_widget("button1").set_sensitive(True)
		self.window.get_widget("button2").set_sensitive(True)
		self.window.get_widget("button3").set_sensitive(True)
		self.window.get_widget("expander1").set_sensitive(True)
		self.planting = 0
	def startplant(self, widget=None, data=None):
		# This greys out buttons so that the user cannot replant twice or do anything stupid
		self.dialog.destroy()
		self.window.get_widget("button1").set_sensitive(False)
		self.window.get_widget("button2").set_sensitive(False)
		self.window.get_widget("button3").set_sensitive(False)
		self.window.get_widget("expander1").set_sensitive(False)
		# Planting starts now
		self.planting = 1
		self.logbuffer.delete(self.logbuffer.get_start_iter(), self.logbuffer.get_end_iter())
		self.iter = self.logbuffer.get_iter_at_offset(0)
		self.logbuffer.insert_with_tags_by_name(self.iter, self.textdata, "blue_foreground")
		self.logbuffer.insert_with_tags_by_name(self.iter, "\rAll the buttons below have been disabled for the plant", "purple_foreground")
		# Invokes HTTP thread
		Httpplant(self.window.get_widget("entry1").get_text(), self.window.get_widget("spinbutton1").get_value_as_int()).start()
	def browsefile(self, widget, data=None):
		# The filedialog is not glade based anymore
		# Simple filedialog here that only accepts torrent files
		self.filedialog = gtk.FileChooserDialog("Browse For Torrent", action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
		if self.lastdirname != "":
			self.filedialog.set_current_folder(self.lastdirname)
		self.torrentfilter = gtk.FileFilter()
		self.torrentfilter.add_pattern("*.torrent")
		self.torrentfilter.set_name("Torrent Files")
		self.filedialog.add_filter(self.torrentfilter)
		self.filedialog.connect("delete_event", lambda self, widget: self.destroy())
		response = self.filedialog.run()
		if response == gtk.RESPONSE_OK:
			self.lastdirname = self.filedialog.get_current_folder()
			self.window.get_widget("entry1").set_text(self.filedialog.get_filename())
			self.filedialog.destroy()
		elif response == gtk.RESPONSE_CANCEL:
			self.filedialog.destroy()
	def destroy(self, widget, data=None):
		# This is so user cannot kill app while a torrent is planting
		# The app should time out anyway after a while
		if self.planting == 1:
			self.dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR)
			self.dialog.set_title("Error: You cannot quit while a torrent is being planted")
			self.dialog.set_markup("\rError: You cannot quit while a torrent is being planted")
			self.dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
			self.dialog.add_buttons(gtk.STOCK_CLOSE,gtk.RESPONSE_CANCEL)
			self.dialog.connect_object("delete_event", self.dialogdestroy, self.dialog)
			response = self.dialog.run()
			if response == gtk.RESPONSE_OK:
				gtk.main_quit()
			elif response == gtk.RESPONSE_CANCEL:
				self.dialog.destroy()
			return True
		else:
			self.dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION)
			self.dialog.set_title("Are you sure you want to quit?")
			self.dialog.set_markup("\rAre you sure you want to quit?")
			self.dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
			self.dialog.add_buttons(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_QUIT,gtk.RESPONSE_OK)
			self.dialog.connect_object("delete_event", self.dialogdestroy, self.dialog)
			response = self.dialog.run()
			if response == gtk.RESPONSE_OK:
				gtk.main_quit()
			elif response == gtk.RESPONSE_CANCEL:
				self.dialog.destroy()
			return True
	def dialogdestroy(self, dialogname, z=None):
		# kills all dialogs
		dialogname.destroy()
		
# not quite sure where this is meant to go
gtk.threads_init()
try:
	app = Plantergui()
	gtk.gdk.threads_enter()
	gtk.main()
	gtk.gdk.threads_leave()
except KeyboardInterrupt:
	sys.exit(1)

#!/usr/bin/env python
# this script plants torrents on the Anatomic P2P network
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
	print "try export PYTHONPATH="
	print "/usr/lib/python2.4/site-packages/"
	sys.exit(1)
import threading

class Httpplant(threading.Thread):
	def __init__ ( self, filename, trackers ):
		self.filename = filename
		self.trackers = trackers
		threading.Thread.__init__(self)
	def run(self):
		from bencode import bencode, bdecode
		from sha import sha
		import os
		try:
			f = open(self.filename, "r")
		except IOError, e:
			app.logbuffer.insert_with_tags_by_name(app.iter, "\rFATAL ERROR: Cannot open file:", e.filename , "red_foreground")
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
				app.logbuffer.insert_with_tags_by_name(app.iter, "\rERROR: Cannot open file:", e.filename, "red_foreground")
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
				app.logbuffer.insert_with_tags_by_name(app.iter, "\rError: Tracker cannot be accessed. Please Try Again"+e, "blue_foreground")
			else:
				message = bdecode(response)
				import types
				if type(message) == types.DictType and message.has_key("failure reason"):
					app.logbuffer.insert_with_tags_by_name(app.iter, "\rError:"+message["failure reason"], "red_foreground")
					app.haltplant()
					sys.exit(1)
				else:
					app.logbuffer.insert_with_tags_by_name(app.iter, "\rMessage from tracker:"+message, "red_foreground")
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
							stracker = stracker.replace("/cache", "/announce")
							bdata["announce"] = stracker		
							bdata["planted"] = 1
							bdata = bencode(bdata)
							try:
								f = open(self.filename, "w")
							except IOError, e:
								app.logbuffer.insert_with_tags_by_name(app.iter, "\rERROR: Cannot write to file:"+e.filename, "red_foreground")  
							else:
								file = f.write(bdata)
								f.close()
								app.logbuffer.insert_with_tags_by_name(app.iter, "\rTorrent Successfully Planted on Anatomic P2P", "green_foreground")  
						else: 
							app.logbuffer.insert_with_tags_by_name(app.iter, "\rError: Supernode Response is very unexpected:"+bdata2, "red_foreground")   
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
					app.logbuffer.insert_with_tags_by_name(app.iter, "\rError: Tracker cannot be accessed. Please Try Again"+e , "red_foreground")  	 
				else:
					message = bdecode(response)
					if type(message) == types.DictType and message.has_key("failure reason"):
						app.logbuffer.insert_with_tags_by_name(app.iter, "\rError:"+message["failure reason"] , "red_foreground")  	 
 					else:
						app.logbuffer.insert_with_tags_by_name(app.iter, "\rMessage from tracker:"+message , "purple_foreground")   
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
							app.logbuffer.insert_with_tags_by_name(app.iter, "\rMessage from Supertracker"+bdata3, "purple_foreground")   
						except ValueError:
							pass
			
			if bdata.has_key("announce-list"):
				del bdata["announce-list"]
			stracker = stracker.replace("/cache", "/announce")
			bdata["announce"] = stracker
			bdata["planted"] = 1
			bdata = bencode(bdata)
			try:
				f = open(self.filename, "w")
			except IOError, e:
				app.logbuffer.insert_with_tags_by_name(app.iter, "\rERROR: Cannot write to file:"+e.filename, "green_foreground")    
			else:
				file = f.write(bdata)
				f.close()
				app.logbuffer.insert_with_tags_by_name(app.iter, "\rTorrent Successfully MultiPlanted on Anatomic P2P (if there are no errors above)", "green_foreground")    
class Plantergui:
	def __init__(self):
		#TODO
		# finish rest of plant script
		gladefile = "planter.glade"
		windowname = "window1"
		self.lastdirname = ""
		self.planting = 0
		self.window = gtk.glade.XML(gladefile, windowname)
		self.window.get_widget("window1").connect("delete_event", self.destroy)
		self.window.get_widget("button2").connect("clicked", self.destroy)
		self.window.get_widget("button3").connect("clicked", self.check)
		self.window.get_widget("button1").connect("clicked", self.browsefile)
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
		if self.window.get_widget("entry1").get_text() == "":
			gladefile = "planter.glade"
			dialogname = "dialog4"
			self.dialog = gtk.glade.XML(gladefile, dialogname)
			self.dialog.get_widget("dialog4").connect_object("delete_event", self.dialogdestroy, dialogname)
			self.dialog.get_widget("button8").connect_object("clicked", self.dialogdestroy, dialogname)
		else:
			gladefile = "planter.glade"
			dialogname = "dialog3"
			self.dialog = gtk.glade.XML(gladefile, dialogname)
			self.dialog.get_widget("dialog3").connect_object("delete_event", self.dialogdestroy, dialogname)
			self.dialog.get_widget("button6").connect_object("clicked", self.dialogdestroy, dialogname)
			self.dialog.get_widget("button7").connect("clicked", self.startplant)
	def haltplant(self, data=None):
		self.logbuffer.insert_with_tags_by_name(self.iter, "\rAll the buttons below have been re-enabled", "purple_foreground")
		self.window.get_widget("button1").set_flags(gtk.SENSITIVE)
		self.window.get_widget("button2").set_flags(gtk.SENSITIVE)
		self.window.get_widget("button3").set_flags(gtk.SENSITIVE)
		self.window.get_widget("expander1").set_flags(gtk.SENSITIVE)
		self.planting = 0
	def startplant(self, widget, data=None):
		self.dialog.get_widget("dialog3").destroy()
		self.window.get_widget("button1").unset_flags(gtk.SENSITIVE)
		self.window.get_widget("button2").unset_flags(gtk.SENSITIVE)
		self.window.get_widget("button3").unset_flags(gtk.SENSITIVE)
		self.window.get_widget("expander1").unset_flags(gtk.SENSITIVE)
		self.planting = 1
		self.logbuffer.delete(self.logbuffer.get_start_iter(), self.logbuffer.get_end_iter())
		self.iter = self.logbuffer.get_iter_at_offset(0)
		self.logbuffer.insert_with_tags_by_name(self.iter, self.textdata, "blue_foreground")
		self.logbuffer.insert_with_tags_by_name(self.iter, "\rAll the buttons below have been disabled for the plant", "purple_foreground")
		Httpplant(self.window.get_widget("entry1").get_text(), self.window.get_widget("spinbutton1").get_value_as_int()).start()
	def browsefile(self, widget, data=None):
		gladefile = "planter.glade"
		dialogname = "filechooserdialog1"
		self.dialog = gtk.glade.XML(gladefile, dialogname)
		if self.lastdirname != "":
			self.dialog.get_widget("filechooserdialog1").set_current_folder(self.lastdirname)
		self.torrentfilter = gtk.FileFilter()
		self.torrentfilter.add_pattern("*.torrent")
		self.torrentfilter.set_name("Torrent Files")
		self.dialog.get_widget("filechooserdialog1").add_filter(self.torrentfilter)
		self.dialog.get_widget("button4").connect_object("clicked", self.dialogdestroy, dialogname)
		self.dialog.get_widget("button5").connect("clicked", self.takefile)
		self.dialog.get_widget("filechooserdialog1").connect_object("delete_event", self.dialogdestroy, dialogname)
	def takefile(self, widget, data=None):
		filename = self.dialog.get_widget("filechooserdialog1").get_filename()
		dirname = self.dialog.get_widget("filechooserdialog1").get_current_folder()
		self.dialog.get_widget("filechooserdialog1").destroy()
		self.lastdirname = dirname
		self.window.get_widget("entry1").set_text(filename)
	def destroy(self, widget, data=None):
		if self.planting == 1:
			gladefile = "planter.glade"
			dialogname = "dialog2"
			self.dialog = gtk.glade.XML(gladefile, dialogname)
			self.dialog.get_widget("okbutton1").connect_object("clicked", self.dialogdestroy, dialogname)
			return True
		else:
			gladefile = "planter.glade"
			dialogname = "dialog1"
			self.dialog = gtk.glade.XML(gladefile, dialogname)
			self.dialog.get_widget("quitbutton").connect("clicked", self.byebye)
			self.dialog.get_widget("cancelbutton1").connect_object("clicked", self.dialogdestroy, dialogname)
		  	self.dialog.get_widget("dialog1").connect_object("delete_event", self.dialogdestroy, dialogname)
			return True
	def dialogdestroy(self, dialogname, z=None):
		self.dialog.get_widget(dialogname).destroy()
	def byebye(self, widget, data=None):
		gtk.main_quit()
gtk.threads_init()
try:
	app = Plantergui()
	gtk.gdk.threads_enter()
	gtk.main()
	gtk.gdk.threads_leave()
except KeyboardInterrupt:
	sys.exit(1)
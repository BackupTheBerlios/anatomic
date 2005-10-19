#!/usr/bin/env python
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
	import gobject
except:
	print "You need to install pygtk or GTK+2"
	print "or set your PYTHONPATH correctly"
	print "Type 'export PYTHONPATH=/usr/lib/python2.4/site-packages/'"
	sys.exit(1)
import threading
from BitTornado.bencode import bencode, bdecode

class Httpplant(threading.Thread):
	def __init__ ( self, bdata, trackers, filename ):
		self.filename = filename
		self.trackers = trackers
		self.bdata = bdata
		threading.Thread.__init__(self)
	def run(self):
		from sha import sha
		import os
		import time
		do_gui_operation(app.wTree.get_widget("label17").set_label , "<big><b>Planting Torrent " + os.path.basename(self.filename) +"</b></big>")
		infohash = sha(bencode(self.bdata['info'])).digest()
		url = ["http://anatomic.berlios.de/network/node-b/cache.php", "http://anatomic.berlios.de/network/node-a/cache.php"]
		if os.path.isfile('strackers.dat') is True and (time.time() - os.path.getmtime('strackers.dat')) < 2592000: # check if file exists and is recent(ish)
			try:
				f = open('strackers.dat', "r")
			except IOError, e:
				do_gui_operation(app.status.set_label, '<span color="red">Warning: Cannot open strackers.dat</span>')
			file = f.read()
			f.close()
			try:
				b2data = bdecode(file)
				url = b2data
			except ValueError, e:
				do_gui_operation(app.status.set_label, '<span color="red">Warning: strackers.dat cannot be decoded</span>')
		else:
			do_gui_operation(app.status.set_label, '<span color="red">Warning: Using default supertracker list</span>')
		from urllib import urlencode
		from random import shuffle
		shuffle(url)
		do_gui_operation(app.icon.set_property, "stock", gtk.STOCK_CONNECT)
		do_gui_operation(app.tooltips.set_tip, app.eventbox, "Connected to internet") # it will be in a few seconds
		# Single Plant
		if self.trackers == 1:
			do_gui_operation(app.status.set_label, "Attempting single tracker plant")
			urldict = {"plant" : 1, "client" : 1}
			urldict = urlencode(urldict)
			urlend = "?"
			urlend += urldict
			status = 0 # for now
			do_gui_operation(app.wTree.get_widget("image2").set_property, "stock", gtk.STOCK_MEDIA_PLAY)
			do_gui_operation(app.wTree.get_widget("label13").set_label, "<big>Communicating with supertrackers</big>")
			for x in url:
				stracker = x
				x += urlend
				try:
					import urllib2
					f = urllib2.Request(x)
					f.add_header('User-agent', 'Anatomic P2P Planter Wizard GUI CVS Edition (S)  +http://anatomic.berlios.de/' )
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
				do_gui_operation(app.fatal, "<big><b>Error: No supertrackers were reached</b></big>\r\rThis is likely to be caused by a problem with your internet connection. If you are sure your internet connection is alive please run anaupdatesnodes to discover more supertrackers.\r\rPressing forward will close this wizard.")
				sys.exit(2)
			# or else
			# bdata3 is a single tracker left behind. tracker is going to have the querystring concatenated on it
			do_gui_operation(app.wTree.get_widget("image2").set_property, "stock", gtk.STOCK_APPLY)
			do_gui_operation(app.progress.set_fraction, 0.3)
			do_gui_operation(app.progress.set_text, "30 percent completed")
			do_gui_operation(app.wTree.get_widget("label13").set_label, "Communicating with supertrackers")
			tracker = bdata3
			tracker = tracker.replace("/announce", "/plant")
			tracker += "?"
			tracker += urlencode({"client" : 1, "plant" : infohash})
			do_gui_operation(app.wTree.get_widget("image3").set_property, "stock", gtk.STOCK_MEDIA_PLAY)
			do_gui_operation(app.wTree.get_widget("label14").set_label, "<big>Planting torrent on trackers</big>")
			try:
				t = urllib2.Request(tracker)
				t.add_header('User-agent', 'Anatomic P2P Planter Wizard GUI CVS Edition (S)  +http://anatomic.berlios.de/' )
				opener = urllib2.build_opener()
				response = opener.open(t).read()
			except IOError, e:
				do_gui_operation(app.fatal, "<big><b>Tracker could not be accessed.</b></big>\rThis is due to a technical fault with the tracker.\r\rPlease press back to return to the previous page and start the plant again.")
				sys.exit(1)
			else:
				try:
					message = bdecode(response)
				except ValueError ,e:
					do_gui_operation(app.fatal, "<big><b>Tracker data cannot be decoded.</b></big>\rThis is due to a technical fault with the tracker.\r\rPlease press back to return to the previous page and start the plant again.")
					sys.exit(1)
				import types
				if type(message) == types.DictType and message.has_key("failure reason"):
					do_gui_operation(app.fatal, "<big><b>Tracker has returned an error message.</b></big>\r\rThe error message is: " + message["failure reason"] + "\rThis is due to a technical fault with the tracker.\rPlease press back to return to the previous page and start the plant again.")
					sys.exit(1)
				else:
					do_gui_operation(app.wTree.get_widget("image3").set_property, "stock", gtk.STOCK_APPLY)
					do_gui_operation(app.wTree.get_widget("label14").set_label, "Planting torrent on trackers")
					do_gui_operation(app.progress.set_fraction, 0.6)
					do_gui_operation(app.progress.set_text, "60 percent completed")
					import random
					strackerlist = [random.choice(url), stracker] # this list contains a stracker and a backup stracker
					qstring = urlencode({"client" : 1, "tpush" : bdata3})
					do_gui_operation(app.wTree.get_widget("image4").set_property, "stock", gtk.STOCK_MEDIA_PLAY)
					do_gui_operation(app.wTree.get_widget("label15").set_label, "<big>Notifying supertrackers</big>")
					for z in strackerlist:
						z += "?"
						z += qstring
						try:
							f3 = urllib2.Request(z)
							f3.add_header('User-agent', 'Anatomic P2P Planter Wizard GUI CVS Edition (S)  +http://anatomic.berlios.de/' )
							opener = urllib2.build_opener()
							data = opener.open(f3).read()
						except IOError:
							pass
					try:
						bdata2 = bdecode(data)
						do_gui_operation(app.wTree.get_widget("image4").set_property, "stock", gtk.STOCK_APPLY)
						do_gui_operation(app.wTree.get_widget("label15").set_label, "Notifying supertrackers")
						do_gui_operation(app.wTree.get_widget("image5").set_property, "stock", gtk.STOCK_MEDIA_PLAY)
						do_gui_operation(app.wTree.get_widget("label16").set_label, "<big>Modifying torrent file</big>")
						do_gui_operation(app.progress.set_fraction, 0.9)
						do_gui_operation(app.progress.set_text, "90 percent completed")
						if bdata2 == "TRUE":
							if self.bdata.has_key("announce-list"):
								del self.bdata["announce-list"]
							#hackwards compatibility
							announcelist = []
							for url in strackerlist:
								url = url.replace("/cache", "/announce")
								announcelist.append(url)
							self.bdata["announcelist"] = [announcelist]
							stracker = stracker.replace("/cache", "/announce")
							self.bdata["announce"] = stracker
							self.bdata["planted"] = 1
							bdata = bencode(self.bdata)
							try:
								f = open(self.filename, "wb")
							except IOError, e:
								do_gui_operation(app.fatal, "<big><b>" + e.filename +  " could not be accessed.</b></big>\r\rPlease make sure you have write access to the torrent file.\rPlease press back to return to the previous page and start the plant again.")
								sys.exit(1)
							else:
								file = f.write(bdata)
								f.close()
								do_gui_operation(app.wTree.get_widget("image5").set_property, "stock", gtk.STOCK_APPLY)
								do_gui_operation(app.wTree.get_widget("label16").set_label, "Modifying torrent file")
								do_gui_operation(app.progress.set_fraction, 1.0)
								do_gui_operation(app.progress.set_text, "100 percent completed!")
								do_gui_operation(app.status.set_label, "Planting completed (click forward to continue)")
								do_gui_operation(app.success, "<big><b>Torrent successfully planted on 1 tracker.</b></big>\r\rThe torrent file specified has now been modified to work on the Anatomic P2P Network.\rThis file can be used by the Anatomic P2P GUI Client or a normal BitTorrent Client.\r\rClick on Finish to exit the wizard.\r\rThank you for using this wizard.")
						else:
							do_gui_operation(app.fatal, "<big><b>The supertracker reported an error.</b></big>\r\rThe error was: " + bdata2 + "\rThis is due to a technical fault with the supertracker.\rPlease press back to return to the previous page and start the plant again.")
							sys.exit(1)
					except ValueError:
							do_gui_operation(app.fatal, "<big><b>The supertracker response cannot be decoded.</b></big>\r\rThis is due to a technical fault with the supertracker.\rPlease press back to return to the previous page and start the plant again.")
							sys.exit(1)
					sys.exit()
		else: # multiple tracker plant
			needed = self.trackers
			do_gui_operation(app.status.set_label,"Attempting multiple tracker plant")
			qstring = "?" #querystring
			qstring += urlencode({"multiseed" : needed, "client" : 1})
			status = 0
			do_gui_operation(app.wTree.get_widget("image2").set_property, "stock", gtk.STOCK_MEDIA_PLAY)
			do_gui_operation(app.wTree.get_widget("label13").set_label, "<big>Communicating with supertrackers</big>")
			import types
			# to make sure data is in a list from tracker
			for x in url:
				stracker = x
				x += qstring
				try:
					import urllib2
					f = urllib2.Request(x)
					f.add_header('User-agent', 'Anatomic P2P Planter Wizard (MS) GUI CVS Edition +http://anatomic.berlios.de/' )
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
				do_gui_operation(app.fatal, "<big><b>Error: No supertrackers were reached</b></big>\r\rThis is likely to be caused by a problem with your internet connection. If you are sure your internet connection is alive please run anaupdatesnodes to discover more supertrackers.\r\rPressing forward will close this wizard.")
				sys.exit(2)
			do_gui_operation(app.wTree.get_widget("image2").set_property, "stock", gtk.STOCK_APPLY)
			do_gui_operation(app.progress.set_fraction, 0.3)
			do_gui_operation(app.progress.set_text, "30 percent completed")
			do_gui_operation(app.wTree.get_widget("label13").set_label, "Communicating with supertrackers")
			import copy
			trackers2 = copy.deepcopy(trackers)
			z = trackers2[0]
			del(trackers2[0])
			trackers2.append(z)
			do_gui_operation(app.wTree.get_widget("image3").set_property, "stock", gtk.STOCK_MEDIA_PLAY)
			do_gui_operation(app.wTree.get_widget("label14").set_label, "<big>Planting torrent on trackers</big>")
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
					do_gui_operation(app.fatal, "<big><b>Tracker could not be accessed.</b></big>\r\rThis is due to a technical fault with the tracker.\r\rPlease press back to return to the previous page and start the plant again.")
					sys.exit(1)
				else:
					message = bdecode(response)
					if type(message) == types.DictType and message.has_key("failure reason"):
						do_gui_operation(app.fatal, "<big><b>Tracker has returned an error message.</b></big>\r\rThe error message is: " + message["failure reason"] + "\rThis is due to a technical fault with the tracker.\rPlease press back to return to the previous page and start the plant again.")
						sys.exit(1)
					else:
						do_gui_operation(app.wTree.get_widget("image3").set_property, "stock", gtk.STOCK_APPLY)
						do_gui_operation(app.wTree.get_widget("label14").set_label, "Planting torrent on trackers")
						do_gui_operation(app.progress.set_fraction, 0.6)
						do_gui_operation(app.progress.set_text, "60 percent completed")
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
						except ValueError:
							pass
			do_gui_operation(app.wTree.get_widget("image4").set_property, "stock", gtk.STOCK_APPLY)
			do_gui_operation(app.wTree.get_widget("label15").set_label, "Notifying supertrackers")
			do_gui_operation(app.wTree.get_widget("image5").set_property, "stock", gtk.STOCK_MEDIA_PLAY)
			do_gui_operation(app.wTree.get_widget("label16").set_label, "<big>Modifying torrent file</big>")
			do_gui_operation(app.progress.set_fraction, 0.9)
			do_gui_operation(app.progress.set_text, "90 percent completed")
			#hackwards compatibility
			announcelist = []
			for url in strackerlist:
				url = url.replace("/cache", "/announce")
				announcelist.append(url)
			self.bdata["announce-list"] = [announcelist]
			stracker = stracker.replace("/cache", "/announce")
			self.bdata["announce"] = stracker
			self.bdata["planted"] = 1
			bdata = bencode(self.bdata)
			try:
				f = open(self.filename, "wb")
			except IOError, e:
				do_gui_operation(app.fatal, "<big><b>" + e.filename +  " could not be accessed.</b></big>\r\rPlease make sure you have write access to the torrent file.\rPlease press back to return to the previous page and start the plant again.")
				sys.exit(1)
			else:
				file = f.write(bdata)
				f.close()
				do_gui_operation(app.wTree.get_widget("image5").set_property, "stock", gtk.STOCK_APPLY)
				do_gui_operation(app.wTree.get_widget("label16").set_label, "Modifying torrent file")
				do_gui_operation(app.progress.set_fraction, 1.0)
				do_gui_operation(app.progress.set_text, "100 percent completed!")
				do_gui_operation(app.status.set_label, "Planting completed (click forward to continue)")
				do_gui_operation(app.success, "<big><b>Torrent successfully planted on " + str(self.trackers) + " trackers.</b></big>\r\rThe torrent file specified has now been modified to work on the Anatomic P2P Network.\rThis file can be used by the Anatomic P2P GUI Client or a normal BitTorrent Client.\r\rClick on Finish to exit the wizard.\rThank you for using this wizard.")

class Planterwizard:
	def __init__(self):
		self.planting = 0 # a flag for whether a torrent is being planted
		gladefile = "wizard.glade" # glade file name
		self.filename = None # no filename as yet
		windowname = "window" # name of main window
		self.selected = None
		self.wTree = gtk.glade.XML(gladefile, windowname) # opens glade file
		self.notebook = self.wTree.get_widget("notebook1") # sets variable notebook
		self.step = self.wTree.get_widget("label_step") # Step x of 4
		self.forward = self.wTree.get_widget("button_next") # sets variable forward button
		self.back = self.wTree.get_widget("button_prev") # sets variable back button
		self.choosebutton =  self.wTree.get_widget("filechooserbutton1")
		self.torrentfilter = gtk.FileFilter()
		self.torrentfilter.add_pattern("*.torrent")
		self.torrentfilter.set_name("Torrent Files")
		self.choosebutton.add_filter(self.torrentfilter)
		self.choosebutton.connect("selection-changed", self.select) # to make sure only torrent files are selected
		self.folder = self.choosebutton.get_current_folder()
		self.closeid = self.wTree.get_widget("window").connect("delete_event", self.destroy) # close window with dialog
		self.forwardid = self.forward.connect("clicked", self.change)
		self.back.connect("clicked", self.change)
		self.status = self.wTree.get_widget("label20")
		self.progress = self.wTree.get_widget("progressbar1")
		self.icon = self.wTree.get_widget("image1")
		self.tooltips = gtk.Tooltips()
		self.final = self.wTree.get_widget("label19")
		self.plantedcheck = 0 # this is done to vo
		self.eventbox = self.wTree.get_widget("eventbox1") # for tooltip
		self.tooltips.set_tip(self.eventbox, "Not connected to internet")
		self.successful = 0
	def fatal(self, data=None):
		self.planting = 0
		self.final.set_label(data)
		self.icon.set_property("stock", gtk.STOCK_DISCONNECT)
		self.tooltips.set_tip(self.eventbox, "Not connected to internet")
		self.status.set_label("") # set it back to normal
		self.wTree.get_widget("label17").set_label("<big><b>Ready to Plant Torrent - Click forward to start.</b></big>")
		for img in range(2,6): # reset
			self.wTree.get_widget("image" + str(img)).set_property("stock", gtk.STOCK_REMOVE)
		self.wTree.get_widget("label13").set_label("Communicating with supertrackers")
		self.wTree.get_widget("label14").set_label("Planting torrent on trackers")
		self.wTree.get_widget("label15").set_label("Notifying supertrackers")
		self.wTree.get_widget("label16").set_label("Modifying torrent file")
		self.progress.set_fraction(0.0)
		self.progress.set_text("Progress Bar")
		self.change(self.forward)
		self.forward.set_sensitive(1)
	def success(self, data=None):
		self.planting = 0
		self.successful = 1
		self.icon.set_property("stock", gtk.STOCK_DISCONNECT)
		self.tooltips.set_tip(self.eventbox, "Not connected to internet")
		self.final.set_label(data)
		self.forward.set_sensitive(1)
		self.forward.disconnect(self.forwardid)
		self.forwardid = self.forward.connect("clicked", self.change)
	def startplant(self, widget, data=None):
		fatalerror = None # throws an error up if it is not present
		try:
			f = open(self.filename, "rb")
			file = f.read()
			f.close()
			data = bdecode(file)
		except (IOError, ValueError), e:
			if type(e) == IOError:
				fatalerror = '<span weight="bold" size="larger">' + self.filename + ' cannot be opened.</span>\r\rThe error returned was: ' + str(e) +'.'
			else:
				fatalerror = '<span weight="bold" size="larger">' + self.filename + ' cannot be decoded.</span>\r\rThe error returned was: ' + str(e) +'.'
			self.dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR)
			self.dialog.set_markup(fatalerror)
			self.dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
			self.dialog.add_buttons(gtk.STOCK_OK,gtk.RESPONSE_OK)
			self.dialog.connect_object("delete_event", self.dialogdestroy, self.dialog)
			response = self.dialog.run()
			if response == gtk.RESPONSE_OK: # the response can't be much else
				self.dialog.destroy()
			self.status.set_label('<span color="red">Fatal Error: Select a new torrent or try again.</span>')
		else:
			if data.has_key("planted") and self.plantedcheck == 0:
				self.dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING)
				self.dialog.set_markup('<span weight="bold" size="larger">Do you wish to replant this torrent?</span>\r\r'  + self.filename + ' has already been planted on the Anatomic P2P Network and may still be active.')
				self.dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
				self.dialog.add_buttons(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK,gtk.RESPONSE_OK)
				self.dialog.connect_object("delete_event", self.dialogdestroy, self.dialog)
				response = self.dialog.run()
				if response == gtk.RESPONSE_OK:
					self.startthreads(data, self.dialog)
					self.plantedcheck = 1
				elif response == gtk.RESPONSE_CANCEL:
					self.dialog.destroy()
			else:
				self.startthreads(data)
	def startthreads(self, data, dialog=None ):
		if dialog != None:
			dialog.destroy()
		self.back.set_sensitive(0)
		self.forward.set_sensitive(0)
		self.status.set_label('Buttons Disabled')
		self.planting = 1
		Httpplant(data, self.wTree.get_widget("spinbutton1").get_value_as_int(), self.filename).start()
	def select(self, widget, data=None):
		self.plantedcheck = 0
		self.forward.set_sensitive(1)
		self.filename = None
		self.forward.disconnect(self.forwardid)
		self.forwardid = self.forward.connect("clicked", self.check)
	def check(self, widget, data=None): # this makes sure the data is a torrent
		filename = self.choosebutton.get_filename()
		if type(filename) == type("filename") and filename.endswith("torrent"):
			self.filename = filename
			self.change(self.forward)
		else:
			self.filename = None
			self.dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR)
			self.dialog.set_markup('<span weight="bold" size="larger">' + filename + ' is not a valid torrent file.</span>\r\rPlease select a valid torrent file.')
			self.dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
			self.dialog.add_buttons(gtk.STOCK_OK,gtk.RESPONSE_OK)
			self.dialog.connect_object("delete_event", self.dialogdestroy, self.dialog)
			response = self.dialog.run()
			if response == gtk.RESPONSE_OK: # the response can't be much else
				self.dialog.destroy()
			self.forward.set_sensitive(0)
	def change(self, widget, data=None):
		if widget.get_name() =="button_next":
			self.notebook.next_page()
		else:
			self.notebook.prev_page()
		self.pagenumber = self.notebook.get_current_page() + 1
		self.step.set_markup("<big><b>Step " + str(self.pagenumber)+ " of 4</b></big>")
		if self.pagenumber == 1 or self.successful == 1:
			self.back.set_sensitive(0)
		else:
			self.back.set_sensitive(1)
		if self.pagenumber == 3:
			self.forward.disconnect(self.forwardid)
			self.forwardid = self.forward.connect("clicked", self.startplant)
			self.wTree.get_widget("window").disconnect(self.closeid)
			self.closeid = self.wTree.get_widget("window").connect("delete_event", self.destroy)
		elif self.pagenumber == 4:
			self.wTree.get_widget("window").disconnect(self.closeid)
			self.closeid = self.wTree.get_widget("window").connect("delete_event", gtk.main_quit)
			if self.successful:
						self.forward.set_property("label", "Finish")
			self.forward.disconnect(self.forwardid)
			self.forwardid = self.forward.connect("clicked", gtk.main_quit)
		elif self.filename or self.pagenumber == 1: # leaves forward on as an override
			self.forward.disconnect(self.forwardid)
			self.forwardid = self.forward.connect("clicked", self.change)
			self.forward.set_sensitive(1)
		elif self.pagenumber == 2:
			self.forward.disconnect(self.forwardid)
			self.forwardid = self.forward.connect("clicked", self.check)
			if self.choosebutton.get_filename() == "":
				self.forward.set_sensitive(0)
	def destroy(self, widget, data=None):
		# This is so user cannot kill app while a torrent is planting
		# The app should time out anyway after a while
		if self.planting == 1:
			self.dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR)
			self.dialog.set_markup('<span weight="bold" size="larger">Error: You cannot quit while a torrent is being planted.</span>\r\rThis is to ensure that problems with the network do not occur.')
			self.dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
			self.dialog.add_buttons(gtk.STOCK_OK,gtk.RESPONSE_OK)
			self.dialog.connect_object("delete_event", self.dialogdestroy, self.dialog)
			response = self.dialog.run()
			if response == gtk.RESPONSE_OK: # the response can't be much else
				self.dialog.destroy()
			return True
		else:
			self.dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION)
			self.dialog.set_markup('<span weight="bold" size="larger">Are you sure you want to quit?</span>\r\rThe wizard has not completed.')
			self.dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
			self.dialog.add_buttons(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_QUIT,gtk.RESPONSE_OK)
			self.dialog.connect_object("delete_event", self.dialogdestroy, self.dialog)
			response = self.dialog.run()
			if response == gtk.RESPONSE_OK:
				gtk.main_quit()
			elif response == gtk.RESPONSE_CANCEL:
				self.dialog.destroy()
			return True
	def dialogdestroy(self, dialogname, data=None):
		# kills all dialogs
		dialogname.destroy()
def do_gui_operation(function, *args, **kw):
    def idle_func():
        gtk.threads_enter()
        try:
            function(*args, **kw)
            return False
        finally:
            gtk.threads_leave()
    gobject.idle_add(idle_func)

gtk.threads_init()
gtk.threads_enter()
app = Planterwizard()
gtk.main()
gtk.threads_leave()

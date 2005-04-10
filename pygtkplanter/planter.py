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
	
class planter:
	def __init__(self):
		gladefile = "planter.glade"
		windowname = "window1"
		self.planting = 0
		self.window = gtk.glade.XML(gladefile, windowname)
		self.window.get_widget("window1").connect("delete_event", self.destroy)
		self.window.get_widget("button2").connect("clicked", self.destroy)
		self.window.get_widget("button1").connect("clicked", self.browsefile)
		self.log = self.window.get_widget("textview1")
		self.logbuffer = gtk.TextBuffer(None)
		self.log.set_buffer(self.logbuffer)
		self.logbuffer.create_tag("blue_foreground", foreground="blue")
		import time
		time = time.ctime()
		self.iter = self.logbuffer.get_iter_at_offset(0)
		self.logbuffer.insert_with_tags_by_name(self.iter, time+" Anatomic P2P Planter CVS Edition", "blue_foreground")
	def browsefile(self, widget, data=None):
		self.lastdialog = "filechooserdialog1"
		gladefile = "planter.glade"
		dialogname = "filechooserdialog1"
		self.dialog = gtk.glade.XML(gladefile, dialogname)
		self.dialog.get_widget("button4").connect_object("clicked", self.dialogdestroy, dialogname)
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
	def dialogdestroy(self, dialogname):
		self.dialog.get_widget(dialogname).destroy()
	def byebye(self, widget, data=None):
		gtk.main_quit()
app = planter()
gtk.main()
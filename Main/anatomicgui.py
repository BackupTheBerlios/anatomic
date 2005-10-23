#!/usr/bin/env python
# thanks to the teachers at the ministy of boredom whose boring lessons gave me time to dream up this crazy idea  ;-)
# GTK is far better than Qt
# Modified for GTK by Kunkie
# Written by Bram Cohen
# see LICENSE.txt for license information

from BitTornado.download_bt1 import BT1Download, defaults, parse_params, get_usage, get_response
from BitTornado.RawServer import RawServer, UPnP_ERROR
from random import seed
from socket import error as socketerror
from BitTornado.bencode import bencode, bdecode
from BitTornado.natpunch import UPnP_test
from threading import Event, Thread
from os.path import abspath, isdir, isfile
from os import sep
from sys import argv, stdout
import sys
from sha import sha
from time import strftime, ctime
from BitTornado.clock import clock
from BitTornado import createPeerID, version
from BitTornado.ConfigDir import ConfigDir
from webbrowser import open_new

assert sys.version >= '2', "Install Python 2.0 or greater"
# I really don't know why this was in BitTornado
try:
    True
except:
    True = 1
    False = 0
    
# this function converts integer n into a time left string
def hours(n):
    if n == 0:
        return 'complete!'
    try:
        n = int(n)
        assert n >= 0 and n < 5184000  # 60 days
    except:
        return '<unknown>'
    m, s = divmod(n, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return '%d hour %02d min %02d sec' % (h, m, s)
    else:
        return '%d min %02d sec' % (m, s)
	
# hmmm I wonder if it better to have ONE displayer to deal with the system
# Version 0.2 perhaps make a single HeadlessDisplayer
class HeadlessDisplayer:
    def __init__(self):
        self.done = False
        self.file = ''
        self.percentDone = ''
        self.timeEst = ''
        self.downloadTo = ''
        self.downRate = ''
        self.upRate = ''
        self.shareRating = ''
        self.seedStatus = ''
        self.peerStatus = ''
        self.errors = []
        self.totalUp = ''
        self.totalDown = ''
        self.last_update_time = -1
        self.fractionDone = ''
        self.status = None
        self.tab = None
        self.tab_label = None
        self.labeldone = None

    def finished(self):
        self.done = True
        self.percentDone = '100'
        self.timeEst = 'Download Succeeded!'
        self.downRate = ''
        self.display()

    def failed(self):
        self.done = True
        self.percentDone = '0'
        self.timeEst = 'Download Failed!'
        self.downRate = ''
        self.display()
        sys.exit(2)

    def error(self, errormsg):
        self.errors.append(errormsg)
        do_gui_operation(app.errors, self.tab, self.errors)

    def setdatalength(self, datalength = None):
        self.datalength = datalength	
  
    def settabs(self, tab = None, tab_label = None):
        self.tab = tab
        self.tab_label = tab_label     

    def display(self, dpflag = Event(), fractionDone = None, timeEst = None,
            downRate = None, upRate = None, activity = None,
            statistics = None, **kws):
        if self.last_update_time + 0.1 > clock() and fractionDone not in (0.0, 1.0) and activity is not None:
            return
        self.last_update_time = clock()
        if fractionDone is not None:
            self.percentDone = str(float(int(fractionDone * 1000)) / 10)
            self.progress = float(fractionDone)
        if timeEst is not None:
            self.timeEst = hours(timeEst)
        if activity is not None and not self.done:
            self.timeEst = activity
        if downRate is not None:
            self.downRate = '%.1f kB/s' % (float(downRate) / (1 << 10))
        else:
            self.downRate = '0.0 kB/s'
        if upRate is not None:
            self.upRate = '%.1f kB/s' % (float(upRate) / (1 << 10))
        else:
            self.upRate = '0.0 kB/s'
        if statistics is not None:
           if (statistics.shareRating < 0) or (statistics.shareRating > 100):
               # utf-8 infinity is a bit small but better than oo (two 'o's)
               self.shareRating = u'\u221E' + ' infinite (%.1f MB up / %.1f MB down)' % (float(statistics.upTotal) / (1<<20), float(statistics.downTotal) / (1<<20))
           else:
               self.shareRating = '%.3f  (%.1f MB up / %.1f MB down)' % (statistics.shareRating, float(statistics.upTotal) / (1<<20), float(statistics.downTotal) / (1<<20))
           if not self.done:
              self.seedStatus = '%d seen now, plus %.3f distributed copies' % (statistics.numSeeds,0.001*int(1000*statistics.numCopies))
           else:
              self.seedStatus = '%d seen recently, plus %.3f distributed copies' % (statistics.numOldSeeds,0.001*int(1000*statistics.numCopies))
           self.peerStatus = '%d seen now, %.1f%% done at %.1f kB/s' % (statistics.numPeers,statistics.percentDone,float(statistics.torrentRate) / (1 << 10))
           if statistics.numPeers + statistics.numSeeds + statistics.numOldSeeds == 0:
              if statistics.last_failed:
                  self.status = "No connections have been made with any trackers."
              else:
                  self.status = "No connections have been made with other users."
           elif not statistics.external_connection_made:
              self.status = "No incoming connections have been made implying a possible firewall issue."
           elif (statistics.numSeeds + statistics.numOldSeeds == 0) and ( (self.done and statistics.numCopies < 1) or (not self.done and statistics.numCopies2 < 1) ):
              self.status = "No complete copies of file seen."
           else:
            self.status = "All is OK."
        else:
           self.seedStatus = "n/a"
           self.peerStatus = "n/a"
           self.shareRating = "n/a"
        # thank you Bill and the Boyz for creating the big inefficient mess below
        # this is a mess but it is needed to achieve cross-compatibility with win32 and X11
        # credits go to the pygtk faq
        # stupid M$
        try:
                if app and self.tab is not None:
                        # not really worth updating the label with the same data again and again
                        if self.labeldone is None:
                                do_gui_operation(self.tab_label.get_widget("label144").set_label, self.file)
                                do_gui_operation(self.tab.get_widget("label100").set_label,'<span weight="bold" size="larger">Torrent Statistics - ' + self.file + '</span>')
                                self.labeldone = 1
                        if self.done:
                                if statistics is not None and float(statistics.downTotal) <  float(statistics.upTotal) :
                                           # the user has downloaded more than uploaded
                                           do_gui_operation(self.tab.get_widget("progressbar1").set_fraction, 1.0)
                                           do_gui_operation(self.tab.get_widget("progressbar1").set_text, "100 percent completed. You are a POWER SEEDER.")
                                elif statistics is not None and float(statistics.downTotal) >=  float(statistics.upTotal):
                                          if float(statistics.downTotal) == 0.0: # upload:download ratio is infinite - will cause divide by zero exception
                                                    do_gui_operation(self.tab.get_widget("progressbar1").set_fraction, 1.0)
                                          else:
                                                    do_gui_operation(self.tab.get_widget("progressbar1").set_fraction, float(statistics.upTotal)  /  float(statistics.downTotal))
                                          do_gui_operation(self.tab.get_widget("progressbar1").set_text, '100 percent completed. Please continue seeding.')
                        elif fractionDone is not None: # probably should be 'else'
                                 if statistics is not None:
                                         do_gui_operation(self.tab.get_widget("progressbar1").set_fraction, self.progress)
                                         do_gui_operation(self.tab.get_widget("progressbar1").set_text, 'Downloading - '+ str(round(float(self.progress * self.datalength) / (1 << 20),2)) + ' of ' + str(round(float(self.datalength) / (1 << 20), 2)) + ' MB downloaded'   )
                        do_gui_operation(self.tab.get_widget("label101").set_label, self.timeEst)
                        do_gui_operation(self.tab.get_widget("label102").set_label, self.downloadTo)
                        do_gui_operation(self.tab.get_widget("label103").set_label, self.downRate)
                        do_gui_operation(self.tab.get_widget("label104").set_label, self.upRate)
                        do_gui_operation(self.tab.get_widget("label105").set_label, self.seedStatus)
                        do_gui_operation(self.tab.get_widget("label106").set_label, self.peerStatus)
                        do_gui_operation(self.tab.get_widget("label107").set_label, self.shareRating)
                        if self.status is not None:
                                do_gui_operation(self.tab.get_widget("label108").set_label, self.status)
                        dpflag.set()
        except:
                pass 
        # really stupid...
        # sometimes the user commands can take place while the stats are going
        # this stops errors

    def chooseFile(self, default, size, saveas, dir):
        self.file = '%s (%.1f MB)' % (default, float(size) / (1 << 20))
        if saveas != '':
            default = saveas
        self.downloadTo = abspath(default)
        return default

    def newpath(self, path):
        self.downloadTo = path
# this is the main thread in the client for downloading stuff
def run(tab=None, tab_label = None, app=None, config=None, configdir=None):
    cols = 80
    h = HeadlessDisplayer()
    while 1:
        myid = createPeerID()
        seed(myid)
        doneflag = Event()
        app.doneflag = doneflag
        def disp_exception(text):
            print text
        rawserver = RawServer(doneflag, config['timeout_check_interval'],
                              config['timeout'], ipv6_enable = config['ipv6_enabled'],
                              failfunc = h.failed, errorfunc = disp_exception)
        upnp_type = UPnP_test(config['upnp_nat_access'])
        while True:
            try:
                listen_port = rawserver.find_and_bind(config['minport'], config['maxport'],
                                config['bind'], ipv6_socket_style = config['ipv6_binds_v4'],
                                upnp = upnp_type, randomizer = config['random_port'])
                break
            except socketerror, e:
                if upnp_type and e == UPnP_ERROR:
                    print 'WARNING: COULD NOT FORWARD VIA UPnP'
                    upnp_type = 0
                    continue
                print "error: Couldn't listen - " + str(e)
                do_gui_operation(app.stop, tab)
                h.failed()
                return

        response = get_response(config['responsefile'], config['url'], h.error)
        if not response:
            break

        infohash = sha(bencode(response['info'])).digest()
        # the infohash is presumed to be unique (ignoring sha1 clashes, which do exist)
        # below is a REALLY bad hack
        dupe = 0
        for torrents in app.torrents:
                if torrents[1].infohash == infohash:
                        dupe = 1
                        break      
        if dupe == 1:
                do_gui_operation(app.dupe)
                break
        dow = BT1Download(h.display, h.finished, h.error, disp_exception, doneflag,
                        config, response, infohash, myid, rawserver, listen_port,
                        configdir)
        h.settabs(tab = tab, tab_label = tab_label)
        app.torrents.append([tab, dow])
        # in the beta2 and previous versions the upload cap was set here
        # this is not needed for the time being because a tab is being opened
        if not dow.saveAs(h.chooseFile, h.newpath):
            break
        # the datalength is needed to work out the progress bar data	
        h.setdatalength(dow.datalength)
        if not dow.initFiles(old_style = True):
            break
        if not dow.startEngine():
            dow.shutdown()
            break
        dow.startRerequester()
        dow.autoStats()
        if not dow.am_I_finished():
            h.display(activity = 'connecting to peers')
        rawserver.listen_forever(dow.getPortHandler())
        h.display(activity = 'shutting down')
        dow.shutdown()
        break
    try:
      rawserver.shutdown()
    except:
      pass
    if not h.done:
        h.failed()

# this is the main interfacial (it's a word ;-]) object
class Client:
	def __init__(self):
		# pick up the parameters straightaway
		self.params = argv[1:]
		self.configdir = ConfigDir('anatomicgui')
		self.defaultsToIgnore = ['responsefile', 'url', 'saveas', 'super_seeder'] # so that by default the old torrent is not loaded
		self.configdir.setDefaults(defaults,self.defaultsToIgnore)
		self.configdefaults = self.configdir.loadConfig()
		# make sure it's gone ;-)
		self.configdefaults['url'] = '' # not in this release
		self.configdefaults['saveas'] = ''
		self.configdefaults['super_seeder'] = 0
		# the bit below is for users who are using the client like btdownloadheadless.py
		try:
				if len(self.params) > 0:
					self.config = parse_params(self.params, self.configdefaults)
				else:
					self.config = self.configdefaults
		except ValueError, e:
					print 'error: ' + str(e) + '\nrun with no args for parameter explanations'
					sys.exit(2)
		if not self.config:
					print get_usage(defaults, 80, self.configdefaults)
					sys.exit(2)
		self.configdir.deleteOldCacheData(self.config['expire_cache_data'])
		self.lastdirname = "" # for the file dialog
		# gtk is not so good at remembering the file names
		# the main glade xml file
		gladefile = "anatomic.glade"
		windowname = "window1"
		self.wTree = gtk.glade.XML(gladefile, windowname)
		# sets up the main parent window
		self.window = self.wTree.get_widget("window1")
		self.window.connect("delete_event", self.destroy)
		# sets up accelerators early on
		# -----------------------------------
		# accelerator for open button (ctrl-o)
		accel_group = gtk.AccelGroup()
		accel_group.connect_group(111, gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.fileselector)
		self.window.add_accel_group(accel_group)	
		# end of accelerator for open button
		# -----------------------------------
		# accelerator for pause/resume button (ctrl-p or ctrl-r)
		accel_group2 = gtk.AccelGroup()
		accel_group2.connect_group(112, gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.repause)
		self.window.add_accel_group(accel_group2)	
		accel_group3 = gtk.AccelGroup()
		accel_group3.connect_group(114, gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.repause) 
		self.window.add_accel_group(accel_group3)		
		# end of accelerator for pause/resume button 
		# -------------------------------------
		# accelerator for cancel button (ctrl-c)
		accel_group4 = gtk.AccelGroup()
		accel_group4.connect_group(99, gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.prompt) 
		self.window.add_accel_group(accel_group4)			
		# end of accelerator for cancel button
		# ----------------------------------------
		# accelerator for settings button (ctrl-s)
		accel_group5 = gtk.AccelGroup()
		accel_group5.connect_group(115, gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.settings) 
		self.window.add_accel_group(accel_group5)	
		# end of accelerator for settings button
		# ---------------------------------------
		# accelerator for about button (ctrl-a)
		accel_group6 = gtk.AccelGroup()
		accel_group6.connect_group(97, gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.about) 
		self.window.add_accel_group(accel_group6)
		# end of accelerator for about button
		# ---------------------------------------
		# accelerator for quit button (ctrl-q)
		accel_group7 = gtk.AccelGroup()
		accel_group7.connect_group(113, gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.destroy) 
		self.window.add_accel_group(accel_group7)
		# end of accelerator for quit button	
		# ---------------------------------------							
		# defining buttons and connecting them
		self.button1 = self.wTree.get_widget("button1")
		self.button1.connect("enter", self.statushandler, "Open a torrent file for download (Ctrl-O).")
		self.button1.connect("leave", self.statushandler, "")	
		self.button1.connect("clicked", self.fileselector)	
		# button 2 is not important at this stage
		self.button3 = self.wTree.get_widget("button3")
		self.button3.set_sensitive(False) # wait for a download
		self.button4 = self.wTree.get_widget("button4")
		self.button4.set_sensitive(False)
		self.button5 = self.wTree.get_widget("button5")
		self.button5.connect("clicked", self.settings)
		self.button5.connect("enter", self.statushandler, "Change this program's settings (Ctrl-S).")
		self.button5.connect("leave", self.statushandler, "")	
		self.button6 = self.wTree.get_widget("button6")
		self.button6.connect("enter", self.statushandler, "About this program (Ctrl-A).")
		self.button6.connect("leave", self.statushandler, "")	
		self.button6.connect("clicked", self.about)
		self.button7 = self.wTree.get_widget("button7")
		self.button7.connect("enter", self.statushandler, "Quit this program and stop all transfers (Ctrl-Q).")
		self.button7.connect("leave", self.statushandler, "")	
		self.button7.connect("clicked", self.destroy)
		# leave for the time being like this
		# end of buttons at the top of the client (tab independent)
		self.tabs = self.wTree.get_widget("notebook3") # pretty important
		self.tabs.connect("switch-page", self.tabchanged)
		self.wTree.get_widget("button13").connect_object("clicked", self.prompt, None, self.wTree)
		self.wTree.get_widget("button13").connect("enter", self.statushandler, "Cancel this transfer (Ctrl-C).")
		self.wTree.get_widget("button13").connect("leave", self.statushandler, "")	
		self.wTree.get_widget("checkbutton2").connect("clicked", self.superseed)
		self.wTree.get_widget("textview2").get_buffer().create_tag("error", foreground="red", scale=pango.SCALE_SMALL)	
		# this deals with the stuff for notebook page 1
		# it's just something to deal with when initiating
		self.wTree.get_widget("hscale2").connect("adjust-bounds", self.move)
		self.wTree.get_widget("hscale2").set_sensitive(False)
		self.wTree.get_widget("hscale3").set_sensitive(False)
		self.wTree.get_widget("hscale3").connect("adjust-bounds", self.move)
		self.wTree.get_widget("spinbutton13").set_sensitive(False)
		self.wTree.get_widget("spinbutton14").set_sensitive(False)
		self.wTree.get_widget("spinbutton13").connect("value-changed", self.move)
		self.wTree.get_widget("spinbutton14").connect("value-changed", self.move)
		# apparently it IS possible to have an empty notebook (but it will look stupid)
		self.statusbar = self.wTree.get_widget("statusbar1")
		self.context_id = self.statusbar.get_context_id("A message saying the program has loaded")
		self.message_id = self.statusbar.push(self.context_id, "Welcome to Anatomic P2P")
		self.deftab = None
		self.torrents = [] # this list will contain the torrents [[ tab , download object], [etc]]
		self.pausebutton = 0 # zero is status button shows pause (i.e. active) and status 1 is status button shows resume (i.e. paused)
		if len(self.params) == 0:
			self.fileselector()
		else:
			# take the chance and presume the user knows what they are doing
			if self.params.count("--saveas") == 0:
					self.filename = self.params[0] # a bit of a presumption
					self.lastdirname = ""
					self.save()
			else: 
				# the user treats the app like btdownloadheadless.py (hopefully)
				# this should work when the user associates this program with torrents
				self.startthreads()
	def statushandler(self, widget=None, data=None):
			# this function handles status bar onmouseover on buttons (they call it 'enter' in GTK) 
			self.context_id = self.statusbar.get_context_id("Onmouseover sort of messages.")
			self.message_id = self.statusbar.push(self.context_id, data)		
	def errors(self, widget=None, data=None):
			# this function is called by the stats object to deal with errors	
			errorlog = widget.get_widget("textview2").get_buffer()
			errorlog.delete(errorlog.get_start_iter(), errorlog.get_end_iter())
			insertmark = errorlog.get_insert()
			for err in data:
					iter = errorlog.get_iter_at_mark(insertmark)
					errorlog.insert_with_tags_by_name(iter, 'ERROR:\r' + err + '\r', "error")
	def newtab(self, widget=None, data=None):
			# This function creates a new tab and the tab_label thing
			# before this is called if a single tab exists should be checked
			gladefile = "anatomic.glade"
			windowname = "vbox17"
			tab = gtk.glade.XML(gladefile, windowname)
			tablabel = "hbox37"
			tab_label = gtk.glade.XML(gladefile, tablabel)
			button = tab_label.get_widget("button13")
			button.connect("enter", self.statushandler, "Cancel this transfer (Ctrl-C).")
			button.connect("leave", self.statushandler, "")	
			button.connect_object("clicked", self.prompt, None, tab)
			tab.get_widget("checkbutton2").connect("clicked", self.superseed)	
			tab.get_widget("textview2").get_buffer().create_tag("error", foreground="red", scale=pango.SCALE_SMALL)			
			self.tabs.append_page(tab.get_widget("vbox17"), tab_label.get_widget("hbox37"))
			self.tabs.set_current_page(-1)
			return (tab, tab_label)
	def tabchanged(self, widget=None, data=None, data2=None):
			# this program changes the pause/resume button when the tab changes
			# unpauseflag basically means it is not paused
			if len(self.torrents) == 0:
				pass # something odd happened
			else:
				pagenum = self.tabs.get_current_page()
				if self.torrents[pagenum][1].unpauseflag.isSet():
					# so the download is not paused
					if self.pausebutton == 0: # the icon is correct
						pass
					else: # i.e. pausebutton is one and top button shows resume
						self.wTree.get_widget("label90").set_label("_Pause\rTransfer")
						self.wTree.get_widget("image6").set_from_stock(gtk.STOCK_MEDIA_PAUSE, 3)
						self.pausebutton = 0
				else: # the implication is the download is paused but it's really not worth checking
					if self.pausebutton == 1:
						pass
					else: # top button shows pause but should show resume
						self.wTree.get_widget("label90").set_label("_Resume\rTransfer")
						self.wTree.get_widget("image6").set_from_stock(gtk.STOCK_MEDIA_PLAY, 3)	
						self.pausebutton == 1	
	def saveconfig(self, widget=None, data=None):
			# this functions saves the configuration permanently
			if self.configdir.saveConfig(self.config):
				self.context_id = self.statusbar.get_context_id("Tells the user about the save")
				self.message_id = self.statusbar.push(self.context_id, "The settings were saved.")
			else:
				self.context_id = self.statusbar.get_context_id("Tells the user about the save")
				self.message_id = self.statusbar.push(self.context_id, "There was an error when saving the settings.")
	def wrap(self, widget=None, data=None, data2=None, data3=None):
			# this function wraps calls with the correct argument for the settings dialog
			# basically switch...case
			if data2 == 99:
				self.dialogdestroy(self.dialog1)
			elif data2 == 97:
				self.apply(self.settingstree.get_widget("button09"))
			else: # 115
				self.apply(self.settingstree.get_widget("button10"))
	def settings(self, widget=None, data=None, data2=None, data3=None):
			# this function loads the settings dialog
			# Hiding the dialog and reloading it doesn't seem to work
			gladefile = "anatomic.glade"
			windowname = "dialog1"
			self.settingstree = gtk.glade.XML(gladefile, windowname)
			self.dialog1 = self.settingstree.get_widget("dialog1")
			self.dialog1.connect_object("delete_event", self.dialogdestroy, self.dialog1)
			# start of accelerators
			accel_group = gtk.AccelGroup()
			accel_group.connect_group(99, gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.wrap)
			self.dialog1.add_accel_group(accel_group)
			accel_group2 = gtk.AccelGroup()
			accel_group2.connect_group(97, gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.wrap)
			self.dialog1.add_accel_group(accel_group2)	
			accel_group3 = gtk.AccelGroup()
			accel_group3.connect_group(115, gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.wrap)
			self.dialog1.add_accel_group(accel_group3)
			# end of accelerators
			# button stuff
			self.settingstree.get_widget("button12").connect_object("clicked", self.dialogdestroy, self.dialog1)
			self.settingstree.get_widget("button12").connect("enter", self.statushandler, "Cancel the changes (Ctrl-C)")
			self.settingstree.get_widget("button12").connect("leave", self.statushandler, "")
			self.settingstree.get_widget("button9").connect("clicked", self.apply)
			self.settingstree.get_widget("button9").connect("enter", self.statushandler, "Save the settings for this current session. (Ctrl-A)")
			self.settingstree.get_widget("button9").connect("leave", self.statushandler, "")
			self.settingstree.get_widget("button10").connect("clicked", self.apply)
			self.settingstree.get_widget("button10").connect("enter", self.statushandler, "Save the settings permanently. (Ctrl-S)")
			self.settingstree.get_widget("button10").connect("leave", self.statushandler, "")			
			# end of button stuff
			self.label120 = self.settingstree.get_widget("label120")
			self.spinbutton3 = self.settingstree.get_widget("spinbutton3")
			self.spinbutton3.set_sensitive(False)
			self.checkbutton1 = self.settingstree.get_widget("checkbutton1")
			self.spinbutton4 = self.settingstree.get_widget("spinbutton4")
			self.spinbutton5 = self.settingstree.get_widget("spinbutton5")
			self.spinbutton6 = self.settingstree.get_widget("spinbutton6")
			self.spinbutton7 = self.settingstree.get_widget("spinbutton7")
			self.spinbutton8 = self.settingstree.get_widget("spinbutton8")
			self.spinbutton9 = self.settingstree.get_widget("spinbutton9")
			self.spinbutton10 = self.settingstree.get_widget("spinbutton10")
			self.spinbutton12 = self.settingstree.get_widget("spinbutton12")
			self.checkbutton1.set_active(self.config["random_port"])
			self.spinbutton10.set_value(self.config["maxport"]) # maximum port
			self.spinbutton12.set_value(self.config["minport"]) # minimum port
			self.spinbutton3.set_value(self.config["alloc_rate"]) # allocation rate
			self.spinbutton4.set_value(self.config["max_uploads"]) # maximum uploads
			self.spinbutton5.set_value(self.config["rerequest_interval"]) # rerequest interval
			self.spinbutton6.set_value(self.config["min_peers"]) # minimum peers to stop rerequesting
			self.spinbutton7.set_value(self.config["display_interval"]) # intervals to change display
			self.spinbutton8.set_value(self.config["max_initiate"]) # maximum connections to initiate
			self.spinbutton9.set_value(self.config["http_timeout"]) # time to call http dead
			alloc_type = ["normal", "background", "pre-allocate", "sparse"] # a list of the allocation numbers for the combo box processing
			if self.config["alloc_type"] == "background":
				self.label120.set_sensitive(True)
				self.spinbutton3.set_sensitive(True)
			else:
				self.label120.set_sensitive(False)
				self.spinbutton3.set_sensitive(False)
			# a stupid hack below
			self.settingstree.get_widget("radiobutton0" + str(alloc_type.index(self.config["alloc_type"]))).set_active(1) # type of allocation
			for widget in self.settingstree.get_widget("radiobutton00").get_group():
				widget.connect("toggled", self.change)
			self.settingstree.get_widget("radiobutton" + str(self.config["upnp_nat_access"])).set_active(1)
			self.entry3 = self.settingstree.get_widget("entry3")
			self.entry3.set_text(self.config["ip"])
			self.filechooserbutton1 = self.settingstree.get_widget("filechooserbutton1")
			if isdir(self.config["default_save"]):
				self.filechooserbutton1.set_current_folder(self.config["default_save"])
	def dupe(self, widget=None, data=None):
			self.dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING)
			self.dialog.set_modal(True)
			self.dialog.set_markup('<span weight="bold" size="larger">This torrent is a duplicate.</span>\r\rThis torrent is already transferring.')
			self.dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
			self.dialog.add_buttons(gtk.STOCK_OK,gtk.RESPONSE_OK)
			response = self.dialog.run()
			if response is not None: # what else can it be
				pagenum = self.tabs.get_current_page()
				self.tabs.remove_page(pagenum)
				self.dialog.destroy()
	def change(self, widget=None, data=None):
			if widget.get_name() == "radiobutton01":
				self.label120.set_sensitive(True)
				self.spinbutton3.set_sensitive(True)
			else:
				self.label120.set_sensitive(False)
				self.spinbutton3.set_sensitive(False)
	def apply(self, widget=None, data=None):
			# collects settings in same order as before
			self.config["random_port"] = self.checkbutton1.get_active()
			self.config["maxport"] = self.spinbutton10.get_value_as_int()
			self.config["minport"] = self.spinbutton12.get_value_as_int()
			self.config["alloc_rate"] = self.spinbutton3.get_value()
			self.config["max_uploads"] = int(self.spinbutton4.get_value())
			self.config["rerequest_interval"] = self.spinbutton5.get_value()
			self.config["min_peers"] = int(self.spinbutton6.get_value())
			self.config["display_interval"] = self.spinbutton7.get_value()
			self.config["max_initiate"] = self.spinbutton8.get_value_as_int()
			self.config["http_timeout"] = self.spinbutton9.get_value_as_int()
			# There must be a better way to do get the data from the radiobutton
			alloc_type = ["normal", "background", "pre-allocate", "sparse"] # a list of the allocation numbers for the combo box processing
			for widget in self.settingstree.get_widget("radiobutton00").get_group():
				if widget.get_active():
					self.config["alloc_type"] = alloc_type[int(widget.get_name()[-1])]
					break
			for widget in self.settingstree.get_widget("radiobutton0").get_group():
					if widget.get_active():
						self.config["upnp_nat_access"] = int(widget.get_name()[-1])
						break
			self.config["ip"] = self.entry3.get_text()
			self.config["default_save"] = self.filechooserbutton1.get_current_folder()
			if widget.get_name() == "button10":
					self.saveconfig()
			self.dialog1.destroy()
	def superseed(self, widget=None, data=None):
		if len(self.torrents) == 0:
			widget.set_active(False)
			return False
		elif widget.get_active(): # this is important otherwise the callback is done twice (pygtk FAQ)
			self.dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION)
			self.dialog.set_modal(True)
			self.dialog.set_markup('<span weight="bold" size="larger">Are you wish to start `super-seeding`?</span>\r\rPlease note this change is irreversible. Super-seeding should only be used by the initial seed of a torrent and it can boost distribution speeds by 30-40%.')
			self.dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
			self.dialog.add_buttons(gtk.STOCK_OK,gtk.RESPONSE_OK,gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL)
			self.dialog.connect_object("delete_event", self.dialogdestroy, self.dialog)
			response = self.dialog.run()
			if response == gtk.RESPONSE_OK:
				pagenum = self.tabs.get_current_page()
				self.torrents[pagenum][1].set_super_seed()
				self.dialog.destroy()
				widget.set_sensitive(False)
				return True
			else:
				self.dialog.destroy()	
				widget.set_active(False)
	def move(self, widget=None, data=None):
			# done extremely deliberately because the value in variable data is complete utter garbage...
			# let's hope the user does not change tab extremely quickly
			pagenum = self.tabs.get_current_page()
			if widget.get_name() == "hscale2" or widget.get_name() == "spinbutton13" : # upload cap
					ucap = widget.get_value()
					self.torrents[pagenum][1].setUploadRate(ucap)
					if widget.get_name() == "spinbutton13": # data is sent to the other widget
							self.torrents[pagenum][0].get_widget("hscale2").set_value(ucap)
					else:
							self.torrents[pagenum][0].get_widget("spinbutton13").set_value(ucap)
			else: # has to therefore be the download cap
					dcap = widget.get_value()
					self.torrents[pagenum][1].setDownloadRate(dcap)
					if widget.get_name() == "spinbutton14": # it seems weird to reassign data to the same object
							self.torrents[pagenum][0].get_widget("hscale3").set_value(dcap)
					else:
							self.torrents[pagenum][0].get_widget("spinbutton14").set_value(dcap)
	def startthreads(self, widget=None, data=None):
			if self.config['saveas'] == '' and self.config['default_save'] != '':
					self.config['saveas'] = self.config['default_save']
			# open a new tab here
			if self.deftab is not None:
				tab = self.deftab
				tab[0].get_widget("hscale2").set_sensitive(True)
				tab[0].get_widget("hscale3").set_sensitive(True)
				tab[0].get_widget("spinbutton13").set_sensitive(True)
				tab[0].get_widget("spinbutton14").set_sensitive(True)
				self.deftab = None
			elif self.tabs.get_n_pages() == 1 and len(self.torrents) == 0:
				tab = (self.wTree, self.wTree) # set the tab as the 1st one
				tab[0].get_widget("hscale2").set_sensitive(True)
				tab[0].get_widget("hscale3").set_sensitive(True)
				tab[0].get_widget("spinbutton13").set_sensitive(True)
				tab[0].get_widget("spinbutton14").set_sensitive(True)
			else:
				tab = self.newtab() # generate new tab as tuple
				# set up the new tab with the right callbacks
				tab[0].get_widget("hscale2").connect("adjust-bounds", self.move)
				tab[0].get_widget("hscale2").set_sensitive(True)
				tab[0].get_widget("hscale3").set_sensitive(True)
				tab[0].get_widget("hscale3").connect("adjust-bounds", self.move)
				tab[0].get_widget("spinbutton13").set_sensitive(True)
				tab[0].get_widget("spinbutton14").set_sensitive(True)
				tab[0].get_widget("spinbutton13").connect("value-changed", self.move)
				tab[0].get_widget("spinbutton14").connect("value-changed", self.move)
			self.button3.set_sensitive(True)
			self.button3.connect("clicked", self.repause)
			self.button3.connect("enter", self.statushandler, "Pause/Resume the selected transfer (in certain situations). (Ctrl-R) or (Ctrl-P)")
			self.button3.connect("leave", self.statushandler, "")	
			self.button4.set_sensitive(True)
			self.button4.connect("enter", self.statushandler, "Cancel the selected transfer. (Ctrl-C)")
			self.button4.connect("leave", self.statushandler, "")	
			self.button4.connect("clicked", self.prompt)
			self.wTree.get_widget("label90").set_label("_Pause\rTransfer")
			self.wTree.get_widget("image6").set_from_stock(gtk.STOCK_MEDIA_PAUSE, 3)
			self.pausebutton = 0
			self.thread = Thread(target = run, args = [tab[0], tab[1], self, self.config, self.configdir])
			self.thread.setDaemon(False)
			self.thread.start()
	def fileselector(self, widget=None, data=None, data2=None, data3=None):
			# There are lots of arguments because the accelerator callback passes a lot
			# displays open dialog and checks things are OK
			self.filedialog = gtk.FileChooserDialog("Browse For Torrent", action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
			if self.lastdirname != "":
				self.filedialog.set_current_folder(self.lastdirname)
			# code below filters out torrent files
			self.torrentfilter = gtk.FileFilter()
			self.torrentfilter.add_pattern("*.torrent")
			self.torrentfilter.set_name("Torrent Files")
			self.filedialog.add_filter(self.torrentfilter)
			self.filedialog.set_modal(True)
			self.filedialog.connect("delete_event", lambda self, widget: self.destroy())
			response = self.filedialog.run()
			if response == gtk.RESPONSE_OK:
				self.lastdirname = self.filedialog.get_current_folder()
				self.filename = self.filedialog.get_filename()
				self.filedialog.destroy()
				self.config['responsefile'] = self.filename
				self.save()
			elif response == gtk.RESPONSE_CANCEL:
				self.filedialog.destroy()
	def save(self, widget=None, data=None):
			self.default = "Use default folder" # this is the button text label
			try:
					# might be worth wrapping this in idle_add
					f = open(self.filename, "rb")
					file = f.read()
					f.close()
					bdata = bdecode(file)
			except (IOError, ValueError), e:
					self.context_id = self.statusbar.get_context_id("Error message because file cannot be opened")
					self.message_id = self.statusbar.push(self.context_id, "Error Opening File: "+str(e))
					if self.filename in self.params: # for torrents pushed from the command line
							self.params.remove(self.filename)
			else:
					# bad workaround for command line
					if self.lastdirname != "":
							temp = self.lastdirname+sep
					else:
							temp = ""
					if bdata["info"].has_key("files"):
							# The torrent is a multi-file torrent
							if isdir(temp+bdata["info"]["name"]): # i.e. The directory is in the same folder as the torrent
									self.config['saveas'] = temp+bdata["info"]["name"]
									self.startthreads()
							else:
									self.filedialog2 = gtk.FileChooserDialog("Choose folder to save to", action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL, self.default, gtk.RESPONSE_REJECT, gtk.STOCK_SAVE,gtk.RESPONSE_OK)) # throw save dialog
									if self.lastdirname != "":
											self.filedialog2.set_current_folder(self.lastdirname)
									self.filedialog2.connect("delete_event", lambda self, widget: self.destroy())
									self.filedialog2.set_modal(True)
									response = self.filedialog2.run()
									if response == gtk.RESPONSE_OK:
											filename = self.filedialog2.get_current_folder()
											self.filedialog2.destroy()
											filename.replace(bdata["info"]["name"], "") # something to try and stop the issue of double saving
											self.config['saveas'] = filename
											self.startthreads()
									elif response == gtk.RESPONSE_REJECT:
											self.filedialog2.destroy()
											self.startthreads()
									else: # cancel
											self.filedialog2.destroy()
					else: # single file torrent
							if isfile(temp+bdata["info"]["name"]): # i.e. The file is in the same folder as the torrent
									self.config['saveas'] = temp+bdata["info"]["name"]
									self.startthreads()
							else:
									self.filedialog2 = gtk.FileChooserDialog("Save Torrent File", action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL, self.default, gtk.RESPONSE_REJECT, gtk.STOCK_SAVE,gtk.RESPONSE_OK)) # throw save dialog
									if self.lastdirname != "":
											self.filedialog2.set_current_folder(self.lastdirname)
									self.filedialog2.set_current_name(bdata["info"]["name"])
									self.filedialog2.set_modal(True)
									self.filedialog2.connect("delete_event", lambda self, widget: self.destroy())
									response = self.filedialog2.run()
									if response == gtk.RESPONSE_OK:
											self.config['saveas'] = self.filedialog2.get_filename()
											self.filedialog2.destroy()
											self.startthreads()
									elif response == gtk.RESPONSE_REJECT:
											self.filedialog2.destroy()
											self.startthreads()
									else: # cancel
											self.filedialog2.destroy()
	def dialogdestroy(self, dialogname, data=None):
		# kills all dialogs
		dialogname.destroy()
	def destroy(self, widget=None, data=None, data2=None, data3=None):
		self.dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION)
		self.dialog.set_modal(True)
		self.dialog.set_markup('<span weight="bold" size="larger">Are you sure you want to quit?</span>\r\rQutting will stop any transferring torrents. Please note that everyone is relied upon to upload as well as download to at least a ratio of 1:1.')
		self.dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
		self.dialog.add_buttons(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_QUIT,gtk.RESPONSE_OK)
		self.dialog.connect_object("delete_event", self.dialogdestroy, self.dialog)
		response = self.dialog.run()
		if response == gtk.RESPONSE_OK:
			self.dialog.destroy()
			self.stop(None, 1)
			return True
		elif response == gtk.RESPONSE_CANCEL:
			self.dialog.destroy()
			return True
	def about(self, widget=None, data=None, data2=None, data3=None):
		# lots of arguments added because of the accelerator
		self.about = gtk.AboutDialog()
		self.about.set_modal(True)
		self.about.connect_object("delete_event", self.dialogdestroy, self.about)
		self.about.set_name("Anatomic P2P (Main)")
		self.about.set_version("Version 0.1 RC1") # Some peole have beta Release Candidate's - how does that work?
		self.about.set_license("Licenced under the GNU General Public License that \rsupercedes the MIT/X Consortium License.\rSee LICENSE.txt for more information.")
		self.about.set_comments("A GUI BitTorrent Client with Anatomic P2P Extensions. \rThanks to the 'Ministry of Boredom' and the 'Boredom Squad' (see source code) for making me so bored that I dreamed up this idea ;)")
		self.about.set_copyright("Copyleft Kunkie 2005. Some Rights Reserved.")
		self.about.set_authors(["Main Author - Kunkie - kunky@mail.berlios.de\r","Thanks also to:\rFilesoup - http://www.filesoup.co.uk/forum/","PyGTK FAQ - http://www.async.com.br/faq/pygtk/","lefrog","Rhynome","'Pythonman'","BerliOS Developer - http://developer.berlios.de/","Idobi Radio - http://www.idobi.com " , "...and finally the whole of the 'Boredom Squad'\rand especially the commander-in-chief. ;-)"])
		gtk.about_dialog_set_url_hook(self.openurl)
		self.about.set_website("http://anatomic.berlios.de/")
		response = self.about.run()
	def openurl(self,widget=None, data=None):
		# I think this was taken from the official client (like a lot of this project)
		Thread(target = open_new(data)).start()
	def repause(self, widget, data=None, transfer=None):
		# one function handles pause and unpause
		if len(self.torrents) == 0:
			pass
		else:
			pagenum = self.tabs.get_current_page()
			download = self.torrents[pagenum][1]
			if download.unpauseflag.isSet():
				if download.Pause():
					self.wTree.get_widget("label90").set_label("_Resume\rTransfer")
					self.wTree.get_widget("image6").set_from_stock(gtk.STOCK_MEDIA_PLAY, 3)
					self.pausebutton = 1
			else: # UnPause Torrent
				download.Unpause()
				self.wTree.get_widget("label90").set_label("_Pause\rTransfer")
				self.wTree.get_widget("image6").set_from_stock(gtk.STOCK_MEDIA_PAUSE, 3)
				self.pausebutton = 0
	def prompt(self, widget=None, data=None, data2=None, data3=None):
		# to check the user doesn't close a tab with no active torrent in it
		if len(self.torrents) == 0:
			pass
		else:
			self.dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION)
			self.dialog.set_markup('<span weight="bold" size="larger">Are you sure you want to stop this torrent?</span>\r\rPlease note that everyone is relied upon to upload as well as download to at least a ratio of 1:1.')
			self.dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
			self.dialog.set_modal(True)
			self.dialog.add_buttons(gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL)
			self.dialog.connect_object("delete_event", self.dialogdestroy, self.dialog)
			response = self.dialog.run()
			if response == gtk.RESPONSE_OK:
					self.dialog.destroy()
					self.stop(data)
			elif response == gtk.RESPONSE_CANCEL:
					self.dialog.destroy()
	def check(self, pagenum=None):
		if len(self.torrents) >= 1:
			self.tabs.remove_page(pagenum)	
		elif len(self.torrents) == 0:	
			# the initial tab has to be set up like it's the beginning again
			# I reckon it is better to get a new one from the XML than sort out the old one
			gladefile = "anatomic.glade"
			windowname = "vbox17"
			tab = gtk.glade.XML(gladefile, windowname)
			tablabel = "hbox37"
			tab_label = gtk.glade.XML(gladefile, tablabel)
			tab_label.get_widget("button13").connect_object("clicked", self.prompt, None ,tab)
			tab_label.get_widget("button13").connect("enter", self.statushandler, "Cancel this transfer (Ctrl-C).")
			tab_label.get_widget("button13").connect("leave", self.statushandler, "")	
			tab.get_widget("checkbutton2").connect("clicked", self.superseed)	
			tab.get_widget("textview2").get_buffer().create_tag("error", foreground="red", scale=pango.SCALE_SMALL)			
			self.tabs.append_page(tab.get_widget("vbox17"), tab_label.get_widget("hbox37"))
			self.tabs.remove_page(pagenum)	
			self.deftab = (tab, tab_label)					
			self.config['saveas'] = ''
			self.config['responsefile'] = ''
			self.wTree.get_widget("label90").set_label("_Pause\rTransfer")
			self.wTree.get_widget("image6").set_from_stock(gtk.STOCK_MEDIA_PAUSE, 3)
			self.pausebutton = 0
			self.button3.set_sensitive(False)
			self.button4.set_sensitive(False)
	def stop(self, widget=None, data=None):
		if widget is not None:
			child = widget.get_widget("vbox17")
			pagenum = self.tabs.page_num(child)
			try:
				self.torrents.remove(self.torrents[pagenum])
			except:
				pass
			self.check(pagenum)	
		elif data:
				for torrent in self.torrents:
					torrent[1].doneflag.set()
				# that should stop the torrent(s)
				gtk.main_quit()
		else:
				pagenum = self.tabs.get_current_page()	
				self.torrents[pagenum][1].doneflag.set()
				self.torrents.remove(self.torrents[pagenum])
				self.check(pagenum)
				# the above code sets the client as if it was starting again

# where would I be without this function (pygtk FAQ)?
def do_gui_operation(function, *args, **kw):
    def idle_func():
        gtk.threads_enter()
        try:
            function(*args, **kw)
            return False
        finally:
            gtk.threads_leave()
    gobject.idle_add(idle_func)

if __name__ == '__main__':
	try:
		import pygtk
		pygtk.require("2.0")
	except:
		pass
	try:
		import gtk
		import gtk.glade
		import pango
		import gobject
	except:
		print "You need to install pygtk or GTK+2"
		print "or set your PYTHONPATH correctly"
		print "Try typing 'export PYTHONPATH=/usr/lib/python2.4/site-packages/'"
		sys.exit(1)
	gtk.threads_init()
	gtk.threads_enter()
	app = Client()
	gtk.main()
	gtk.threads_leave()

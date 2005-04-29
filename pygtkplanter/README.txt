Anatomic P2P GUI Planter (0.1 BETA)
===================================
Licenced under the MIT / X Consortium Licence

System Requirements
-------------------

Linux, Windows, (Mac OSX w/ X11, GTK + lots of other dependencies)
PyGTK 
Python 2.3 or 2.4


So what does this app do?
-------------------------

This application notifies supertrackers and trackers on the Anatomic P2P Network
that the given file will be shared on the network. This program takes input from
an normal torrent file and 'plants' it on the network. The tracker urls are
changed in the file in a system christened 'hackwards compatibility'. This means
that users using an old BitTorrent Client can use the Anatomic P2P network.

How to use this app
-------------------

Run the Application

This will be:

(linux)
python planter.py or ./planter.py

(windows) 
double click on planter.exe

If all dependencies are OK the program should popup.
You should make a normal torrent file from the file(s) you are going to share.
Once this has been created select the file using the browse menu.
(Advanced users can choose how many trackers to seed on - EXPERIMENTAL)
Click on 'Plant Torrent File'
Accept the Warning
The torrent file should start to plant
The text box shows the current status
Eventually if all has worked well the message 'Torrent Successfully Planted on Anatomic P2P' should be received
The torrent file will then be overwritten and this file should be distributed

Bear in mind this is a BETA and things may not work perfectly

Contact
-------

Please report any bugs to the database at:
http://developer.berlios.de/bugs/?group_id=2947
or through the email address below.

You can visit the website at:
http://anatomic.berlios.de
or email be at:
kunky@mail.berlios.de

The latest code can be found in the CVS server. Instructions to access the CVS
Server are below:

cvs -d:pserver:anonymous@cvs.anatomic.berlios.de:/cvsroot/anatomic login 
 
cvs -z3 -d:pserver:anonymous@cvs.anatomic.berlios.de:/cvsroot/anatomic co pygtkplanter

Anybody can help development of Anatomic P2P - Any patches would be greatfully received




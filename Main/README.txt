Anatomic P2P GUI Client (0.1 BETA2)
==================================
Licenced under the MIT / X Consortium Licence

System Requirements
-------------------

Linux, Windows, (Mac OSX w/ X11, GTK + lots of other dependencies)
PyGTK
GTK+ Runtimes > GTK+2 (See below)
Python 2.3 or 2.4

As with every program on Windows there is no guarantee that everything will work

GTK+ Runtimes
-----------------
A windows version can be downloaded from ftp://ftp.berlios.de/pub/anatomic/gtk-win32-2.6.8-rc1.exe.
Linux users should find a version of GTK+ from their distribution provider.
Mac users can download all dependencies from http://fink.sourceforge.net

So what does this app do?
-------------------------------

This program is a modified version of BitTornado using a PyGTK frontend and it can
access torrents on the Anatomic P2P Network.
Before use a torrent file is needed. These can be found all over the internet.

How to use this app
------------------------

Run the Application
Add a torrent file name or any options if desired

This will be:

(linux / osx)
execute 'python anatomicgui.py' or './anatomicgui.py'

(windows)
double click on anatomicgui.exe

Bear in mind this is a BETA and things may not work perfectly

Contact
-------

Please report any bugs to the database at:
http://developer.berlios.de/bugs/?group_id=2947
or through the email address below.

You can visit the website at:
http://anatomic.berlios.de
or email me at:
kunky@mail.berlios.de

The latest code can be found in the CVS server. Instructions to access the CVS
Server are below:

cvs -d:pserver:anonymous@cvs.anatomic.berlios.de:/cvsroot/anatomic login

cvs -z3 -d:pserver:anonymous@cvs.anatomic.berlios.de:/cvsroot/anatomic co guiclient

Anybody can help development of Anatomic P2P - Any patches would be gratefully received




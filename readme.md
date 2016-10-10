ChanLink v0.1.6	by Dustin G
http://chan-link.sourceforge.net/



OVERVIEW
--------

ChanLink is a program that forwards messages (or other 'events'
like joins, bans, etc.) from one chat server to another.  The
two servers do not have to be of the same protocol, but they may
be.  In example, you may wish to forward events in a channel on
an IRC server to a channel on Battle.net (Blizzard Entertainment's
free multiplayer gaming service).  Thus, you don't have to launch
a game in order to talk to your friends who are chatting on the
game servers.

ChanLink is written in Python, which means that it requires the
Python interpreter to run.  Get version 2.1.1 or later (required)
at http://www.python.org/.  This program should run on any platform
that runs Python, but has only been tested on Linux and Windows.

ChanLink is developed on Linux Mandrake (kernel 2.4).  The
development IRC server is ircd-hybrid.  Thus, ChanLink has, at
this point, only been tested on ircd-hybrid.  Please let me know
if ChanLink will not run on your IRC server (please include the
IRC server version, your version of Python, a description of the
problem, and if possible, a log of ChanLink's output at the time
the problem occured.



FILES
----

 * chan-link.py - main source (and executable...) file
 * protocol.py - contains protocol-specific network code and a
   wrapper to interface with chan-link.py
 * database.py - the bot's user database

 * readme.txt - you are reading it
 * changes.txt - changelog
 * notes.txt - release notes, bugs, todo list



INSTALL
-------

1. Make sure you have Python 2.1.1 or later installed on your box.

2. Unpack ChanLink into the installation directory (any directory
   you can write to will do).

3. Edit database.py (its in text format) to set the bot master's
   nickname, username, and hostname (Python regular expressions
   are supported: .+ matches 1 or more of any character excecpt
   newline (\n), .* matches 0 or more.  Make sure all entries
   follow the Python syntax (described in the file), and most
   important, MAKE SURE THAT ALL ENTRIES ARE *IRC LOWERCASE*
   (defined in the IRC RFC) (this is not necessarily just the
   normal lowercase [i.e. 'A' -> 'a'] ).
   Note- this step will be unnecessary in a later release.

4. Edit chan-link.py and scroll to the very bottom.  Configure
   which servers, channels, protocols, server nicknames, etc.
   here.

5. You're done!  Type 'python chan-link.py' at a command line
   to run ChanLink.
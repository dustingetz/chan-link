#!/usr/bin/env python
#
# chan-link.py v0.1.6
# chan-link.py copyright (C) 2002 Dustin G [email]
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#        
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# Dustin G [email]
#
# $Id: chan-link.py,v 0.1.6.1 2002/07/23 21:29:31 dustin Exp $

#******************************************************************
#WARNING: Make sure you do not accidentally link a
#channel to itself on the same server!  The bot will flood out
#if you're lucky.  XXX

#TODO
############
# logs!

from database import user_re_database

RELAY_CHAN_MISC=1
TTY_OUTPUT=1


import protocol

import string
from sys import exit
from time import sleep
import re

nm_to_n=   protocol.nm_to_n
nm_to_u=   protocol.nm_to_u
nm_to_uh=  protocol.nm_to_uh
nm_to_h=   protocol.nm_to_h
irc_lower= protocol.irc_lower

def get_user_priv_level(nm):
    possibleprivs=[]
    for r in user_re_database.keys():
        m=re.match(r, nm)
        if m != None:
            possibleprivs.append(user_re_database[r])
    if not possibleprivs: return 10 # guest

    hi=0
    for p in possibleprivs:
        if p>hi: hi=p

    return hi
        

class ServerList:
    def __init__(self):
        self.servers=[]

    def __len__(self):
        return self.get_no_of_servers()
    def add_server(self, host, port, type, channel, server_nick=None):
        server_nick=server_nick or host[-12:]
        self.servers.append((host, port, type, channel, server_nick))

    def get_server(self, n):
        return self.servers[n]
    def get_all_servers(self):
        return self.servers

    def get_host(self, n):
        return self.servers[n][0]
    def get_port(self, n):
        return self.servers[n][1]
    def get_protocol(self, n):
        return string.lower(self.servers[n][2])
    def get_channel(self, n):
        return self.servers[n][3]
    def get_server_nick(self, n):
        return self.servers[n][4]

    def get_no_of_servers(self):
        return len(self.servers)

class Link:
    def __init__(self, server_list):
        self.server_list=server_list
        self.servers=[]
        self.ircobj=protocol.Box()
        self.ircobj.add_global_handler(
            "all_events",
            self._dispatcher,
            -10)
        for i in ['join','quit','privmsg','pubmsg','mode',
                  'nick','disconnect','kick','part']:
            self.ircobj.add_global_handler(i, self._outputer, 0)

    def _dispatcher(self, c, e):
        m = "on_" + e.eventtype()
        if hasattr(self, m):
                getattr(self,m)(c,e)

    def connect(self):
        for i in range(self.server_list.get_no_of_servers()):
            if server_list.get_protocol(i) == 'irc':
                self.servers.append(self.ircobj.IRCServer())
            elif server_list.get_protocol(i) == 'bnet':
                self.servers.append(self.ircobj.BnetServer())
        for i in range(self.server_list.get_no_of_servers()):
            self.servers[i].connect(
                self.server_list.get_host(i),
                self.server_list.get_port(i),
                'dlink'+str(i))
            self.servers[i].set_bot_channel(self.server_list.get_channel(i))
            self.servers[i].set_server_nick(self.server_list.get_server_nick(i))
    def on_welcome(self, c, e):
        if TTY_OUTPUT:
            print '%s: \t%s %s' % (e.source(), e.eventtype(), e.arguments())
        c.join(c.get_bot_channel())

    def start(self):
        self.ircobj.process_forever()

    def quit(self, msg='ChanLink Closed'):
        for i in self.servers:
            i.quit(msg)
        self.die()

    def die(self):
        for i in self.servers:
            i.disconnect()
        exit(0)

    def on_pubmsg(self, c, e):
        if get_user_priv_level(e.source()) >= 10:
            for i in range(len(self.server_list)):
                if self.servers[i] != c:
                    self.servers[i].privmsg(server_list.get_channel(i),
                          '<%s@%s:%s> %s' % (nm_to_n(e.source()),
                                             c.get_protocol(),
                                             c.get_server_nick(),
                                             e.arguments()[0]))

    def on_privmsg(self, c, e):
        command=e.arguments()[0]
        #privmsg triggers here
        if get_user_priv_level(e.source()) >= 99:#botmasters only
            #administrative or restricted commands
            if command == '.die':
                self.die()
            elif command[:5] == '.quit':
                self.quit(command[6:])
                self.die()
            elif command[:5] == '.join':
                pass


            # commands .reload and .load don't work...
            # perhaps the module is buffered?
#            elif command[:7] == '.reload':
#                del user_re_database # this raises UnboundLocalError !?
#                from database import user_re_database
#            elif command[:5] == '.load':
#                exec('from %s import *'%(command[6:]))
            
        if get_user_priv_level(e.source()) >= 10:#everyone but banned
            if command[:5] == '.list':
                c.privmsg(nm_to_n(e.source()), "List command recieved")
            if command[:7] == '.whoami':
                c.privmsg(nm_to_n(e.source()),
                         "You are %s, privledge level %s." %
                         (e.source(), get_user_priv_level(e.source())))


    def on_kick(self, c, e):
        #rejoin channel if kicked 
        if e.arguments()[0] == c.nickname:
            c.join(c.get_bot_channel())
        
        #relay KICK msgs
        if RELAY_CHAN_MISC:
            for i in range(len(self.server_list)):
                if self.servers[i] != c:
                    self.servers[i].privmsg(self.server_list.get_channel(i),
                          '*** %s@%s:%s kicked %s@%s:%s from %s@%s:%s (%s)' % (
                                nm_to_n(e.source()),
                                c.get_protocol(),
                                c.get_server_nick(),
                                e.arguments()[0],
                                c.get_protocol(),
                                c.get_server_nick(),
                                e.target(),
                                c.get_protocol(),
                                c.get_server_nick(),
                                e.arguments()[1]
                                ))

    def on_part(self, c, e):
        if RELAY_CHAN_MISC:
            for i in range(len(self.server_list)):
                if self.servers[i] != c:
                    self.servers[i].privmsg(self.server_list.get_channel(i),
                          '*** %s@%s:%s has left %s@%s:%s' % (
                               nm_to_n(e.source()),
                               c.get_protocol(),
                               c.get_server_nick(),
                               e.target(),
                               c.get_protocol(),
                               c.get_server_nick()
                               ))

    def on_join(self, c, e):
        if RELAY_CHAN_MISC:
            for i in range(len(self.server_list)):
                if self.servers[i] != c:
                    self.servers[i].privmsg(self.server_list.get_channel(i),
                          '*** %s@%s:%s has joined %s@%s:%s' % (
                                nm_to_n(e.source()),
                                c.get_protocol(),
                                c.get_server_nick(),
                                e.target(),
                                c.get_protocol(),
                                c.get_server_nick()
                                ))

    def on_nick(self, c, e):
        if RELAY_CHAN_MISC:
            for i in range(len(self.server_list)):
                if self.servers[i] != c:
                    self.servers[i].privmsg(self.server_list.get_channel(i),
                          '*** %s@%s:%s is now known as %s' % (
                                          nm_to_n(e.source()),
                                          c.get_protocol(),
                                          c.get_server_nick(),
                                          e.target()
                                          ))
                                        
    def on_quit(self, c, e):
        if RELAY_CHAN_MISC:
            for i in range(len(self.server_list)):
                if self.servers[i] != c:
                    self.servers[i].privmsg(self.server_list.get_channel(i),
                          '*** %s@%s:%s has quit (%s)' % (nm_to_n(e.source()),
                                                       c.get_protocol(),
                                                       c.get_server_nick(),
                                                       e.arguments()[0]))
    
    #Prints useful data for logging
    def _outputer(self, c, e):
        if TTY_OUTPUT:
            print '%s: \t%s %s' % (e.source(), e.eventtype(), e.arguments())
            #if e.eventtype() == 'pubmsg':
            #    if TTY_OUTPUT: print e.arguments()



server_list=ServerList()
#format: add_server(host, port, protocol, channel, server nickname)
# server nickname is a short string to ID the server
# example: add_server('east.gamesnet.net',6667,'irc','#clanvt','egamesnet')
server_list.add_server('localhost',6667,'irc','#link1','dust')
server_list.add_server('localhost',6667,'irc','#link2','dust')
link=Link(server_list)
link.connect()
link.start()

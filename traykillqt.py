#!/usr/bin/env python
#
#   rfkillgtk.py
#   
#   Copyright 2012 Gasper Zejn <zejn@kiberpipa.org>
#   
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions
#   are met:
#   
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#   * Neither the name of the  nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#   
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#   A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#   OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#   THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#   


IGNORE_LIST = [
    'hci0',
    'phy0',
    ]

import rfkill

import sys
import signal

from PyQt4 import QtGui
from PyQt4.QtCore import QTimer


def sigint_handler(*args):
    sys.stderr.write('interrupted\n')
    QtGui.QApplication.quit()

class SystemTrayIcon(QtGui.QSystemTrayIcon):
    NAME_MAP = {
        'sony-wifi': 'Wifi',
        'sony-wwan': 'Mobile',
        'sony-bluetooth': 'Bluetooth',
    }

    def __init__(self, icon, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)

        self.icon_on = QtGui.QIcon("icons/user-online.png")
        self.icon_mixed = QtGui.QIcon("icons/user-invisible.png")
        self.icon_off = QtGui.QIcon("icons/user-busy.png")

        self.switches = rfkill.list_switches(IGNORE_LIST)
        self.refreshIconState()

    def __getattr__(self, name):
        prefix = 'onToggle_'
        if name.startswith(prefix):
            n = int(name[len(prefix):])
            def _inner():
                return self.onToggle(n)
            return _inner

    def refreshIconState(self):
        all_on = all([sw.get_state() == 1 for sw in self.switches])
        all_off = all([sw.get_state() != 1 for sw in self.switches])
        if all_on:
            self.icon = self.icon_on
            msg = 'all on'
        elif all_off:
            self.icon = self.icon_off
            msg = 'all off'
        else:
            self.icon = self.icon_mixed
            msg = 'mixed'
        self.setIcon(self.icon)
        self.rebuildMenu()
    
    def rebuildMenu(self):
        menu = QtGui.QMenu(self.parent())

        for n, sw in enumerate(self.switches):
            name = sw.get_name()
            state = sw.get_state() == 1 and 'on' or 'off'
            otherstate = state == 'on' and 'off' or 'on'
            menu.addAction("%s %s, click to turn %s" % (self.NAME_MAP.get(name, name), state, otherstate), getattr(self, 'onToggle_%d' % n))

        menu.addAction("Kill all", self.onKillAll)
        exitAction = menu.addAction("Exit", self.onQuit)
        self.setContextMenu(menu)

    def onKillAll(self):
        for sw in self.switches:
            sw.set_state(0)
        self.refreshIconState()

    def onToggle(self, idx, *args, **kwargs):
        sw = self.switches[idx]
        if sw.get_state() == 1:
            state = 0
        else:
            state = 1
        sw.set_state(state)
        self.refreshIconState()

    def onQuit(self):
        QtGui.QApplication.quit()

def main():
    app = QtGui.QApplication(sys.argv)
    w = QtGui.QWidget()
    trayIcon = SystemTrayIcon(QtGui.QIcon("icons/user-invisible.png"), w)
    trayIcon.show()
    signal.signal(signal.SIGINT, sigint_handler)
    timer = QTimer()
    timer.start(100)  # You may change this if you wish.
    timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


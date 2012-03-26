#!/usr/bin/env python
#
#   traykillwx.py
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
import wx

class RFKillIcon(wx.TaskBarIcon):
    TBMENU_CLOSE = 1000
    TBMENU_KILLALL = 1001
    TBMENU_SWITCHES_START = 1002

    NAME_MAP = {
        'sony-wifi': 'Wifi',
        'sony-wwan': 'Mobile',
        'sony-bluetooth': 'Bluetooth',
    }

    def __init__(self, app, *args, **kwargs):
        self.app = app
        super(RFKillIcon, self).__init__(*args, **kwargs)
        # setup events
        wx.EVT_TASKBAR_RIGHT_UP(self, self.onPopupMenu)
        wx.EVT_MENU(self, self.TBMENU_KILLALL, self.onKillAll)
        wx.EVT_MENU(self, self.TBMENU_CLOSE, self.onExit)
        
        self.switches = rfkill.list_switches(IGNORE_LIST)
        for n, sw in enumerate(self.switches):
            wx.EVT_MENU(self, self.TBMENU_SWITCHES_START + n, self.onToggleRFKill)

        self.icon_on = wx.Icon("icons/user-online.png", wx.BITMAP_TYPE_PNG)
        self.icon_mixed = wx.Icon("icons/user-invisible.png", wx.BITMAP_TYPE_PNG)
        self.icon_off = wx.Icon("icons/user-busy.png", wx.BITMAP_TYPE_PNG)
        
        self.refreshIconState()
    
    def onKillAll(self, evt):
        for sw in self.switches:
            sw.set_state(0)
        self.refreshIconState()

    def onToggleRFKill(self, evt):
        idx = (evt.GetId() - self.TBMENU_SWITCHES_START)
        sw = self.switches[idx]
        if sw.get_state() == 1:
            state = 0
        else:
            state = 1
        sw.set_state(state)
        self.refreshIconState()
    
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
        self.SetIcon(self.icon, "rfkill: " + msg)

    def onExit(self, evt):
        self.app.ExitMainLoop()

    def onPopupMenu(self, evt):
        menu = wx.Menu()
        for n, sw in enumerate(self.switches):
            state = sw.get_state() == 1 and 'on' or 'off'
            otherstate = state == 'on' and 'off' or 'on'
            name = sw.get_name()
            menu.Append(self.TBMENU_SWITCHES_START + n, "%s %s, click to turn %s" % (self.NAME_MAP.get(name, name), state, otherstate))
        menu.Append(self.TBMENU_KILLALL, "Kill all")
        menu.Append(self.TBMENU_CLOSE, "Quit")
        self.PopupMenu(menu)
        menu.Destroy()

if __name__ == "__main__":
    app= wx.PySimpleApp()
    tbicon = RFKillIcon(app)
    app.MainLoop()
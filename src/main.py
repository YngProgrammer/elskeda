# -*- coding: utf-8 -*-

import wx
import game

class App(wx.App):
    def __init__(self):
        wx.App.__init__(self)

        # Initialize and set game as top window
        self.game = game.Game(10, 500, 60, 20)
        self.SetTopWindow(self.game)

        # Start playing
        self.game.generate()

if __name__ == '__main__':
    app = App()
    app.MainLoop()

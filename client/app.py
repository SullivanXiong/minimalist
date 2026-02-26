#!/usr/bin/env python3
"""Minimalist — Linear-inspired project management tool."""

import wx

from minimalist.main import MainFrame


def main():
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()


if __name__ == '__main__':
    main()

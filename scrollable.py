"""Tkinter modified Frame widgets inherited XView and/or YView."""
import tkinter as tk
from tkinter import ttk


TK_GEOMETRY_METHODS = tuple(set([
    m for m in
    list(tk.Pack.__dict__.keys()) +
    list(tk.Grid.__dict__.keys()) +
    list(tk.Place.__dict__.keys())
    if m[0] != "_" and m != "config" and m != "configure"
]))

TK_XYVIEW_METHODS = tuple(set([
    m for m in
    list(tk.XView.__dict__.keys()) +
    list(tk.YView.__dict__.keys())
    if m[0] != "_" and m != "config" and m != "configure"
]))


class ScrollableOuter(tk.Frame):
    """Custom frame widget.
    This will be parent of widget inherited XView and/or YView"""
    def __init__(self, master, scroll=None, cnf={}, **kw):
        tk.Frame.__init__(self, master)
        if scroll is None:
            scroll = tk.X + tk.Y
        self.__x_scr, self.__y_scr, self.__interior = None, None, None
        if tk.Y in scroll:
            self.__y_scr = tk.Scrollbar(self, orient=tk.VERTICAL)
            self.__y_scr.grid(row=0, column=1, sticky=tk.NW+tk.S)
        if tk.X in scroll:
            self.__x_scr = tk.Scrollbar(self, orient=tk.HORIZONTAL)
            self.__x_scr.grid(row=1, column=0, sticky=tk.E+tk.W)
        tk.Frame.config(self, cnf, **kw)

    def set_interior(self, widget):
        self.__interior = widget
        if self.__x_scr is not None:
            widget.configure(xscrollcommand=self.__x_scr.set)
            self.__x_scr.config(command=widget.xview)
        if self.__y_scr is not None:
            widget.configure(yscrollcommand=self.__y_scr.set)
            self.__y_scr.config(command=widget.yview)
        widget.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

    interior = property(fget=lambda self: self.__interior)

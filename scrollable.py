"""Tkinter modified Frame widgets inherited XView and/or YView."""
import tkinter as tk
from tkinter import ttk
from composite import TK_GEOMETRY_METHODS, InteriorAndExterior


TK_XYVIEW_METHODS = tuple(set([
    m for m in
    list(tk.XView.__dict__.keys()) +
    list(tk.YView.__dict__.keys())
    if m[0] != '_' and m != 'config' and m != 'configure'
]))


class ScrollableOuter(tk.Frame):
    """Custom frame widget.
    This will be parent of widget inherited XView and/or YView"""
    def __init__(self, master, scroll=None, **kw):
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
        tk.Frame.config(self, **kw)

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


class XYFrame(tk.Frame, tk.XView, tk.YView, InteriorAndExterior):
    """Pure tkinter composite widget made with Canvas(outer) and Frame(core).
    Scrollable Frame widget.
    """
    def __init__(self, master=None, **kw):
        exterior = tk.Canvas(master, highlightthickness=0, takefocus=False)
        tk.Frame.__init__(self, exterior)

        self.__id = exterior.create_window(0, 0, window=self, anchor=tk.NW)
        self.bind('<Configure>', self.__on_config, '+')

        InteriorAndExterior.__init__(self, exterior)

        for m in TK_XYVIEW_METHODS:
            setattr(self, m, getattr(exterior, m))

        exterior.bind('<MouseWheel>', self.on_scroll, '+')
        self.bind('<MouseWheel>', self.on_scroll, '+')
        self.bbox = exterior.grid_bbox

        exter_move = [
            'relief', 'cursor', 'bd', 'highlightthickness', 'borderwidth',
            'height', 'width']
        inter_move = ['takefocus']

        for k in exter_move:
            self._common_kw.pop(k)
            self._exterior_kw[k] = k

        for k in inter_move:
            self._common_kw.pop(k)
            self._interior_kw[k] = k

        self.config = self.configure
        self.config(**kw)

    def on_scroll(self, event):
        """On scroll event."""
        u, l = self._exterior.yview()
        if u == 0 and l == 1:
            return None
        direction = 0
        if event.num == 5 or event.delta == -120:
            direction = 1
        if event.num == 4 or event.delta == 120:
            direction = -1
        self._exterior.yview_scroll(direction, tk.UNITS)

    def on_focus_moveto_y(self, event):
        widget_y = event.widget.winfo_y()
        widget_h = event.widget.winfo_reqheight()
        y1, y2, reqh = widget_y, widget_y + widget_h, self.winfo_reqheight()
        yv_u, yv_l = self._exterior.yview()
        if not (yv_u <= y1/reqh <= yv_l) or not (yv_u <= y2/reqh <= yv_l):
            self._exterior.yview_moveto(widget_y/reqh)

    def on_focus_moveto_x(self, event):
        widget_x = event.widget.winfo_x()
        widget_w = event.widget.winfo_reqwidth()
        x1, x2, reqw = widget_x, widget_x + widget_w, self.winfo_reqwidth()
        xv_u, xv_l = self._exterior.xview()
        if not (xv_u <= x1/reqw <= xv_l) or not (xv_u <= x2/reqw <= xv_l):
            self._exterior.xview_moveto(widget_x/reqw)

    def __on_config(self, *dummy):
        frame_reqh = tk.Frame.winfo_reqheight(self)
        exterior_h = self._exterior.winfo_height()
        frame_reqw = tk.Frame.winfo_reqwidth(self)
        exterior_w = self._exterior.winfo_width()
        if frame_reqh != exterior_h or frame_reqw != exterior_w:
            self._exterior.update_idletasks()
            self._exterior.config(scrollregion=self._exterior.bbox(self.__id))

    def configure(self, **kw):
        return InteriorAndExterior.configure(self, **kw)

    def destroy(self):
        return InteriorAndExterior.destroy(self)

    def keys(self):
        return InteriorAndExterior.keys(self)

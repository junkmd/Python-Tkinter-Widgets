"""Tkinter modified Frame widgets inherited XView and/or YView."""
import tkinter as tk
from tkinter import ttk


TK_GEOMETRY_METHODS = tuple(set([
    m for m in
    list(tk.Pack.__dict__.keys()) +
    list(tk.Grid.__dict__.keys()) +
    list(tk.Place.__dict__.keys())
    if m[0] != '_' and m != 'config' and m != 'configure'
]))

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


class XYFrame(tk.Frame, tk.XView, tk.YView):
    """Pure tkinter composite widget made with Canvas(outer) and Frame(core).
    Scrollable Frame widget.
    """
    def __init__(self, master=None, **kw):
        self.__outer = tk.Canvas(master, highlightthickness=0, takefocus=False)
        tk.Frame.__init__(self, self.__outer)

        self.__id = self.__outer.create_window(0, 0, window=self, anchor=tk.NW)
        self.bind('<Configure>', self.__on_config, '+')

        for m in TK_GEOMETRY_METHODS + TK_XYVIEW_METHODS + (
                'winfo_parent',
                ):
            setattr(self, m, getattr(self.__outer, m))

        self.__outer.bind('<MouseWheel>', self.on_scroll, '+')
        self.bind('<MouseWheel>', self.on_scroll, '+')
        self.bbox = self.__outer.grid_bbox

        canvas_keys = self.__outer.keys()
        frame_keys = tk.Frame.keys(self)
        common_factors = list(set(canvas_keys) & set(frame_keys))
        canvas_specs = list(set(canvas_keys) - set(frame_keys))
        frame_specs = list(set(frame_keys) - set(canvas_keys))
        self.__common_k = [
            'highlightbackground', 'bg', 'highlightcolor', 'background']
        common_but_frame = ['takefocus']
        common_but_canvas = list(set(common_factors) - set(common_but_frame))
        self.__frame_k = frame_specs + common_but_frame
        self.__canvas_k = canvas_specs + common_but_canvas

        self.config = self.configure
        self.config(**kw)

    def configure(self, **kw):
        frame_kw, canvas_kw = {}, {}
        for k, v in kw.items():
            if k in self.__common_k:
                frame_kw[k] = v
                canvas_kw[k] = v
            elif k in self.__frame_k:
                frame_kw[k] = v
            elif k in self.__canvas_k:
                canvas_kw[k] = v
        self.__outer.config(**canvas_kw)
        tk.Frame.config(self, **frame_kw)

    def on_scroll(self, event):
        """On scroll event."""
        u, l = self.__outer.yview()
        if u == 0 and l == 1:
            return None
        direction = 0
        if event.num == 5 or event.delta == -120:
            direction = 1
        if event.num == 4 or event.delta == 120:
            direction = -1
        self.__outer.yview_scroll(direction, tk.UNITS)

    def on_focus_moveto_y(self, event):
        widget_y = event.widget.winfo_y()
        widget_h = event.widget.winfo_reqheight()
        y1, y2, reqh = widget_y, widget_y + widget_h, self.winfo_reqheight()
        yv_u, yv_l = self.__outer.yview()
        if not (yv_u <= y1/reqh <= yv_l) or not (yv_u <= y2/reqh <= yv_l):
            self.__outer.yview_moveto(widget_y/reqh)

    def on_focus_moveto_x(self, event):
        widget_x = event.widget.winfo_x()
        widget_w = event.widget.winfo_reqwidth()
        x1, x2, reqw = widget_x, widget_x + widget_w, self.winfo_reqwidth()
        xv_u, xv_l = self.__outer.xview()
        if not (xv_u <= x1/reqw <= xv_l) or not (xv_u <= x2/reqw <= xv_l):
            self.__outer.xview_moveto(widget_x/reqw)

    def __on_config(self, *dummy):
        if tk.Frame.winfo_reqheight(self) != self.__outer.winfo_height() \
                or tk.Frame.winfo_reqwidth(self) != self.__outer.winfo_width():
            self.__outer.update_idletasks()
            self.__outer.config(scrollregion=self.__outer.bbox(self.__id))

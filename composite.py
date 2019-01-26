"""Tkinter combination widgets' base classes."""
import tkinter as tk
from tkinter import ttk


TK_GEOMETRY_METHODS = tuple(set([
    m for m in
    list(tk.Pack.__dict__.keys()) +
    list(tk.Grid.__dict__.keys()) +
    list(tk.Place.__dict__.keys())
    if m[0] != '_' and m != 'config' and m != 'configure'
]))


class InteriorAndExterior(tk.Misc):
    """Internal class."""
    def __init__(self, exterior):
        self._exterior = exterior
        for m in TK_GEOMETRY_METHODS:
            setattr(self, m, getattr(exterior, m))
        self.winfo_parent = exterior.winfo_parent
        inter_keys = self.keys()
        exter_keys = exterior.keys()
        common_keys = list(set(inter_keys) & set(exter_keys))
        inter_only = list(set(inter_keys) - set(exter_keys))
        exter_only = list(set(exter_keys) - set(inter_keys))
        c_kw, i_kw, e_kw = {}, {}, {}
        for keys, kw in zip(
                [common_keys, inter_only, exter_only],
                [c_kw, i_kw, e_kw]):
            for k in keys:
                kw[k] = k
        self._common_kw = c_kw
        self._interior_kw, self._exterior_kw = i_kw, e_kw

    def _dispatch_each_options(self, **kw):
        """Internal function.
        Returns interior, exterior option."""
        inter_opts, exter_opts = {}, {}
        for k, v in kw.items():
            if k in self._common_kw.keys():
                inter_opts[self._common_kw[k]] = kw[k]
                exter_opts[self._common_kw[k]] = kw[k]
            if k in self._interior_kw.keys():
                inter_opts[self._interior_kw[k]] = kw[k]
            if k in self._exterior_kw.keys():
                exter_opts[self._exterior_kw[k]] = kw[k]
        return (inter_opts, exter_opts)

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


class CompositeWidgetError(Exception):
    pass


class InteriorAndExterior:
    """Internal class."""
    def __init__(self, exterior):
        self._exterior = exterior

        if self in self._exterior.winfo_children():
            pass
        else:
            raise CompositeWidgetError(
                "Interior must be childrens of Exterior.")

        for m in TK_GEOMETRY_METHODS:
            setattr(self, m, getattr(exterior, m))
        self.winfo_parent = exterior.winfo_parent
        self._base = self.__class__.mro()[1]
        inter_keys = self._base.keys(self)
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
        self.config = self.configure

    def _dispatch_each_options(self, **kw):
        """Internal function.
        Returns interior, exterior option."""
        inter_opts, exter_opts = {}, {}
        for k, v in kw.items():
            if k in self._common_kw.keys():
                inter_opts[self._common_kw[k]] = kw[k]
                exter_opts[self._common_kw[k]] = kw[k]
            elif k in self._interior_kw.keys():
                inter_opts[self._interior_kw[k]] = kw[k]
            elif k in self._exterior_kw.keys():
                exter_opts[self._exterior_kw[k]] = kw[k]
            else:
                raise tk.TclError('unknown option \"%s\"' % ('-' + k, ))
        return (inter_opts, exter_opts)

    def destroy(self):
        """Destroy this and all descendants widgets."""
        # Destroy self._exterior and its children widgets including interior.
        # For avoiding RecursionError,
        # removing self(interior) from self._exterior.children and
        # destroy the interior and its children widgets
        # before self._exterior.destroy() method will destroy the interior.

        del_dict = {}  # deleting from self._exterior.children dictionary
        for k, v in self._exterior.children.items():
            if v is self:
                del_dict[k] = v
        for k, v in del_dict.items():
            del self._exterior.children[k]
            v.destroy()
        self._exterior.destroy()

    def keys(self):
        inter = self._interior_kw.keys()
        exter = self._exterior_kw.keys()
        common = self._common_kw.keys()
        keyset = list(set(list(inter) + list(exter) + list(common)))
        keyset.sort()
        return keyset

    def configure(self, **kw):
        inter_kw, exter_kw = self._dispatch_each_options(**kw)
        self._exterior.config(**exter_kw)
        self._base.config(self, **inter_kw)

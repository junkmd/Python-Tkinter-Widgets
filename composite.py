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


class CompositeWidgetError(tk.TclError):
    pass


class InteriorAndExterior:
    """Internal class."""
    def __init__(self, exterior):
        self._exterior = exterior

        if self not in exterior.winfo_children():
            raise CompositeWidgetError(
                "Interior must be childrens of Exterior.")

        for m in TK_GEOMETRY_METHODS:
            setattr(self, m, getattr(exterior, m))

        self._base = self.__class__.mro()[1]  # Base class of composite widget.
        if not issubclass(self._base, tk.Widget):
            raise CompositeWidgetError(
                "Base class of composite widget "
                "must be subclass of tk.BaseWidget.")

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
        self.winfo_parent = exterior.winfo_parent
        self.config = self.configure = self.__configure
        self._base.__setitem__ = self.__setitem
        self.keys = self.__keys
        self.cget = self.__cget
        self._base.__getitem__ = self.__cget
        self.destroy = self.__destroy

    def __dispatch_each_options(self, **kw):
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

    def __destroy(self):
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
        self._base.destroy(self)
        self._exterior.destroy()

    def __keys(self):
        """Return a list of all resource names of this widget."""
        inter = self._interior_kw.keys()
        exter = self._exterior_kw.keys()
        common = self._common_kw.keys()
        keys = list(set(list(inter) + list(exter) + list(common)))
        keys.sort()
        return keys

    def __configure(self, **kw):
        """Configure resources of a widget.
        The values for resources are specified as keyword
        arguments. To get an overview about
        the allowed keyword arguments call the method keys."""
        inter_kw, exter_kw = self.__dispatch_each_options(**kw)
        self._exterior.config(**exter_kw)
        self._base.config(self, **inter_kw)

    def __setitem(self, key, value):
        self.__configure(**{key: value})

    def __cget(self, key):
        """Return the resource value for a KEY given as string."""
        if key in self._common_kw.keys():
            return self._base.cget(self, self._common_kw[key])
        else:
            if key in self._interior_kw.keys():
                return self._base.cget(self, self._interior_kw[key])
            elif key in self._exterior_kw.keys():
                return self._exterior.cget(self._exterior_kw[key])
            else:
                raise CompositeWidgetError('unknown option \"-%s\"' % key)

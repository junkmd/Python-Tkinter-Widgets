"""
references:

https://www.tcl.tk/man/tcl8.4/TkCmd/entry.htm
"""
import tkinter as tk
from numbers import Number


class Validation(object):
    """Container for the properties of a validation."""
    def __init__(self, widget, **kw):
        self.__widget = widget
        self.__kw = kw

    @property
    def type_of_action(self):
        """
        Type of action.
        1 for insert,
        0 for delete,
        -1 for focus, forced or changing textvariable.
        """
        return int(self.__kw['d'])

    @property
    def index(self):
        """
        Index of the beginning of the insertion or deletion.
        -1 for focus, forced or changing textvariable."""
        return int(self.__kw['i'])

    @property
    def text_if_allowed(self):
        """
        The text in the entry will have if the change is allowed.
        """
        return self.__kw['P']

    @property
    def text_before_change(self):
        """
        The text in the entry before the change.
        """
        return self.__kw['s']

    @property
    def text_what_changed(self):
        """
        The text in the entry being inserted or deleted.
        """
        return self.__kw['S']

    @property
    def type_of_validation(self):
        """
        The value of the entry's validate option.
        """
        return self.__kw['v']

    @property
    def reason_for_callback(self):
        """
        The reason for this callback.
        Returns 'focusin', 'focusout', 'key', or 'forced'.
        """
        return self.__kw['V']

    @property
    def widget(self):
        """
        The entry widget.
        """
        return self.__widget

    def __repr__(self):
        members = [m for m in dir(self) if m[0] != '_']
        items = []
        for m in members:
            val = getattr(self, m)
            if isinstance(val, Number):
                items.append('%s=%s' % (m, val))
            elif isinstance(val, str):
                items.append('%s=\'%s\'' % (m, val))
            else:
                items.append('%s=%s' % (m, val.__repr__()))
        return '<validation %s>' % " ".join(items)


class BaseEntryWithValidator(tk.Entry):
    """Internal class for tkinter Entry with valiator."""
    # reference of tcl/tk built-in commands is below;
    # https://www.tcl.tk/man/tcl8.4/TkCmd/entry.htm
    def __init__(self, master, **kw):
        """Construct an entry widget with validator."""
        tk.Entry.__init__(self, master)
        vcmd = (
            self.register(self.__vcmd_callback),
            '%d', '%i', '%P', '%s', '%S', '%v', '%V'
        )
        # reference of validatecommand arguments is below;
        # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/entry-validation.html
        #
        # '%d'	Action code: 0 for an attempted deletion, 1 for
        #       an attempted insertion, or -1 if the callback was called for
        #       focus in, focus out, or a change to the textvariable.
        #
        # '%i'	When the user attempts to insert or delete text,
        #       this argument will be the index of the beginning of
        #       the insertion or deletion. If the callback was due to
        #       focus in, focus out, or a change to the textvariable,
        #       the argument will be -1.
        #
        # '%P'	The value that the text will have if the change is allowed.
        #
        # '%s'	The text in the entry before the change.
        #
        # '%S'	If the call was due to an insertion or deletion, this argument
        #       will be the text being inserted or deleted.
        #
        # '%v'	The current value of the widget's validate option.
        #
        # '%V'	The reason for this callback: one of 'focusin', 'focusout',
        #       'key', or 'forced' if the textvariable was changed.
        #
        # '%W'	The name of the widget.
        #
        tk.Entry.configure(self, validate='all', vcmd=vcmd)
        tk.Entry.configure(self, **kw)

    def __vcmd_callback(self, d, i, P, s, S, v, V):
        """Internal function.
        Callback function of native Entry's 'validatecommand' option."""
        validation = Validation(self, d=d, i=i, P=P, s=s, S=S, v=v, V=V)
        return self.validate(validation)

    def validate(self, validation):
        """
        Validating the changing text in the entry.
        """
        return True


class Entry_LimitedLen(BaseEntryWithValidator):
    def __init__(self, master, length=None, **kw):
        self.__len = length
        BaseEntryWithValidator.__init__(self, master, **kw)

    def validate(self, validation):
        if self.__len is None:
            return True
        after = validation.text_if_allowed
        if len(after) > self.__len:
            return False
        else:
            return True


if __name__ == "__main__":
    root = tk.Tk()
    ent = Entry_LimitedLen(root, length=10)
    ent.pack()

    root.mainloop()
